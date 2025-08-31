# IntelliTrust Blockchain Implementation

This directory contains the blockchain implementation for IntelliTrust, providing secure document verification through multiple blockchain networks.

## 🏗️ Architecture

The blockchain implementation supports multiple blockchain networks:

- **Ethereum** (Primary) - For public blockchain verification
- **Polygon** - For low-cost, high-speed transactions
- **Hyperledger Fabric** - For enterprise/private blockchain networks
- **Mock Blockchain** - For development and testing

## 📁 File Structure

```
blockchain/
├── DocumentVerification.sol    # Smart contract for Ethereum/Polygon
├── deploy_contract.py          # Contract deployment script
├── network-config.yaml         # Hyperledger Fabric configuration
├── README.md                   # This file
├── ethereum_deployment.json    # Ethereum deployment info (generated)
├── polygon_deployment.json     # Polygon deployment info (generated)
└── contract_abi.json          # Contract ABI (generated)
```

## 🔧 Smart Contract

### DocumentVerification.sol

A Solidity smart contract that provides:

- **Document Anchoring**: Store document hashes on blockchain
- **Document Verification**: Verify document authenticity
- **Document Revocation**: Revoke compromised documents
- **Access Control**: Role-based permissions
- **Event Logging**: Audit trail for all operations

### Key Functions

```solidity
// Anchor a document to blockchain
function anchorDocument(string memory documentHash, string memory userDid, string memory metadata)

// Verify document authenticity
function verifyDocument(string memory documentHash) returns (bool exists, string memory userDid, uint256 timestamp, string memory metadata)

// Revoke a document
function revokeDocument(string memory documentHash, string memory reason)
```

## 🚀 Deployment

### Prerequisites

1. **Ethereum/Polygon Setup**:
   - Infura account (or other RPC provider)
   - MetaMask or similar wallet
   - Test ETH/MATIC for gas fees

2. **Environment Variables**:
   ```bash
   ETHEREUM_RPC_URL=https://sepolia.infura.io/v3/YOUR_PROJECT_ID
   POLYGON_RPC_URL=https://polygon-mumbai.infura.io/v3/YOUR_PROJECT_ID
   PRIVATE_KEY=your-private-key-here
   ```

### Deploy Smart Contract

1. **Install Dependencies**:
   ```bash
   cd blockchain
   pip install web3 eth-account py-solc-x
   ```

2. **Deploy Contract**:
   ```bash
   python deploy_contract.py
   ```

3. **Update Configuration**:
   - Copy contract addresses from generated JSON files
   - Update your `.env` file with the contract addresses

## 🔗 Backend Integration

### Blockchain Service

The backend uses `BlockchainService` class for all blockchain operations:

```python
from app.services.blockchain_service import BlockchainService

# Initialize service
blockchain_service = BlockchainService()

# Anchor document
result = await blockchain_service.anchor_document(
    file_hash="abc123...",
    user_did="did:example:user123",
    metadata={"title": "Degree Certificate"}
)

# Verify document
verification = await blockchain_service.verify_document("abc123...")
```

### Configuration

Set blockchain type in your `.env` file:

```bash
# Choose blockchain type
BLOCKCHAIN_TYPE=ethereum  # or polygon, hyperledger_fabric, mock

# Network configuration
ETHEREUM_RPC_URL=https://sepolia.infura.io/v3/YOUR_PROJECT_ID
POLYGON_RPC_URL=https://polygon-mumbai.infura.io/v3/YOUR_PROJECT_ID
CONTRACT_ADDRESS=0x1234567890abcdef...
PRIVATE_KEY=your-private-key-here
```

## 🧪 Testing

### Run Blockchain Tests

```bash
cd backend
python test_blockchain.py
```

This will test:
- ✅ Network connectivity
- ✅ Document anchoring
- ✅ Document verification
- ✅ Document history
- ✅ Document revocation
- ✅ Multiple document handling

### Test Results

