# Backend API Summary - IntelliTrust

## Overview
This document provides a comprehensive summary of all backend APIs implemented in the IntelliTrust system. The APIs are organized by functionality and include all endpoints needed for the complete system.

## 🔐 Authentication APIs (`/api/v1/auth`)

### Core Authentication
- `POST /auth/register` - Register new user account
- `POST /auth/login` - User login (form data)
- `POST /auth/login-json` - User login (JSON)
- `POST /auth/logout` - User logout
- `POST /auth/refresh` - Refresh access token

### Password Management
- `POST /auth/forgot-password` - Request password reset
- `POST /auth/reset-password` - Reset password with token
- `POST /auth/change-password` - Change password (authenticated)

### Two-Factor Authentication
- `POST /auth/enable-2fa` - Enable 2FA for user
- `POST /auth/disable-2fa` - Disable 2FA for user
- `POST /auth/verify-2fa` - Verify 2FA code

## 👥 User Management APIs (`/api/v1/users`)

### User Profile
- `GET /users/me` - Get current user profile
- `PUT /users/me` - Update current user profile
- `DELETE /users/me` - Delete current user account

### User Administration (Admin Only)
- `GET /users` - Get all users (admin)
- `GET /users/{user_id}` - Get specific user (admin)
- `PUT /users/{user_id}` - Update user (admin)
- `DELETE /users/{user_id}` - Delete user (admin)
- `POST /users/{user_id}/activate` - Activate user (admin)
- `POST /users/{user_id}/deactivate` - Deactivate user (admin)

## 📄 Document Management APIs (`/api/v1/documents`)

### Document Operations
- `POST /documents/upload` - Upload new document
- `GET /documents` - Get user's documents (with filters)
- `GET /documents/{document_id}` - Get specific document
- `PUT /documents/{document_id}` - Update document metadata
- `DELETE /documents/{document_id}` - Delete document

### Document Verification
- `POST /documents/{document_id}/verify` - Request document verification
- `GET /documents/{document_id}/verification-status` - Get verification status

### Document Sharing
- `POST /documents/{document_id}/share` - Share document with user
- `GET /documents/shared-with-me` - Get documents shared with user
- `DELETE /documents/{document_id}/share/{user_id}` - Remove document sharing

## 🎓 Credential Management APIs (`/api/v1/credentials`)

### Credential Operations
- `POST /credentials/issue` - Issue new credential
- `GET /credentials/my-credentials` - Get user's credentials
- `GET /credentials/issued-credentials` - Get credentials issued by user
- `GET /credentials/{credential_id}` - Get specific credential
- `PUT /credentials/{credential_id}` - Update credential
- `DELETE /credentials/{credential_id}` - Delete credential

### Credential Status
- `POST /credentials/{credential_id}/revoke` - Revoke credential
- `POST /credentials/{credential_id}/renew` - Renew credential
- `GET /credentials/{credential_id}/qr-code` - Generate QR code for credential

### Credential Types
- `GET /credentials/types` - Get available credential types
- `POST /credentials/types` - Create new credential type (admin)

## 🔍 Verification APIs (`/api/v1/verifications`)

### Document Verification
- `POST /verifications/verify-document` - Verify document by hash
- `POST /verifications/verify-credential` - Verify credential by ID
- `POST /verifications/verify-qr` - Verify QR code

### Verification History
- `GET /verifications/my-verifications` - Get user's verification history
- `GET /verifications/{verification_id}` - Get specific verification
- `GET /verifications/document/{document_id}` - Get verifications for document

### Verification Results
- `GET /verifications/{verification_id}/result` - Get verification result
- `POST /verifications/{verification_id}/approve` - Approve verification (admin)
- `POST /verifications/{verification_id}/reject` - Reject verification (admin)

## 🏢 Organization Management APIs (`/api/v1/organizations`)

### Organization Operations
- `POST /organizations` - Create new organization
- `GET /organizations` - Get organizations (with filters)
- `GET /organizations/{organization_id}` - Get specific organization
- `PUT /organizations/{organization_id}` - Update organization
- `DELETE /organizations/{organization_id}` - Delete organization

### Organization Members
- `GET /organizations/{organization_id}/members` - Get organization members
- `POST /organizations/{organization_id}/members` - Add member to organization
- `DELETE /organizations/{organization_id}/members/{user_id}` - Remove member

### Organization Verification
- `POST /organizations/{organization_id}/verify` - Request organization verification
- `GET /organizations/{organization_id}/verification-status` - Get verification status

## ⛓️ Blockchain APIs (`/api/v1/blockchain`)

### Document Anchoring
- `POST /blockchain/anchor-document` - Anchor document to blockchain
- `GET /blockchain/document/{document_id}/transaction` - Get blockchain transaction
- `POST /blockchain/revoke-document` - Revoke document on blockchain

### Blockchain Verification
- `GET /blockchain/verify/{document_hash}` - Verify document on blockchain
- `GET /blockchain/document/{document_id}/history` - Get document blockchain history

### Network Status
- `GET /blockchain/network-status` - Get blockchain network status
- `GET /blockchain/transactions` - Get user's blockchain transactions
- `GET /blockchain/demo-stats` - Get demo statistics

## 🤖 AI Analysis APIs (`/api/v1/ai-analysis`)

### Document Analysis
- `POST /ai-analysis/analyze-document` - Analyze document with AI
- `GET /ai-analysis/document/{document_id}` - Get AI analysis results
- `POST /ai-analysis/batch-analyze` - Batch analyze documents

