const hre = require("hardhat");

async function main() {
  console.log("Deploying ProvenanceRegistry contract...");

  // Get the contract factory
  const ProvenanceRegistry = await hre.ethers.getContractFactory("ProvenanceRegistry");

  // Deploy the contract
  const registry = await ProvenanceRegistry.deploy();

  await registry.waitForDeployment();

  const address = await registry.getAddress();

  console.log(`✅ ProvenanceRegistry deployed to: ${address}`);
  console.log("\nYou can now interact with the contract using this address.");
  console.log("\nExample usage:");
  console.log("  npx hardhat run scripts/interact.js --network localhost");

  // Display some initial state
  const totalRecords = await registry.totalRecords();
  console.log(`\nInitial total records: ${totalRecords}`);

  return address;
}

// Execute deployment
main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });

module.exports = { main };
