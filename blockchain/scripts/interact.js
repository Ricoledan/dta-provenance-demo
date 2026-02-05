const hre = require("hardhat");
const crypto = require("crypto");

async function main() {
  // Get signers
  const [deployer] = await hre.ethers.getSigners();
  console.log("Interacting with contract using account:", deployer.address);

  // Deploy the contract (or use existing address)
  const ProvenanceRegistry = await hre.ethers.getContractFactory("ProvenanceRegistry");
  const registry = await ProvenanceRegistry.deploy();
  await registry.waitForDeployment();
  const address = await registry.getAddress();

  console.log("Contract deployed at:", address);

  // Example DTA metadata (simplified for demo)
  const dtaMetadata = {
    source: {
      datasetName: "Healthcare Imaging Dataset",
      datasetVersion: "1.0.0",
      providerName: "General Hospital ML Research"
    },
    provenance: {
      dataGenerationMethod: "DICOM medical imaging",
      dateDataGenerated: "2024-01-15T00:00:00Z",
      dataType: "Image",
      dataFormat: "DICOM/PNG"
    },
    use: {
      intendedUse: "ML model training for pneumonia detection",
      sensitiveData: true,
      sensitiveDataCategories: ["PHI", "Medical imaging"]
    }
  };

  // Convert metadata to JSON and compute hash
  const metadataJson = JSON.stringify(dtaMetadata);
  const metadataHash = "0x" + crypto.createHash("sha256").update(metadataJson).digest("hex");

  // Simulated IPFS URI (in production, upload to IPFS first)
  const metadataURI = "ipfs://QmExample123456789abcdefghijklmnopqrstuvwxyz";

  console.log("\n📝 Registering provenance record...");
  console.log("Dataset:", dtaMetadata.source.datasetName);
  console.log("Metadata URI:", metadataURI);
  console.log("Metadata Hash:", metadataHash);

  // Register provenance
  const tx = await registry.registerProvenance(
    dtaMetadata.source.datasetName,
    metadataURI,
    metadataHash
  );

  const receipt = await tx.wait();
  console.log("\n✅ Transaction successful!");
  console.log("Transaction hash:", receipt.hash);
  console.log("Block number:", receipt.blockNumber);
  console.log("Gas used:", receipt.gasUsed.toString());

  // Extract recordId from event
  const event = receipt.logs.find(log => {
    try {
      const parsed = registry.interface.parseLog(log);
      return parsed.name === "RecordCreated";
    } catch {
      return false;
    }
  });

  let recordId;
  if (event) {
    const parsed = registry.interface.parseLog(event);
    recordId = parsed.args.recordId;
    console.log("\n📋 Record ID:", recordId);
  }

  // Retrieve the provenance record
  if (recordId) {
    console.log("\n🔍 Retrieving provenance record...");
    const record = await registry.getProvenance(recordId);

    console.log("\nProvenance Record:");
    console.log("  Dataset Name:", record.datasetName);
    console.log("  Metadata URI:", record.metadataURI);
    console.log("  Metadata Hash:", record.metadataHash);
    console.log("  Provider:", record.provider);
    console.log("  Timestamp:", new Date(Number(record.timestamp) * 1000).toISOString());
    console.log("  Verified:", record.verified);

    // Validate metadata
    console.log("\n✓ Validating metadata...");
    const isValid = await registry.validateMetadata(recordId, metadataJson);
    console.log("Metadata validation:", isValid ? "✅ VALID" : "❌ INVALID");

    // Verify record (simulate verification by auditor)
    console.log("\n✓ Verifying record...");
    const verifyTx = await registry.verifyRecord(recordId);
    await verifyTx.wait();
    console.log("✅ Record verified!");

    // Check total records
    const totalRecords = await registry.totalRecords();
    console.log("\nTotal records in registry:", totalRecords.toString());

    // Get provider records
    const providerRecords = await registry.getProviderRecords(deployer.address);
    console.log("Records by this provider:", providerRecords.length);
  }

  console.log("\n🎉 Demo complete!");
  console.log("\nKey Takeaways:");
  console.log("  - Provenance metadata stored immutably on blockchain");
  console.log("  - Full metadata stored off-chain (IPFS) for cost efficiency");
  console.log("  - Cryptographic hash enables tamper detection");
  console.log("  - Smart contract provides trustless verification");
  console.log("\n⚠️  Remember: Gas costs scale with usage!");
  console.log("    This single registration cost:", receipt.gasUsed.toString(), "gas");
  console.log("    At 50 gwei and $2000 ETH, that's ~$",
    (Number(receipt.gasUsed) * 50 * 2000 / 1e18).toFixed(2));
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });
