from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, BackgroundTasks
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List, Optional
import httpx
import json
import logging
from datetime import datetime

from app.core.database import get_db
from app.core.config import settings
from app.models.user import User
from app.models.document import Document, DocumentStatus
from app.models.ai_analysis import AIAnalysis, AIAnalysisResult
from app.schemas.ai_analysis import AIAnalysisCreate, AIAnalysisResponse
from app.core.security import get_current_user
from app.services.file_storage import FileStorageService
from app.services.ai_integration import AIIntegrationService

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/analyze-document", response_model=AIAnalysisResponse)
async def analyze_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    document_type: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Upload and analyze a document using AI engine
    """
    try:
        # Validate file
        if not file.filename:
            raise HTTPException(status_code=400, detail="No file provided")
        
        # Check file size
        if file.size and file.size > settings.MAX_FILE_SIZE:
            raise HTTPException(status_code=400, detail="File too large")
        
        # Upload file to storage
        file_storage = FileStorageService()
        file_url = await file_storage.upload_file(file)
        
        # Create document record
        document = Document(
            title=file.filename,
            file_hash=file_storage.calculate_hash(file),
            file_size=file.size or 0,
            file_type=file.content_type or "application/octet-stream",
            file_url=file_url,
            owner_id=current_user.id,
            document_type=document_type or "other",
            status=DocumentStatus.PENDING_VERIFICATION
        )
        db.add(document)
        db.commit()
        db.refresh(document)
        
        # Start AI analysis in background
        background_tasks.add_task(
            perform_ai_analysis,
            document.id,
            file_url,
            file_storage.calculate_hash(file),
            db
        )
        
        return AIAnalysisResponse(
            document_id=document.id,
            status="processing",
            message="Document uploaded and analysis started"
        )
        
    except Exception as e:
        logger.error(f"Error in document analysis: {str(e)}")
        raise HTTPException(status_code=500, detail="Analysis failed")

@router.get("/document/{document_id}", response_model=AIAnalysisResponse)
async def get_analysis_results(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get AI analysis results for a document
    """
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Check permissions
    if document.owner_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Access denied")
    
    analysis = db.query(AIAnalysis).filter(AIAnalysis.document_id == document_id).first()
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    return AIAnalysisResponse(
        document_id=document_id,
        status="completed",
        analysis_results=analysis.results,
        confidence_score=analysis.confidence_score,
        is_authentic=analysis.is_authentic
    )

@router.get("/batch/{batch_id}")
async def get_batch_analysis_results(
    batch_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get batch analysis results
    """
    # Implementation for batch analysis results
    pass

async def perform_ai_analysis(document_id: int, file_url: str, file_hash: str, db: Session):
    """
    Background task to perform AI analysis
    """
    try:
        ai_service = AIIntegrationService()
        
        # Call AI engine
        analysis_results = await ai_service.analyze_document(file_url)
        
        # Create analysis record
        analysis = AIAnalysis(
            document_id=document_id,
            analysis_type="comprehensive",
            results=analysis_results,
            confidence_score=analysis_results.get("authenticity_score", 0.0),
            is_authentic=analysis_results.get("is_authentic", False),
            processing_time=analysis_results.get("processing_time", 0)
        )
        
        # Update document status
        document = db.query(Document).filter(Document.id == document_id).first()
        if document:
            document.ai_verified = analysis.is_authentic
            document.ai_confidence_score = int(analysis.confidence_score * 100)
            document.status = DocumentStatus.VERIFIED if analysis.is_authentic else DocumentStatus.REJECTED
            document.verified_at = datetime.utcnow()
        
        db.add(analysis)
        db.commit()
        
        logger.info(f"AI analysis completed for document {document_id}")
        
    except Exception as e:
        logger.error(f"Error in background AI analysis: {str(e)}")
        # Update document status to failed
        document = db.query(Document).filter(Document.id == document_id).first()
        if document:
            document.status = DocumentStatus.REJECTED
            db.commit()
