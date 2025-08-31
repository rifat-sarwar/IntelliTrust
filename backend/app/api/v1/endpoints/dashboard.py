from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from typing import Dict, Any, List
from datetime import datetime, timedelta
import logging

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.document import Document, DocumentStatus
from app.models.credential import Credential, CredentialType
from app.models.verification import Verification
from app.models.blockchain import BlockchainTransaction
from app.models.ai_analysis import AIAnalysis

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/stats")
async def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get dashboard statistics for the current user
    """
    try:
        # Get user's documents
        user_documents = db.query(Document).filter(Document.owner_id == current_user.id)
        
        # Document statistics
        total_documents = user_documents.count()
        verified_documents = user_documents.filter(Document.status == DocumentStatus.VERIFIED).count()
        pending_documents = user_documents.filter(Document.status == DocumentStatus.PENDING_VERIFICATION).count()
        rejected_documents = user_documents.filter(Document.status == DocumentStatus.REJECTED).count()
        
        # Credential statistics
        user_credentials = db.query(Credential).filter(Credential.holder_id == current_user.id)
        total_credentials = user_credentials.count()
        active_credentials = user_credentials.filter(Credential.status == "active").count()
        expired_credentials = user_credentials.filter(Credential.status == "expired").count()
        
        # Verification statistics
        user_verifications = db.query(Verification).filter(Verification.verifier_id == current_user.id)
        total_verifications = user_verifications.count()
        successful_verifications = user_verifications.filter(Verification.status == "completed").count()
        
        # Blockchain statistics
        user_transactions = db.query(BlockchainTransaction).filter(BlockchainTransaction.user_id == current_user.id)
        total_transactions = user_transactions.count()
        confirmed_transactions = user_transactions.filter(BlockchainTransaction.status == "confirmed").count()
        
        # AI Analysis statistics
        user_ai_analyses = db.query(AIAnalysis).join(Document).filter(Document.owner_id == current_user.id)
        total_ai_analyses = user_ai_analyses.count()
        authentic_documents = user_ai_analyses.filter(AIAnalysis.is_authentic == True).count()
        
        # Recent activity (last 30 days)
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        recent_documents = user_documents.filter(Document.created_at >= thirty_days_ago).count()
        recent_verifications = user_verifications.filter(Verification.created_at >= thirty_days_ago).count()
        
        return {
            "documents": {
                "total": total_documents,
                "verified": verified_documents,
                "pending": pending_documents,
                "rejected": rejected_documents,
                "recent": recent_documents
            },
            "credentials": {
                "total": total_credentials,
                "active": active_credentials,
                "expired": expired_credentials
            },
            "verifications": {
                "total": total_verifications,
                "successful": successful_verifications,
                "recent": recent_verifications
            },
            "blockchain": {
                "total_transactions": total_transactions,
                "confirmed_transactions": confirmed_transactions
            },
            "ai_analysis": {
                "total_analyses": total_ai_analyses,
                "authentic_documents": authentic_documents,
                "authenticity_rate": (authentic_documents / total_ai_analyses * 100) if total_ai_analyses > 0 else 0
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting dashboard stats: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get dashboard statistics")

@router.get("/recent-activity")
async def get_recent_activity(
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get recent activity for the current user
    """
    try:
        # Get recent documents
        recent_documents = db.query(Document).filter(
            Document.owner_id == current_user.id
        ).order_by(Document.created_at.desc()).limit(limit).all()
        
        # Get recent verifications
        recent_verifications = db.query(Verification).filter(
            Verification.verifier_id == current_user.id
        ).order_by(Verification.created_at.desc()).limit(limit).all()
        
        # Get recent blockchain transactions
        recent_transactions = db.query(BlockchainTransaction).filter(
            BlockchainTransaction.user_id == current_user.id
        ).order_by(BlockchainTransaction.created_at.desc()).limit(limit).all()
        
        # Combine and sort activities
        activities = []
        
        for doc in recent_documents:
            activities.append({
                "type": "document_uploaded",
                "timestamp": doc.created_at,
                "title": f"Document '{doc.title}' uploaded",
                "status": doc.status,
                "id": doc.id
            })
        
        for ver in recent_verifications:
            activities.append({
                "type": "verification_completed",
                "timestamp": ver.created_at,
                "title": f"Verification completed for document {ver.document_id}",
                "status": ver.status,
                "id": ver.id
            })
        
        for tx in recent_transactions:
            activities.append({
                "type": "blockchain_transaction",
                "timestamp": tx.created_at,
                "title": f"Blockchain transaction {tx.transaction_hash[:10]}...",
                "status": tx.status,
                "id": tx.id
            })
        
        # Sort by timestamp
        activities.sort(key=lambda x: x["timestamp"], reverse=True)
        
        return {
            "activities": activities[:limit],
            "total": len(activities)
        }
        
    except Exception as e:
        logger.error(f"Error getting recent activity: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get recent activity")

