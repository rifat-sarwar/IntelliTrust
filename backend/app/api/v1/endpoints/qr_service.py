from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional
import qrcode
import json
import base64
from io import BytesIO
from datetime import datetime, timedelta
import logging

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.document import Document
from app.models.credential import Credential
from app.services.qr_service import QRCodeService as QRService

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/generate/document/{document_id}")
async def generate_document_qr(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Generate QR code for a document
    """
    try:
        # Get document
        document = db.query(Document).filter(Document.id == document_id).first()
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Check permissions
        if document.owner_id != current_user.id and current_user.role not in ["admin", "issuer"]:
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Generate QR code data
        qr_data = {
            "type": "document",
            "document_id": document.id,
            "file_hash": document.file_hash,
            "title": document.title,
            "document_type": document.document_type,
            "status": document.status,
            "blockchain_hash": document.blockchain_hash,
            "ai_verified": document.ai_verified,
            "ai_confidence_score": document.ai_confidence_score,
            "created_at": document.created_at.isoformat(),
            "verified_at": document.verified_at.isoformat() if document.verified_at else None,
            "expires_at": document.expires_at.isoformat() if document.expires_at else None
        }
        
        # Generate QR code
        qr_service = QRService()
        qr_code = qr_service.generate_qr_code(json.dumps(qr_data))
        
        return {
            "document_id": document_id,
            "qr_code": qr_code,
            "qr_data": qr_data,
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error generating document QR code: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate QR code")

@router.post("/generate/credential/{credential_id}")
async def generate_credential_qr(
    credential_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Generate QR code for a credential
    """
    try:
        # Get credential
        credential = db.query(Credential).filter(Credential.id == credential_id).first()
        if not credential:
            raise HTTPException(status_code=404, detail="Credential not found")
        
        # Check permissions
        if credential.holder_id != current_user.id and current_user.role not in ["admin", "issuer"]:
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Generate QR code data
        qr_data = {
            "type": "credential",
            "credential_id": credential.id,
            "credential_type": credential.credential_type,
            "holder_did": credential.holder.did if credential.holder else None,
            "issuer_did": credential.issuer.did if credential.issuer else None,
            "status": credential.status,
            "issued_at": credential.issued_at.isoformat() if credential.issued_at else None,
            "expires_at": credential.expires_at.isoformat() if credential.expires_at else None,
            "revoked_at": credential.revoked_at.isoformat() if credential.revoked_at else None,
            "metadata": credential.metadata
        }
        
        # Generate QR code
        qr_service = QRService()
        qr_code = qr_service.generate_qr_code(json.dumps(qr_data))
        
        return {
            "credential_id": credential_id,
            "qr_code": qr_code,
            "qr_data": qr_data,
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error generating credential QR code: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate QR code")

@router.post("/scan")
async def scan_qr_code(
    qr_data: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Scan and verify QR code data
    """
    try:
        # Parse QR data
        try:
            data = json.loads(qr_data)
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid QR code data")
        
        qr_type = data.get("type")
        
        if qr_type == "document":
            return await scan_document_qr(data, db, current_user)
        elif qr_type == "credential":
            return await scan_credential_qr(data, db, current_user)
        else:
            raise HTTPException(status_code=400, detail="Unknown QR code type")
        
    except Exception as e:
        logger.error(f"Error scanning QR code: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to scan QR code")

async def scan_document_qr(data: Dict[str, Any], db: Session, current_user: User) -> Dict[str, Any]:
    """
    Scan document QR code
    """
    document_id = data.get("document_id")
    file_hash = data.get("file_hash")
    
    if not document_id or not file_hash:
        raise HTTPException(status_code=400, detail="Invalid document QR code data")
    
    # Get document from database
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        return {
            "type": "document",
            "status": "not_found",
            "message": "Document not found in database",
            "qr_data": data
        }
    
    # Verify file hash
    if document.file_hash != file_hash:
        return {
            "type": "document",
            "status": "tampered",
            "message": "Document hash mismatch - possible tampering",
            "qr_data": data,
            "database_hash": document.file_hash
        }
    
    # Check if document is expired
    is_expired = False
    if document.expires_at and document.expires_at < datetime.utcnow():
        is_expired = True
    
    # Get verification status
    verification_status = "unknown"
    if document.blockchain_hash:
        verification_status = "blockchain_verified"
    elif document.ai_verified:
        verification_status = "ai_verified"
    elif document.status == "verified":
        verification_status = "manually_verified"
    
    return {
        "type": "document",
        "status": "valid",
        "document": {
            "id": document.id,
            "title": document.title,
            "document_type": document.document_type,
            "status": document.status,
            "ai_verified": document.ai_verified,
            "ai_confidence_score": document.ai_confidence_score,
            "blockchain_hash": document.blockchain_hash,
            "created_at": document.created_at.isoformat(),
            "verified_at": document.verified_at.isoformat() if document.verified_at else None,
            "expires_at": document.expires_at.isoformat() if document.expires_at else None,
            "is_expired": is_expired
        },
        "verification_status": verification_status,
        "scanned_at": datetime.utcnow().isoformat(),
        "scanned_by": current_user.id
    }

async def scan_credential_qr(data: Dict[str, Any], db: Session, current_user: User) -> Dict[str, Any]:
    """
    Scan credential QR code
    """
    credential_id = data.get("credential_id")
    
    if not credential_id:
        raise HTTPException(status_code=400, detail="Invalid credential QR code data")
    
    # Get credential from database
    credential = db.query(Credential).filter(Credential.id == credential_id).first()
    if not credential:
        return {
            "type": "credential",
            "status": "not_found",
            "message": "Credential not found in database",
            "qr_data": data
        }
    
    # Check if credential is expired
    is_expired = False
    if credential.expires_at and credential.expires_at < datetime.utcnow():
        is_expired = True
    
    # Check if credential is revoked
    is_revoked = credential.status == "revoked"
    
    return {
        "type": "credential",
        "status": "valid",
        "credential": {
            "id": credential.id,
            "credential_type": credential.credential_type,
            "status": credential.status,
            "holder_did": credential.holder.did if credential.holder else None,
            "issuer_did": credential.issuer.did if credential.issuer else None,
            "issued_at": credential.issued_at.isoformat() if credential.issued_at else None,
            "expires_at": credential.expires_at.isoformat() if credential.expires_at else None,
            "revoked_at": credential.revoked_at.isoformat() if credential.revoked_at else None,
            "is_expired": is_expired,
            "is_revoked": is_revoked
        },
        "scanned_at": datetime.utcnow().isoformat(),
        "scanned_by": current_user.id
    }

@router.get("/verify/{verification_code}")
async def verify_qr_code(
    verification_code: str,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Verify QR code without authentication (public endpoint)
    """
    try:
        # Decode verification code
        try:
            decoded_data = base64.b64decode(verification_code).decode('utf-8')
            data = json.loads(decoded_data)
        except (base64.binascii.Error, json.JSONDecodeError, UnicodeDecodeError):
            raise HTTPException(status_code=400, detail="Invalid verification code")
        
        qr_type = data.get("type")
        
        if qr_type == "document":
            return await verify_document_public(data, db)
        elif qr_type == "credential":
            return await verify_credential_public(data, db)
        else:
            raise HTTPException(status_code=400, detail="Unknown verification code type")
        
    except Exception as e:
        logger.error(f"Error verifying QR code: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to verify QR code")

async def verify_document_public(data: Dict[str, Any], db: Session) -> Dict[str, Any]:
    """
    Verify document QR code publicly
    """
    document_id = data.get("document_id")
    file_hash = data.get("file_hash")
    
    if not document_id or not file_hash:
        raise HTTPException(status_code=400, detail="Invalid document verification code")
    
    # Get document from database
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        return {
            "type": "document",
            "status": "not_found",
            "message": "Document not found"
        }
    
    # Verify file hash
    if document.file_hash != file_hash:
        return {
            "type": "document",
            "status": "tampered",
            "message": "Document hash mismatch"
        }
    
    # Check if document is expired
    is_expired = False
    if document.expires_at and document.expires_at < datetime.utcnow():
        is_expired = True
    
    return {
        "type": "document",
        "status": "valid",
        "title": document.title,
        "document_type": document.document_type,
        "ai_verified": document.ai_verified,
        "blockchain_hash": document.blockchain_hash is not None,
        "is_expired": is_expired,
        "verified_at": datetime.utcnow().isoformat()
    }

async def verify_credential_public(data: Dict[str, Any], db: Session) -> Dict[str, Any]:
    """
    Verify credential QR code publicly
    """
    credential_id = data.get("credential_id")
    
    if not credential_id:
        raise HTTPException(status_code=400, detail="Invalid credential verification code")
    
    # Get credential from database
    credential = db.query(Credential).filter(Credential.id == credential_id).first()
    if not credential:
        return {
            "type": "credential",
            "status": "not_found",
            "message": "Credential not found"
        }
    
    # Check if credential is expired
    is_expired = False
    if credential.expires_at and credential.expires_at < datetime.utcnow():
        is_expired = True
    
    # Check if credential is revoked
    is_revoked = credential.status == "revoked"
    
    return {
        "type": "credential",
        "status": "valid" if not is_expired and not is_revoked else "invalid",
        "credential_type": credential.credential_type,
        "is_expired": is_expired,
        "is_revoked": is_revoked,
        "verified_at": datetime.utcnow().isoformat()
    }

@router.get("/history")
async def get_qr_scan_history(
    limit: int = Query(10, description="Number of records to return"),
    offset: int = Query(0, description="Number of records to skip"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get QR code scan history for the current user
    """
    try:
        # This would typically query a QR scan history table
        # For now, return a placeholder response
        return {
            "scans": [],
            "total": 0,
            "limit": limit,
            "offset": offset
        }
        
    except Exception as e:
        logger.error(f"Error getting QR scan history: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get scan history")
