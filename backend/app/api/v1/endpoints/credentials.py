from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
import logging
from datetime import datetime, timedelta
import qrcode
import json
import base64
from io import BytesIO

from app.core.database import get_db
from app.core.config import settings
from app.models.user import User
from app.models.document import Document
from app.models.credential import Credential, CredentialTypeEnum
from app.schemas.credential import CredentialCreate, CredentialResponse, CredentialUpdate
from app.core.security import get_current_user
from app.services.qr_service import QRCodeService
from app.services.blockchain_service import BlockchainService

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/issue", response_model=CredentialResponse)
async def issue_credential(
    background_tasks: BackgroundTasks,
    credential_data: CredentialCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Issue a new verifiable credential
    """
    try:
        # Check if user can issue credentials
        if current_user.role not in ["admin", "issuer"]:
            raise HTTPException(status_code=403, detail="Only issuers can issue credentials")
        
        # Verify document exists and is verified
        document = db.query(Document).filter(Document.id == credential_data.document_id).first()
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        if document.status != "verified":
            raise HTTPException(status_code=400, detail="Document must be verified before issuing credential")
        
        # Check if credential already exists
        existing_credential = db.query(Credential).filter(
            Credential.document_id == credential_data.document_id,
            Credential.holder_id == credential_data.holder_id
        ).first()
        
        if existing_credential:
            raise HTTPException(status_code=400, detail="Credential already exists for this document and holder")
        
        # Create credential
        credential = Credential(
            document_id=credential_data.document_id,
            holder_id=credential_data.holder_id,
            issuer_id=current_user.id,
            credential_type=credential_data.credential_type,
            title=credential_data.title,
            description=credential_data.description,
            metadata=credential_data.metadata,
            issued_at=datetime.utcnow(),
            expires_at=datetime.utcnow() + timedelta(days=credential_data.validity_days),
            status="active"
        )
        
        db.add(credential)
        db.commit()
        db.refresh(credential)
        
        # Generate QR code in background
        background_tasks.add_task(
            generate_credential_qr,
            credential.id,
            db
        )
        
        # Anchor to blockchain in background
        background_tasks.add_task(
            anchor_credential_to_blockchain,
            credential.id,
            document.file_hash,
            current_user.did,
            db
        )
        
        return CredentialResponse(
            id=credential.id,
            title=credential.title,
            credential_type=credential.credential_type,
            holder_id=credential.holder_id,
            issuer_id=credential.issuer_id,
            status=credential.status,
            issued_at=credential.issued_at,
            expires_at=credential.expires_at
        )
        
    except Exception as e:
        logger.error(f"Error issuing credential: {str(e)}")
        raise HTTPException(status_code=500, detail="Credential issuance failed")

@router.get("/my-credentials")
async def get_my_credentials(
    limit: int = 10,
    offset: int = 0,
    status: Optional[str] = None,
    credential_type: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get credentials for the current user
    """
    try:
        query = db.query(Credential).filter(Credential.holder_id == current_user.id)
        
        if status:
            query = query.filter(Credential.status == status)
        
        if credential_type:
            query = query.filter(Credential.credential_type == credential_type)
        
        # Get total count
        total = query.count()
        
        # Get paginated credentials
        credentials = query.order_by(Credential.issued_at.desc()).offset(offset).limit(limit).all()
        
        return [
            {
                "id": cred.id,
                "credential_type": cred.credential_type,
                "status": cred.status,
                "issued_at": cred.issued_at.isoformat() if cred.issued_at else None,
                "expires_at": cred.expires_at.isoformat() if cred.expires_at else None,
                "revoked_at": cred.revoked_at.isoformat() if cred.revoked_at else None,
                "issuer": {
                    "id": cred.issuer.id,
                    "name": cred.issuer.full_name,
                    "organization": cred.issuer.organization.name if cred.issuer.organization else None
                } if cred.issuer else None,
                "document": {
                    "id": cred.document.id,
                    "title": cred.document.title,
                    "document_type": cred.document.document_type
                } if cred.document else None,
                "metadata": cred.metadata
            }
            for cred in credentials
        ]
        
    except Exception as e:
        logger.error(f"Error getting user credentials: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get credentials")

@router.get("/issued-credentials", response_model=List[CredentialResponse])
async def get_issued_credentials(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    limit: int = 10,
    offset: int = 0
):
    """
    Get credentials issued by the current user
    """
    if current_user.role not in ["admin", "issuer"]:
        raise HTTPException(status_code=403, detail="Only issuers can view issued credentials")
    
    credentials = db.query(Credential).filter(
        Credential.issuer_id == current_user.id
    ).order_by(Credential.issued_at.desc()).offset(offset).limit(limit).all()
    
    return [
        CredentialResponse(
            id=cred.id,
            title=cred.title,
            credential_type=cred.credential_type,
            holder_id=cred.holder_id,
            issuer_id=cred.issuer_id,
            status=cred.status,
            issued_at=cred.issued_at,
            expires_at=cred.expires_at
        )
        for cred in credentials
    ]

@router.get("/{credential_id}", response_model=CredentialResponse)
async def get_credential(
    credential_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get specific credential details
    """
    credential = db.query(Credential).filter(Credential.id == credential_id).first()
    if not credential:
        raise HTTPException(status_code=404, detail="Credential not found")
    
    # Check permissions
    if (credential.holder_id != current_user.id and 
        credential.issuer_id != current_user.id and 
        current_user.role != "admin"):
        raise HTTPException(status_code=403, detail="Access denied")
    
    return CredentialResponse(
        id=credential.id,
        title=credential.title,
        credential_type=credential.credential_type,
        holder_id=credential.holder_id,
        issuer_id=credential.issuer_id,
        status=credential.status,
        issued_at=credential.issued_at,
        expires_at=credential.expires_at,
        metadata=credential.metadata
    )

@router.put("/{credential_id}/revoke")
async def revoke_credential(
    credential_id: int,
    reason: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Revoke a credential
    """
    credential = db.query(Credential).filter(Credential.id == credential_id).first()
    if not credential:
        raise HTTPException(status_code=404, detail="Credential not found")
    
    # Check permissions
    if (credential.issuer_id != current_user.id and current_user.role != "admin"):
        raise HTTPException(status_code=403, detail="Only issuer or admin can revoke credentials")
    
    # Update credential status
    credential.status = "revoked"
    credential.revoked_at = datetime.utcnow()
    credential.revoked_by_id = current_user.id
    credential.revocation_reason = reason
    
    db.commit()
    
    # Revoke on blockchain in background
    background_tasks = BackgroundTasks()
    background_tasks.add_task(
        revoke_credential_on_blockchain,
        credential_id,
        reason,
        db
    )
    
    return {"message": "Credential revoked successfully"}

@router.get("/{credential_id}/qr-code")
async def get_credential_qr(
    credential_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get QR code for credential verification
    """
    credential = db.query(Credential).filter(Credential.id == credential_id).first()
    if not credential:
        raise HTTPException(status_code=404, detail="Credential not found")
    
    # Check permissions
    if credential.holder_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Generate QR code data
    qr_data = {
        "credential_id": credential.id,
        "document_hash": credential.document.file_hash,
        "verification_url": f"{settings.NEXT_PUBLIC_APP_URL}/verify/{credential.id}"
    }
    
    qr_service = QRCodeService()
    qr_code_base64 = qr_service.generate_qr_code(json.dumps(qr_data))
    
    return {
        "credential_id": credential.id,
        "qr_code": qr_code_base64,
        "verification_url": qr_data["verification_url"]
    }

async def generate_credential_qr(credential_id: int, db: Session):
    """
    Background task to generate QR code for credential
    """
    try:
        credential = db.query(Credential).filter(Credential.id == credential_id).first()
        if not credential:
            return
        
        # Generate QR code data
        qr_data = {
            "credential_id": credential.id,
            "document_hash": credential.document.file_hash,
            "verification_url": f"{settings.NEXT_PUBLIC_APP_URL}/verify/{credential.id}"
        }
        
        qr_service = QRCodeService()
        qr_code_base64 = qr_service.generate_qr_code(json.dumps(qr_data))
        
        # Store QR code in credential metadata
        if not credential.metadata:
            credential.metadata = {}
        credential.metadata["qr_code"] = qr_code_base64
        
        db.commit()
        logger.info(f"QR code generated for credential {credential_id}")
        
    except Exception as e:
        logger.error(f"Error generating QR code: {str(e)}")

async def anchor_credential_to_blockchain(credential_id: int, file_hash: str, user_did: str, db: Session):
    """
    Background task to anchor credential to blockchain
    """
    try:
        blockchain_service = BlockchainService()
        
        # Anchor credential to blockchain
        result = await blockchain_service.anchor_document(file_hash, user_did)
        
        # Update credential with blockchain info
        credential = db.query(Credential).filter(Credential.id == credential_id).first()
        if credential:
            if not credential.metadata:
                credential.metadata = {}
            credential.metadata["blockchain_hash"] = result["blockchain_hash"]
            credential.metadata["transaction_hash"] = result["transaction_hash"]
            db.commit()
        
        logger.info(f"Credential {credential_id} anchored to blockchain")
        
    except Exception as e:
        logger.error(f"Error anchoring credential to blockchain: {str(e)}")

async def revoke_credential_on_blockchain(credential_id: int, reason: str, db: Session):
    """
    Background task to revoke credential on blockchain
    """
    try:
        credential = db.query(Credential).filter(Credential.id == credential_id).first()
        if not credential:
            return
        
        blockchain_service = BlockchainService()
        
        # Revoke on blockchain
        await blockchain_service.revoke_document(
            credential.document.file_hash,
            credential.issuer.did,
            reason
        )
        
        logger.info(f"Credential {credential_id} revoked on blockchain")
        
    except Exception as e:
        logger.error(f"Error revoking credential on blockchain: {str(e)}")
