#!/bin/bash

# Quick IntelliTrust Blockchain Demo
# Runs essential commands for short presentation

echo "🚀 IntelliTrust Quick Demo"
echo "=========================="

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

wait_for_user() {
    echo -e "${YELLOW}Press Enter to continue...${NC}"
    read
}

# Check if in blockchain directory
if [ ! -f "contracts/DocumentVerification.sol" ]; then
    echo "❌ Please run from blockchain directory"
    exit 1
fi

# 1. Show Contract Structure
print_step "1. Smart Contract Overview"
echo "Contract structure:"
cat contracts/DocumentVerification.sol | head -20
wait_for_user

echo "Role definitions:"
grep -A 3 "Role definitions" contracts/DocumentVerification.sol
wait_for_user

echo "Document structure:"
grep -A 10 "struct Document" contracts/DocumentVerification.sol
wait_for_user

# 2. Start Blockchain & Deploy
print_step "2. Live Demo - Starting blockchain..."
npx hardhat node > /dev/null 2>&1 &
NODE_PID=$!
sleep 3

if kill -0 $NODE_PID 2>/dev/null; then
    print_success "Local blockchain started"
else
    echo "❌ Failed to start blockchain"
    exit 1
fi

print_step "Deploying contract..."
DEPLOY_OUTPUT=$(npx hardhat run scripts/deploy.js --network localhost 2>&1)
echo "$DEPLOY_OUTPUT"

CONTRACT_ADDRESS=$(echo "$DEPLOY_OUTPUT" | grep "DocumentVerification deployed to:" | awk '{print $NF}')

if [ -n "$CONTRACT_ADDRESS" ]; then
    print_success "Contract deployed: $CONTRACT_ADDRESS"
    echo "$CONTRACT_ADDRESS" > contract_address.txt
else
    echo "❌ Deployment failed"
    kill $NODE_PID 2>/dev/null
    exit 1
fi

wait_for_user

# 3. Interactive Console
print_step "3. Interactive Testing"
echo "Starting Hardhat console..."
echo ""
echo "📋 Quick Commands to run:"
echo "========================="
echo ""
echo "// Get contract instance"
echo "const DocumentVerification = await ethers.getContractFactory('DocumentVerification');"
echo "const contract = await DocumentVerification.attach('$CONTRACT_ADDRESS');"
echo ""
echo "// Test document anchoring"
echo "const documentHash = 'a1b2c3d4e5f6789012345678901234567890abcdef1234567890abcdef12345678';"
echo "const userDid = 'did:example:123456789';"
echo "const metadata = '{\"title\":\"Birth Certificate\",\"issuer\":\"Government\"}';"
echo ""
echo "const tx = await contract.anchorDocument(documentHash, userDid, metadata, {"
echo "    value: ethers.parseEther('0.001')"
echo "});"
echo "await tx.wait();"
echo "console.log('Document anchored!');"
echo ""
echo "// Verify document"
echo "const result = await contract.verifyDocument(documentHash);"
echo "console.log('Exists:', result[0]);"
echo "console.log('Owner:', result[1]);"
echo "console.log('Timestamp:', new Date(result[2] * 1000));"
echo "console.log('Revoked:', result[4]);"
echo ""
echo "// Test security"
echo "const [deployer, user1] = await ethers.getSigners();"
echo "const userContract = contract.connect(user1);"
echo "try {"
echo "    await userContract.anchorDocument('test123', 'did:test:123', '{}', {"
echo "        value: ethers.parseEther('0.001')"
echo "    });"
echo "} catch (error) {"
echo "    console.log('✅ Security working: Access blocked');"
echo "}"
echo ""
echo "// Show audit trail"
echo "const history = await contract.getDocumentHistory(documentHash);"
echo "console.log('Document History:');"
echo "for (let i = 0; i < history[0].length; i++) {"
echo "    console.log(\`- \${new Date(history[0][i] * 1000)}: \${history[1][i]} by \${history[3][i]}\`);"
echo "}"
echo ""
echo "Type 'exit' to close console"

wait_for_user

# Start console
npx hardhat console --network localhost

# Cleanup
print_step "4. Cleanup"
kill $NODE_PID 2>/dev/null
rm -f contract_address.txt

print_success "Demo completed!"
echo ""
echo "🎉 Quick Demo Summary:"
echo "✅ Contract structure shown"
echo "✅ Blockchain deployed"
echo "✅ Interactive testing completed"
echo "✅ Security features demonstrated"
