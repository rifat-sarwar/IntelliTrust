from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime

class VerificationCreate(BaseModel):
    document_id: Optional[int] = None
    credential_id: Optional[int] = None
    verification_type: str
    metadata: Optional[Dict[str, Any]] = None

class VerificationResponse(BaseModel):
    id: int
    document_id: Optional[int] = None
    credential_id: Optional[int] = None
    verification_type: str
    status: str
    message: Optional[str] = None
    result: Optional[Dict[str, Any]] = None
    verified_at: Optional[datetime] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class QRVerificationRequest(BaseModel):
    qr_data: str

class QRVerificationResponse(BaseModel):
    verified: bool
    verification_type: str
    document_info: Optional[Dict[str, Any]] = None
    credential_info: Optional[Dict[str, Any]] = None
    blockchain_verified: bool
    verification_timestamp: datetime
    reason: Optional[str] = None
