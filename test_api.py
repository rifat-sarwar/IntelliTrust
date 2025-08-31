#!/usr/bin/env python3
import requests
import json

# Test the API endpoints
BASE_URL = "http://localhost:8000/api/v1"

def test_health():
    """Test health endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"Health check: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Health check failed: {e}")
        return False

def test_auth():
    """Test authentication"""
    try:
        # Test login
        login_data = {
            "username": "admin@intellitrust.com",
            "password": "admin123"
        }
        response = requests.post(f"{BASE_URL}/auth/login-json", json=login_data)
        print(f"Login: {response.status_code}")
        if response.status_code == 200:
            token = response.json()["access_token"]
            print(f"Token: {token[:20]}...")
            return token
        else:
            print(f"Login failed: {response.text}")
            return None
    except Exception as e:
        print(f"Auth test failed: {e}")
        return None

def test_documents(token):
    """Test document endpoints"""
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        # Test get documents
        response = requests.get(f"{BASE_URL}/documents", headers=headers)
        print(f"Get documents: {response.status_code}")
        if response.status_code == 200:
            documents = response.json()
            print(f"Found {len(documents)} documents")
            for doc in documents:
                print(f"  - {doc['title']} ({doc['document_type']})")
        else:
            print(f"Get documents failed: {response.text}")
    except Exception as e:
        print(f"Documents test failed: {e}")

if __name__ == "__main__":
    print("Testing IntelliTrust API...")
    
    # Test health
    if not test_health():
        print("Health check failed, API might not be running")
        exit(1)
    
    # Test auth
    token = test_auth()
    if not token:
        print("Authentication failed")
        exit(1)
    
    # Test documents
    test_documents(token)
    
    print("API test completed!")
