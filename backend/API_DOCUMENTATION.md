# IntelliTrust API Documentation

## Overview

The IntelliTrust API provides a comprehensive set of endpoints for AI-driven, blockchain-backed document lifecycle management. The API is built with FastAPI and follows RESTful principles.

## Base URL

```
http://localhost:8000/api/v1
```

## Authentication

All API endpoints require authentication using JWT tokens. Include the token in the Authorization header:

```
Authorization: Bearer <your-jwt-token>
```

## Endpoints

### Authentication

#### POST /auth/login
Authenticate user and get access token.

**Request Body:**
```json
{
  "username": "user@example.com",
  "password": "password123"
}
```

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "username": "user@example.com",
    "full_name": "John Doe",
    "role": "issuer"
  }
}
```

#### POST /auth/register
Register a new user account.

**Request Body:**
```json
{
  "username": "newuser@example.com",
  "email": "newuser@example.com",
  "password": "password123",
  "full_name": "New User",
  "role": "holder"
}
```

### Documents

#### POST /documents/upload
Upload a new document for verification.

**Request:** Multipart form data
- `file`: Document file (PDF, JPG, PNG)
- `document_type`: Type of document
- `title`: Document title
- `description`: Document description

**Response:**
```json
{
  "id": 1,
  "title": "Bachelor Degree",
  "status": "pending_verification",
  "file_hash": "abc123...",
  "uploaded_at": "2024-01-15T10:30:00Z"
}
```

#### GET /documents
Get list of user's documents.

**Query Parameters:**
- `status`: Filter by status (draft, pending_verification, verified, rejected)
- `document_type`: Filter by document type
- `limit`: Number of results (default: 10)
- `offset`: Pagination offset (default: 0)

#### GET /documents/{document_id}
Get specific document details.

#### PUT /documents/{document_id}
Update document metadata.

#### DELETE /documents/{document_id}
Delete a document.

### AI Analysis

#### POST /ai-analysis/analyze-document
Upload and analyze a document using AI engine.

**Request:** Multipart form data
- `file`: Document file
- `document_type`: Optional document type

**Response:**
```json
{
  "document_id": 1,
  "status": "processing",
  "message": "Document uploaded and analysis started"
}
```

#### GET /ai-analysis/document/{document_id}
Get AI analysis results for a document.

**Response:**
```json
{
  "document_id": 1,
  "status": "completed",
  "analysis_results": {
    "document_type": "academic_degree",
    "forensic_analysis": {
      "score": 0.95,
      "details": "..."
    },
    "template_validation": {
      "score": 0.88,
      "details": "..."
    },
    "content_analysis": {
      "score": 0.92,
      "details": "..."
    },
    "authenticity_score": 0.92,
    "is_authentic": true
  },
  "confidence_score": 0.92,
  "is_authentic": true
}
```

### Blockchain

#### POST /blockchain/anchor-document
Anchor a verified document to the blockchain.

**Request Body:**
```json
{
  "document_id": 1
}
```

**Response:**
```json
{
  "document_id": 1,
  "status": "processing",
  "message": "Document anchoring to blockchain started"
}
```

#### GET /blockchain/document/{document_id}/transaction
Get blockchain transaction for a document.

**Response:**
```json
{
  "document_id": 1,
  "transaction_hash": "0xabc123...",
  "block_number": 12345,
  "status": "confirmed",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

#### GET /blockchain/verify/{document_hash}
Verify document authenticity on blockchain.

**Response:**
```json
{
  "document_hash": "abc123...",
  "blockchain_verified": true,
  "block_number": 12345,
  "transaction_hash": "0xabc123...",
  "document_info": {
    "title": "Bachelor Degree",
    "owner_did": "did:example:123",
    "issued_at": "2024-01-15T10:30:00Z"
  }
}
```

#### GET /blockchain/network-status
Get blockchain network status.

**Response:**
```json
{
  "network": "Hyperledger Fabric",
  "status": "online",
  "peers_online": 4,
  "total_peers": 4,
  "latest_block": 12345,
  "channel_name": "intellitrust-channel"
}
```

### Credentials

#### POST /credentials/issue
Issue a new verifiable credential.

**Request Body:**
```json
{
  "document_id": 1,
  "holder_id": 2,
  "credential_type": "academic_degree",
  "title": "Bachelor of Computer Science",
  "description": "Degree credential for Computer Science",
  "validity_days": 365
}
```

**Response:**
```json
{
  "id": 1,
  "title": "Bachelor of Computer Science",
  "credential_type": "academic_degree",
  "holder_id": 2,
  "issuer_id": 1,
  "status": "active",
  "issued_at": "2024-01-15T10:30:00Z",
  "expires_at": "2025-01-15T10:30:00Z"
}
```

#### GET /credentials/my-credentials
Get user's credentials (as holder).

**Query Parameters:**
- `status`: Filter by status (active, expired, revoked)
- `limit`: Number of results (default: 10)
- `offset`: Pagination offset (default: 0)

#### GET /credentials/issued-credentials
Get credentials issued by the current user.

#### GET /credentials/{credential_id}
Get specific credential details.

#### PUT /credentials/{credential_id}/revoke
Revoke a credential.

**Request Body:**
```json
{
  "reason": "Credential compromised"
}
```

#### GET /credentials/{credential_id}/qr-code
Get QR code for credential verification.

**Response:**
```json
{
  "credential_id": 1,
  "qr_code": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA...",
  "verification_url": "http://localhost:3000/verify/1"
}
```

### Verifications

#### POST /verifications/verify-document
Verify a document by its hash.

**Request Body:**
```json
{
  "document_hash": "abc123..."
}
```

**Response:**
```json
{
  "id": 1,
  "document_id": 1,
  "verification_type": "document_verification",
  "status": "processing",
  "message": "Document verification started"
}
```

#### POST /verifications/verify-credential
Verify a credential by its ID.

**Request Body:**
```json
{
  "credential_id": 1
}
```

#### GET /verifications/{verification_id}
Get verification result.

**Response:**
```json
{
  "id": 1,
  "document_id": 1,
  "verification_type": "document_verification",
  "status": "completed",
  "result": {
    "blockchain_verified": true,
    "ai_verified": true,
    "overall_verified": true,
    "blockchain_result": {...},
    "ai_result": {...}
  },
  "verified_at": "2024-01-15T10:30:00Z"
}
```

#### POST /verifications/verify-qr
Verify document/credential from QR code data.

**Request Body:**
```json
{
  "qr_data": "{\"type\":\"credential_verification\",\"credential_id\":1}"
}
```

**Response:**
```json
{
  "verified": true,
  "verification_type": "credential_verification",
  "credential_info": {
    "id": 1,
    "title": "Bachelor of Computer Science",
    "issuer": "University of Technology",
    "holder": "John Doe",
    "issued_at": "2024-01-15T10:30:00Z",
    "expires_at": "2025-01-15T10:30:00Z"
  },
  "blockchain_verified": true,
  "verification_timestamp": "2024-01-15T10:30:00Z"
}
```

### Organizations

#### POST /organizations
Create a new organization (admin only).

**Request Body:**
```json
{
  "name": "University of Technology",
  "description": "Leading technology university",
  "organization_type": "academic",
  "website": "https://university.edu",
  "email": "admin@university.edu",
  "phone": "+1-555-123-4567",
  "address": "123 University Ave",
  "country": "USA"
}
```

#### GET /organizations
Get list of organizations.

**Query Parameters:**
- `status`: Filter by status (pending, verified, rejected)
- `limit`: Number of results (default: 10)
- `offset`: Pagination offset (default: 0)

#### GET /organizations/{organization_id}
Get specific organization details.

#### PUT /organizations/{organization_id}
Update organization details.

#### PUT /organizations/{organization_id}/verify
Verify an organization (admin only).

#### PUT /organizations/{organization_id}/reject
Reject an organization (admin only).

**Request Body:**
```json
{
  "reason": "Insufficient documentation"
}
```

#### GET /organizations/{organization_id}/members
Get organization members.

### Users

#### GET /users/me
Get current user profile.

#### PUT /users/me
Update current user profile.

#### GET /users
Get list of users (admin only).

### Webhooks

#### POST /webhooks/{webhook_id}
Receive webhook notifications.

**Headers:**
```
X-Webhook-Signature: sha256=abc123...
```

**Request Body:**
```json
{
  "event": "document.verified",
  "data": {
    "document_id": 1,
    "status": "verified",
    "timestamp": "2024-01-15T10:30:00Z"
  }
}
```

## Error Responses

All endpoints return consistent error responses:

```json
{
  "detail": "Error message description"
}
```

Common HTTP status codes:
- `200`: Success
- `201`: Created
- `400`: Bad Request
- `401`: Unauthorized
- `403`: Forbidden
- `404`: Not Found
- `422`: Validation Error
- `500`: Internal Server Error

## Rate Limiting

API requests are rate-limited:
- 60 requests per minute per user
- 1000 requests per hour per user

Rate limit headers are included in responses:
```
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 59
X-RateLimit-Reset: 1642234567
```

## Pagination

List endpoints support pagination with `limit` and `offset` parameters. Response includes pagination metadata:

```json
{
  "items": [...],
  "total": 100,
  "limit": 10,
  "offset": 0,
  "has_more": true
}
```

## File Upload

File upload endpoints accept multipart form data with the following restrictions:
- Maximum file size: 10MB
- Supported formats: PDF, JPG, JPEG, PNG, TIFF
- Files are automatically scanned for malware

## WebSocket Support

Real-time updates are available via WebSocket connections:

```
ws://localhost:8000/ws
```

Events include:
- `document.verified`
- `credential.issued`
- `blockchain.transaction`
- `verification.completed`

## SDKs and Libraries

Official SDKs are available for:
- Python: `pip install intellitrust-sdk`
- JavaScript: `npm install @intellitrust/sdk`
- Java: Available in Maven Central

## Support

For API support and questions:
- Documentation: https://docs.intellitrust.com
- Email: api-support@intellitrust.com
- Status Page: https://status.intellitrust.com
