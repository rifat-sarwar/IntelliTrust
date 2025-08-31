from fastapi import APIRouter
from app.api.v1.endpoints import (
    auth,
    users,
    documents,
    credentials,
    verifications,
    organizations,
    blockchain,
    ai_analysis,
    webhooks,
    dashboard,
    reports,
    qr_service
)
from fastapi import APIRouter

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(documents.router, prefix="/documents", tags=["documents"])
api_router.include_router(credentials.router, prefix="/credentials", tags=["credentials"])
api_router.include_router(verifications.router, prefix="/verifications", tags=["verifications"])
api_router.include_router(organizations.router, prefix="/organizations", tags=["organizations"])
api_router.include_router(blockchain.router, prefix="/blockchain", tags=["blockchain"])
api_router.include_router(ai_analysis.router, prefix="/ai-analysis", tags=["ai-analysis"])
api_router.include_router(webhooks.router, prefix="/webhooks", tags=["webhooks"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])
api_router.include_router(reports.router, prefix="/reports", tags=["reports"])
api_router.include_router(qr_service.router, prefix="/qr", tags=["qr-service"])

# Health check endpoint
@api_router.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "IntelliTrust API",
        "version": "1.0.0"
    }

# Root endpoint
@api_router.get("/")
async def root():
    return {
        "message": "Welcome to IntelliTrust API",
        "docs": "/docs",
        "health": "/health",
        "version": "1.0.0"
    }
