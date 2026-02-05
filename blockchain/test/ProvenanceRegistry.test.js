const { expect } = require("chai");
const { ethers } = require("hardhat");

describe("ProvenanceRegistry", function () {
  let provenanceRegistry;
  let owner;
  let provider1;
  let provider2;
  let verifier;

  // Test data
  const datasetName = "Healthcare Imaging Dataset";
  const metadataURI = "ipfs://QmTest123456789";
  const metadataHash = ethers.keccak256(ethers.toUtf8Bytes('{"test": "metadata"}'));
  const metadataJSON = '{"test": "metadata"}';

  beforeEach(async function () {
    // Get signers
    [owner, provider1, provider2, verifier] = await ethers.getSigners();

    // Deploy contract
    const ProvenanceRegistry = await ethers.getContractFactory("ProvenanceRegistry");
    provenanceRegistry = await ProvenanceRegistry.deploy();
    await provenanceRegistry.waitForDeployment();
  });

  describe("Deployment", function () {
    it("Should deploy with zero total records", async function () {
      expect(await provenanceRegistry.totalRecords()).to.equal(0);
    });

    it("Should have correct contract address", async function () {
      expect(await provenanceRegistry.getAddress()).to.be.properAddress;
    });
  });

  describe("Register Provenance", function () {
    it("Should register a new provenance record", async function () {
      const tx = await provenanceRegistry.connect(provider1).registerProvenance(
        datasetName,
        metadataURI,
        metadataHash
      );

      const receipt = await tx.wait();
      expect(receipt.status).to.equal(1);

      // Check total records increased
      expect(await provenanceRegistry.totalRecords()).to.equal(1);
    });

    it("Should emit RecordCreated event", async function () {
      const tx = await provenanceRegistry.connect(provider1).registerProvenance(
        datasetName,
        metadataURI,
        metadataHash
      );

      const receipt = await tx.wait();
      const event = receipt.logs.find(
        (log) => log.fragment && log.fragment.name === "RecordCreated"
      );

      expect(event).to.not.be.undefined;
      expect(event.args[1]).to.equal(provider1.address);
      expect(event.args[2]).to.equal(datasetName);
      expect(event.args[3]).to.equal(metadataHash);
    });

    it("Should return a valid record ID", async function () {
      const tx = await provenanceRegistry.connect(provider1).registerProvenance(
        datasetName,
        metadataURI,
        metadataHash
      );

      const receipt = await tx.wait();
      const event = receipt.logs.find(
        (log) => log.fragment && log.fragment.name === "RecordCreated"
      );

      expect(event).to.not.be.undefined;
      const recordId = event.args[0];
      expect(recordId).to.be.properHex(64); // bytes32 is 64 hex chars + 0x prefix = 66 total
    });

    it("Should store record with correct data", async function () {
      const tx = await provenanceRegistry.connect(provider1).registerProvenance(
        datasetName,
        metadataURI,
        metadataHash
      );

      const receipt = await tx.wait();
      const event = receipt.logs.find(
        (log) => log.fragment && log.fragment.name === "RecordCreated"
      );
      const recordId = event.args[0];

      const record = await provenanceRegistry.getProvenance(recordId);

      expect(record.datasetName).to.equal(datasetName);
      expect(record.metadataURI).to.equal(metadataURI);
      expect(record.metadataHash).to.equal(metadataHash);
      expect(record.provider).to.equal(provider1.address);
      expect(record.verified).to.equal(false);
      expect(record.exists).to.equal(true);
    });

    it("Should add record to provider's records", async function () {
      await provenanceRegistry.connect(provider1).registerProvenance(
        datasetName,
        metadataURI,
        metadataHash
      );

      const providerRecords = await provenanceRegistry.getProviderRecords(provider1.address);
      expect(providerRecords.length).to.equal(1);

      const count = await provenanceRegistry.getProviderRecordCount(provider1.address);
      expect(count).to.equal(1);
    });

    it("Should fail with empty dataset name", async function () {
      await expect(
        provenanceRegistry.connect(provider1).registerProvenance("", metadataURI, metadataHash)
      ).to.be.revertedWith("Dataset name cannot be empty");
    });

    it("Should fail with empty metadata URI", async function () {
      await expect(
        provenanceRegistry.connect(provider1).registerProvenance(datasetName, "", metadataHash)
      ).to.be.revertedWith("Metadata URI cannot be empty");
    });

    it("Should fail with zero metadata hash", async function () {
      await expect(
        provenanceRegistry
          .connect(provider1)
          .registerProvenance(datasetName, metadataURI, ethers.ZeroHash)
      ).to.be.revertedWith("Metadata hash cannot be zero");
    });

    it("Should allow multiple records from same provider", async function () {
      await provenanceRegistry.connect(provider1).registerProvenance(
        datasetName,
        metadataURI,
        metadataHash
      );

      const datasetName2 = "ML Training Dataset";
      const metadataURI2 = "ipfs://QmTest987654321";
      const metadataHash2 = ethers.keccak256(ethers.toUtf8Bytes('{"test": "metadata2"}'));

      await provenanceRegistry.connect(provider1).registerProvenance(
        datasetName2,
        metadataURI2,
        metadataHash2
      );

      expect(await provenanceRegistry.totalRecords()).to.equal(2);
      expect(await provenanceRegistry.getProviderRecordCount(provider1.address)).to.equal(2);
    });

    it("Should allow different providers to register", async function () {
      await provenanceRegistry.connect(provider1).registerProvenance(
        datasetName,
        metadataURI,
        metadataHash
      );

      await provenanceRegistry.connect(provider2).registerProvenance(
        "IoT Sensor Data",
        "ipfs://QmIoT123",
        ethers.keccak256(ethers.toUtf8Bytes('{"sensor": "data"}'))
      );

      expect(await provenanceRegistry.totalRecords()).to.equal(2);
      expect(await provenanceRegistry.getProviderRecordCount(provider1.address)).to.equal(1);
      expect(await provenanceRegistry.getProviderRecordCount(provider2.address)).to.equal(1);
    });
  });

  describe("Get Provenance", function () {
    let recordId;

    beforeEach(async function () {
      const tx = await provenanceRegistry.connect(provider1).registerProvenance(
        datasetName,
        metadataURI,
        metadataHash
      );

      const receipt = await tx.wait();
      const event = receipt.logs.find(
        (log) => log.fragment && log.fragment.name === "RecordCreated"
      );
      recordId = event.args[0];
    });

    it("Should retrieve existing record", async function () {
      const record = await provenanceRegistry.getProvenance(recordId);

      expect(record.datasetName).to.equal(datasetName);
      expect(record.metadataURI).to.equal(metadataURI);
      expect(record.provider).to.equal(provider1.address);
    });

    it("Should fail for non-existent record", async function () {
      const fakeRecordId = ethers.keccak256(ethers.toUtf8Bytes("fake"));
      await expect(provenanceRegistry.getProvenance(fakeRecordId)).to.be.revertedWith(
        "Record does not exist"
      );
    });
  });

  describe("Verify Record", function () {
    let recordId;

    beforeEach(async function () {
      const tx = await provenanceRegistry.connect(provider1).registerProvenance(
        datasetName,
        metadataURI,
        metadataHash
      );

      const receipt = await tx.wait();
      const event = receipt.logs.find(
        (log) => log.fragment && log.fragment.name === "RecordCreated"
      );
      recordId = event.args[0];
    });

    it("Should verify a record", async function () {
      await provenanceRegistry.connect(verifier).verifyRecord(recordId);

      const record = await provenanceRegistry.getProvenance(recordId);
      expect(record.verified).to.equal(true);
    });

    it("Should emit RecordVerified event", async function () {
      const tx = await provenanceRegistry.connect(verifier).verifyRecord(recordId);
      const receipt = await tx.wait();
      const event = receipt.logs.find(
        (log) => log.fragment && log.fragment.name === "RecordVerified"
      );

      expect(event).to.not.be.undefined;
      expect(event.args[0]).to.equal(recordId);
      expect(event.args[1]).to.equal(verifier.address);
    });

    it("Should fail for non-existent record", async function () {
      const fakeRecordId = ethers.keccak256(ethers.toUtf8Bytes("fake"));
      await expect(provenanceRegistry.connect(verifier).verifyRecord(fakeRecordId)).to.be.revertedWith(
        "Record does not exist"
      );
    });

    it("Should fail if already verified", async function () {
      await provenanceRegistry.connect(verifier).verifyRecord(recordId);

      await expect(provenanceRegistry.connect(verifier).verifyRecord(recordId)).to.be.revertedWith(
        "Record already verified"
      );
    });

    it("Should allow any address to verify", async function () {
      // This demonstrates that the contract doesn't have access control for verification
      // In production, you'd want to restrict this to trusted verifiers
      await provenanceRegistry.connect(provider2).verifyRecord(recordId);

      const record = await provenanceRegistry.getProvenance(recordId);
      expect(record.verified).to.equal(true);
    });
  });

  describe("Validate Metadata", function () {
    let recordId;

    beforeEach(async function () {
      // Use SHA-256 hash for the metadata
      const sha256Hash = ethers.sha256(ethers.toUtf8Bytes(metadataJSON));

      const tx = await provenanceRegistry.connect(provider1).registerProvenance(
        datasetName,
        metadataURI,
        sha256Hash
      );

      const receipt = await tx.wait();
      const event = receipt.logs.find(
        (log) => log.fragment && log.fragment.name === "RecordCreated"
      );
      recordId = event.args[0];
    });

    it("Should validate correct metadata", async function () {
      const isValid = await provenanceRegistry.validateMetadata(recordId, metadataJSON);
      expect(isValid).to.equal(true);
    });

    it("Should reject incorrect metadata", async function () {
      const wrongMetadata = '{"test": "wrong"}';
      const isValid = await provenanceRegistry.validateMetadata(recordId, wrongMetadata);
      expect(isValid).to.equal(false);
    });

    it("Should fail for non-existent record", async function () {
      const fakeRecordId = ethers.keccak256(ethers.toUtf8Bytes("fake"));
      await expect(
        provenanceRegistry.validateMetadata(fakeRecordId, metadataJSON)
      ).to.be.revertedWith("Record does not exist");
    });
  });

  describe("Update Metadata", function () {
    let recordId;
    const newMetadataURI = "ipfs://QmUpdated123456";
    const newMetadataHash = ethers.keccak256(ethers.toUtf8Bytes('{"updated": "metadata"}'));

    beforeEach(async function () {
      const tx = await provenanceRegistry.connect(provider1).registerProvenance(
        datasetName,
        metadataURI,
        metadataHash
      );

      const receipt = await tx.wait();
      const event = receipt.logs.find(
        (log) => log.fragment && log.fragment.name === "RecordCreated"
      );
      recordId = event.args[0];
    });

    it("Should update metadata by provider", async function () {
      await provenanceRegistry
        .connect(provider1)
        .updateMetadata(recordId, newMetadataURI, newMetadataHash);

      const record = await provenanceRegistry.getProvenance(recordId);
      expect(record.metadataURI).to.equal(newMetadataURI);
      expect(record.metadataHash).to.equal(newMetadataHash);
    });

    it("Should emit MetadataUpdated event", async function () {
      const tx = await provenanceRegistry
        .connect(provider1)
        .updateMetadata(recordId, newMetadataURI, newMetadataHash);

      const receipt = await tx.wait();
      const event = receipt.logs.find(
        (log) => log.fragment && log.fragment.name === "MetadataUpdated"
      );

      expect(event).to.not.be.undefined;
      expect(event.args[0]).to.equal(recordId);
      expect(event.args[1]).to.equal(newMetadataURI);
      expect(event.args[2]).to.equal(newMetadataHash);
    });

    it("Should fail if not the provider", async function () {
      await expect(
        provenanceRegistry
          .connect(provider2)
          .updateMetadata(recordId, newMetadataURI, newMetadataHash)
      ).to.be.revertedWith("Only provider can update record");
    });

    it("Should fail for non-existent record", async function () {
      const fakeRecordId = ethers.keccak256(ethers.toUtf8Bytes("fake"));
      await expect(
        provenanceRegistry
          .connect(provider1)
          .updateMetadata(fakeRecordId, newMetadataURI, newMetadataHash)
      ).to.be.revertedWith("Record does not exist");
    });

    it("Should fail with empty metadata URI", async function () {
      await expect(
        provenanceRegistry.connect(provider1).updateMetadata(recordId, "", newMetadataHash)
      ).to.be.revertedWith("Metadata URI cannot be empty");
    });

    it("Should fail with zero metadata hash", async function () {
      await expect(
        provenanceRegistry.connect(provider1).updateMetadata(recordId, newMetadataURI, ethers.ZeroHash)
      ).to.be.revertedWith("Metadata hash cannot be zero");
    });
  });

  describe("Provider Records", function () {
    it("Should return empty array for provider with no records", async function () {
      const records = await provenanceRegistry.getProviderRecords(provider1.address);
      expect(records.length).to.equal(0);
    });

    it("Should return zero count for provider with no records", async function () {
      const count = await provenanceRegistry.getProviderRecordCount(provider1.address);
      expect(count).to.equal(0);
    });

    it("Should track multiple records for a provider", async function () {
      // Register 3 records
      await provenanceRegistry.connect(provider1).registerProvenance(
        "Dataset 1",
        "ipfs://1",
        ethers.keccak256(ethers.toUtf8Bytes('{"id": "1"}'))
      );

      await provenanceRegistry.connect(provider1).registerProvenance(
        "Dataset 2",
        "ipfs://2",
        ethers.keccak256(ethers.toUtf8Bytes('{"id": "2"}'))
      );

      await provenanceRegistry.connect(provider1).registerProvenance(
        "Dataset 3",
        "ipfs://3",
        ethers.keccak256(ethers.toUtf8Bytes('{"id": "3"}'))
      );

      const records = await provenanceRegistry.getProviderRecords(provider1.address);
      expect(records.length).to.equal(3);

      const count = await provenanceRegistry.getProviderRecordCount(provider1.address);
      expect(count).to.equal(3);
    });
  });

  describe("Record Exists", function () {
    it("Should return false for non-existent record", async function () {
      const fakeRecordId = ethers.keccak256(ethers.toUtf8Bytes("fake"));
      const exists = await provenanceRegistry.recordExists(fakeRecordId);
      expect(exists).to.equal(false);
    });

    it("Should return true for existing record", async function () {
      const tx = await provenanceRegistry.connect(provider1).registerProvenance(
        datasetName,
        metadataURI,
        metadataHash
      );

      const receipt = await tx.wait();
      const event = receipt.logs.find(
        (log) => log.fragment && log.fragment.name === "RecordCreated"
      );
      const recordId = event.args[0];

      const exists = await provenanceRegistry.recordExists(recordId);
      expect(exists).to.equal(true);
    });
  });

  describe("Gas Optimization", function () {
    it("Should have reasonable gas costs for registration", async function () {
      const tx = await provenanceRegistry.connect(provider1).registerProvenance(
        datasetName,
        metadataURI,
        metadataHash
      );

      const receipt = await tx.wait();
      const gasUsed = receipt.gasUsed;

      // Gas should be less than 250k for a registration
      expect(gasUsed).to.be.lessThan(250000);
      console.log(`      Gas used for registration: ${gasUsed}`);
    });

    it("Should have reasonable gas costs for verification", async function () {
      const tx1 = await provenanceRegistry.connect(provider1).registerProvenance(
        datasetName,
        metadataURI,
        metadataHash
      );

      const receipt1 = await tx1.wait();
      const event = receipt1.logs.find(
        (log) => log.fragment && log.fragment.name === "RecordCreated"
      );
      const recordId = event.args[0];

      const tx2 = await provenanceRegistry.connect(verifier).verifyRecord(recordId);
      const receipt2 = await tx2.wait();
      const gasUsed = receipt2.gasUsed;

      // Gas should be less than 50k for verification
      expect(gasUsed).to.be.lessThan(50000);
      console.log(`      Gas used for verification: ${gasUsed}`);
    });
  });
});