The test script provides detailed output showing:
- Transaction hashes
- Block numbers
- Gas usage
- Network status
- Error handling

## 🔒 Security Features

### Access Control
- Role-based permissions
- Owner-only functions
- Authorized user management

### Data Integrity
- Cryptographic hashing
- Immutable audit trail
- Timestamp verification

### Privacy
- Only document hashes stored on blockchain
- Metadata encryption support
- User DID-based identification

## 📊 Performance

### Gas Optimization
- Efficient smart contract design
- Minimal storage usage
- Optimized function calls

### Scalability
- Support for multiple networks
- Batch processing capabilities
- Event-driven architecture

## 🌐 Network Support

### Ethereum (Sepolia Testnet)
- **RPC URL**: `https://sepolia.infura.io/v3/YOUR_PROJECT_ID`
- **Chain ID**: 11155111
- **Block Time**: ~12 seconds
- **Gas Cost**: ~$0.01-0.10 per transaction

### Polygon (Mumbai Testnet)
- **RPC URL**: `https://polygon-mumbai.infura.io/v3/YOUR_PROJECT_ID`
- **Chain ID**: 80001
- **Block Time**: ~2 seconds
- **Gas Cost**: ~$0.001-0.01 per transaction

### Hyperledger Fabric
- **Network**: Private/Consortium
- **Block Time**: Configurable
- **Gas Cost**: None (private network)

## 🔄 Migration Guide

### From Mock to Real Blockchain

1. **Deploy Smart Contract**:
   ```bash
   python deploy_contract.py
   ```

2. **Update Environment**:
   ```bash
   BLOCKCHAIN_TYPE=ethereum
   CONTRACT_ADDRESS=0x1234567890abcdef...
   PRIVATE_KEY=your-private-key-here
   ```

3. **Test Integration**:
   ```bash
   python test_blockchain.py
   ```

4. **Update Backend**:
   - Restart backend service
   - Verify blockchain connectivity
   - Test document operations

## 🛠️ Troubleshooting

### Common Issues

1. **Connection Failed**:
   - Check RPC URL
   - Verify network connectivity
   - Ensure Infura project is active

2. **Transaction Failed**:
   - Check gas fees
   - Verify account balance
   - Check contract address

3. **Contract Not Found**:
   - Verify contract deployment
   - Check contract address
   - Ensure correct network

### Debug Mode

Enable debug logging in your `.env`:

```bash
LOG_LEVEL=DEBUG
```

## 📈 Monitoring

### Blockchain Metrics
- Transaction count
- Gas usage
- Block confirmation time
- Network status

### Health Checks
- Network connectivity
- Contract availability
- Account balance
- Transaction success rate

## 🔮 Future Enhancements

### Planned Features
- **Multi-chain Support**: Support for more blockchain networks
- **Layer 2 Solutions**: Integration with Polygon, Arbitrum, Optimism
- **Zero-Knowledge Proofs**: Privacy-preserving verification
- **Cross-chain Verification**: Verify documents across multiple chains

### Performance Improvements
- **Batch Processing**: Process multiple documents in single transaction
- **Gas Optimization**: Further reduce transaction costs
- **Caching**: Implement blockchain data caching
- **Indexing**: Add blockchain event indexing

## 📚 Resources

### Documentation
- [Web3.py Documentation](https://web3py.readthedocs.io/)
- [Solidity Documentation](https://docs.soliditylang.org/)
- [Ethereum Development](https://ethereum.org/developers/)

### Tools
- [Remix IDE](https://remix.ethereum.org/) - Smart contract development
- [Etherscan](https://etherscan.io/) - Blockchain explorer
- [Polygonscan](https://polygonscan.com/) - Polygon explorer

### Testing Networks
- [Sepolia Faucet](https://sepoliafaucet.com/) - Get test ETH
- [Polygon Faucet](https://faucet.polygon.technology/) - Get test MATIC

---

**Note**: This implementation provides a production-ready blockchain integration for document verification. For production deployment, ensure proper security measures, key management, and network configuration.
