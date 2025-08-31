from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, desc
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import logging
import csv
from io import StringIO
from fastapi.responses import StreamingResponse

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User, UserRole
from app.models.document import Document, DocumentStatus, DocumentType
from app.models.credential import Credential, CredentialType
from app.models.verification import Verification
from app.models.blockchain import BlockchainTransaction
from app.models.ai_analysis import AIAnalysis
from app.models.organization import Organization

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/documents")
async def generate_document_report(
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    document_type: Optional[DocumentType] = Query(None),
    status: Optional[DocumentStatus] = Query(None),
    format: str = Query("json", description="Report format: json or csv"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Generate document report
    """
    try:
        # Build query
        query = db.query(Document)
        
        # Apply filters
        if start_date:
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
            query = query.filter(Document.created_at >= start_dt)
        
        if end_date:
            end_dt = datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1)
            query = query.filter(Document.created_at < end_dt)
        
        if document_type:
            query = query.filter(Document.document_type == document_type)
        
        if status:
            query = query.filter(Document.status == status)
        
        # Apply user permissions
        if current_user.role != "admin":
            query = query.filter(Document.owner_id == current_user.id)
        
        documents = query.order_by(desc(Document.created_at)).all()
        
        if format.lower() == "csv":
            return generate_csv_report(documents, "documents")
        else:
            return {
                "report_type": "documents",
                "generated_at": datetime.utcnow().isoformat(),
                "filters": {
                    "start_date": start_date,
                    "end_date": end_date,
                    "document_type": document_type.value if document_type else None,
                    "status": status.value if status else None
                },
                "total_documents": len(documents),
                "documents": [
                    {
                        "id": doc.id,
                        "title": doc.title,
                        "document_type": doc.document_type,
                        "status": doc.status,
                        "file_hash": doc.file_hash,
                        "ai_verified": doc.ai_verified,
                        "ai_confidence_score": doc.ai_confidence_score,
                        "blockchain_hash": doc.blockchain_hash,
                        "created_at": doc.created_at.isoformat(),
                        "verified_at": doc.verified_at.isoformat() if doc.verified_at else None,
                        "owner_id": doc.owner_id,
                        "issuer_id": doc.issuer_id
                    }
                    for doc in documents
                ]
            }
            
    except Exception as e:
        logger.error(f"Error generating document report: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate document report")

@router.get("/verifications")
async def generate_verification_report(
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    status: Optional[str] = Query(None),
    format: str = Query("json", description="Report format: json or csv"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Generate verification report
    """
    try:
        # Build query
        query = db.query(Verification)
        
        # Apply filters
        if start_date:
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
            query = query.filter(Verification.created_at >= start_dt)
        
        if end_date:
            end_dt = datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1)
            query = query.filter(Verification.created_at < end_dt)
        
        if status:
            query = query.filter(Verification.status == status)
        
        # Apply user permissions
        if current_user.role != "admin":
            query = query.filter(Verification.verifier_id == current_user.id)
        
        verifications = query.order_by(desc(Verification.created_at)).all()
        
        if format.lower() == "csv":
            return generate_csv_report(verifications, "verifications")
        else:
            return {
                "report_type": "verifications",
                "generated_at": datetime.utcnow().isoformat(),
                "filters": {
                    "start_date": start_date,
                    "end_date": end_date,
                    "status": status
                },
                "total_verifications": len(verifications),
                "verifications": [
                    {
                        "id": ver.id,
                        "document_id": ver.document_id,
                        "verifier_id": ver.verifier_id,
                        "status": ver.status,
                        "result": ver.result,
                        "created_at": ver.created_at.isoformat(),
                        "completed_at": ver.completed_at.isoformat() if ver.completed_at else None
                    }
                    for ver in verifications
                ]
            }
            
    except Exception as e:
        logger.error(f"Error generating verification report: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate verification report")

@router.get("/blockchain")
async def generate_blockchain_report(
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    status: Optional[str] = Query(None),
    format: str = Query("json", description="Report format: json or csv"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Generate blockchain transaction report
    """
    try:
        # Build query
        query = db.query(BlockchainTransaction)
        
        # Apply filters
        if start_date:
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
            query = query.filter(BlockchainTransaction.created_at >= start_dt)
        
        if end_date:
            end_dt = datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1)
            query = query.filter(BlockchainTransaction.created_at < end_dt)
        
        if status:
            query = query.filter(BlockchainTransaction.status == status)
        
        # Apply user permissions
        if current_user.role != "admin":
            query = query.filter(BlockchainTransaction.user_id == current_user.id)
        
        transactions = query.order_by(desc(BlockchainTransaction.created_at)).all()
        
        if format.lower() == "csv":
            return generate_csv_report(transactions, "blockchain")
        else:
            return {
                "report_type": "blockchain_transactions",
                "generated_at": datetime.utcnow().isoformat(),
                "filters": {
                    "start_date": start_date,
                    "end_date": end_date,
                    "status": status
                },
                "total_transactions": len(transactions),
                "transactions": [
                    {
                        "id": tx.id,
                        "document_id": tx.document_id,
                        "user_id": tx.user_id,
                        "transaction_hash": tx.transaction_hash,
                        "block_number": tx.block_number,
                        "status": tx.status,
                        "operation_type": tx.operation_type,
                        "created_at": tx.created_at.isoformat()
                    }
                    for tx in transactions
                ]
            }
            
    except Exception as e:
        logger.error(f"Error generating blockchain report: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate blockchain report")

@router.get("/ai-analysis")
async def generate_ai_analysis_report(
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    is_authentic: Optional[bool] = Query(None),
    format: str = Query("json", description="Report format: json or csv"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Generate AI analysis report
    """
    try:
        # Build query
        query = db.query(AIAnalysis).join(Document)
        
        # Apply filters
        if start_date:
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
            query = query.filter(AIAnalysis.created_at >= start_dt)
        
        if end_date:
            end_dt = datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1)
            query = query.filter(AIAnalysis.created_at < end_dt)
        
        if is_authentic is not None:
            query = query.filter(AIAnalysis.is_authentic == is_authentic)
        
        # Apply user permissions
        if current_user.role != "admin":
            query = query.filter(Document.owner_id == current_user.id)
        
        analyses = query.order_by(desc(AIAnalysis.created_at)).all()
        
        if format.lower() == "csv":
            return generate_csv_report(analyses, "ai_analysis")
        else:
            return {
                "report_type": "ai_analysis",
                "generated_at": datetime.utcnow().isoformat(),
                "filters": {
                    "start_date": start_date,
                    "end_date": end_date,
                    "is_authentic": is_authentic
                },
                "total_analyses": len(analyses),
                "analyses": [
                    {
                        "id": analysis.id,
                        "document_id": analysis.document_id,
                        "analysis_type": analysis.analysis_type,
                        "confidence_score": analysis.confidence_score,
                        "is_authentic": analysis.is_authentic,
                        "processing_time": analysis.processing_time,
                        "created_at": analysis.created_at.isoformat()
                    }
                    for analysis in analyses
                ]
            }
            
    except Exception as e:
        logger.error(f"Error generating AI analysis report: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate AI analysis report")

@router.get("/users")
async def generate_user_report(
    role: Optional[UserRole] = Query(None),
    status: Optional[str] = Query(None),
    format: str = Query("json", description="Report format: json or csv"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Generate user report (admin only)
    """
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        # Build query
        query = db.query(User)
        
        # Apply filters
        if role:
            query = query.filter(User.role == role)
        
        if status:
            query = query.filter(User.status == status)
        
        users = query.order_by(desc(User.created_at)).all()
        
        if format.lower() == "csv":
            return generate_csv_report(users, "users")
        else:
            return {
                "report_type": "users",
                "generated_at": datetime.utcnow().isoformat(),
                "filters": {
                    "role": role.value if role else None,
                    "status": status
                },
                "total_users": len(users),
                "users": [
                    {
                        "id": user.id,
                        "username": user.username,
                        "email": user.email,
                        "full_name": user.full_name,
                        "role": user.role,
                        "status": user.status,
                        "organization_id": user.organization_id,
                        "created_at": user.created_at.isoformat(),
                        "last_login": user.last_login.isoformat() if user.last_login else None
                    }
                    for user in users
                ]
            }
            
    except Exception as e:
        logger.error(f"Error generating user report: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate user report")

@router.get("/summary")
async def generate_summary_report(
    period: str = Query("30d", description="Period: 7d, 30d, 90d, 1y"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Generate summary report for the specified period
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
        
        # Build base queries
        base_doc_query = db.query(Document)
        base_ver_query = db.query(Verification)
        base_tx_query = db.query(BlockchainTransaction)
        base_ai_query = db.query(AIAnalysis)
        
        # Apply date filters
        docs_in_period = base_doc_query.filter(
            and_(Document.created_at >= start_date, Document.created_at <= end_date)
        )
        vers_in_period = base_ver_query.filter(
            and_(Verification.created_at >= start_date, Verification.created_at <= end_date)
        )
        txs_in_period = base_tx_query.filter(
            and_(BlockchainTransaction.created_at >= start_date, BlockchainTransaction.created_at <= end_date)
        )
        ais_in_period = base_ai_query.filter(
            and_(AIAnalysis.created_at >= start_date, AIAnalysis.created_at <= end_date)
        )
        
        # Apply user permissions
        if current_user.role != "admin":
            docs_in_period = docs_in_period.filter(Document.owner_id == current_user.id)
            vers_in_period = vers_in_period.filter(Verification.verifier_id == current_user.id)
            txs_in_period = txs_in_period.filter(BlockchainTransaction.user_id == current_user.id)
            ais_in_period = ais_in_period.join(Document).filter(Document.owner_id == current_user.id)
        
        # Get statistics
        total_docs = docs_in_period.count()
        verified_docs = docs_in_period.filter(Document.status == DocumentStatus.VERIFIED).count()
        total_vers = vers_in_period.count()
        successful_vers = vers_in_period.filter(Verification.status == "completed").count()
        total_txs = txs_in_period.count()
        confirmed_txs = txs_in_period.filter(BlockchainTransaction.status == "confirmed").count()
        total_ais = ais_in_period.count()
        authentic_docs = ais_in_period.filter(AIAnalysis.is_authentic == True).count()
        
        # Calculate rates
        verification_rate = (verified_docs / total_docs * 100) if total_docs > 0 else 0
        success_rate = (successful_vers / total_vers * 100) if total_vers > 0 else 0
        confirmation_rate = (confirmed_txs / total_txs * 100) if total_txs > 0 else 0
        authenticity_rate = (authentic_docs / total_ais * 100) if total_ais > 0 else 0
        
        return {
            "report_type": "summary",
            "period": period,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "generated_at": datetime.utcnow().isoformat(),
            "statistics": {
                "documents": {
                    "total": total_docs,
                    "verified": verified_docs,
                    "verification_rate": verification_rate
                },
                "verifications": {
                    "total": total_vers,
                    "successful": successful_vers,
                    "success_rate": success_rate
                },
                "blockchain": {
                    "total_transactions": total_txs,
                    "confirmed": confirmed_txs,
                    "confirmation_rate": confirmation_rate
                },
                "ai_analysis": {
                    "total_analyses": total_ais,
                    "authentic": authentic_docs,
                    "authenticity_rate": authenticity_rate
                }
            }
        }
        
    except Exception as e:
        logger.error(f"Error generating summary report: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate summary report")

def generate_csv_report(data: List, report_type: str) -> StreamingResponse:
    """
    Generate CSV report from data
    """
    try:
        output = StringIO()
        writer = csv.writer(output)
        
        if report_type == "documents":
            writer.writerow([
                "ID", "Title", "Document Type", "Status", "File Hash", 
                "AI Verified", "AI Confidence Score", "Blockchain Hash",
                "Created At", "Verified At", "Owner ID", "Issuer ID"
            ])
            for doc in data:
                writer.writerow([
                    doc.id, doc.title, doc.document_type, doc.status,
                    doc.file_hash, doc.ai_verified, doc.ai_confidence_score,
                    doc.blockchain_hash, doc.created_at, doc.verified_at,
                    doc.owner_id, doc.issuer_id
                ])
        
        elif report_type == "verifications":
            writer.writerow([
                "ID", "Document ID", "Verifier ID", "Status", "Result",
                "Created At", "Completed At"
            ])
            for ver in data:
                writer.writerow([
                    ver.id, ver.document_id, ver.verifier_id, ver.status,
                    str(ver.result), ver.created_at, ver.completed_at
                ])
        
        elif report_type == "blockchain":
            writer.writerow([
                "ID", "Document ID", "User ID", "Transaction Hash",
                "Block Number", "Status", "Operation Type", "Created At"
            ])
            for tx in data:
                writer.writerow([
                    tx.id, tx.document_id, tx.user_id, tx.transaction_hash,
                    tx.block_number, tx.status, tx.operation_type, tx.created_at
                ])
        
        elif report_type == "ai_analysis":
            writer.writerow([
                "ID", "Document ID", "Analysis Type", "Confidence Score",
                "Is Authentic", "Processing Time", "Created At"
            ])
            for analysis in data:
                writer.writerow([
                    analysis.id, analysis.document_id, analysis.analysis_type,
                    analysis.confidence_score, analysis.is_authentic,
                    analysis.processing_time, analysis.created_at
                ])
        
        elif report_type == "users":
            writer.writerow([
                "ID", "Username", "Email", "Full Name", "Role", "Status",
                "Organization ID", "Created At", "Last Login"
            ])
            for user in data:
                writer.writerow([
                    user.id, user.username, user.email, user.full_name,
                    user.role, user.status, user.organization_id,
                    user.created_at, user.last_login
                ])
        
        output.seek(0)
        
        return StreamingResponse(
            iter([output.getvalue()]),
            media_type="text/csv",
            headers={
                "Content-Disposition": f"attachment; filename={report_type}_report_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv"
            }
        )
        
    except Exception as e:
        logger.error(f"Error generating CSV report: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to generate CSV report")
