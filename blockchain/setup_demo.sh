#!/bin/bash

# IntelliTrust Blockchain Demo Setup Script
# This script sets up the blockchain environment for judges' demonstration

set -e

echo "🚀 IntelliTrust Blockchain Demo Setup"
echo "======================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if we're in the blockchain directory
if [ ! -f "hardhat.config.js" ]; then
    print_error "Please run this script from the blockchain directory"
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    print_error "Node.js is not installed. Please install Node.js first."
    exit 1
fi

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    print_error "npm is not installed. Please install npm first."
    exit 1
fi

print_status "Installing dependencies..."
npm install

print_status "Compiling smart contracts..."
npx hardhat compile

print_success "Smart contracts compiled successfully!"

echo ""
echo "🎯 Demo Options:"
echo "1. Local Hardhat Network (Recommended for demo)"
echo "2. Sepolia Testnet (Real testnet, requires ETH)"
echo "3. Polygon Mumbai Testnet (Real testnet, requires MATIC)"
echo ""

read -p "Choose demo option (1-3): " demo_option

case $demo_option in
    1)
        print_status "Setting up local Hardhat network..."
        
        # Start local hardhat node
        print_status "Starting local blockchain network..."
        npx hardhat node &
        HARDHAT_PID=$!
        
        # Wait for network to start
        sleep 5
        
        # Deploy contract to local network
        print_status "Deploying smart contract to local network..."
        npx hardhat run scripts/deploy.js --network localhost
        
        print_success "Local blockchain setup complete!"
        print_info "Network URL: http://127.0.0.1:8545"
        print_info "Contract deployed successfully!"
        
        # Save deployment info
        if [ -f "deployments/localhost-31337.json" ]; then
            CONTRACT_ADDRESS=$(cat deployments/localhost-31337.json | grep -o '"contractAddress": "[^"]*"' | cut -d'"' -f4)
            print_info "Contract Address: $CONTRACT_ADDRESS"
            
            # Create environment file for backend
            cat > ../backend/.env.blockchain << EOF
# Blockchain Configuration for Demo
BLOCKCHAIN_TYPE=ethereum
ETHEREUM_RPC_URL=http://127.0.0.1:8545
CONTRACT_ADDRESS=$CONTRACT_ADDRESS
PRIVATE_KEY=0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80
NETWORK_NAME=localhost
CHAIN_ID=31337
EOF
            
            print_success "Environment file created: ../backend/.env.blockchain"
            print_info "Copy this to your backend .env file for blockchain integration"
        fi
        
        echo ""
        print_success "🎉 Local blockchain demo is ready!"
        print_info "To stop the local network, run: kill $HARDHAT_PID"
        ;;
        
    2)
        print_status "Setting up Sepolia testnet deployment..."
        
        # Check if .env file exists with Sepolia configuration
        if [ ! -f ".env.sepolia" ]; then
            print_warning "Sepolia configuration not found. Creating template..."
            cat > .env.sepolia << EOF
# Sepolia Testnet Configuration
SEPOLIA_RPC_URL=https://sepolia.infura.io/v3/YOUR_PROJECT_ID
PRIVATE_KEY=YOUR_PRIVATE_KEY_HERE
ETHERSCAN_API_KEY=YOUR_ETHERSCAN_API_KEY
EOF
            
            print_error "Please configure .env.sepolia with your Sepolia credentials"
            print_info "You'll need:"
            print_info "  - Infura/Alchemy RPC URL"
            print_info "  - Private key with test ETH"
            print_info "  - Etherscan API key (optional)"
            exit 1
        fi
        
        # Load environment variables
        source .env.sepolia
        
        # Deploy to Sepolia
        print_status "Deploying to Sepolia testnet..."
        npx hardhat run scripts/deploy.js --network sepolia
        
        print_success "Sepolia deployment complete!"
        print_warning "Note: This deployment costs real gas fees (testnet ETH)"
        ;;
        
    3)
        print_status "Setting up Polygon Mumbai testnet deployment..."
        
        # Check if .env file exists with Mumbai configuration
        if [ ! -f ".env.mumbai" ]; then
            print_warning "Mumbai configuration not found. Creating template..."
            cat > .env.mumbai << EOF
# Polygon Mumbai Testnet Configuration
MUMBAI_RPC_URL=https://polygon-mumbai.infura.io/v3/YOUR_PROJECT_ID
PRIVATE_KEY=YOUR_PRIVATE_KEY_HERE
POLYGONSCAN_API_KEY=YOUR_POLYGONSCAN_API_KEY
EOF
            
            print_error "Please configure .env.mumbai with your Mumbai credentials"
            print_info "You'll need:"
            print_info "  - Infura/Alchemy RPC URL"
            print_info "  - Private key with test MATIC"
            print_info "  - Polygonscan API key (optional)"
            exit 1
        fi
        
        # Load environment variables
        source .env.mumbai
        
        # Deploy to Mumbai
        print_status "Deploying to Polygon Mumbai testnet..."
        npx hardhat run scripts/deploy.js --network mumbai
        
        print_success "Mumbai deployment complete!"
        print_warning "Note: This deployment costs real gas fees (testnet MATIC)"
        ;;
        
    *)
        print_error "Invalid option selected"
        exit 1
        ;;
esac

echo ""
print_success "🎉 Blockchain setup complete!"
echo ""
print_info "Next steps for demo:"
print_info "1. Update backend .env file with blockchain configuration"
print_info "2. Run the blockchain demo: python demo_blockchain.py"
print_info "3. Start the application and show live UI integration"
echo ""
print_info "Demo credentials:"
print_info "  - Holder: test@example.com / testpass123"
print_info "  - Issuer: issuer@university.edu / issuer123"
print_info "  - Verifier: verifier@company.com / verifier123"
print_info "  - Admin: admin@intellitrust.com / admin123"
