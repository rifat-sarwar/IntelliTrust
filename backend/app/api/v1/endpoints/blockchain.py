from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
import logging
from datetime import datetime

from app.core.database import get_db
from app.core.config import settings
from app.models.user import User
from app.models.document import Document
from app.models.blockchain import BlockchainTransaction
from app.schemas.blockchain import BlockchainTransactionCreate, BlockchainTransactionResponse
from app.core.security import get_current_user
from app.services.blockchain_service import BlockchainService

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/anchor-document", response_model=BlockchainTransactionResponse)
async def anchor_document_to_blockchain(
    background_tasks: BackgroundTasks,
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Anchor a verified document to the blockchain
    """
    try:
        # Get document
        document = db.query(Document).filter(Document.id == document_id).first()
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        
        # Check permissions
        if document.owner_id != current_user.id and current_user.role not in ["admin", "issuer"]:
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Check if document is verified
        if document.status != "verified":
            raise HTTPException(status_code=400, detail="Document must be verified before anchoring")
        
        # Check if already anchored
        if document.blockchain_hash:
            raise HTTPException(status_code=400, detail="Document already anchored to blockchain")
        
        # Start blockchain anchoring in background
        background_tasks.add_task(
            anchor_document_background,
            document_id,
            document.file_hash,
            current_user.did,
            db
        )
        
        return BlockchainTransactionResponse(
            document_id=document_id,
            status="processing",
            message="Document anchoring to blockchain started"
        )
        
    except Exception as e:
        logger.error(f"Error anchoring document: {str(e)}")
        raise HTTPException(status_code=500, detail="Blockchain anchoring failed")

@router.get("/document/{document_id}/transaction", response_model=BlockchainTransactionResponse)
async def get_blockchain_transaction(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get blockchain transaction for a document
    """
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Check permissions
    if document.owner_id != current_user.id and current_user.role not in ["admin", "verifier"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    transaction = db.query(BlockchainTransaction).filter(
        BlockchainTransaction.document_id == document_id
    ).first()
    
    if not transaction:
        raise HTTPException(status_code=404, detail="Blockchain transaction not found")
    
    return BlockchainTransactionResponse(
        document_id=document_id,
        transaction_hash=transaction.transaction_hash,
        block_number=transaction.block_number,
        status=transaction.status,
        timestamp=transaction.created_at
    )

@router.get("/verify/{document_hash}")
async def verify_document_on_blockchain(
    document_hash: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Verify document authenticity on blockchain
    """
    try:
        blockchain_service = BlockchainService()
        
        # Verify on blockchain
        verification_result = await blockchain_service.verify_document(document_hash)
        
        # Get document from database
        document = db.query(Document).filter(Document.file_hash == document_hash).first()
        
        return {
            "document_hash": document_hash,
            "blockchain_verified": verification_result["verified"],
            "block_number": verification_result.get("block_number"),
            "transaction_hash": verification_result.get("transaction_hash"),
            "document_info": {
                "title": document.title if document else None,
                "owner_did": document.owner.did if document and document.owner else None,
                "issued_at": document.created_at if document else None
            }
        }
        
    except Exception as e:
        logger.error(f"Error verifying document on blockchain: {str(e)}")
        raise HTTPException(status_code=500, detail="Blockchain verification failed")

@router.get("/network-status")
async def get_blockchain_network_status():
    """
    Get blockchain network status and health
    """
    try:
        blockchain_service = BlockchainService()
        network_status = await blockchain_service.get_network_status()
        
        return {
            "network": "Hyperledger Fabric",
            "status": network_status["status"],
            "peers_online": network_status["peers_online"],
            "total_peers": network_status["total_peers"],
            "latest_block": network_status["latest_block"],
            "channel_name": settings.FABRIC_CHANNEL_NAME
        }
        
    except Exception as e:
        logger.error(f"Error getting network status: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get network status")

@router.get("/transactions")
async def get_user_transactions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    limit: int = 10,
    offset: int = 0
):
    """
    Get user's blockchain transactions
    """
    transactions = db.query(BlockchainTransaction).filter(
        BlockchainTransaction.user_id == current_user.id
    ).order_by(BlockchainTransaction.created_at.desc()).offset(offset).limit(limit).all()
    
    return {
        "transactions": [
            {
                "id": tx.id,
                "document_id": tx.document_id,
                "transaction_hash": tx.transaction_hash,
                "block_number": tx.block_number,
                "status": tx.status,
                "created_at": tx.created_at
            }
            for tx in transactions
        ],
        "total": len(transactions)
    }

@router.get("/demo-stats")
async def get_demo_statistics():
    """
    Get demo statistics for competition presentation
    """
    try:
        blockchain_service = BlockchainService()
        blockchain_info = await blockchain_service.get_blockchain_info()
        
        return {
            "project_name": "IntelliTrust - AI-Powered Blockchain Document Verification",
            "competition_ready": True,
            "blockchain_capabilities": blockchain_info.get("demo_features", {}),
            "performance_metrics": blockchain_info.get("performance_metrics", {}),
            "total_documents_processed": blockchain_info.get("total_documents", 0),
            "total_transactions": blockchain_info.get("total_transactions", 0),
            "network_status": blockchain_info.get("network_status", {}),
            "key_features": [
                "🔐 Secure Document Anchoring",
                "🔍 AI-Powered Document Analysis", 
                "📊 Real-time Audit Trail",
                "🌐 Multi-Blockchain Support",
                "⚡ High Performance Architecture",
                "🛡️ Enterprise Security",
                "📱 Modern Web Interface",
                "🔗 Blockchain Verification"
            ],
            "use_cases": [
                "Academic Credential Verification",
                "Medical Record Authentication", 
                "Legal Document Validation",
                "Financial Document Security",
                "Government Certificate Verification"
            ]
        }
        
    except Exception as e:
        logger.error(f"Error getting demo stats: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get demo statistics")

async def anchor_document_background(document_id: int, file_hash: str, user_did: str, db: Session):
    """
    Background task to anchor document to blockchain
    """
    try:
        blockchain_service = BlockchainService()
        
        # Anchor document to blockchain
        result = await blockchain_service.anchor_document(file_hash, user_did)
        
        # Create transaction record
        transaction = BlockchainTransaction(
            document_id=document_id,
            user_id=db.query(User).filter(User.did == user_did).first().id,
            transaction_hash=result["transaction_hash"],
            block_number=result["block_number"],
            status="confirmed",
            operation_type="anchor_document"
        )
        
        # Update document
        document = db.query(Document).filter(Document.id == document_id).first()
        if document:
            document.blockchain_hash = result["blockchain_hash"]
            document.blockchain_tx_id = result["transaction_hash"]
        
        db.add(transaction)
        db.commit()
        
        logger.info(f"Document {document_id} anchored to blockchain successfully")
        
    except Exception as e:
        logger.error(f"Error in background blockchain anchoring: {str(e)}")
        # Update transaction status to failed
        transaction = db.query(BlockchainTransaction).filter(
            BlockchainTransaction.document_id == document_id
        ).first()
        if transaction:
            transaction.status = "failed"
            db.commit()
