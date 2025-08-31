from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
import hashlib
import os
from datetime import datetime

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.document import Document, DocumentStatus, DocumentType
from app.schemas.document import (
    DocumentCreate,
    DocumentResponse,
    DocumentUpdate,
    DocumentList
)

router = APIRouter()

@router.post("/upload", response_model=DocumentResponse)
async def upload_document(
    file: UploadFile = File(...),
    title: str = Form(...),
    description: Optional[str] = Form(None),
    document_type: DocumentType = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Upload a new document.
    """
    # Validate file type
    allowed_types = ["pdf", "jpg", "jpeg", "png", "tiff"]
    file_extension = file.filename.split(".")[-1].lower()
    if file_extension not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type {file_extension} not allowed. Allowed types: {allowed_types}"
        )
    
    # Read file content and calculate hash
    content = await file.read()
    file_hash = hashlib.sha256(content).hexdigest()
    
    # Check if document already exists
    existing_doc = db.query(Document).filter(Document.file_hash == file_hash).first()
    if existing_doc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Document with this content already exists"
        )
    
    # Save file (in production, use cloud storage)
    file_path = f"uploads/{file_hash}_{file.filename}"
    os.makedirs("uploads", exist_ok=True)
    with open(file_path, "wb") as f:
        f.write(content)
    
    # Create document record
    db_document = Document(
        title=title,
        description=description,
        document_type=document_type.value if hasattr(document_type, 'value') else document_type,
        file_hash=file_hash,
        file_size=len(content),
        file_type=file_extension,
        file_url=file_path,
        owner_id=current_user.id,
        status=DocumentStatus.DRAFT
    )
    
    db.add(db_document)
    db.commit()
    db.refresh(db_document)
    
    return DocumentResponse(
        id=db_document.id,
        title=db_document.title,
        description=db_document.description,
        document_type=db_document.document_type.value if hasattr(db_document.document_type, 'value') else db_document.document_type,
        status=db_document.status,
        file_hash=db_document.file_hash,
        file_size=db_document.file_size,
        file_type=db_document.file_type,
        file_url=db_document.file_url,
        owner_id=db_document.owner_id,
        issuer_id=db_document.issuer_id,
        organization_id=db_document.organization_id,
        blockchain_hash=db_document.blockchain_hash,
        blockchain_tx_id=db_document.blockchain_tx_id,
        ai_verified=db_document.ai_verified,
        ai_confidence_score=db_document.ai_confidence_score,
        created_at=db_document.created_at,
        updated_at=db_document.updated_at,
        verified_at=db_document.verified_at,
        expires_at=db_document.expires_at
    )

@router.get("/", response_model=DocumentList)
def get_documents(
    skip: int = 0,
    limit: int = 100,
    status: Optional[DocumentStatus] = None,
    document_type: Optional[DocumentType] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Get list of documents for current user.
    """
    query = db.query(Document).filter(Document.owner_id == current_user.id)
    
    if status:
        query = query.filter(Document.status == status)
    if document_type:
        query = query.filter(Document.document_type == document_type)
    
    # Get total count
    total = query.count()
    
    # Get paginated documents
    documents = query.offset(skip).limit(limit).all()
    
    return DocumentList(
        documents=[
            DocumentResponse(
                id=doc.id,
                title=doc.title,
                description=doc.description,
                document_type=doc.document_type.value if hasattr(doc.document_type, 'value') else doc.document_type,
                status=doc.status,
                file_hash=doc.file_hash,
                file_size=doc.file_size,
                file_type=doc.file_type,
                file_url=doc.file_url,
                owner_id=doc.owner_id,
                issuer_id=doc.issuer_id,
                organization_id=doc.organization_id,
                blockchain_hash=doc.blockchain_hash,
                blockchain_tx_id=doc.blockchain_tx_id,
                ai_verified=doc.ai_verified,
                ai_confidence_score=doc.ai_confidence_score,
                created_at=doc.created_at,
                updated_at=doc.updated_at,
                verified_at=doc.verified_at,
                expires_at=doc.expires_at
            )
            for doc in documents
        ],
        total=total,
        skip=skip,
        limit=limit
    )

@router.get("/{document_id}", response_model=DocumentResponse)
def get_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Get a specific document by ID.
    """
    document = db.query(Document).filter(
        Document.id == document_id,
        Document.owner_id == current_user.id
    ).first()
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    return DocumentResponse(
        id=document.id,
        title=document.title,
        description=document.description,
        document_type=document.document_type,
        status=document.status,
        file_hash=document.file_hash,
        file_size=document.file_size,
        file_type=document.file_type,
        file_url=document.file_url,
        owner_id=document.owner_id,
        issuer_id=document.issuer_id,
        organization_id=document.organization_id,
        blockchain_hash=document.blockchain_hash,
        blockchain_tx_id=document.blockchain_tx_id,
        ai_verified=document.ai_verified,
        ai_confidence_score=document.ai_confidence_score,
        created_at=document.created_at,
        updated_at=document.updated_at,
        verified_at=document.verified_at,
        expires_at=document.expires_at
    )

@router.put("/{document_id}", response_model=DocumentResponse)
def update_document(
    document_id: int,
    document_update: DocumentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Update a document.
    """
    document = db.query(Document).filter(
        Document.id == document_id,
        Document.owner_id == current_user.id
    ).first()
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    # Update fields
    for field, value in document_update.dict(exclude_unset=True).items():
        setattr(document, field, value)
    
    document.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(document)
    
    return DocumentResponse(
        id=document.id,
        title=document.title,
        description=document.description,
        document_type=document.document_type,
        status=document.status,
        file_hash=document.file_hash,
        file_size=document.file_size,
        file_type=document.file_type,
        file_url=document.file_url,
        owner_id=document.owner_id,
        issuer_id=document.issuer_id,
        organization_id=document.organization_id,
        blockchain_hash=document.blockchain_hash,
        blockchain_tx_id=document.blockchain_tx_id,
        ai_verified=document.ai_verified,
        ai_confidence_score=document.ai_confidence_score,
        created_at=document.created_at,
        updated_at=document.updated_at,
        verified_at=document.verified_at,
        expires_at=document.expires_at
    )

@router.delete("/{document_id}")
def delete_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Delete a document.
    """
    document = db.query(Document).filter(
        Document.id == document_id,
        Document.owner_id == current_user.id
    ).first()
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    # Delete file
    if os.path.exists(document.file_url):
        os.remove(document.file_url)
    
    db.delete(document)
    db.commit()
    
    return {"message": "Document deleted successfully"}
