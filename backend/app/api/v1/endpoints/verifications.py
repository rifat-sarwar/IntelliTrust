from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
import logging
from datetime import datetime
import json

from app.core.database import get_db
from app.core.config import settings
from app.models.user import User
from app.models.document import Document
from app.models.credential import Credential
from app.models.verification import Verification, VerificationLog
from app.schemas.verification import VerificationCreate, VerificationResponse
from app.core.security import get_current_user
from app.services.blockchain_service import BlockchainService
from app.services.ai_integration import AIIntegrationService

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/verify-document", response_model=VerificationResponse)
async def verify_document(
    background_tasks: BackgroundTasks,
    document_hash: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Verify a document by its hash
    """
    try:
        # Find document by hash
        document = db.query(Document).filter(Document.file_hash == document_hash).first()
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Create verification record
        verification = Verification(
            document_id=document.id,
            verifier_id=current_user.id,
            verification_type="document_verification",
            status="processing"
        )
        
        db.add(verification)
        db.commit()
        db.refresh(verification)
        
        # Start verification process in background
        background_tasks.add_task(
            perform_document_verification,
            verification.id,
            document_hash,
            db
        )
        
        return VerificationResponse(
            id=verification.id,
            document_id=document.id,
            verification_type="document_verification",
            status="processing",
            message="Document verification started"
        )
        
    except Exception as e:
        logger.error(f"Error starting document verification: {str(e)}")
        raise HTTPException(status_code=500, detail="Verification failed")

@router.post("/verify-credential", response_model=VerificationResponse)
async def verify_credential(
    background_tasks: BackgroundTasks,
    credential_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Verify a credential by its ID
    """
    try:
        # Find credential
        credential = db.query(Credential).filter(Credential.id == credential_id).first()
        if not credential:
            raise HTTPException(status_code=404, detail="Credential not found")
        
        # Create verification record
        verification = Verification(
            credential_id=credential.id,
            verifier_id=current_user.id,
            verification_type="credential_verification",
            status="processing"
        )
        
        db.add(verification)
        db.commit()
        db.refresh(verification)
        
        # Start verification process in background
        background_tasks.add_task(
            perform_credential_verification,
            verification.id,
            credential_id,
            db
        )
        
        return VerificationResponse(
            id=verification.id,
            credential_id=credential.id,
            verification_type="credential_verification",
            status="processing",
            message="Credential verification started"
        )
        
    except Exception as e:
        logger.error(f"Error starting credential verification: {str(e)}")
        raise HTTPException(status_code=500, detail="Verification failed")

@router.get("/{verification_id}", response_model=VerificationResponse)
async def get_verification_result(
    verification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get verification result
    """
    verification = db.query(Verification).filter(Verification.id == verification_id).first()
    if not verification:
        raise HTTPException(status_code=404, detail="Verification not found")
    
    # Check permissions
    if verification.verifier_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Access denied")
    
    return VerificationResponse(
        id=verification.id,
        document_id=verification.document_id,
        credential_id=verification.credential_id,
        verification_type=verification.verification_type,
        status=verification.status,
        result=verification.result,
        verified_at=verification.verified_at
    )

@router.get("/my-verifications", response_model=List[VerificationResponse])
async def get_my_verifications(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    limit: int = 10,
    offset: int = 0
):
    """
    Get user's verification history
    """
    verifications = db.query(Verification).filter(
        Verification.verifier_id == current_user.id
    ).order_by(Verification.created_at.desc()).offset(offset).limit(limit).all()
    
    return [
        VerificationResponse(
            id=ver.id,
            document_id=ver.document_id,
            credential_id=ver.credential_id,
            verification_type=ver.verification_type,
            status=ver.status,
            result=ver.result,
            verified_at=ver.verified_at
        )
        for ver in verifications
    ]

@router.post("/verify-qr")
async def verify_qr_code(
    qr_data: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Verify document/credential from QR code data
    """
    try:
        # Parse QR code data
        try:
            qr_info = json.loads(qr_data)
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid QR code data")
        
        verification_type = qr_info.get("type")
        
        if verification_type == "credential_verification":
            credential_id = qr_info.get("credential_id")
            if not credential_id:
                raise HTTPException(status_code=400, detail="Missing credential ID in QR data")
            
            # Verify credential
            credential = db.query(Credential).filter(Credential.id == credential_id).first()
            if not credential:
                raise HTTPException(status_code=404, detail="Credential not found")
            
            # Check if credential is valid
            if credential.status != "active":
                return {
                    "verified": False,
                    "reason": f"Credential is {credential.status}",
                    "credential_info": {
                        "id": credential.id,
                        "title": credential.title,
                        "status": credential.status
                    }
                }
            
            # Verify on blockchain
            blockchain_service = BlockchainService()
            blockchain_result = await blockchain_service.verify_document(credential.document.file_hash)
            
            return {
                "verified": blockchain_result["verified"] and credential.status == "active",
                "credential_info": {
                    "id": credential.id,
                    "title": credential.title,
                    "issuer": credential.issuer.full_name,
                    "holder": credential.holder.full_name,
                    "issued_at": credential.issued_at,
                    "expires_at": credential.expires_at
                },
                "blockchain_verified": blockchain_result["verified"],
                "verification_timestamp": datetime.utcnow()
            }
            
        elif verification_type == "document_verification":
            document_hash = qr_info.get("document_hash")
            if not document_hash:
                raise HTTPException(status_code=400, detail="Missing document hash in QR data")
            
            # Verify document
            document = db.query(Document).filter(Document.file_hash == document_hash).first()
            if not document:
                raise HTTPException(status_code=404, detail="Document not found")
            
            # Verify on blockchain
            blockchain_service = BlockchainService()
            blockchain_result = await blockchain_service.verify_document(document_hash)
            
            return {
                "verified": blockchain_result["verified"] and document.status == "verified",
                "document_info": {
                    "id": document.id,
                    "title": document.title,
                    "owner": document.owner.full_name,
                    "status": document.status,
                    "verified_at": document.verified_at
                },
                "blockchain_verified": blockchain_result["verified"],
                "verification_timestamp": datetime.utcnow()
            }
        
        else:
            raise HTTPException(status_code=400, detail="Unknown verification type")
            
    except Exception as e:
        logger.error(f"Error verifying QR code: {str(e)}")
        raise HTTPException(status_code=500, detail="QR verification failed")

async def perform_document_verification(verification_id: int, document_hash: str, db: Session):
    """
    Background task to perform document verification
    """
    try:
        verification = db.query(Verification).filter(Verification.id == verification_id).first()
        if not verification:
            return
        
        document = db.query(Document).filter(Document.file_hash == document_hash).first()
        if not document:
            verification.status = "failed"
            verification.result = {"error": "Document not found"}
            db.commit()
            return
        
        # Perform blockchain verification
        blockchain_service = BlockchainService()
        blockchain_result = await blockchain_service.verify_document(document_hash)
        
        # Perform AI verification if needed
        ai_result = None
        if document.ai_verified is None:
            ai_service = AIIntegrationService()
            ai_result = await ai_service.get_analysis_results(document_hash)
        
        # Determine overall verification result
        blockchain_verified = blockchain_result["verified"]
        ai_verified = document.ai_verified if document.ai_verified is not None else (ai_result is not None)
        
        overall_verified = blockchain_verified and ai_verified
        
        # Update verification record
        verification.status = "completed"
        verification.result = {
            "blockchain_verified": blockchain_verified,
            "ai_verified": ai_verified,
            "overall_verified": overall_verified,
            "blockchain_result": blockchain_result,
            "ai_result": ai_result
        }
        verification.verified_at = datetime.utcnow()
        
        # Create verification log
        log = VerificationLog(
            verification_id=verification.id,
            action="document_verification",
            details=verification.result
        )
        
        db.add(log)
        db.commit()
        
        logger.info(f"Document verification completed: {verification_id}")
        
    except Exception as e:
        logger.error(f"Error in document verification: {str(e)}")
        verification = db.query(Verification).filter(Verification.id == verification_id).first()
        if verification:
            verification.status = "failed"
            verification.result = {"error": str(e)}
            db.commit()

async def perform_credential_verification(verification_id: int, credential_id: int, db: Session):
    """
    Background task to perform credential verification
    """
    try:
        verification = db.query(Verification).filter(Verification.id == verification_id).first()
        if not verification:
            return
        
        credential = db.query(Credential).filter(Credential.id == credential_id).first()
        if not credential:
            verification.status = "failed"
            verification.result = {"error": "Credential not found"}
            db.commit()
            return
        
        # Check credential status
        if credential.status != "active":
            verification.status = "completed"
            verification.result = {
                "verified": False,
                "reason": f"Credential is {credential.status}",
                "credential_status": credential.status
            }
            verification.verified_at = datetime.utcnow()
            db.commit()
            return
        
        # Verify underlying document on blockchain
        blockchain_service = BlockchainService()
        blockchain_result = await blockchain_service.verify_document(credential.document.file_hash)
        
        # Determine overall verification result
        overall_verified = blockchain_result["verified"] and credential.status == "active"
        
        # Update verification record
        verification.status = "completed"
        verification.result = {
            "blockchain_verified": blockchain_result["verified"],
            "credential_status": credential.status,
            "overall_verified": overall_verified,
            "blockchain_result": blockchain_result
        }
        verification.verified_at = datetime.utcnow()
        
        # Create verification log
        log = VerificationLog(
            verification_id=verification.id,
            action="credential_verification",
            details=verification.result
        )
        
        db.add(log)
        db.commit()
        
        logger.info(f"Credential verification completed: {verification_id}")
        
    except Exception as e:
        logger.error(f"Error in credential verification: {str(e)}")
        verification = db.query(Verification).filter(Verification.id == verification_id).first()
        if verification:
            verification.status = "failed"
            verification.result = {"error": str(e)}
            db.commit()
