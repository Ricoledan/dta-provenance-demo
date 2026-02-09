const hre = require("hardhat");
const fs = require("fs");
const path = require("path");

async function main() {
  const networkName = hre.network.name;
  console.log(`\n🚀 Deploying ProvenanceRegistry to ${networkName}...`);

  // Get the contract factory
  const ProvenanceRegistry = await hre.ethers.getContractFactory("ProvenanceRegistry");

  // Deploy the contract
  console.log("📝 Deploying contract...");
  const registry = await ProvenanceRegistry.deploy();
  await registry.waitForDeployment();

  const address = await registry.getAddress();
  console.log(`✅ ProvenanceRegistry deployed to: ${address}`);

  // Wait for confirmations on live networks (not needed for local networks)
  if (networkName !== "localhost" && networkName !== "hardhat") {
    console.log("\n⏳ Waiting for block confirmations...");
    const deploymentTx = registry.deploymentTransaction();
    if (deploymentTx) {
      const confirmations = 5;
      await deploymentTx.wait(confirmations);
      console.log(`✅ ${confirmations} block confirmations received`);
    }
  }

  // Save deployment address
  const deploymentsDir = path.join(__dirname, "..", "deployments");
  if (!fs.existsSync(deploymentsDir)) {
    fs.mkdirSync(deploymentsDir, { recursive: true });
  }

  const deploymentInfo = {
    address: address,
    network: networkName,
    chainId: hre.network.config.chainId,
    deployer: (await hre.ethers.getSigners())[0].address,
    timestamp: new Date().toISOString(),
    blockNumber: registry.deploymentTransaction() ?
      (await registry.deploymentTransaction().wait()).blockNumber : null,
    txHash: registry.deploymentTransaction() ?
      registry.deploymentTransaction().hash : null
  };

  const deploymentFile = path.join(deploymentsDir, `${networkName}.json`);
  fs.writeFileSync(deploymentFile, JSON.stringify(deploymentInfo, null, 2));
  console.log(`\n💾 Deployment info saved to: deployments/${networkName}.json`);

  // Display some initial state
  const totalRecords = await registry.totalRecords();
  console.log(`\n📊 Initial total records: ${totalRecords}`);

  // Verify contract on block explorer (if on supported network and API key is set)
  const shouldVerify = process.env.VERIFY === "true" || process.argv.includes("--verify");
  const supportedNetworks = ["polygon", "polygonAmoy", "arbitrum", "arbitrumSepolia"];

  if (shouldVerify && supportedNetworks.includes(networkName)) {
    console.log("\n🔍 Verifying contract on block explorer...");

    try {
      // Wait a bit more to ensure the contract is indexed
      console.log("⏳ Waiting for block explorer to index the contract...");
      await new Promise(resolve => setTimeout(resolve, 10000));

      await hre.run("verify:verify", {
        address: address,
        constructorArguments: [],
      });

      console.log("✅ Contract verified successfully!");

      // Add verification info to deployment file
      deploymentInfo.verified = true;
      deploymentInfo.verifiedAt = new Date().toISOString();
      fs.writeFileSync(deploymentFile, JSON.stringify(deploymentInfo, null, 2));

    } catch (error) {
      if (error.message.includes("Already Verified")) {
        console.log("✅ Contract already verified!");
        deploymentInfo.verified = true;
        fs.writeFileSync(deploymentFile, JSON.stringify(deploymentInfo, null, 2));
      } else {
        console.log("❌ Verification failed:", error.message);
        console.log("You can verify manually later with:");
        console.log(`npx hardhat verify --network ${networkName} ${address}`);
        deploymentInfo.verified = false;
        deploymentInfo.verificationError = error.message;
        fs.writeFileSync(deploymentFile, JSON.stringify(deploymentInfo, null, 2));
      }
    }
  } else if (!shouldVerify) {
    console.log("\n⚠️  Skipping contract verification (use --verify flag or VERIFY=true to verify)");
  } else {
    console.log(`\n⚠️  Contract verification not supported on ${networkName}`);
  }

  // Display explorer link
  const explorerUrls = {
    polygon: `https://polygonscan.com/address/${address}`,
    polygonAmoy: `https://amoy.polygonscan.com/address/${address}`,
    arbitrum: `https://arbiscan.io/address/${address}`,
    arbitrumSepolia: `https://sepolia.arbiscan.io/address/${address}`
  };

  if (explorerUrls[networkName]) {
    console.log(`\n🔗 View on explorer: ${explorerUrls[networkName]}`);
  }

  console.log("\n📋 Summary:");
  console.log(`  Network: ${networkName} (Chain ID: ${hre.network.config.chainId})`);
  console.log(`  Contract: ${address}`);
  console.log(`  Deployer: ${deploymentInfo.deployer}`);
  console.log(`  Block: ${deploymentInfo.blockNumber || "N/A"}`);
  console.log(`  Tx Hash: ${deploymentInfo.txHash || "N/A"}`);

  console.log("\n✅ Deployment complete!");
  console.log("\n📝 Next steps:");
  console.log(`  1. Interact: npx hardhat run scripts/interact.js --network ${networkName}`);
  console.log(`  2. Test: npx hardhat test --network ${networkName}`);
  if (explorerUrls[networkName]) {
    console.log(`  3. Verify (if not done): npx hardhat verify --network ${networkName} ${address}`);
  }

  return address;
}

// Execute deployment
if (require.main === module) {
  main()
    .then(() => process.exit(0))
    .catch((error) => {
      console.error("\n❌ Deployment failed:");
      console.error(error);
      process.exit(1);
    });
}

module.exports = { main };
