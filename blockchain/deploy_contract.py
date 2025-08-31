#!/usr/bin/env python3
"""
Smart Contract Deployment Script for IntelliTrust
Deploys the DocumentVerification contract to Ethereum/Polygon networks
"""

import os
import json
from web3 import Web3
from eth_account import Account
import solcx

# Compile the smart contract
def compile_contract():
    """Compile the DocumentVerification smart contract"""
    try:
        # Read the contract source
        with open('DocumentVerification.sol', 'r') as file:
            contract_source = file.read()
        
        # Compile the contract
        compiled_sol = solcx.compile_standard({
            "language": "Solidity",
            "sources": {
                "DocumentVerification.sol": {
                    "content": contract_source
                }
            },
            "settings": {
                "outputSelection": {
                    "*": {
                        "*": ["abi", "metadata", "evm.bytecode", "evm.sourceMap"]
                    }
                }
            }
        }, solc_version="0.8.19")
        
        # Extract the contract
        contract = compiled_sol['contracts']['DocumentVerification.sol']['DocumentVerification']
        
        return {
            'abi': contract['abi'],
            'bytecode': contract['evm']['bytecode']['object']
        }
        
    except Exception as e:
        print(f"Error compiling contract: {e}")
        return None

def deploy_contract(w3, account, contract_abi, contract_bytecode):
    """Deploy the contract to the blockchain"""
    try:
        # Create contract instance
        contract = w3.eth.contract(abi=contract_abi, bytecode=contract_bytecode)
        
        # Build transaction
        construct_txn = contract.constructor().build_transaction({
            'from': account.address,
            'gas': 2000000,
            'gasPrice': w3.eth.gas_price,
            'nonce': w3.eth.get_transaction_count(account.address),
        })
        
        # Sign transaction
        signed_txn = w3.eth.account.sign_transaction(construct_txn, account.key)
        
        # Send transaction
        tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
        
        # Wait for transaction receipt
        tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        
        return {
            'contract_address': tx_receipt.contractAddress,
            'transaction_hash': tx_hash.hex(),
            'block_number': tx_receipt.blockNumber,
            'gas_used': tx_receipt.gasUsed
        }
        
    except Exception as e:
        print(f"Error deploying contract: {e}")
        return None

def main():
    """Main deployment function"""
    print("🚀 IntelliTrust Smart Contract Deployment")
    print("=" * 50)
    
    # Environment variables
    ethereum_rpc_url = os.getenv('ETHEREUM_RPC_URL')
    polygon_rpc_url = os.getenv('POLYGON_RPC_URL')
    private_key = os.getenv('PRIVATE_KEY')
    
    if not private_key:
        print("❌ PRIVATE_KEY environment variable not set")
        return
    
    # Compile contract
    print("📝 Compiling smart contract...")
    contract_data = compile_contract()
    if not contract_data:
        print("❌ Contract compilation failed")
        return
    
    print("✅ Contract compiled successfully")
    
    # Create account
    account = Account.from_key(private_key)
    print(f"👤 Deploying from account: {account.address}")
    
    # Deploy to Ethereum (if configured)
    if ethereum_rpc_url and ethereum_rpc_url != 'https://sepolia.infura.io/v3/YOUR_PROJECT_ID':
        print("\n🔗 Deploying to Ethereum...")
        try:
            w3 = Web3(Web3.HTTPProvider(ethereum_rpc_url))
            if w3.is_connected():
                result = deploy_contract(w3, account, contract_data['abi'], contract_data['bytecode'])
                if result:
                    print(f"✅ Contract deployed to Ethereum")
                    print(f"   Address: {result['contract_address']}")
                    print(f"   Transaction: {result['transaction_hash']}")
                    print(f"   Block: {result['block_number']}")
                    print(f"   Gas Used: {result['gas_used']}")
                    
                    # Save deployment info
                    deployment_info = {
                        'network': 'ethereum',
                        'contract_address': result['contract_address'],
                        'transaction_hash': result['transaction_hash'],
                        'block_number': result['block_number'],
                        'gas_used': result['gas_used'],
                        'abi': contract_data['abi']
                    }
                    
                    with open('ethereum_deployment.json', 'w') as f:
                        json.dump(deployment_info, f, indent=2)
                    
                    print("💾 Deployment info saved to ethereum_deployment.json")
                else:
                    print("❌ Ethereum deployment failed")
            else:
                print("❌ Could not connect to Ethereum network")
        except Exception as e:
            print(f"❌ Ethereum deployment error: {e}")
    
    # Deploy to Polygon (if configured)
    if polygon_rpc_url and polygon_rpc_url != 'https://polygon-mumbai.infura.io/v3/YOUR_PROJECT_ID':
        print("\n🔗 Deploying to Polygon...")
        try:
            w3 = Web3(Web3.HTTPProvider(polygon_rpc_url))
            if w3.is_connected():
                result = deploy_contract(w3, account, contract_data['abi'], contract_data['bytecode'])
                if result:
                    print(f"✅ Contract deployed to Polygon")
                    print(f"   Address: {result['contract_address']}")
                    print(f"   Transaction: {result['transaction_hash']}")
                    print(f"   Block: {result['block_number']}")
                    print(f"   Gas Used: {result['gas_used']}")
                    
                    # Save deployment info
                    deployment_info = {
                        'network': 'polygon',
                        'contract_address': result['contract_address'],
                        'transaction_hash': result['transaction_hash'],
                        'block_number': result['block_number'],
                        'gas_used': result['gas_used'],
                        'abi': contract_data['abi']
                    }
                    
                    with open('polygon_deployment.json', 'w') as f:
                        json.dump(deployment_info, f, indent=2)
                    
                    print("💾 Deployment info saved to polygon_deployment.json")
                else:
                    print("❌ Polygon deployment failed")
            else:
                print("❌ Could not connect to Polygon network")
        except Exception as e:
            print(f"❌ Polygon deployment error: {e}")
    
    # Save contract ABI for backend use
    with open('contract_abi.json', 'w') as f:
        json.dump(contract_data['abi'], f, indent=2)
    
    print("\n📋 Next Steps:")
    print("1. Update your .env file with the contract addresses")
    print("2. Set CONTRACT_ADDRESS to the deployed contract address")
    print("3. Ensure your backend has the correct RPC URLs")
    print("4. Test the blockchain integration")

if __name__ == "__main__":
    main()
