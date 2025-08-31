from fastapi import APIRouter, Request, HTTPException, status
from typing import Any, Dict
import hmac
import hashlib
import json

from app.core.config import settings

router = APIRouter()

@router.post("/document-verified")
async def document_verified_webhook(request: Request) -> Any:
    """
    Webhook for when a document is verified.
    """
    # Verify webhook signature
    signature = request.headers.get("X-Webhook-Signature")
    if not verify_webhook_signature(request, signature):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid webhook signature"
        )
    
    body = await request.json()
    
    # Process the webhook
    # In a real implementation, you would:
    # 1. Update document status
    # 2. Send notifications
    # 3. Trigger blockchain operations
    # 4. Update analytics
    
    return {"status": "success", "message": "Document verification webhook processed"}

@router.post("/credential-issued")
async def credential_issued_webhook(request: Request) -> Any:
    """
    Webhook for when a credential is issued.
    """
    # Verify webhook signature
    signature = request.headers.get("X-Webhook-Signature")
    if not verify_webhook_signature(request, signature):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid webhook signature"
        )
    
    body = await request.json()
    
    # Process the webhook
    return {"status": "success", "message": "Credential issuance webhook processed"}

@router.post("/ai-analysis-complete")
async def ai_analysis_complete_webhook(request: Request) -> Any:
    """
    Webhook for when AI analysis is complete.
    """
    # Verify webhook signature
    signature = request.headers.get("X-Webhook-Signature")
    if not verify_webhook_signature(request, signature):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid webhook signature"
        )
    
    body = await request.json()
    
    # Process the webhook
    return {"status": "success", "message": "AI analysis webhook processed"}

def verify_webhook_signature(request: Request, signature: str) -> bool:
    """
    Verify webhook signature for security.
    """
    if not signature:
        return False
    
    # Get the raw body
    body = request.body()
    
    # Calculate expected signature
    expected_signature = hmac.new(
        settings.WEBHOOK_SECRET.encode(),
        body,
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(signature, expected_signature)
