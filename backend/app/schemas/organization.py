from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from app.models.organization import OrganizationType

class OrganizationCreate(BaseModel):
    name: str
    description: Optional[str] = None
    organization_type: OrganizationType
    website: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    country: Optional[str] = None

class OrganizationUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    website: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    country: Optional[str] = None

class OrganizationResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    organization_type: OrganizationType
    status: str
    website: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    country: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    verified_at: Optional[datetime] = None
    rejected_at: Optional[datetime] = None
    rejection_reason: Optional[str] = None

    class Config:
        from_attributes = True
