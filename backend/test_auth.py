#!/usr/bin/env python3
"""
Test script for IntelliTrust authentication flow
"""

import requests
import json

# API base URL
BASE_URL = "http://localhost:8000/api/v1"

def test_register():
    """Test user registration."""
    print("🔐 Testing User Registration")
    print("=" * 40)
    
    register_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpassword123",
        "full_name": "Test User"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/register", json=register_data)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            user_data = response.json()
            print("✅ Registration successful!")
            print(f"   User ID: {user_data['id']}")
            print(f"   Username: {user_data['username']}")
            print(f"   Status: {user_data['status']}")
            print(f"   Role: {user_data['role']}")
            return user_data
        else:
            print(f"❌ Registration failed: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error during registration: {e}")
        return None

def test_login(username, password):
    """Test user login."""
    print(f"\n🔑 Testing User Login")
    print("=" * 40)
    
    login_data = {
        "username": username,
        "password": password
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/login-json", json=login_data)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            token_data = response.json()
            print("✅ Login successful!")
            print(f"   Token Type: {token_data['token_type']}")
            print(f"   Expires In: {token_data['expires_in']} seconds")
            return token_data['access_token']
        else:
            print(f"❌ Login failed: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error during login: {e}")
        return None

def test_admin_login():
    """Test admin login."""
    print(f"\n👑 Testing Admin Login")
    print("=" * 40)
    
    admin_data = {
        "username": "admin",
        "password": "admin123"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/login-json", json=admin_data)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            token_data = response.json()
            print("✅ Admin login successful!")
            print(f"   Token Type: {token_data['token_type']}")
            print(f"   Expires In: {token_data['expires_in']} seconds")
            return token_data['access_token']
        else:
            print(f"❌ Admin login failed: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error during admin login: {e}")
        return None

def test_protected_endpoint(token):
    """Test accessing a protected endpoint."""
    print(f"\n🛡️ Testing Protected Endpoint")
    print("=" * 40)
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{BASE_URL}/auth/me", headers=headers)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            user_data = response.json()
            print("✅ Protected endpoint access successful!")
            print(f"   User ID: {user_data['id']}")
            print(f"   Username: {user_data['username']}")
            print(f"   Role: {user_data['role']}")
            print(f"   Status: {user_data['status']}")
            return True
        else:
            print(f"❌ Protected endpoint access failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error accessing protected endpoint: {e}")
        return False

def test_admin_endpoints(admin_token):
    """Test admin endpoints."""
    print(f"\n👑 Testing Admin Endpoints")
    print("=" * 40)
    
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    try:
        # Get all users
        response = requests.get(f"{BASE_URL}/users/", headers=headers)
        print(f"Get Users Status Code: {response.status_code}")
        
        if response.status_code == 200:
            users = response.json()
            print(f"✅ Admin can access users list! Found {len(users)} users")
            for user in users:
                print(f"   - {user['username']} ({user['role']}) - {user['status']}")
        else:
            print(f"❌ Admin users access failed: {response.text}")
            
    except Exception as e:
        print(f"❌ Error accessing admin endpoints: {e}")

def main():
    print("🚀 IntelliTrust Authentication Test")
    print("=" * 50)
    
    # Test 1: Register a new user
    user_data = test_register()
    
    # Test 2: Login with the new user
    if user_data:
        token = test_login(user_data['username'], "testpassword123")
        
        # Test 3: Access protected endpoint
        if token:
            test_protected_endpoint(token)
    
    # Test 4: Admin login
    admin_token = test_admin_login()
    
    # Test 5: Admin endpoints
    if admin_token:
        test_admin_endpoints(admin_token)
        test_protected_endpoint(admin_token)
    
    print(f"\n🎉 Authentication test completed!")

if __name__ == "__main__":
    main()
