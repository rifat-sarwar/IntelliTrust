from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class BlockchainTransactionCreate(BaseModel):
    document_id: int
    operation_type: str = "anchor_document"
    metadata: Optional[dict] = None

class BlockchainTransactionResponse(BaseModel):
    document_id: int
    status: str
    message: Optional[str] = None
    transaction_hash: Optional[str] = None
    block_number: Optional[int] = None
    timestamp: Optional[datetime] = None

class BlockchainVerificationResponse(BaseModel):
    document_hash: str
    blockchain_verified: bool
    block_number: Optional[int] = None
    transaction_hash: Optional[str] = None
    document_info: Optional[dict] = None

class NetworkStatusResponse(BaseModel):
    network: str
    status: str
    peers_online: int
    total_peers: int
    latest_block: int
    channel_name: str
