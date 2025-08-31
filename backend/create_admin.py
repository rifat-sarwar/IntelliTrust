#!/usr/bin/env python3
"""
Script to create an admin user for IntelliTrust
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.core.security import get_password_hash
from app.models.user import User, UserRole, UserStatus

def create_admin_user(username: str, email: str, password: str, full_name: str = None):
    """Create an admin user."""
    db = SessionLocal()
    try:
        # Check if admin user already exists
        existing_user = db.query(User).filter(
            (User.email == email) | (User.username == username)
        ).first()
        
        if existing_user:
            print(f"User with username '{username}' or email '{email}' already exists!")
            return False
        
        # Create admin user
        admin_user = User(
            username=username,
            email=email,
            hashed_password=get_password_hash(password),
            full_name=full_name or username,
            role=UserRole.ADMIN,
            status=UserStatus.ACTIVE,
            did=f"did:intellitrust:{username}"
        )
        
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)
        
        print(f"✅ Admin user '{username}' created successfully!")
        print(f"   ID: {admin_user.id}")
        print(f"   Email: {admin_user.email}")
        print(f"   Role: {admin_user.role}")
        print(f"   Status: {admin_user.status}")
        print(f"   DID: {admin_user.did}")
        print(f"\nYou can now login with:")
        print(f"   Username: {username}")
        print(f"   Password: {password}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating admin user: {e}")
        db.rollback()
        return False
    finally:
        db.close()

def main():
    print("🔐 IntelliTrust Admin User Creator")
    print("=" * 40)
    
    # Default admin credentials
    default_username = "admin"
    default_email = "admin@intellitrust.com"
    default_password = "admin123"
    
    print(f"Creating default admin user:")
    print(f"  Username: {default_username}")
    print(f"  Email: {default_email}")
    print(f"  Password: {default_password}")
    print()
    
    # Create the admin user
    success = create_admin_user(default_username, default_email, default_password)
    
    if success:
        print("\n🎉 Admin user created successfully!")
        print("\nYou can now:")
        print("1. Login with the admin credentials")
        print("2. Access admin endpoints to manage users")
        print("3. Activate/deactivate other users")
    else:
        print("\n❌ Failed to create admin user")

if __name__ == "__main__":
    main()
