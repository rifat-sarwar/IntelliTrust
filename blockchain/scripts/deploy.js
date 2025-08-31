const { ethers, upgrades } = require("hardhat");
const fs = require("fs");
const path = require("path");

async function main() {
  console.log("🚀 Deploying IntelliTrust Document Verification Contract...");
  
  // Get the contract factory
  const DocumentVerification = await ethers.getContractFactory("DocumentVerification");
  
  // Get deployer account
  const [deployer] = await ethers.getSigners();
  console.log("📝 Deploying contracts with account:", deployer.address);
  console.log("💰 Account balance:", ethers.formatEther(await deployer.provider.getBalance(deployer.address)), "ETH");
  
  try {
    // Deploy the contract
    console.log("🔨 Deploying DocumentVerification contract...");
    const documentVerification = await DocumentVerification.deploy();
    
    // Wait for deployment
    await documentVerification.waitForDeployment();
    const contractAddress = await documentVerification.getAddress();
    
    console.log("✅ DocumentVerification deployed to:", contractAddress);
    
    // Get network information
    const network = await ethers.provider.getNetwork();
    const networkName = network.name === "unknown" ? "localhost" : network.name;
    const chainId = network.chainId;
    
    console.log("🌐 Network:", networkName);
    console.log("🔗 Chain ID:", chainId);
    
    // Verify contract deployment
    console.log("🔍 Verifying contract deployment...");
    const code = await ethers.provider.getCode(contractAddress);
    if (code === "0x") {
      throw new Error("Contract deployment failed - no code at address");
    }
    console.log("✅ Contract verification successful");
    
    // Test basic functionality
    console.log("🧪 Testing basic contract functionality...");
    
    // Test contract stats
    const stats = await documentVerification.getContractStats();
    console.log("📊 Contract Stats:");
    console.log("   Total Documents:", stats[0].toString());
    console.log("   Total Revoked:", stats[1].toString());
    console.log("   Max Metadata Size:", stats[2].toString());
    console.log("   Max Documents Per User:", stats[3].toString());
    console.log("   Min Anchoring Fee:", ethers.formatEther(stats[4]), "ETH");
    
    // Test role assignment
    const adminRole = await documentVerification.DEFAULT_ADMIN_ROLE();
    const anchorRole = await documentVerification.ANCHOR_ROLE();
    const revokeRole = await documentVerification.REVOKE_ROLE();
    
    console.log("🔐 Role Verification:");
    console.log("   Admin Role:", adminRole);
    console.log("   Anchor Role:", anchorRole);
    console.log("   Revoke Role:", revokeRole);
    
    // Check if deployer has admin role
    const hasAdminRole = await documentVerification.hasRole(adminRole, deployer.address);
    console.log("   Deployer has admin role:", hasAdminRole);
    
    if (!hasAdminRole) {
      throw new Error("Deployer should have admin role");
    }
    
    console.log("✅ Basic functionality test passed");
    
    // Save deployment information
    const deploymentInfo = {
      contractName: "DocumentVerification",
      contractAddress: contractAddress,
      network: networkName,
      chainId: chainId,
      deployer: deployer.address,
      deploymentTime: new Date().toISOString(),
      constructorArgs: [],
      abi: DocumentVerification.interface.formatJson(),
      roles: {
        adminRole: adminRole,
        anchorRole: anchorRole,
        revokeRole: revokeRole,
      },
      stats: {
        totalDocuments: stats[0].toString(),
        totalRevoked: stats[1].toString(),
        maxMetadataSize: stats[2].toString(),
        maxDocumentsPerUser: stats[3].toString(),
        minAnchoringFee: ethers.formatEther(stats[4]),
      }
    };
    
    // Create deployment directory if it doesn't exist
    const deploymentDir = path.join(__dirname, "..", "deployments");
    if (!fs.existsSync(deploymentDir)) {
      fs.mkdirSync(deploymentDir, { recursive: true });
    }
    
    // Save deployment info to file
    const deploymentFile = path.join(deploymentDir, `${networkName}-${chainId}.json`);
    fs.writeFileSync(deploymentFile, JSON.stringify(deploymentInfo, null, 2));
    console.log("💾 Deployment info saved to:", deploymentFile);
    
    // Create environment file template
    const envTemplate = `# Blockchain Configuration for ${networkName} (Chain ID: ${chainId})
CONTRACT_ADDRESS=${contractAddress}
NETWORK_NAME=${networkName}
CHAIN_ID=${chainId}
DEPLOYER_ADDRESS=${deployer.address}

# Add this to your .env file
BLOCKCHAIN_TYPE=${networkName === "ethereum" || networkName === "sepolia" ? "ethereum" : "polygon"}
${networkName === "ethereum" || networkName === "sepolia" ? "ETHEREUM_RPC_URL" : "POLYGON_RPC_URL"}=YOUR_RPC_URL_HERE
PRIVATE_KEY=YOUR_PRIVATE_KEY_HERE
`;
    
    const envFile = path.join(deploymentDir, `${networkName}-${chainId}.env`);
    fs.writeFileSync(envFile, envTemplate);
    console.log("📝 Environment template saved to:", envFile);
    
    console.log("\n🎉 Deployment completed successfully!");
    console.log("=" * 50);
    console.log("📋 Next steps:");
    console.log("1. Copy the contract address to your .env file");
    console.log("2. Set up your RPC URL and private key");
    console.log("3. Test the contract with sample transactions");
    console.log("4. Verify the contract on Etherscan/Polygonscan");
    
    if (networkName !== "localhost" && networkName !== "hardhat") {
      console.log("\n🔍 To verify on Etherscan/Polygonscan:");
      console.log(`npx hardhat verify --network ${networkName} ${contractAddress}`);
    }
    
    return {
      contractAddress,
      networkName,
      chainId,
      deploymentInfo
    };
    
  } catch (error) {
    console.error("❌ Deployment failed:", error.message);
    console.error("Stack trace:", error.stack);
    throw error;
  }
}

// Handle script execution
if (require.main === module) {
  main()
    .then(() => {
      console.log("✅ Deployment script completed");
      process.exit(0);
    })
    .catch((error) => {
      console.error("❌ Deployment script failed:", error);
      process.exit(1);
    });
}

module.exports = { main };
