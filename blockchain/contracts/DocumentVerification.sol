// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "@openzeppelin/contracts/utils/ReentrancyGuard.sol";
import "@openzeppelin/contracts/access/AccessControl.sol";
import "@openzeppelin/contracts/utils/Pausable.sol";

/**
 * @title DocumentVerification
 * @dev Secure smart contract for anchoring and verifying document hashes on blockchain
 * @author IntelliTrust
 * @notice This contract provides document verification with security features
 */
contract DocumentVerification is ReentrancyGuard, AccessControl, Pausable {
    
    // Role definitions
    bytes32 public constant ANCHOR_ROLE = keccak256("ANCHOR_ROLE");
    bytes32 public constant REVOKE_ROLE = keccak256("REVOKE_ROLE");
    bytes32 public constant ADMIN_ROLE = keccak256("ADMIN_ROLE");
    
    // Events
    event DocumentAnchored(
        string indexed documentHash,
        string indexed userDid,
        address indexed anchorer,
        uint256 timestamp,
        string metadata,
        uint256 documentId
    );
    
    event DocumentRevoked(
        string indexed documentHash,
        string reason,
        address indexed revoker,
        uint256 timestamp,
        uint256 documentId
    );
    
    event DocumentUpdated(
        string indexed documentHash,
        string newMetadata,
        address indexed updater,
        uint256 timestamp,
        uint256 documentId
    );
    
    // Structs
    struct Document {
        string userDid;
        uint256 timestamp;
        string metadata;
        bool exists;
        bool revoked;
        string revocationReason;
        uint256 revocationTimestamp;
        address anchorer;
        address revoker;
        uint256 documentId;
        uint256 version;
    }
    
    struct DocumentHistory {
        uint256 timestamp;
        string action;
        string metadata;
        address actor;
    }
    
    // State variables
    mapping(string => Document) public documents;
    mapping(string => bool) public documentExists;
    mapping(uint256 => DocumentHistory[]) public documentHistory;
    mapping(address => uint256[]) public userDocuments;
    
    // Counters
    uint256 private _documentIdCounter = 0;
    uint256 private _totalDocuments = 0;
    uint256 private _totalRevoked = 0;
    
    // Configuration
    uint256 public maxMetadataSize = 10000; // 10KB limit
    uint256 public maxDocumentsPerUser = 1000;
    uint256 public minAnchoringFee = 0.001 ether;
    
    // Modifiers
    modifier onlyValidHash(string memory documentHash) {
        require(bytes(documentHash).length == 64, "Invalid document hash length");
        require(_isValidHexString(documentHash), "Invalid document hash format");
        _;
    }
    
    modifier onlyValidDid(string memory userDid) {
        require(bytes(userDid).length >= 10, "User DID too short");
        require(bytes(userDid).length <= 255, "User DID too long");
        _;
    }
    
    modifier onlyValidMetadata(string memory metadata) {
        require(bytes(metadata).length <= maxMetadataSize, "Metadata too large");
        _;
    }
    
    modifier onlyDocumentExists(string memory documentHash) {
        require(documentExists[documentHash], "Document does not exist");
        _;
    }
    
    modifier onlyDocumentNotRevoked(string memory documentHash) {
        require(!documents[documentHash].revoked, "Document is revoked");
        _;
    }
    
    // Constructor
    constructor() {
        _grantRole(DEFAULT_ADMIN_ROLE, msg.sender);
        _grantRole(ADMIN_ROLE, msg.sender);
        _grantRole(ANCHOR_ROLE, msg.sender);
        _grantRole(REVOKE_ROLE, msg.sender);
    }
    
    /**
     * @dev Anchor a document hash to the blockchain
     * @param documentHash The hash of the document (64 character hex string)
     * @param userDid The DID of the user who owns the document
     * @param metadata Additional metadata about the document (JSON string)
     */
    function anchorDocument(
        string memory documentHash,
        string memory userDid,
        string memory metadata
    ) 
        external 
        payable 
        nonReentrant 
        whenNotPaused 
        onlyRole(ANCHOR_ROLE)
        onlyValidHash(documentHash)
        onlyValidDid(userDid)
        onlyValidMetadata(metadata)
    {
        require(!documentExists[documentHash], "Document already exists");
        require(msg.value >= minAnchoringFee, "Insufficient anchoring fee");
        
        // Check user document limit
        require(userDocuments[msg.sender].length < maxDocumentsPerUser, "User document limit exceeded");
        
        // Generate document ID
        _documentIdCounter++;
        uint256 documentId = _documentIdCounter;
        
        // Create document
        Document memory newDocument = Document({
            userDid: userDid,
            timestamp: block.timestamp,
            metadata: metadata,
            exists: true,
            revoked: false,
            revocationReason: "",
            revocationTimestamp: 0,
            anchorer: msg.sender,
            revoker: address(0),
            documentId: documentId,
            version: 1
        });
        
        // Store document
        documents[documentHash] = newDocument;
        documentExists[documentHash] = true;
        userDocuments[msg.sender].push(documentId);
        
        // Add to history
        documentHistory[documentId].push(DocumentHistory({
            timestamp: block.timestamp,
            action: "ANCHORED",
            metadata: metadata,
            actor: msg.sender
        }));
        
        // Update counters
        _totalDocuments++;
        
        emit DocumentAnchored(documentHash, userDid, msg.sender, block.timestamp, metadata, documentId);
    }
    
    /**
     * @dev Verify if a document exists and get its details
     * @param documentHash The hash of the document to verify
     * @return exists Whether the document exists
     * @return userDid The DID of the document owner
     * @return timestamp When the document was anchored
     * @return metadata Additional metadata
     * @return revoked Whether the document is revoked
     * @return documentId The unique document ID
     */
    function verifyDocument(string memory documentHash) 
        external 
        view 
        onlyValidHash(documentHash)
        returns (
            bool exists,
            string memory userDid,
            uint256 timestamp,
            string memory metadata,
            bool revoked,
            uint256 documentId
        )
    {
        Document memory doc = documents[documentHash];
        return (
            doc.exists,
            doc.userDid,
            doc.timestamp,
            doc.metadata,
            doc.revoked,
            doc.documentId
        );
    }
    
    /**
     * @dev Revoke a document
     * @param documentHash The hash of the document to revoke
     * @param reason The reason for revocation
     */
    function revokeDocument(
        string memory documentHash, 
        string memory reason
    ) 
        external 
        nonReentrant 
        whenNotPaused 
        onlyRole(REVOKE_ROLE)
        onlyValidHash(documentHash)
        onlyDocumentExists(documentHash)
        onlyDocumentNotRevoked(documentHash)
    {
        require(bytes(reason).length > 0, "Revocation reason required");
        require(bytes(reason).length <= 1000, "Revocation reason too long");
        
        Document storage doc = documents[documentHash];
        doc.revoked = true;
        doc.revocationReason = reason;
        doc.revocationTimestamp = block.timestamp;
        doc.revoker = msg.sender;
        
        // Add to history
        documentHistory[doc.documentId].push(DocumentHistory({
            timestamp: block.timestamp,
            action: "REVOKED",
            metadata: reason,
            actor: msg.sender
        }));
        
        // Update counters
        _totalRevoked++;
        
        emit DocumentRevoked(documentHash, reason, msg.sender, block.timestamp, doc.documentId);
    }
    
    /**
     * @dev Update document metadata
     * @param documentHash The hash of the document to update
     * @param newMetadata The new metadata
     */
    function updateDocumentMetadata(
        string memory documentHash,
        string memory newMetadata
    ) 
        external 
        nonReentrant 
        whenNotPaused 
        onlyRole(ANCHOR_ROLE)
        onlyValidHash(documentHash)
        onlyValidMetadata(newMetadata)
        onlyDocumentExists(documentHash)
        onlyDocumentNotRevoked(documentHash)
    {
        Document storage doc = documents[documentHash];
        doc.metadata = newMetadata;
        doc.version++;
        
        // Add to history
        documentHistory[doc.documentId].push(DocumentHistory({
            timestamp: block.timestamp,
            action: "UPDATED",
            metadata: newMetadata,
            actor: msg.sender
        }));
        
        emit DocumentUpdated(documentHash, newMetadata, msg.sender, block.timestamp, doc.documentId);
    }
    
    /**
     * @dev Get document history
     * @param documentHash The hash of the document
     * @return timestamps Array of timestamps
     * @return actions Array of actions
     * @return metadatas Array of metadata
     * @return actors Array of actors
     */
    function getDocumentHistory(string memory documentHash)
        external
        view
        onlyValidHash(documentHash)
        onlyDocumentExists(documentHash)
        returns (
            uint256[] memory timestamps,
            string[] memory actions,
            string[] memory metadatas,
            address[] memory actors
        )
    {
        Document memory doc = documents[documentHash];
        DocumentHistory[] memory history = documentHistory[doc.documentId];
        
        uint256 length = history.length;
        timestamps = new uint256[](length);
        actions = new string[](length);
        metadatas = new string[](length);
        actors = new address[](length);
        
        for (uint256 i = 0; i < length; i++) {
            timestamps[i] = history[i].timestamp;
            actions[i] = history[i].action;
            metadatas[i] = history[i].metadata;
            actors[i] = history[i].actor;
        }
    }
    
    /**
     * @dev Get user documents
     * @param user The user address
     * @return documentIds Array of document IDs
     */
    function getUserDocuments(address user)
        external
        view
        returns (uint256[] memory documentIds)
    {
        return userDocuments[user];
    }
    
    /**
     * @dev Get contract statistics
     * @return totalDocuments Total number of documents
     * @return totalRevoked Total number of revoked documents
     * @return maxMetadataSize Maximum metadata size
     * @return maxDocumentsPerUser Maximum documents per user
     * @return minAnchoringFee Minimum anchoring fee
     */
    function getContractStats()
        external
        view
        returns (
            uint256 totalDocuments,
            uint256 totalRevoked,
            uint256 maxMetadataSize,
            uint256 maxDocumentsPerUser,
            uint256 minAnchoringFee
        )
    {
        return (
            _totalDocuments,
            _totalRevoked,
            maxMetadataSize,
            maxDocumentsPerUser,
            minAnchoringFee
        );
    }
    
    /**
     * @dev Update contract configuration (admin only)
     * @param newMaxMetadataSize New maximum metadata size
     * @param newMaxDocumentsPerUser New maximum documents per user
     * @param newMinAnchoringFee New minimum anchoring fee
     */
    function updateConfiguration(
        uint256 newMaxMetadataSize,
        uint256 newMaxDocumentsPerUser,
        uint256 newMinAnchoringFee
    )
        external
        onlyRole(ADMIN_ROLE)
    {
        require(newMaxMetadataSize > 0, "Max metadata size must be greater than 0");
        require(newMaxDocumentsPerUser > 0, "Max documents per user must be greater than 0");
        
        maxMetadataSize = newMaxMetadataSize;
        maxDocumentsPerUser = newMaxDocumentsPerUser;
        minAnchoringFee = newMinAnchoringFee;
    }
    
    /**
     * @dev Pause contract (admin only)
     */
    function pause() external onlyRole(ADMIN_ROLE) {
        _pause();
    }
    
    /**
     * @dev Unpause contract (admin only)
     */
    function unpause() external onlyRole(ADMIN_ROLE) {
        _unpause();
    }
    
    /**
     * @dev Withdraw contract balance (admin only)
     */
    function withdrawBalance() external onlyRole(ADMIN_ROLE) {
        uint256 balance = address(this).balance;
        require(balance > 0, "No balance to withdraw");
        
        (bool success, ) = payable(msg.sender).call{value: balance}("");
        require(success, "Withdrawal failed");
    }
    
    /**
     * @dev Check if string is valid hex
     * @param str The string to check
     * @return True if valid hex string
     */
    function _isValidHexString(string memory str) internal pure returns (bool) {
        bytes memory b = bytes(str);
        for (uint256 i = 0; i < b.length; i++) {
            bytes1 char = b[i];
            if (!(char >= 0x30 && char <= 0x39) && // 0-9
                !(char >= 0x61 && char <= 0x66) && // a-f
                !(char >= 0x41 && char <= 0x46)) { // A-F
                return false;
            }
        }
        return true;
    }
    
    /**
     * @dev Override required by Solidity
     */
    function supportsInterface(bytes4 interfaceId)
        public
        view
        override(AccessControl)
        returns (bool)
    {
        return super.supportsInterface(interfaceId);
    }
    
    /**
     * @dev Receive function to accept ETH
     */
    receive() external payable {
        // Accept ETH payments
    }
}
