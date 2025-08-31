from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user, get_current_user_with_role
from app.models.user import User, UserRole, UserStatus
from app.schemas.auth import UserResponse

router = APIRouter()

@router.get("/", response_model=List[UserResponse])
def get_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_with_role(UserRole.ADMIN))
) -> Any:
    """
    Get all users (Admin only).
    """
    users = db.query(User).offset(skip).limit(limit).all()
    return [
        UserResponse(
            id=user.id,
            username=user.username,
            email=user.email,
            full_name=user.full_name,
            role=user.role,
            status=user.status,
            did=user.did,
            created_at=user.created_at
        )
        for user in users
    ]

@router.get("/pending", response_model=List[UserResponse])
def get_pending_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_with_role(UserRole.ADMIN))
) -> Any:
    """
    Get all pending users (Admin only).
    """
    users = db.query(User).filter(User.status == UserStatus.PENDING).all()
    return [
        UserResponse(
            id=user.id,
            username=user.username,
            email=user.email,
            full_name=user.full_name,
            role=user.role,
            status=user.status,
            did=user.did,
            created_at=user.created_at
        )
        for user in users
    ]

@router.post("/{user_id}/activate")
def activate_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_with_role(UserRole.ADMIN))
) -> Any:
    """
    Activate a user (Admin only).
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if user.status == UserStatus.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is already active"
        )
    
    user.status = UserStatus.ACTIVE
    db.commit()
    db.refresh(user)
    
    return {
        "message": f"User {user.username} has been activated",
        "user_id": user.id,
        "status": user.status
    }

@router.post("/{user_id}/deactivate")
def deactivate_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_with_role(UserRole.ADMIN))
) -> Any:
    """
    Deactivate a user (Admin only).
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if user.status != UserStatus.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User is not active"
        )
    
    user.status = UserStatus.INACTIVE
    db.commit()
    db.refresh(user)
    
    return {
        "message": f"User {user.username} has been deactivated",
        "user_id": user.id,
        "status": user.status
    }

@router.post("/{user_id}/suspend")
def suspend_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_with_role(UserRole.ADMIN))
) -> Any:
    """
    Suspend a user (Admin only).
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    user.status = UserStatus.SUSPENDED
    db.commit()
    db.refresh(user)
    
    return {
        "message": f"User {user.username} has been suspended",
        "user_id": user.id,
        "status": user.status
    }

@router.get("/me", response_model=UserResponse)
def get_current_user_info(
    current_user: User = Depends(get_current_user)
) -> Any:
    """
    Get current user information.
    """
    return UserResponse(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        full_name=current_user.full_name,
        role=current_user.role,
        status=current_user.status,
        did=current_user.did,
        created_at=current_user.created_at
    )
