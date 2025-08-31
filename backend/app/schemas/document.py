from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel
from app.models.document import DocumentType, DocumentStatus

class DocumentBase(BaseModel):
    title: str
    description: Optional[str] = None
    document_type: DocumentType

class DocumentCreate(DocumentBase):
    pass

class DocumentUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    document_type: Optional[DocumentType] = None

class DocumentResponse(DocumentBase):
    id: int
    status: DocumentStatus
    file_hash: str
    file_size: int
    file_type: str
    file_url: str
    owner_id: int
    issuer_id: Optional[int] = None
    organization_id: Optional[int] = None
    blockchain_hash: Optional[str] = None
    blockchain_tx_id: Optional[str] = None
    ai_verified: bool
    ai_confidence_score: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    verified_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class DocumentList(BaseModel):
    documents: List[DocumentResponse]
    total: int
    skip: int
    limit: int

class DocumentMetadata(BaseModel):
    key: str
    value: str
    value_type: str = "string"

class DocumentVersion(BaseModel):
    version_number: int
    file_hash: str
    file_size: int
    change_reason: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True
