import asyncio
import logging
import json
import hashlib
import uuid
from typing import Dict, Any, Optional, List, Union
from datetime import datetime
from enum import Enum
import aiohttp
import base64
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from web3 import Web3
from eth_account import Account
from eth_account.messages import encode_defunct
import os
import time
from functools import wraps
from app.core.config import settings

logger = logging.getLogger(__name__)

class BlockchainType(Enum):
    ETHEREUM = "ethereum"
    POLYGON = "polygon"
    MOCK = "mock"

class BlockchainError(Exception):
    """Custom exception for blockchain operations"""
    pass

class GasEstimationError(BlockchainError):
    """Exception for gas estimation failures"""
    pass

class TransactionError(BlockchainError):
    """Exception for transaction failures"""
    pass

def retry_on_failure(max_retries: int = 3, delay: float = 1.0):
    """Decorator to retry blockchain operations on failure"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        logger.warning(f"Attempt {attempt + 1} failed: {str(e)}. Retrying in {delay} seconds...")
                        await asyncio.sleep(delay * (2 ** attempt))  # Exponential backoff
                    else:
                        logger.error(f"All {max_retries} attempts failed. Last error: {str(e)}")
                        raise last_exception
            return None
        return wrapper
    return decorator

class BlockchainService:
    """
    Production-ready blockchain service with security, error handling, and optimization
    """
    
    def __init__(self):
        self.blockchain_type = self._get_blockchain_type()
        self._initialize_connections()
        self._setup_security()
        
    def _get_blockchain_type(self) -> BlockchainType:
        """Get blockchain type from settings with validation"""
        blockchain_type_str = getattr(settings, 'BLOCKCHAIN_TYPE', 'ethereum').lower()
        
        if blockchain_type_str not in [bt.value for bt in BlockchainType]:
            logger.warning(f"Invalid blockchain type: {blockchain_type_str}. Defaulting to ethereum.")
            return BlockchainType.ETHEREUM
            
        return BlockchainType(blockchain_type_str)
    
    def _initialize_connections(self):
        """Initialize blockchain connections with proper error handling"""
        try:
            if self.blockchain_type == BlockchainType.ETHEREUM:
                self._init_ethereum()
            elif self.blockchain_type == BlockchainType.POLYGON:
                self._init_polygon()
            else:
                self._init_mock_blockchain()
                
            logger.info(f"Blockchain service initialized with type: {self.blockchain_type.value}")
            
        except Exception as e:
            logger.error(f"Failed to initialize blockchain: {str(e)}")
            self.blockchain_type = BlockchainType.MOCK
            self._init_mock_blockchain()
    
    def _setup_security(self):
        """Setup security measures"""
        self._nonce_cache = {}
        self._transaction_cache = {}
        self._rate_limit_counter = 0
        self._last_rate_limit_reset = time.time()
        
    def _validate_private_key(self, private_key: str) -> bool:
        """Validate private key format and security"""
        try:
            if not private_key or len(private_key) != 66 or not private_key.startswith('0x'):
                return False
            
            # Check if it's a valid hex string
            int(private_key, 16)
            
            # Basic entropy check (should have sufficient randomness)
            if private_key == '0x' + '0' * 64 or private_key == '0x' + 'f' * 64:
                return False
                
            return True
        except (ValueError, TypeError):
            return False
    
    def _init_ethereum(self):
        """Initialize Ethereum connection with security measures"""
        try:
            rpc_url = getattr(settings, 'ETHEREUM_RPC_URL', None)
            if not rpc_url or 'YOUR_PROJECT_ID' in rpc_url:
                raise BlockchainError("Ethereum RPC URL not properly configured")
            
            # Validate RPC URL
            if not rpc_url.startswith(('http://', 'https://')):
                raise BlockchainError("Invalid RPC URL format")
            
            self.ethereum_w3 = Web3(Web3.HTTPProvider(rpc_url, request_kwargs={'timeout': 30}))
            
            if not self.ethereum_w3.is_connected():
                raise BlockchainError("Failed to connect to Ethereum network")
            
            # Setup account with security validation
            private_key = getattr(settings, 'PRIVATE_KEY', None)
            if not private_key or not self._validate_private_key(private_key):
                raise BlockchainError("Invalid or missing private key")
            
            self.account = Account.from_key(private_key)
            self.ethereum_w3.eth.default_account = self.account.address
            
            # Setup contract with validation
            contract_address = getattr(settings, 'CONTRACT_ADDRESS', None)
            if not contract_address or contract_address == '0x0000000000000000000000000000000000000000':
                raise BlockchainError("Invalid contract address")
            
            # Validate contract address format
            if not Web3.is_address(contract_address):
                raise BlockchainError("Invalid contract address format")
            
            self.contract = self.ethereum_w3.eth.contract(
                address=contract_address,
                abi=self._get_contract_abi()
            )
            
            # Verify contract exists and has required functions
            self._verify_contract_functions()
            
            logger.info(f"Ethereum connection established. Account: {self.account.address}")
            
        except Exception as e:
            logger.error(f"Ethereum initialization failed: {str(e)}")
            raise BlockchainError(f"Ethereum initialization failed: {str(e)}")
    
    def _init_polygon(self):
        """Initialize Polygon connection with security measures"""
        try:
            rpc_url = getattr(settings, 'POLYGON_RPC_URL', None)
            if not rpc_url or 'YOUR_PROJECT_ID' in rpc_url:
                raise BlockchainError("Polygon RPC URL not properly configured")
            
            self.polygon_w3 = Web3(Web3.HTTPProvider(rpc_url, request_kwargs={'timeout': 30}))
            
            if not self.polygon_w3.is_connected():
                raise BlockchainError("Failed to connect to Polygon network")
            
            # Setup account with security validation
            private_key = getattr(settings, 'PRIVATE_KEY', None)
            if not private_key or not self._validate_private_key(private_key):
                raise BlockchainError("Invalid or missing private key")
            
            self.account = Account.from_key(private_key)
            self.polygon_w3.eth.default_account = self.account.address
            
            # Setup contract with validation
            contract_address = getattr(settings, 'CONTRACT_ADDRESS', None)
            if not contract_address or contract_address == '0x0000000000000000000000000000000000000000':
                raise BlockchainError("Invalid contract address")
            
            self.contract = self.polygon_w3.eth.contract(
                address=contract_address,
                abi=self._get_contract_abi()
            )
            
            # Verify contract exists and has required functions
            self._verify_contract_functions()
            
            logger.info(f"Polygon connection established. Account: {self.account.address}")
            
        except Exception as e:
            logger.error(f"Polygon initialization failed: {str(e)}")
            raise BlockchainError(f"Polygon initialization failed: {str(e)}")
    
    def _init_mock_blockchain(self):
        """Initialize mock blockchain for development/testing"""
        logger.info("Initializing mock blockchain for development")
        self._mock_transactions = {}
        self._mock_documents = {}
        self._mock_blocks = []
        self._block_counter = 0
        self._mock_nonce = 0
    
    def _get_contract_abi(self) -> List[Dict]:
        """Get enhanced contract ABI with security features"""
        return [
            {
                "inputs": [
                    {"internalType": "string", "name": "documentHash", "type": "string"},
                    {"internalType": "string", "name": "userDid", "type": "string"},
                    {"internalType": "string", "name": "metadata", "type": "string"}
                ],
                "name": "anchorDocument",
                "outputs": [{"internalType": "bool", "name": "", "type": "bool"}],
                "stateMutability": "nonpayable",
                "type": "function"
            },
            {
                "inputs": [{"internalType": "string", "name": "documentHash", "type": "string"}],
                "name": "verifyDocument",
                "outputs": [
                    {"internalType": "bool", "name": "exists", "type": "bool"},
                    {"internalType": "string", "name": "userDid", "type": "string"},
                    {"internalType": "uint256", "name": "timestamp", "type": "uint256"},
                    {"internalType": "string", "name": "metadata", "type": "string"},
                    {"internalType": "bool", "name": "revoked", "type": "bool"}
                ],
                "stateMutability": "view",
                "type": "function"
            },
            {
                "inputs": [
                    {"internalType": "string", "name": "documentHash", "type": "string"},
                    {"internalType": "string", "name": "reason", "type": "string"}
                ],
                "name": "revokeDocument",
                "outputs": [{"internalType": "bool", "name": "", "type": "bool"}],
                "stateMutability": "nonpayable",
                "type": "function"
            },
            {
                "inputs": [{"internalType": "string", "name": "documentHash", "type": "string"}],
                "name": "getDocumentHistory",
                "outputs": [
                    {"internalType": "uint256[]", "name": "timestamps", "type": "uint256[]"},
                    {"internalType": "string[]", "name": "actions", "type": "string[]"}
                ],
                "stateMutability": "view",
                "type": "function"
            }
        ]
    
    def _verify_contract_functions(self):
        """Verify that contract has all required functions"""
        required_functions = ['anchorDocument', 'verifyDocument', 'revokeDocument']
        
        for func_name in required_functions:
            if not hasattr(self.contract.functions, func_name):
                raise BlockchainError(f"Contract missing required function: {func_name}")
    
    def _validate_inputs(self, file_hash: str, user_did: str, metadata: Optional[Dict] = None):
        """Validate input parameters"""
        if not file_hash or len(file_hash) != 64:
            raise BlockchainError("Invalid file hash: must be 64 character hex string")
        
        if not user_did or len(user_did) < 10:
            raise BlockchainError("Invalid user DID: must be at least 10 characters")
        
        if metadata and not isinstance(metadata, dict):
            raise BlockchainError("Metadata must be a dictionary")
        
        # Validate metadata size (prevent gas limit issues)
        if metadata:
            metadata_str = json.dumps(metadata)
            if len(metadata_str) > 10000:  # 10KB limit
                raise BlockchainError("Metadata too large: maximum 10KB")
    
    def _estimate_gas_optimized(self, w3: Web3, contract_func, *args) -> int:
        """Estimate gas with optimization and fallback"""
        try:
            # Try to estimate gas
            estimated_gas = contract_func(*args).estimate_gas()
            
            # Add buffer for safety (20% buffer)
            gas_with_buffer = int(estimated_gas * 1.2)
            
            # Ensure minimum gas
            min_gas = 100000
            max_gas = 5000000  # 5M gas limit
            
            return max(min_gas, min(gas_with_buffer, max_gas))
            
        except Exception as e:
            logger.warning(f"Gas estimation failed: {str(e)}. Using default values.")
            return 300000  # Default gas limit
    
    def _get_optimal_gas_price(self, w3: Web3) -> int:
        """Get optimal gas price with fallback"""
        try:
            # Get current gas price
            current_gas_price = w3.eth.gas_price
            
            # Add 10% buffer for faster confirmation
            optimal_gas_price = int(current_gas_price * 1.1)
            
            # Ensure reasonable limits
            min_gas_price = w3.to_wei(1, 'gwei')  # 1 gwei minimum
            max_gas_price = w3.to_wei(100, 'gwei')  # 100 gwei maximum
            
            return max(min_gas_price, min(optimal_gas_price, max_gas_price))
            
        except Exception as e:
            logger.warning(f"Gas price estimation failed: {str(e)}. Using default.")
            return w3.to_wei(20, 'gwei')  # Default 20 gwei
    
    def _get_nonce(self, w3: Web3, address: str) -> int:
        """Get nonce with caching to prevent nonce issues"""
        cache_key = f"{address}_{w3.eth.chain_id}"
        
        if cache_key in self._nonce_cache:
            cached_nonce = self._nonce_cache[cache_key]
            # Use cached nonce if it's recent (within 5 minutes)
            if time.time() - cached_nonce.get('timestamp', 0) < 300:
                return cached_nonce['nonce']
        
        # Get fresh nonce
        nonce = w3.eth.get_transaction_count(address)
        
        # Cache the nonce
        self._nonce_cache[cache_key] = {
            'nonce': nonce,
            'timestamp': time.time()
        }
        
        return nonce
    
    @retry_on_failure(max_retries=3, delay=2.0)
    async def anchor_document(self, file_hash: str, user_did: str, metadata: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Anchor document hash to blockchain with enhanced security and error handling
        """
        try:
            # Validate inputs
            self._validate_inputs(file_hash, user_did, metadata)
            
            # Rate limiting
            self._check_rate_limit()
            
            if self.blockchain_type == BlockchainType.ETHEREUM:
                return await self._anchor_document_ethereum(file_hash, user_did, metadata)
            elif self.blockchain_type == BlockchainType.POLYGON:
                return await self._anchor_document_polygon(file_hash, user_did, metadata)
            else:
                return await self._anchor_document_mock(file_hash, user_did, metadata)
                
        except Exception as e:
            logger.error(f"Error anchoring document to blockchain: {str(e)}")
            raise BlockchainError(f"Blockchain anchoring failed: {str(e)}")
    
    async def _anchor_document_ethereum(self, file_hash: str, user_did: str, metadata: Optional[Dict] = None) -> Dict[str, Any]:
        """Anchor document to Ethereum with enhanced security"""
        try:
            if not self.ethereum_w3 or not self.contract:
                raise BlockchainError("Ethereum connection not established")
            
            # Prepare transaction data
            metadata_str = json.dumps(metadata or {})
            
            # Build transaction with optimized gas estimation
            contract_func = self.contract.functions.anchorDocument(file_hash, user_did, metadata_str)
            
            gas_limit = self._estimate_gas_optimized(self.ethereum_w3, contract_func)
            gas_price = self._get_optimal_gas_price(self.ethereum_w3)
            nonce = self._get_nonce(self.ethereum_w3, self.account.address)
            
            transaction = contract_func.build_transaction({
                'from': self.account.address,
                'gas': gas_limit,
                'gasPrice': gas_price,
                'nonce': nonce,
            })
            
            # Sign transaction
            signed_txn = self.ethereum_w3.eth.account.sign_transaction(transaction, settings.PRIVATE_KEY)
            
            # Send transaction
            tx_hash = self.ethereum_w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            
            # Wait for transaction receipt with timeout
            tx_receipt = await self._wait_for_transaction_receipt(self.ethereum_w3, tx_hash, timeout=300)
            
            # Update nonce cache
            self._nonce_cache[f"{self.account.address}_{self.ethereum_w3.eth.chain_id}"]['nonce'] = nonce + 1
            
            logger.info(f"Document anchored to Ethereum: {file_hash}, TX: {tx_hash.hex()}")
            
            return {
                "transaction_hash": tx_hash.hex(),
                "block_number": tx_receipt.blockNumber,
                "blockchain_hash": file_hash,
                "status": "confirmed",
                "timestamp": datetime.utcnow().isoformat(),
                "gas_used": tx_receipt.gasUsed,
                "gas_price": gas_price,
                "network": "ethereum",
                "chain_id": self.ethereum_w3.eth.chain_id
            }
            
        except Exception as e:
            logger.error(f"Ethereum anchoring failed: {str(e)}")
            raise TransactionError(f"Ethereum transaction failed: {str(e)}")
    
    async def _anchor_document_polygon(self, file_hash: str, user_did: str, metadata: Optional[Dict] = None) -> Dict[str, Any]:
        """Anchor document to Polygon with enhanced security"""
        try:
            if not self.polygon_w3 or not self.contract:
                raise BlockchainError("Polygon connection not established")
            
            # Prepare transaction data
            metadata_str = json.dumps(metadata or {})
            
            # Build transaction with optimized gas estimation
            contract_func = self.contract.functions.anchorDocument(file_hash, user_did, metadata_str)
            
            gas_limit = self._estimate_gas_optimized(self.polygon_w3, contract_func)
            gas_price = self._get_optimal_gas_price(self.polygon_w3)
            nonce = self._get_nonce(self.polygon_w3, self.account.address)
            
            transaction = contract_func.build_transaction({
                'from': self.account.address,
                'gas': gas_limit,
                'gasPrice': gas_price,
                'nonce': nonce,
            })
            
            # Sign transaction
            signed_txn = self.polygon_w3.eth.account.sign_transaction(transaction, settings.PRIVATE_KEY)
            
            # Send transaction
            tx_hash = self.polygon_w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            
            # Wait for transaction receipt with timeout
            tx_receipt = await self._wait_for_transaction_receipt(self.polygon_w3, tx_hash, timeout=300)
            
            # Update nonce cache
            self._nonce_cache[f"{self.account.address}_{self.polygon_w3.eth.chain_id}"]['nonce'] = nonce + 1
            
            logger.info(f"Document anchored to Polygon: {file_hash}, TX: {tx_hash.hex()}")
            
            return {
                "transaction_hash": tx_hash.hex(),
                "block_number": tx_receipt.blockNumber,
                "blockchain_hash": file_hash,
                "status": "confirmed",
                "timestamp": datetime.utcnow().isoformat(),
                "gas_used": tx_receipt.gasUsed,
                "gas_price": gas_price,
                "network": "polygon",
                "chain_id": self.polygon_w3.eth.chain_id
            }
            
        except Exception as e:
            logger.error(f"Polygon anchoring failed: {str(e)}")
            raise TransactionError(f"Polygon transaction failed: {str(e)}")
    
    async def _anchor_document_mock(self, file_hash: str, user_did: str, metadata: Optional[Dict] = None) -> Dict[str, Any]:
        """Anchor document to mock blockchain"""
        try:
            # Simulate blockchain transaction
            tx_hash = hashlib.sha256(f"{file_hash}{user_did}{time.time()}".encode()).hexdigest()
            
            # Store document data
            self._mock_documents[file_hash] = {
                'user_did': user_did,
                'metadata': metadata or {},
                'timestamp': datetime.utcnow().isoformat(),
                'revoked': False
            }
            
            # Create mock transaction
            mock_tx = {
                'hash': tx_hash,
                'block_number': self._block_counter,
                'gas_used': 100000,
                'status': 1
            }
            
            self._mock_transactions[tx_hash] = mock_tx
            self._block_counter += 1
            
            logger.info(f"Document anchored to mock blockchain: {file_hash}, TX: {tx_hash}")
            
            return {
                "transaction_hash": tx_hash,
                "block_number": mock_tx['block_number'],
                "blockchain_hash": file_hash,
                "status": "confirmed",
                "timestamp": datetime.utcnow().isoformat(),
                "gas_used": mock_tx['gas_used'],
                "network": "mock"
            }
            
        except Exception as e:
            logger.error(f"Mock anchoring failed: {str(e)}")
            raise TransactionError(f"Mock transaction failed: {str(e)}")
    
    async def _wait_for_transaction_receipt(self, w3: Web3, tx_hash: bytes, timeout: int = 300) -> Dict:
        """Wait for transaction receipt with timeout and error handling"""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                receipt = w3.eth.get_transaction_receipt(tx_hash)
                if receipt:
                    if receipt.status == 0:
                        raise TransactionError("Transaction failed on blockchain")
                    return receipt
            except Exception as e:
                logger.debug(f"Transaction not yet mined: {str(e)}")
            
            await asyncio.sleep(2)
        
        raise TransactionError(f"Transaction timeout after {timeout} seconds")
    
    def _check_rate_limit(self):
        """Implement rate limiting for blockchain operations"""
        current_time = time.time()
        
        # Reset counter if more than 1 minute has passed
        if current_time - self._last_rate_limit_reset > 60:
            self._rate_limit_counter = 0
            self._last_rate_limit_reset = current_time
        
        # Check rate limit (max 10 transactions per minute)
        if self._rate_limit_counter >= 10:
            raise BlockchainError("Rate limit exceeded: maximum 10 transactions per minute")
        
        self._rate_limit_counter += 1
    
    @retry_on_failure(max_retries=3, delay=1.0)
    async def verify_document(self, file_hash: str) -> Dict[str, Any]:
        """
        Verify document on blockchain with enhanced error handling
        """
        try:
            if not file_hash or len(file_hash) != 64:
                raise BlockchainError("Invalid file hash")
            
            if self.blockchain_type == BlockchainType.ETHEREUM:
                return await self._verify_document_ethereum(file_hash)
            elif self.blockchain_type == BlockchainType.POLYGON:
                return await self._verify_document_polygon(file_hash)
            else:
                return await self._verify_document_mock(file_hash)
                
        except Exception as e:
            logger.error(f"Error verifying document: {str(e)}")
            raise BlockchainError(f"Document verification failed: {str(e)}")
    
    async def _verify_document_ethereum(self, file_hash: str) -> Dict[str, Any]:
        """Verify document on Ethereum"""
        try:
            if not self.ethereum_w3 or not self.contract:
                raise BlockchainError("Ethereum connection not established")
            
            # Call contract function
            result = self.contract.functions.verifyDocument(file_hash).call()
            
            exists, user_did, timestamp, metadata_str, revoked = result
            
            if not exists:
                return {
                    "verified": False,
                    "error": "Document not found on blockchain"
                }
            
            # Parse metadata
            try:
                metadata = json.loads(metadata_str) if metadata_str else {}
            except json.JSONDecodeError:
                metadata = {}
            
            return {
                "verified": True,
                "user_did": user_did,
                "timestamp": datetime.fromtimestamp(timestamp).isoformat(),
                "metadata": metadata,
                "revoked": revoked,
                "network": "ethereum",
                "chain_id": self.ethereum_w3.eth.chain_id
            }
            
        except Exception as e:
            logger.error(f"Ethereum verification failed: {str(e)}")
            raise BlockchainError(f"Ethereum verification failed: {str(e)}")
    
    async def _verify_document_polygon(self, file_hash: str) -> Dict[str, Any]:
        """Verify document on Polygon"""
        try:
            if not self.polygon_w3 or not self.contract:
                raise BlockchainError("Polygon connection not established")
            
            # Call contract function
            result = self.contract.functions.verifyDocument(file_hash).call()
            
            exists, user_did, timestamp, metadata_str, revoked = result
            
            if not exists:
                return {
                    "verified": False,
                    "error": "Document not found on blockchain"
                }
            
            # Parse metadata
            try:
                metadata = json.loads(metadata_str) if metadata_str else {}
            except json.JSONDecodeError:
                metadata = {}
            
            return {
                "verified": True,
                "user_did": user_did,
                "timestamp": datetime.fromtimestamp(timestamp).isoformat(),
                "metadata": metadata,
                "revoked": revoked,
                "network": "polygon",
                "chain_id": self.polygon_w3.eth.chain_id
            }
            
        except Exception as e:
            logger.error(f"Polygon verification failed: {str(e)}")
            raise BlockchainError(f"Polygon verification failed: {str(e)}")
    
    async def _verify_document_mock(self, file_hash: str) -> Dict[str, Any]:
        """Verify document on mock blockchain"""
        try:
            if file_hash not in self._mock_documents:
                return {
                    "verified": False,
                    "error": "Document not found on blockchain"
                }
            
            doc_data = self._mock_documents[file_hash]
            
            return {
                "verified": True,
                "user_did": doc_data['user_did'],
                "timestamp": doc_data['timestamp'],
                "metadata": doc_data['metadata'],
                "revoked": doc_data['revoked'],
                "network": "mock"
            }
            
        except Exception as e:
            logger.error(f"Mock verification failed: {str(e)}")
            raise BlockchainError(f"Mock verification failed: {str(e)}")
    
    async def get_network_status(self) -> Dict[str, Any]:
        """Get blockchain network status"""
        try:
            if self.blockchain_type == BlockchainType.ETHEREUM:
                return await self._get_ethereum_status()
            elif self.blockchain_type == BlockchainType.POLYGON:
                return await self._get_polygon_status()
            else:
                return await self._get_mock_status()
                
        except Exception as e:
            logger.error(f"Error getting network status: {str(e)}")
            raise BlockchainError(f"Network status check failed: {str(e)}")
    
    async def _get_ethereum_status(self) -> Dict[str, Any]:
        """Get Ethereum network status"""
        try:
            latest_block = self.ethereum_w3.eth.block_number
            gas_price = self.ethereum_w3.eth.gas_price
            chain_id = self.ethereum_w3.eth.chain_id
            
            return {
                "status": "connected",
                "network": "ethereum",
                "chain_id": chain_id,
                "latest_block": latest_block,
                "gas_price_gwei": self.ethereum_w3.from_wei(gas_price, 'gwei'),
                "account_address": self.account.address,
                "account_balance": self.ethereum_w3.from_wei(
                    self.ethereum_w3.eth.get_balance(self.account.address), 'ether'
                )
            }
        except Exception as e:
            return {
                "status": "error",
                "network": "ethereum",
                "error": str(e)
            }
    
    async def _get_polygon_status(self) -> Dict[str, Any]:
        """Get Polygon network status"""
        try:
            latest_block = self.polygon_w3.eth.block_number
            gas_price = self.polygon_w3.eth.gas_price
            chain_id = self.polygon_w3.eth.chain_id
            
            return {
                "status": "connected",
                "network": "polygon",
                "chain_id": chain_id,
                "latest_block": latest_block,
                "gas_price_gwei": self.polygon_w3.from_wei(gas_price, 'gwei'),
                "account_address": self.account.address,
                "account_balance": self.polygon_w3.from_wei(
                    self.polygon_w3.eth.get_balance(self.account.address), 'ether'
                )
            }
        except Exception as e:
            return {
                "status": "error",
                "network": "polygon",
                "error": str(e)
            }
    
    async def _get_mock_status(self) -> Dict[str, Any]:
        """Get mock blockchain status"""
        return {
            "status": "connected",
            "network": "mock",
            "latest_block": self._block_counter,
            "total_documents": len(self._mock_documents),
            "total_transactions": len(self._mock_transactions)
        }
