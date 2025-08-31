from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime
from app.models.credential import CredentialTypeEnum

class CredentialCreate(BaseModel):
    document_id: int
    holder_id: int
    credential_type: CredentialTypeEnum
    title: str
    description: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    validity_days: int = 365

class CredentialUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    status: Optional[str] = None

class CredentialResponse(BaseModel):
    id: int
    title: str
    credential_type: CredentialTypeEnum
    holder_id: int
    issuer_id: int
    status: str
    issued_at: datetime
    expires_at: Optional[datetime] = None
    revoked_at: Optional[datetime] = None
    revocation_reason: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True

class CredentialVerificationResponse(BaseModel):
    credential_id: int
    verified: bool
    verification_details: Dict[str, Any]
    blockchain_verified: bool
    ai_verified: bool
    issuer_info: Dict[str, Any]
    holder_info: Dict[str, Any]
    document_info: Dict[str, Any]