### Analysis Results
- `GET /ai-analysis/results/{analysis_id}` - Get specific analysis result
- `GET /ai-analysis/batch/{batch_id}` - Get batch analysis results
- `GET /ai-analysis/statistics` - Get AI analysis statistics

## 📊 Dashboard APIs (`/api/v1/dashboard`)

### User Dashboard
- `GET /dashboard/stats` - Get user dashboard statistics
- `GET /dashboard/recent-activity` - Get recent activity
- `GET /dashboard/analytics` - Get analytics data

### Admin Dashboard
- `GET /dashboard/admin/stats` - Get admin dashboard statistics (admin only)

## 📈 Reports APIs (`/api/v1/reports`)

### Report Generation
- `GET /reports/documents` - Generate document report
- `GET /reports/verifications` - Generate verification report
- `GET /reports/blockchain` - Generate blockchain report
- `GET /reports/ai-analysis` - Generate AI analysis report
- `GET /reports/users` - Generate user report (admin only)
- `GET /reports/summary` - Generate summary report

### Report Formats
- All report endpoints support JSON and CSV formats
- CSV reports are downloadable files
- Reports include filtering by date, status, and other criteria

## 📱 QR Service APIs (`/api/v1/qr`)

### QR Code Generation
- `POST /qr/generate/document/{document_id}` - Generate QR code for document
- `POST /qr/generate/credential/{credential_id}` - Generate QR code for credential

### QR Code Scanning
- `POST /qr/scan` - Scan and verify QR code
- `GET /qr/verify/{verification_code}` - Verify QR code publicly
- `GET /qr/history` - Get QR scan history

## 🔔 Webhook APIs (`/api/v1/webhooks`)

### Webhook Management
- `POST /webhooks` - Create webhook endpoint
- `GET /webhooks` - Get webhook endpoints
- `PUT /webhooks/{webhook_id}` - Update webhook endpoint
- `DELETE /webhooks/{webhook_id}` - Delete webhook endpoint

### Webhook Events
- `POST /webhooks/{webhook_id}` - Receive webhook event
- `GET /webhooks/{webhook_id}/events` - Get webhook event history

## 🏥 Health & System APIs

### Health Checks
- `GET /health` - System health check
- `GET /` - API root endpoint

### System Information
- `GET /system/info` - Get system information
- `GET /system/status` - Get system status
- `GET /system/metrics` - Get system metrics

## 📋 API Features

### Authentication & Security
- JWT-based authentication
- Role-based access control (RBAC)
- Two-factor authentication support
- Rate limiting (60 requests/minute, 1000/hour)
- Input validation and sanitization

### Data Management
- Pagination support (limit/offset)
- Filtering by multiple criteria
- Sorting options
- Bulk operations where applicable

### File Handling
- File upload with validation
- Multiple file format support (PDF, JPG, PNG, TIFF)
- File size limits (10MB max)
- Automatic file hash calculation

### Error Handling
- Consistent error response format
- Detailed error messages
- HTTP status codes
- Logging and monitoring

### Performance
- Background task processing
- Caching support
- Database query optimization
- Async/await support

## 🔧 API Configuration

### Environment Variables
```bash
# Database
DATABASE_URL=postgresql://user:pass@localhost/db

# Security
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# File Storage
S3_ENDPOINT_URL=http://localhost:9000
S3_ACCESS_KEY_ID=minioadmin
S3_SECRET_ACCESS_KEY=minioadmin123
S3_BUCKET_NAME=intellitrust-documents

# AI Engine
AI_ENGINE_URL=http://localhost:8001

# Blockchain
BLOCKCHAIN_TYPE=ethereum
ETHEREUM_RPC_URL=https://sepolia.infura.io/v3/YOUR_PROJECT_ID
CONTRACT_ADDRESS=0x1234567890abcdef...
PRIVATE_KEY=your-private-key

# Rate Limiting
RATE_LIMIT_PER_MINUTE=60
RATE_LIMIT_PER_HOUR=1000
```

### Response Formats

#### Success Response
```json
{
  "data": {...},
  "message": "Operation successful",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

#### Error Response
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data",
    "details": {...}
  },
  "timestamp": "2024-01-15T10:30:00Z"
}
```

#### Paginated Response
```json
{
  "items": [...],
  "total": 100,
  "limit": 10,
  "offset": 0,
  "has_more": true
}
```

## 🚀 Deployment

### Requirements
- Python 3.11+
- PostgreSQL 15+
- Redis 7+
- Docker & Docker Compose

### Quick Start
```bash
# Clone repository
git clone <repository-url>
cd IntelliTrust

# Set up environment
cp .env.example .env
# Edit .env with your configuration

# Start services
docker-compose up -d

# Run migrations
cd backend
alembic upgrade head

# Start API server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### API Documentation
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- OpenAPI JSON: `http://localhost:8000/openapi.json`

## 📞 Support

### Documentation
- API Documentation: `/docs`
- Database Schema: `backend/DATABASE.md`
- Blockchain Setup: `blockchain/README.md`

### Testing
- API Tests: `backend/test_api.py`
- Authentication Tests: `backend/test_auth.py`
- Blockchain Tests: `backend/test_blockchain.py`

### Monitoring
- Health Check: `/health`
- System Status: `/system/status`
- Metrics: `/system/metrics`

---

**Note**: This API summary covers all the endpoints implemented in the IntelliTrust backend system. The APIs are designed to be RESTful, secure, and scalable for production use.
