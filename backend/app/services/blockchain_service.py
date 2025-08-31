import asyncio
import logging
import json
import hashlib
import uuid
from typing import Dict, Any, Optional, List
from datetime import datetime
from enum import Enum
import aiohttp
import base64
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from app.core.config import settings

logger = logging.getLogger(__name__)

class BlockchainType(Enum):
    HYPERLEDGER_FABRIC = "hyperledger_fabric"
    ETHEREUM = "ethereum"
    POLYGON = "polygon"
    MOCK = "mock"

class BlockchainService:
    def __init__(self):
        self.blockchain_type = getattr(settings, 'BLOCKCHAIN_TYPE', BlockchainType.MOCK)
        self.network_config_path = getattr(settings, 'FABRIC_NETWORK_CONFIG_PATH', None)
        self.channel_name = getattr(settings, 'FABRIC_CHANNEL_NAME', 'mychannel')
        self.chaincode_name = getattr(settings, 'FABRIC_CHAINCODE_NAME', 'intellitrust')
        
        # Ethereum/Polygon settings
        self.ethereum_rpc_url = getattr(settings, 'ETHEREUM_RPC_URL', None)
        self.polygon_rpc_url = getattr(settings, 'POLYGON_RPC_URL', None)
        self.contract_address = getattr(settings, 'CONTRACT_ADDRESS', None)
        self.private_key = getattr(settings, 'PRIVATE_KEY', None)
        
        # Mock storage for development
        self._mock_transactions = {}
        self._mock_documents = {}
        self._mock_blocks = []
        self._block_counter = 0
        
        # Initialize blockchain connection
        self._initialize_blockchain()

    def _initialize_blockchain(self):
        """Initialize blockchain connection based on type"""
        try:
            if self.blockchain_type == BlockchainType.HYPERLEDGER_FABRIC:
                self._init_hyperledger_fabric()
            elif self.blockchain_type == BlockchainType.ETHEREUM:
                self._init_ethereum()
            elif self.blockchain_type == BlockchainType.POLYGON:
                self._init_polygon()
            elif self.blockchain_type == BlockchainType.MOCK:
                self._init_mock_blockchain()
            
            logger.info(f"Blockchain service initialized with type: {self.blockchain_type.value}")
        except Exception as e:
            logger.error(f"Failed to initialize blockchain: {str(e)}")
            # Fallback to mock blockchain
            self.blockchain_type = BlockchainType.MOCK
            self._init_mock_blockchain()

    def _init_hyperledger_fabric(self):
        """Initialize Hyperledger Fabric connection"""
        try:
            # Try to import fabric-sdk-py
            import fabric_sdk_py
            logger.info("Hyperledger Fabric SDK loaded successfully")
        except ImportError:
            logger.warning("fabric-sdk-py not available, using mock implementation")
            self.blockchain_type = BlockchainType.MOCK
            self._init_mock_blockchain()

    def _init_ethereum(self):
        """Initialize Ethereum connection"""
        if not self.ethereum_rpc_url:
            logger.warning("Ethereum RPC URL not configured, using mock implementation")
            self.blockchain_type = BlockchainType.MOCK
            self._init_mock_blockchain()

    def _init_polygon(self):
        """Initialize Polygon connection"""
        if not self.polygon_rpc_url:
            logger.warning("Polygon RPC URL not configured, using mock implementation")
            self.blockchain_type = BlockchainType.MOCK
            self._init_mock_blockchain()

    def _init_mock_blockchain(self):
        """Initialize mock blockchain for development"""
        logger.info("Initializing mock blockchain for development")
        self._mock_transactions = {}
        self._mock_documents = {}
        self._mock_blocks = []
        self._block_counter = 0

    async def anchor_document(self, file_hash: str, user_did: str, metadata: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Anchor document hash to blockchain
        """
        try:
            if self.blockchain_type == BlockchainType.HYPERLEDGER_FABRIC:
                return await self._anchor_document_fabric(file_hash, user_did, metadata)
            elif self.blockchain_type == BlockchainType.ETHEREUM:
                return await self._anchor_document_ethereum(file_hash, user_did, metadata)
            elif self.blockchain_type == BlockchainType.POLYGON:
                return await self._anchor_document_polygon(file_hash, user_did, metadata)
            else:
                return await self._anchor_document_mock(file_hash, user_did, metadata)
        except Exception as e:
            logger.error(f"Error anchoring document to blockchain: {str(e)}")
            raise Exception(f"Blockchain anchoring failed: {str(e)}")

    async def _anchor_document_fabric(self, file_hash: str, user_did: str, metadata: Optional[Dict] = None) -> Dict[str, Any]:
        """Anchor document to Hyperledger Fabric"""
        try:
            # This would use the actual Fabric SDK
            # For now, we'll use mock implementation
            return await self._anchor_document_mock(file_hash, user_did, metadata)
        except Exception as e:
            logger.error(f"Fabric anchoring failed: {str(e)}")
            # Fallback to mock
            return await self._anchor_document_mock(file_hash, user_did, metadata)

    async def _anchor_document_ethereum(self, file_hash: str, user_did: str, metadata: Optional[Dict] = None) -> Dict[str, Any]:
        """Anchor document to Ethereum"""
        try:
            # Ethereum smart contract interaction
            transaction_data = {
                "file_hash": file_hash,
                "user_did": user_did,
                "timestamp": int(datetime.utcnow().timestamp()),
                "metadata": metadata or {}
            }
            
            # This would interact with Ethereum smart contract
            # For now, we'll use mock implementation
            return await self._anchor_document_mock(file_hash, user_did, metadata)
        except Exception as e:
            logger.error(f"Ethereum anchoring failed: {str(e)}")
            # Fallback to mock
            return await self._anchor_document_mock(file_hash, user_did, metadata)

    async def _anchor_document_polygon(self, file_hash: str, user_did: str, metadata: Optional[Dict] = None) -> Dict[str, Any]:
        """Anchor document to Polygon"""
        try:
            # Polygon smart contract interaction (similar to Ethereum)
            return await self._anchor_document_ethereum(file_hash, user_did, metadata)
        except Exception as e:
            logger.error(f"Polygon anchoring failed: {str(e)}")
            # Fallback to mock
            return await self._anchor_document_mock(file_hash, user_did, metadata)

    async def _anchor_document_mock(self, file_hash: str, user_did: str, metadata: Optional[Dict] = None) -> Dict[str, Any]:
        """Mock document anchoring for development"""
        try:
            # Generate transaction ID
            transaction_id = str(uuid.uuid4())
            
            # Create transaction data
            transaction_data = {
                "transaction_id": transaction_id,
                "file_hash": file_hash,
                "user_did": user_did,
                "timestamp": datetime.utcnow().isoformat(),
                "metadata": metadata or {},
                "operation": "anchor_document",
                "block_number": self._block_counter + 1
            }
            
            # Store transaction
            self._mock_transactions[transaction_id] = transaction_data
            self._mock_documents[file_hash] = {
                "transaction_id": transaction_id,
                "anchored_at": datetime.utcnow().isoformat(),
                "status": "confirmed"
            }
            
            # Create block
            block_data = {
                "block_number": self._block_counter + 1,
                "timestamp": datetime.utcnow().isoformat(),
                "transactions": [transaction_id],
                "previous_hash": self._get_previous_block_hash(),
                "hash": self._calculate_block_hash(transaction_data)
            }
            self._mock_blocks.append(block_data)
            self._block_counter += 1
            
            logger.info(f"Document anchored to mock blockchain: {file_hash}")
            
            return {
                "transaction_hash": transaction_id,
                "block_number": block_data["block_number"],
                "blockchain_hash": file_hash,
                "status": "confirmed",
                "timestamp": transaction_data["timestamp"]
            }
            
        except Exception as e:
            logger.error(f"Error in mock anchoring: {str(e)}")
            raise Exception(f"Mock blockchain anchoring failed: {str(e)}")

    async def verify_document(self, file_hash: str) -> Dict[str, Any]:
        """
        Verify document on blockchain
        """
        try:
            if self.blockchain_type == BlockchainType.HYPERLEDGER_FABRIC:
                return await self._verify_document_fabric(file_hash)
            elif self.blockchain_type == BlockchainType.ETHEREUM:
                return await self._verify_document_ethereum(file_hash)
            elif self.blockchain_type == BlockchainType.POLYGON:
                return await self._verify_document_polygon(file_hash)
            else:
                return await self._verify_document_mock(file_hash)
        except Exception as e:
            logger.error(f"Error verifying document on blockchain: {str(e)}")
            return {
                "verified": False,
                "error": str(e)
            }

    async def _verify_document_fabric(self, file_hash: str) -> Dict[str, Any]:
        """Verify document on Hyperledger Fabric"""
        try:
            # This would query the actual Fabric network
            return await self._verify_document_mock(file_hash)
        except Exception as e:
            logger.error(f"Fabric verification failed: {str(e)}")
            return await self._verify_document_mock(file_hash)

    async def _verify_document_ethereum(self, file_hash: str) -> Dict[str, Any]:
        """Verify document on Ethereum"""
        try:
            # This would query the Ethereum smart contract
            return await self._verify_document_mock(file_hash)
        except Exception as e:
            logger.error(f"Ethereum verification failed: {str(e)}")
            return await self._verify_document_mock(file_hash)

    async def _verify_document_polygon(self, file_hash: str) -> Dict[str, Any]:
        """Verify document on Polygon"""
        try:
            return await self._verify_document_ethereum(file_hash)
        except Exception as e:
            logger.error(f"Polygon verification failed: {str(e)}")
            return await self._verify_document_mock(file_hash)

    async def _verify_document_mock(self, file_hash: str) -> Dict[str, Any]:
        """Mock document verification for development"""
        try:
            if file_hash in self._mock_documents:
                doc_info = self._mock_documents[file_hash]
                transaction_id = doc_info["transaction_id"]
                transaction = self._mock_transactions.get(transaction_id)
                
                if transaction:
                    return {
                        "verified": True,
                        "block_number": transaction.get("block_number"),
                        "transaction_hash": transaction_id,
                        "timestamp": transaction.get("timestamp"),
                        "user_did": transaction.get("user_did"),
                        "metadata": transaction.get("metadata", {})
                    }
            
            return {
                "verified": False,
                "error": "Document not found on blockchain"
            }
            
        except Exception as e:
            logger.error(f"Error in mock verification: {str(e)}")
            return {
                "verified": False,
                "error": str(e)
            }

    async def get_network_status(self) -> Dict[str, Any]:
        """
        Get blockchain network status
        """
        try:
            if self.blockchain_type == BlockchainType.HYPERLEDGER_FABRIC:
                return await self._get_network_status_fabric()
            elif self.blockchain_type == BlockchainType.ETHEREUM:
                return await self._get_network_status_ethereum()
            elif self.blockchain_type == BlockchainType.POLYGON:
                return await self._get_network_status_polygon()
            else:
                return await self._get_network_status_mock()
        except Exception as e:
            logger.error(f"Error getting network status: {str(e)}")
            return {
                "status": "offline",
                "error": str(e)
            }

    async def _get_network_status_fabric(self) -> Dict[str, Any]:
        """Get Hyperledger Fabric network status"""
        try:
            # This would query the actual Fabric network
            return await self._get_network_status_mock()
        except Exception as e:
            logger.error(f"Fabric network status failed: {str(e)}")
            return await self._get_network_status_mock()

    async def _get_network_status_ethereum(self) -> Dict[str, Any]:
        """Get Ethereum network status"""
        try:
            if self.ethereum_rpc_url:
                async with aiohttp.ClientSession() as session:
                    async with session.post(self.ethereum_rpc_url, json={
                        "jsonrpc": "2.0",
                        "method": "eth_blockNumber",
                        "params": [],
                        "id": 1
                    }) as response:
                        if response.status == 200:
                            data = await response.json()
                            return {
                                "status": "online",
                                "latest_block": int(data.get("result", "0x0"), 16),
                                "network": "ethereum"
                            }
            
            return await self._get_network_status_mock()
        except Exception as e:
            logger.error(f"Ethereum network status failed: {str(e)}")
            return await self._get_network_status_mock()

    async def _get_network_status_polygon(self) -> Dict[str, Any]:
        """Get Polygon network status"""
        try:
            if self.polygon_rpc_url:
                async with aiohttp.ClientSession() as session:
                    async with session.post(self.polygon_rpc_url, json={
                        "jsonrpc": "2.0",
                        "method": "eth_blockNumber",
                        "params": [],
                        "id": 1
                    }) as response:
                        if response.status == 200:
                            data = await response.json()
                            return {
                                "status": "online",
                                "latest_block": int(data.get("result", "0x0"), 16),
                                "network": "polygon"
                            }
            
            return await self._get_network_status_mock()
        except Exception as e:
            logger.error(f"Polygon network status failed: {str(e)}")
            return await self._get_network_status_mock()

    async def _get_network_status_mock(self) -> Dict[str, Any]:
        """Get mock blockchain network status"""
        try:
            return {
                "status": "online",
                "peers_online": 1,
                "total_peers": 1,
                "latest_block": self._block_counter,
                "channel_name": self.channel_name,
                "network": "mock",
                "transactions_count": len(self._mock_transactions)
            }
        except Exception as e:
            logger.error(f"Error in mock network status: {str(e)}")
            return {
                "status": "offline",
                "error": str(e)
            }

    async def get_document_history(self, file_hash: str) -> List[Dict[str, Any]]:
        """
        Get document transaction history
        """
        try:
            if self.blockchain_type == BlockchainType.HYPERLEDGER_FABRIC:
                return await self._get_document_history_fabric(file_hash)
            elif self.blockchain_type == BlockchainType.ETHEREUM:
                return await self._get_document_history_ethereum(file_hash)
            elif self.blockchain_type == BlockchainType.POLYGON:
                return await self._get_document_history_polygon(file_hash)
            else:
                return await self._get_document_history_mock(file_hash)
        except Exception as e:
            logger.error(f"Error getting document history: {str(e)}")
            return []

    async def _get_document_history_fabric(self, file_hash: str) -> List[Dict[str, Any]]:
        """Get document history from Hyperledger Fabric"""
        try:
            return await self._get_document_history_mock(file_hash)
        except Exception as e:
            logger.error(f"Fabric document history failed: {str(e)}")
            return await self._get_document_history_mock(file_hash)

    async def _get_document_history_ethereum(self, file_hash: str) -> List[Dict[str, Any]]:
        """Get document history from Ethereum"""
        try:
            return await self._get_document_history_mock(file_hash)
        except Exception as e:
            logger.error(f"Ethereum document history failed: {str(e)}")
            return await self._get_document_history_mock(file_hash)

    async def _get_document_history_polygon(self, file_hash: str) -> List[Dict[str, Any]]:
        """Get document history from Polygon"""
        try:
            return await self._get_document_history_ethereum(file_hash)
        except Exception as e:
            logger.error(f"Polygon document history failed: {str(e)}")
            return await self._get_document_history_mock(file_hash)

    async def _get_document_history_mock(self, file_hash: str) -> List[Dict[str, Any]]:
        """Get mock document history for development"""
        try:
            history = []
            
            # Find all transactions related to this document
            for transaction_id, transaction in self._mock_transactions.items():
                if transaction.get("file_hash") == file_hash:
                    history.append({
                        "transaction_id": transaction_id,
                        "operation": transaction.get("operation"),
                        "timestamp": transaction.get("timestamp"),
                        "block_number": transaction.get("block_number"),
                        "user_did": transaction.get("user_did"),
                        "metadata": transaction.get("metadata", {})
                    })
            
            # Sort by timestamp
            history.sort(key=lambda x: x["timestamp"])
            return history
            
        except Exception as e:
            logger.error(f"Error in mock document history: {str(e)}")
            return []

    async def revoke_document(self, file_hash: str, user_did: str, reason: str) -> Dict[str, Any]:
        """
        Revoke document on blockchain
        """
        try:
            if self.blockchain_type == BlockchainType.HYPERLEDGER_FABRIC:
                return await self._revoke_document_fabric(file_hash, user_did, reason)
            elif self.blockchain_type == BlockchainType.ETHEREUM:
                return await self._revoke_document_ethereum(file_hash, user_did, reason)
            elif self.blockchain_type == BlockchainType.POLYGON:
                return await self._revoke_document_polygon(file_hash, user_did, reason)
            else:
                return await self._revoke_document_mock(file_hash, user_did, reason)
        except Exception as e:
            logger.error(f"Error revoking document on blockchain: {str(e)}")
            raise Exception(f"Blockchain revocation failed: {str(e)}")

    async def _revoke_document_fabric(self, file_hash: str, user_did: str, reason: str) -> Dict[str, Any]:
        """Revoke document on Hyperledger Fabric"""
        try:
            return await self._revoke_document_mock(file_hash, user_did, reason)
        except Exception as e:
            logger.error(f"Fabric revocation failed: {str(e)}")
            return await self._revoke_document_mock(file_hash, user_did, reason)

    async def _revoke_document_ethereum(self, file_hash: str, user_did: str, reason: str) -> Dict[str, Any]:
        """Revoke document on Ethereum"""
        try:
            return await self._revoke_document_mock(file_hash, user_did, reason)
        except Exception as e:
            logger.error(f"Ethereum revocation failed: {str(e)}")
            return await self._revoke_document_mock(file_hash, user_did, reason)

    async def _revoke_document_polygon(self, file_hash: str, user_did: str, reason: str) -> Dict[str, Any]:
        """Revoke document on Polygon"""
        try:
            return await self._revoke_document_ethereum(file_hash, user_did, reason)
        except Exception as e:
            logger.error(f"Polygon revocation failed: {str(e)}")
            return await self._revoke_document_mock(file_hash, user_did, reason)

    async def _revoke_document_mock(self, file_hash: str, user_did: str, reason: str) -> Dict[str, Any]:
        """Mock document revocation for development"""
        try:
            # Generate transaction ID
            transaction_id = str(uuid.uuid4())
            
            # Create revocation transaction
            transaction_data = {
                "transaction_id": transaction_id,
                "file_hash": file_hash,
                "user_did": user_did,
                "reason": reason,
                "timestamp": datetime.utcnow().isoformat(),
                "operation": "revoke_document",
                "block_number": self._block_counter + 1
            }
            
            # Store transaction
            self._mock_transactions[transaction_id] = transaction_data
            
            # Update document status
            if file_hash in self._mock_documents:
                self._mock_documents[file_hash]["status"] = "revoked"
                self._mock_documents[file_hash]["revoked_at"] = datetime.utcnow().isoformat()
                self._mock_documents[file_hash]["revocation_reason"] = reason
            
            # Create block
            block_data = {
                "block_number": self._block_counter + 1,
                "timestamp": datetime.utcnow().isoformat(),
                "transactions": [transaction_id],
                "previous_hash": self._get_previous_block_hash(),
                "hash": self._calculate_block_hash(transaction_data)
            }
            self._mock_blocks.append(block_data)
            self._block_counter += 1
            
            logger.info(f"Document revoked on mock blockchain: {file_hash}")
            
            return {
                "transaction_hash": transaction_id,
                "block_number": block_data["block_number"],
                "status": "revoked",
                "timestamp": transaction_data["timestamp"]
            }
            
        except Exception as e:
            logger.error(f"Error in mock revocation: {str(e)}")
            raise Exception(f"Mock blockchain revocation failed: {str(e)}")

    def _get_previous_block_hash(self) -> str:
        """Get hash of the previous block"""
        if not self._mock_blocks:
            return "0000000000000000000000000000000000000000000000000000000000000000"
        return self._mock_blocks[-1]["hash"]

    def _calculate_block_hash(self, transaction_data: Dict) -> str:
        """Calculate hash for a block"""
        block_content = json.dumps(transaction_data, sort_keys=True)
        return hashlib.sha256(block_content.encode()).hexdigest()

    async def close_connection(self):
        """
        Close blockchain connection
        """
        try:
            logger.info("Blockchain connection closed")
        except Exception as e:
            logger.error(f"Error closing blockchain connection: {str(e)}")

    async def get_blockchain_info(self) -> Dict[str, Any]:
        """
        Get comprehensive blockchain information
        """
        try:
            network_status = await self.get_network_status()
            
            return {
                "blockchain_type": self.blockchain_type.value,
                "network_status": network_status,
                "total_transactions": len(self._mock_transactions),
                "total_blocks": len(self._mock_blocks),
                "total_documents": len(self._mock_documents),
                "configuration": {
                    "channel_name": self.channel_name,
                    "chaincode_name": self.chaincode_name,
                    "ethereum_rpc_url": self.ethereum_rpc_url is not None,
                    "polygon_rpc_url": self.polygon_rpc_url is not None,
                    "contract_address": self.contract_address is not None
                }
            }
        except Exception as e:
            logger.error(f"Error getting blockchain info: {str(e)}")
            return {
                "error": str(e)
            }
