#!/usr/bin/env python3
"""
Script to create test users for all roles in IntelliTrust
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.core.security import get_password_hash
from app.models.user import User, UserRole, UserStatus

def create_test_user(username: str, email: str, password: str, full_name: str, role: UserRole):
    """Create a test user with specified role."""
    db = SessionLocal()
    try:
        # Check if user already exists
        existing_user = db.query(User).filter(
            (User.email == email) | (User.username == username)
        ).first()
        
        if existing_user:
            print(f"User with username '{username}' or email '{email}' already exists!")
            return False
        
        # Create user
        test_user = User(
            username=username,
            email=email,
            hashed_password=get_password_hash(password),
            full_name=full_name,
            role=role,
            status=UserStatus.ACTIVE,
            did=f"did:intellitrust:{username}"
        )
        
        db.add(test_user)
        db.commit()
        db.refresh(test_user)
        
        print(f"✅ {role.value.title()} user '{username}' created successfully!")
        print(f"   ID: {test_user.id}")
        print(f"   Email: {test_user.email}")
        print(f"   Role: {test_user.role}")
        print(f"   Status: {test_user.status}")
        print(f"   DID: {test_user.did}")
        print(f"\nYou can now login with:")
        print(f"   Username: {username}")
        print(f"   Password: {password}")
        print()
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating {role.value} user: {e}")
        db.rollback()
        return False
    finally:
        db.close()

def main():
    print("🔐 IntelliTrust Test Users Creator")
    print("=" * 50)
    
    # Test users for each role
    test_users = [
        {
            "username": "testuser",
            "email": "test@example.com", 
            "password": "testpass123",
            "full_name": "Test User",
            "role": UserRole.HOLDER
        },
        {
            "username": "issuer_user",
            "email": "issuer@university.edu",
            "password": "issuer123",
            "full_name": "University Issuer",
            "role": UserRole.ISSUER
        },
        {
            "username": "verifier_user", 
            "email": "verifier@company.com",
            "password": "verifier123",
            "full_name": "Company Verifier",
            "role": UserRole.VERIFIER
        },
        {
            "username": "admin_user",
            "email": "admin@intellitrust.com",
            "password": "admin123", 
            "full_name": "System Admin",
            "role": UserRole.ADMIN
        }
    ]
    
    success_count = 0
    for user_data in test_users:
        print(f"Creating {user_data['role'].value} user...")
        if create_test_user(**user_data):
            success_count += 1
    
    print(f"\n🎉 Created {success_count}/{len(test_users)} test users successfully!")
    print("\nTest Credentials:")
    print("=" * 30)
    for user_data in test_users:
        print(f"{user_data['role'].value.title()}: {user_data['email']} / {user_data['password']}")
    
    print("\nYou can now:")
    print("1. Login with any of these credentials")
    print("2. See different UI interfaces for each role")
    print("3. Test role-based functionality")

if __name__ == "__main__":
    main()
