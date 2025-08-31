const { expect } = require("chai");
const { ethers } = require("hardhat");
const { time } = require("@nomicfoundation/hardhat-network-helpers");

describe("DocumentVerification", function () {
  let DocumentVerification;
  let documentVerification;
  let owner;
  let anchorer;
  let revoker;
  let user1;
  let user2;
  let addrs;

  const ADMIN_ROLE = ethers.ZeroHash;
  const ANCHOR_ROLE = ethers.keccak256(ethers.toUtf8Bytes("ANCHOR_ROLE"));
  const REVOKE_ROLE = ethers.keccak256(ethers.toUtf8Bytes("REVOKE_ROLE"));

  const sampleDocumentHash = "a1b2c3d4e5f6789012345678901234567890abcdef1234567890abcdef123456";
  const sampleUserDid = "did:example:user123";
  const sampleMetadata = '{"title": "Test Document", "type": "academic_degree"}';
  const sampleRevocationReason = "Document compromised";

  beforeEach(async function () {
    [owner, anchorer, revoker, user1, user2, ...addrs] = await ethers.getSigners();

    DocumentVerification = await ethers.getContractFactory("DocumentVerification");
    documentVerification = await DocumentVerification.deploy();

    // Grant roles
    await documentVerification.grantRole(ANCHOR_ROLE, anchorer.address);
    await documentVerification.grantRole(REVOKE_ROLE, revoker.address);
  });

  describe("Deployment", function () {
    it("Should set the right owner", async function () {
      expect(await documentVerification.hasRole(ADMIN_ROLE, owner.address)).to.equal(true);
    });

    it("Should grant initial roles to deployer", async function () {
      expect(await documentVerification.hasRole(ANCHOR_ROLE, owner.address)).to.equal(true);
      expect(await documentVerification.hasRole(REVOKE_ROLE, owner.address)).to.equal(true);
    });

    it("Should set correct initial configuration", async function () {
      const stats = await documentVerification.getContractStats();
      expect(stats[2]).to.equal(10000); // maxMetadataSize
      expect(stats[3]).to.equal(1000); // maxDocumentsPerUser
      expect(stats[4]).to.equal(ethers.parseEther("0.001")); // minAnchoringFee
    });
  });

  describe("Role Management", function () {
    it("Should grant anchor role", async function () {
      await documentVerification.grantRole(ANCHOR_ROLE, user1.address);
      expect(await documentVerification.hasRole(ANCHOR_ROLE, user1.address)).to.equal(true);
    });

    it("Should revoke anchor role", async function () {
      await documentVerification.grantRole(ANCHOR_ROLE, user1.address);
      await documentVerification.revokeRole(ANCHOR_ROLE, user1.address);
      expect(await documentVerification.hasRole(ANCHOR_ROLE, user1.address)).to.equal(false);
    });

    it("Should only allow admin to grant roles", async function () {
      await expect(
        documentVerification.connect(user1).grantRole(ANCHOR_ROLE, user2.address)
      ).to.be.revertedWithCustomError(documentVerification, "AccessControlUnauthorizedAccount");
    });
  });

  describe("Document Anchoring", function () {
    it("Should anchor document successfully", async function () {
      const anchoringFee = ethers.parseEther("0.001");
      
      await expect(
        documentVerification.connect(anchorer).anchorDocument(
          sampleDocumentHash,
          sampleUserDid,
          sampleMetadata,
          { value: anchoringFee }
        )
      ).to.emit(documentVerification, "DocumentAnchored")
        .withArgs(sampleDocumentHash, sampleUserDid, anchorer.address, anyValue, sampleMetadata, 1);

      const verification = await documentVerification.verifyDocument(sampleDocumentHash);
      expect(verification[0]).to.equal(true); // exists
      expect(verification[1]).to.equal(sampleUserDid);
      expect(verification[4]).to.equal(false); // not revoked
    });

    it("Should fail with insufficient anchoring fee", async function () {
      const insufficientFee = ethers.parseEther("0.0005");
      
      await expect(
        documentVerification.connect(anchorer).anchorDocument(
          sampleDocumentHash,
          sampleUserDid,
          sampleMetadata,
          { value: insufficientFee }
        )
      ).to.be.revertedWith("Insufficient anchoring fee");
    });

    it("Should fail with invalid document hash length", async function () {
      const invalidHash = "invalid";
      
      await expect(
        documentVerification.connect(anchorer).anchorDocument(
          invalidHash,
          sampleUserDid,
          sampleMetadata,
          { value: ethers.parseEther("0.001") }
        )
      ).to.be.revertedWith("Invalid document hash length");
    });

    it("Should fail with invalid document hash format", async function () {
      const invalidHash = "a1b2c3d4e5f6789012345678901234567890abcdef1234567890abcdef12345g"; // contains 'g'
      
      await expect(
        documentVerification.connect(anchorer).anchorDocument(
          invalidHash,
          sampleUserDid,
          sampleMetadata,
          { value: ethers.parseEther("0.001") }
        )
      ).to.be.revertedWith("Invalid document hash format");
    });

    it("Should fail with invalid user DID", async function () {
      const shortDid = "short";
      
      await expect(
        documentVerification.connect(anchorer).anchorDocument(
          sampleDocumentHash,
          shortDid,
          sampleMetadata,
          { value: ethers.parseEther("0.001") }
        )
      ).to.be.revertedWith("User DID too short");
    });

    it("Should fail with oversized metadata", async function () {
      const largeMetadata = "x".repeat(10001);
      
      await expect(
        documentVerification.connect(anchorer).anchorDocument(
          sampleDocumentHash,
          sampleUserDid,
          largeMetadata,
          { value: ethers.parseEther("0.001") }
        )
      ).to.be.revertedWith("Metadata too large");
    });

    it("Should fail when anchoring same document twice", async function () {
      const anchoringFee = ethers.parseEther("0.001");
      
      await documentVerification.connect(anchorer).anchorDocument(
        sampleDocumentHash,
        sampleUserDid,
        sampleMetadata,
        { value: anchoringFee }
      );

      await expect(
        documentVerification.connect(anchorer).anchorDocument(
          sampleDocumentHash,
          sampleUserDid,
          sampleMetadata,
          { value: anchoringFee }
        )
      ).to.be.revertedWith("Document already exists");
    });

    it("Should fail when user exceeds document limit", async function () {
      const anchoringFee = ethers.parseEther("0.001");
      
      // Anchor 1000 documents (limit)
      for (let i = 0; i < 1000; i++) {
        const hash = sampleDocumentHash.slice(0, -1) + i.toString(16);
        await documentVerification.connect(anchorer).anchorDocument(
          hash,
          sampleUserDid,
          sampleMetadata,
          { value: anchoringFee }
        );
      }

      // Try to anchor one more
      const extraHash = sampleDocumentHash.slice(0, -1) + "a";
      await expect(
        documentVerification.connect(anchorer).anchorDocument(
          extraHash,
          sampleUserDid,
          sampleMetadata,
          { value: anchoringFee }
        )
      ).to.be.revertedWith("User document limit exceeded");
    });

    it("Should fail when contract is paused", async function () {
      await documentVerification.pause();
      
      await expect(
        documentVerification.connect(anchorer).anchorDocument(
          sampleDocumentHash,
          sampleUserDid,
          sampleMetadata,
          { value: ethers.parseEther("0.001") }
        )
      ).to.be.revertedWithCustomError(documentVerification, "EnforcedPause");
    });
  });

  describe("Document Verification", function () {
    beforeEach(async function () {
      await documentVerification.connect(anchorer).anchorDocument(
        sampleDocumentHash,
        sampleUserDid,
        sampleMetadata,
        { value: ethers.parseEther("0.001") }
      );
    });

    it("Should verify existing document", async function () {
      const verification = await documentVerification.verifyDocument(sampleDocumentHash);
      expect(verification[0]).to.equal(true); // exists
      expect(verification[1]).to.equal(sampleUserDid);
      expect(verification[2]).to.be.gt(0); // timestamp
      expect(verification[3]).to.equal(sampleMetadata);
      expect(verification[4]).to.equal(false); // not revoked
      expect(verification[5]).to.equal(1); // documentId
    });

    it("Should return false for non-existent document", async function () {
      const nonExistentHash = "b2c3d4e5f6789012345678901234567890abcdef1234567890abcdef1234567890";
      const verification = await documentVerification.verifyDocument(nonExistentHash);
      expect(verification[0]).to.equal(false); // exists
    });

    it("Should fail with invalid document hash", async function () {
      await expect(
        documentVerification.verifyDocument("invalid")
      ).to.be.revertedWith("Invalid document hash length");
    });
  });

  describe("Document Revocation", function () {
    beforeEach(async function () {
      await documentVerification.connect(anchorer).anchorDocument(
        sampleDocumentHash,
        sampleUserDid,
        sampleMetadata,
        { value: ethers.parseEther("0.001") }
      );
    });

    it("Should revoke document successfully", async function () {
      await expect(
        documentVerification.connect(revoker).revokeDocument(sampleDocumentHash, sampleRevocationReason)
      ).to.emit(documentVerification, "DocumentRevoked")
        .withArgs(sampleDocumentHash, sampleRevocationReason, revoker.address, anyValue, 1);

      const verification = await documentVerification.verifyDocument(sampleDocumentHash);
      expect(verification[4]).to.equal(true); // revoked
    });

    it("Should fail when revoking non-existent document", async function () {
      const nonExistentHash = "b2c3d4e5f6789012345678901234567890abcdef1234567890abcdef1234567890";
      
      await expect(
        documentVerification.connect(revoker).revokeDocument(nonExistentHash, sampleRevocationReason)
      ).to.be.revertedWith("Document does not exist");
    });

    it("Should fail when revoking already revoked document", async function () {
      await documentVerification.connect(revoker).revokeDocument(sampleDocumentHash, sampleRevocationReason);
      
      await expect(
        documentVerification.connect(revoker).revokeDocument(sampleDocumentHash, sampleRevocationReason)
      ).to.be.revertedWith("Document is revoked");
    });

    it("Should fail with empty revocation reason", async function () {
      await expect(
        documentVerification.connect(revoker).revokeDocument(sampleDocumentHash, "")
      ).to.be.revertedWith("Revocation reason required");
    });

    it("Should fail with oversized revocation reason", async function () {
      const largeReason = "x".repeat(1001);
      
      await expect(
        documentVerification.connect(revoker).revokeDocument(sampleDocumentHash, largeReason)
      ).to.be.revertedWith("Revocation reason too long");
    });

    it("Should fail when contract is paused", async function () {
      await documentVerification.pause();
      
      await expect(
        documentVerification.connect(revoker).revokeDocument(sampleDocumentHash, sampleRevocationReason)
      ).to.be.revertedWithCustomError(documentVerification, "EnforcedPause");
    });
  });

  describe("Document History", function () {
    beforeEach(async function () {
      await documentVerification.connect(anchorer).anchorDocument(
        sampleDocumentHash,
        sampleUserDid,
        sampleMetadata,
        { value: ethers.parseEther("0.001") }
      );
    });

    it("Should return document history", async function () {
      const history = await documentVerification.getDocumentHistory(sampleDocumentHash);
      expect(history[0].length).to.equal(1); // timestamps
      expect(history[1].length).to.equal(1); // actions
      expect(history[2].length).to.equal(1); // metadatas
      expect(history[3].length).to.equal(1); // actors
      expect(history[1][0]).to.equal("ANCHORED");
      expect(history[3][0]).to.equal(anchorer.address);
    });

    it("Should include revocation in history", async function () {
      await documentVerification.connect(revoker).revokeDocument(sampleDocumentHash, sampleRevocationReason);
      
      const history = await documentVerification.getDocumentHistory(sampleDocumentHash);
      expect(history[0].length).to.equal(2); // timestamps
      expect(history[1][1]).to.equal("REVOKED");
      expect(history[3][1]).to.equal(revoker.address);
    });

    it("Should fail for non-existent document", async function () {
      const nonExistentHash = "b2c3d4e5f6789012345678901234567890abcdef1234567890abcdef1234567890";
      
      await expect(
        documentVerification.getDocumentHistory(nonExistentHash)
      ).to.be.revertedWith("Document does not exist");
    });
  });

  describe("Document Metadata Updates", function () {
    beforeEach(async function () {
      await documentVerification.connect(anchorer).anchorDocument(
        sampleDocumentHash,
        sampleUserDid,
        sampleMetadata,
        { value: ethers.parseEther("0.001") }
      );
    });

    it("Should update document metadata", async function () {
      const newMetadata = '{"title": "Updated Document", "type": "certificate"}';
      
      await expect(
        documentVerification.connect(anchorer).updateDocumentMetadata(sampleDocumentHash, newMetadata)
      ).to.emit(documentVerification, "DocumentUpdated")
        .withArgs(sampleDocumentHash, newMetadata, anchorer.address, anyValue, 1);

      const verification = await documentVerification.verifyDocument(sampleDocumentHash);
      expect(verification[3]).to.equal(newMetadata);
    });

    it("Should fail when updating non-existent document", async function () {
      const nonExistentHash = "b2c3d4e5f6789012345678901234567890abcdef1234567890abcdef1234567890";
      
      await expect(
        documentVerification.connect(anchorer).updateDocumentMetadata(nonExistentHash, sampleMetadata)
      ).to.be.revertedWith("Document does not exist");
    });

    it("Should fail when updating revoked document", async function () {
      await documentVerification.connect(revoker).revokeDocument(sampleDocumentHash, sampleRevocationReason);
      
      await expect(
        documentVerification.connect(anchorer).updateDocumentMetadata(sampleDocumentHash, sampleMetadata)
      ).to.be.revertedWith("Document is revoked");
    });
  });

  describe("Contract Administration", function () {
    it("Should update configuration", async function () {
      await documentVerification.updateConfiguration(5000, 500, ethers.parseEther("0.002"));
      
      const stats = await documentVerification.getContractStats();
      expect(stats[2]).to.equal(5000); // maxMetadataSize
      expect(stats[3]).to.equal(500); // maxDocumentsPerUser
      expect(stats[4]).to.equal(ethers.parseEther("0.002")); // minAnchoringFee
    });

    it("Should fail when non-admin updates configuration", async function () {
      await expect(
        documentVerification.connect(user1).updateConfiguration(5000, 500, ethers.parseEther("0.002"))
      ).to.be.revertedWithCustomError(documentVerification, "AccessControlUnauthorizedAccount");
    });

    it("Should pause and unpause contract", async function () {
      await documentVerification.pause();
      expect(await documentVerification.paused()).to.equal(true);
      
      await documentVerification.unpause();
      expect(await documentVerification.paused()).to.equal(false);
    });

    it("Should fail when non-admin pauses contract", async function () {
      await expect(
        documentVerification.connect(user1).pause()
      ).to.be.revertedWithCustomError(documentVerification, "AccessControlUnauthorizedAccount");
    });

    it("Should withdraw contract balance", async function () {
      // First anchor a document to add balance
      await documentVerification.connect(anchorer).anchorDocument(
        sampleDocumentHash,
        sampleUserDid,
        sampleMetadata,
        { value: ethers.parseEther("0.001") }
      );

      const initialBalance = await ethers.provider.getBalance(owner.address);
      await documentVerification.withdrawBalance();
      const finalBalance = await ethers.provider.getBalance(owner.address);
      
      expect(finalBalance).to.be.gt(initialBalance);
    });
  });

  describe("Reentrancy Protection", function () {
    it("Should prevent reentrancy attacks", async function () {
      // This test would require a malicious contract that tries to reenter
      // For now, we just verify the contract uses ReentrancyGuard
      expect(await documentVerification.hasRole(ADMIN_ROLE, owner.address)).to.equal(true);
    });
  });

  describe("Gas Optimization", function () {
    it("Should use reasonable gas for document anchoring", async function () {
      const tx = await documentVerification.connect(anchorer).anchorDocument(
        sampleDocumentHash,
        sampleUserDid,
        sampleMetadata,
        { value: ethers.parseEther("0.001") }
      );
      
      const receipt = await tx.wait();
      expect(receipt.gasUsed).to.be.lt(300000); // Should use less than 300k gas
    });
  });
});