@router.get("/analytics")
async def get_analytics(
    period: str = "30d",  # 7d, 30d, 90d, 1y
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get analytics data for the current user
    """
    try:
        # Calculate date range
        end_date = datetime.utcnow()
        if period == "7d":
            start_date = end_date - timedelta(days=7)
        elif period == "30d":
            start_date = end_date - timedelta(days=30)
        elif period == "90d":
            start_date = end_date - timedelta(days=90)
        elif period == "1y":
            start_date = end_date - timedelta(days=365)
        else:
            start_date = end_date - timedelta(days=30)
        
        # Document uploads over time
        document_uploads = db.query(
            func.date(Document.created_at).label('date'),
            func.count(Document.id).label('count')
        ).filter(
            and_(
                Document.owner_id == current_user.id,
                Document.created_at >= start_date
            )
        ).group_by(func.date(Document.created_at)).all()
        
        # Verifications over time
        verifications = db.query(
            func.date(Verification.created_at).label('date'),
            func.count(Verification.id).label('count')
        ).filter(
            and_(
                Verification.verifier_id == current_user.id,
                Verification.created_at >= start_date
            )
        ).group_by(func.date(Verification.created_at)).all()
        
        # Blockchain transactions over time
        transactions = db.query(
            func.date(BlockchainTransaction.created_at).label('date'),
            func.count(BlockchainTransaction.id).label('count')
        ).filter(
            and_(
                BlockchainTransaction.user_id == current_user.id,
                BlockchainTransaction.created_at >= start_date
            )
        ).group_by(func.date(BlockchainTransaction.created_at)).all()
        
        # Document type distribution
        document_types = db.query(
            Document.document_type,
            func.count(Document.id).label('count')
        ).filter(
            Document.owner_id == current_user.id
        ).group_by(Document.document_type).all()
        
        # Verification success rate
        total_verifications = db.query(Verification).filter(
            and_(
                Verification.verifier_id == current_user.id,
                Verification.created_at >= start_date
            )
        ).count()
        
        successful_verifications = db.query(Verification).filter(
            and_(
                Verification.verifier_id == current_user.id,
                Verification.status == "completed",
                Verification.created_at >= start_date
            )
        ).count()
        
        success_rate = (successful_verifications / total_verifications * 100) if total_verifications > 0 else 0
        
        return {
            "period": period,
            "document_uploads": [
                {"date": str(item.date), "count": item.count}
                for item in document_uploads
            ],
            "verifications": [
                {"date": str(item.date), "count": item.count}
                for item in verifications
            ],
            "blockchain_transactions": [
                {"date": str(item.date), "count": item.count}
                for item in transactions
            ],
            "document_type_distribution": [
                {"type": item.document_type, "count": item.count}
                for item in document_types
            ],
            "verification_success_rate": success_rate,
            "total_verifications": total_verifications,
            "successful_verifications": successful_verifications
        }
        
    except Exception as e:
        logger.error(f"Error getting analytics: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get analytics data")

@router.get("/admin/stats")
async def get_admin_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get admin dashboard statistics (admin only)
    """
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        # System-wide statistics
        total_users = db.query(User).count()
        total_documents = db.query(Document).count()
        total_verifications = db.query(Verification).count()
        total_transactions = db.query(BlockchainTransaction).count()
        
        # User statistics by role
        users_by_role = db.query(
            User.role,
            func.count(User.id).label('count')
        ).group_by(User.role).all()
        
        # Document statistics by status
        documents_by_status = db.query(
            Document.status,
            func.count(Document.id).label('count')
        ).group_by(Document.status).all()
        
        # Recent system activity
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        recent_users = db.query(User).filter(User.created_at >= thirty_days_ago).count()
        recent_documents = db.query(Document).filter(Document.created_at >= thirty_days_ago).count()
        recent_verifications = db.query(Verification).filter(Verification.created_at >= thirty_days_ago).count()
        
        # AI Analysis statistics
        total_ai_analyses = db.query(AIAnalysis).count()
        authentic_documents = db.query(AIAnalysis).filter(AIAnalysis.is_authentic == True).count()
        authenticity_rate = (authentic_documents / total_ai_analyses * 100) if total_ai_analyses > 0 else 0
        
        return {
            "system": {
                "total_users": total_users,
                "total_documents": total_documents,
                "total_verifications": total_verifications,
                "total_transactions": total_transactions,
                "recent_users": recent_users,
                "recent_documents": recent_documents,
                "recent_verifications": recent_verifications
            },
            "users_by_role": [
                {"role": item.role, "count": item.count}
                for item in users_by_role
            ],
            "documents_by_status": [
                {"status": item.status, "count": item.count}
                for item in documents_by_status
            ],
            "ai_analysis": {
                "total_analyses": total_ai_analyses,
                "authentic_documents": authentic_documents,
                "authenticity_rate": authenticity_rate
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting admin stats: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get admin statistics")
