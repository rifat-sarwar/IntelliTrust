from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
import logging
from datetime import datetime

from app.core.database import get_db
from app.models.user import User
from app.models.organization import Organization
from app.schemas.organization import OrganizationCreate, OrganizationResponse, OrganizationUpdate
from app.core.security import get_current_user

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/", response_model=OrganizationResponse)
async def create_organization(
    organization_data: OrganizationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new organization
    """
    try:
        # Check if user can create organizations
        if current_user.role not in ["admin"]:
            raise HTTPException(status_code=403, detail="Only admins can create organizations")
        
        # Check if organization already exists
        existing_org = db.query(Organization).filter(
            Organization.name == organization_data.name
        ).first()
        
        if existing_org:
            raise HTTPException(status_code=400, detail="Organization with this name already exists")
        
        # Create organization
        organization = Organization(
            name=organization_data.name,
            description=organization_data.description,
            organization_type=organization_data.organization_type,
            website=organization_data.website,
            email=organization_data.email,
            phone=organization_data.phone,
            address=organization_data.address,
            country=organization_data.country,
            created_by_id=current_user.id,
            status="pending"
        )
        
        db.add(organization)
        db.commit()
        db.refresh(organization)
        
        return OrganizationResponse(
            id=organization.id,
            name=organization.name,
            description=organization.description,
            organization_type=organization.organization_type,
            status=organization.status,
            created_at=organization.created_at
        )
        
    except Exception as e:
        logger.error(f"Error creating organization: {str(e)}")
        raise HTTPException(status_code=500, detail="Organization creation failed")

@router.get("/", response_model=List[OrganizationResponse])
async def get_organizations(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    status: Optional[str] = None,
    limit: int = 10,
    offset: int = 0
):
    """
    Get list of organizations
    """
    query = db.query(Organization)
    
    if status:
        query = query.filter(Organization.status == status)
    
    # Non-admins can only see verified organizations
    if current_user.role not in ["admin"]:
        query = query.filter(Organization.status == "verified")
    
    organizations = query.order_by(Organization.created_at.desc()).offset(offset).limit(limit).all()
    
    return [
        OrganizationResponse(
            id=org.id,
            name=org.name,
            description=org.description,
            organization_type=org.organization_type,
            status=org.status,
            created_at=org.created_at
        )
        for org in organizations
    ]

@router.get("/{organization_id}", response_model=OrganizationResponse)
async def get_organization(
    organization_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get specific organization details
    """
    organization = db.query(Organization).filter(Organization.id == organization_id).first()
    if not organization:
        raise HTTPException(status_code=404, detail="Organization not found")
    
    # Check permissions
    if (organization.status != "verified" and 
        current_user.role not in ["admin"] and
        current_user.organization_id != organization_id):
        raise HTTPException(status_code=403, detail="Access denied")
    
    return OrganizationResponse(
        id=organization.id,
        name=organization.name,
        description=organization.description,
        organization_type=organization.organization_type,
        status=organization.status,
        website=organization.website,
        email=organization.email,
        phone=organization.phone,
        address=organization.address,
        country=organization.country,
        created_at=organization.created_at,
        verified_at=organization.verified_at
    )

@router.put("/{organization_id}", response_model=OrganizationResponse)
async def update_organization(
    organization_id: int,
    organization_data: OrganizationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update organization details
    """
    organization = db.query(Organization).filter(Organization.id == organization_id).first()
    if not organization:
        raise HTTPException(status_code=404, detail="Organization not found")
    
    # Check permissions
    if (current_user.role not in ["admin"] and 
        current_user.organization_id != organization_id):
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Update fields
    if organization_data.name is not None:
        organization.name = organization_data.name
    if organization_data.description is not None:
        organization.description = organization_data.description
    if organization_data.website is not None:
        organization.website = organization_data.website
    if organization_data.email is not None:
        organization.email = organization_data.email
    if organization_data.phone is not None:
        organization.phone = organization_data.phone
    if organization_data.address is not None:
        organization.address = organization_data.address
    if organization_data.country is not None:
        organization.country = organization_data.country
    
    organization.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(organization)
    
    return OrganizationResponse(
        id=organization.id,
        name=organization.name,
        description=organization.description,
        organization_type=organization.organization_type,
        status=organization.status,
        website=organization.website,
        email=organization.email,
        phone=organization.phone,
        address=organization.address,
        country=organization.country,
        created_at=organization.created_at,
        verified_at=organization.verified_at
    )

@router.put("/{organization_id}/verify")
async def verify_organization(
    organization_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Verify an organization (admin only)
    """
    if current_user.role not in ["admin"]:
        raise HTTPException(status_code=403, detail="Only admins can verify organizations")
    
    organization = db.query(Organization).filter(Organization.id == organization_id).first()
    if not organization:
        raise HTTPException(status_code=404, detail="Organization not found")
    
    organization.status = "verified"
    organization.verified_at = datetime.utcnow()
    organization.verified_by_id = current_user.id
    
    db.commit()
    
    return {"message": "Organization verified successfully"}

@router.put("/{organization_id}/reject")
async def reject_organization(
    organization_id: int,
    reason: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Reject an organization (admin only)
    """
    if current_user.role not in ["admin"]:
        raise HTTPException(status_code=403, detail="Only admins can reject organizations")
    
    organization = db.query(Organization).filter(Organization.id == organization_id).first()
    if not organization:
        raise HTTPException(status_code=404, detail="Organization not found")
    
    organization.status = "rejected"
    organization.rejection_reason = reason
    organization.rejected_at = datetime.utcnow()
    organization.rejected_by_id = current_user.id
    
    db.commit()
    
    return {"message": "Organization rejected successfully"}

@router.get("/{organization_id}/members")
async def get_organization_members(
    organization_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    limit: int = 10,
    offset: int = 0
):
    """
    Get organization members
    """
    organization = db.query(Organization).filter(Organization.id == organization_id).first()
    if not organization:
        raise HTTPException(status_code=404, detail="Organization not found")
    
    # Check permissions
    if (current_user.role not in ["admin"] and 
        current_user.organization_id != organization_id):
        raise HTTPException(status_code=403, detail="Access denied")
    
    members = db.query(User).filter(
        User.organization_id == organization_id
    ).order_by(User.created_at.desc()).offset(offset).limit(limit).all()
    
    return {
        "organization_id": organization_id,
        "organization_name": organization.name,
        "members": [
            {
                "id": member.id,
                "username": member.username,
                "full_name": member.full_name,
                "email": member.email,
                "role": member.role,
                "status": member.status,
                "created_at": member.created_at
            }
            for member in members
        ],
        "total": len(members)
    }
