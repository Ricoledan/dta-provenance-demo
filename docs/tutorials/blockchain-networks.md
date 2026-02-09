# Deploying to Multiple Blockchain Networks

This guide explains how to deploy the DTA Provenance smart contracts to various blockchain networks including Polygon and Arbitrum mainnets and testnets.

## Overview

The blockchain implementation supports multiple networks:

- **Polygon (Mainnet)** - Low-cost, Ethereum-compatible L2
- **Polygon Amoy (Testnet)** - Free testnet for Polygon (replaces Mumbai)
- **Arbitrum One (Mainnet)** - High-performance Ethereum L2
- **Arbitrum Sepolia (Testnet)** - Free testnet for Arbitrum
- **Localhost** - Local development with Hardhat Network

## Prerequisites

### Required

- Node.js v16+ and npm
- A crypto wallet (MetaMask recommended)
- Private key for deployment account

### Optional (for verification)

- Polygonscan API key (free from [polygonscan.com](https://polygonscan.com/apis))
- Arbiscan API key (free from [arbiscan.io](https://arbiscan.io/apis))

## Setup

### 1. Install Dependencies

```bash
cd blockchain
npm install
```

This will install:
- `hardhat` - Development framework
- `@nomicfoundation/hardhat-verify` - Contract verification plugin
- `dotenv` - Environment variable management
- `ethers.js` - Ethereum library
- `@openzeppelin/contracts` - Secure contract libraries

### 2. Configure Environment

Copy the example environment file:

```bash
cp .env.example .env
```

Edit `.env` and add your configuration:

```bash
# Your private key (WITHOUT the 0x prefix)
PRIVATE_KEY=your_64_character_private_key_here

# Polygon Configuration
POLYGON_RPC_URL=https://polygon-rpc.com
POLYGON_AMOY_RPC_URL=https://rpc-amoy.polygon.technology
POLYGONSCAN_API_KEY=your_polygonscan_api_key

# Arbitrum Configuration
ARBITRUM_RPC_URL=https://arb1.arbitrum.io/rpc
ARBITRUM_SEPOLIA_RPC_URL=https://sepolia-rollup.arbitrum.io/rpc
ARBISCAN_API_KEY=your_arbiscan_api_key

# Optional: Enable gas reporting
REPORT_GAS=false
```

!!! warning "Security Warning"
    - **NEVER** commit your `.env` file to version control
    - **NEVER** share your private key
    - Use a separate wallet for testing with minimal funds
    - The `.env.example` file is safe to commit (no secrets)

### 3. Get Test Tokens

For testnet deployments, you need free test tokens:

#### Polygon Amoy Testnet

1. Get MATIC from [Polygon Faucet](https://faucet.polygon.technology/)
2. Select "Polygon Amoy" network
3. Enter your wallet address
4. You'll receive ~0.5 test MATIC

#### Arbitrum Sepolia Testnet

1. Get Sepolia ETH from [Sepolia Faucet](https://sepoliafaucet.com/)
2. Bridge to Arbitrum Sepolia via [Arbitrum Bridge](https://bridge.arbitrum.io/)
3. Or use [Chainlink Faucet](https://faucets.chain.link/) for Arbitrum Sepolia directly

### 4. Get RPC URLs (Optional but Recommended)

For better reliability, use dedicated RPC providers:

#### Alchemy (Recommended)

1. Sign up at [alchemy.com](https://www.alchemy.com/)
2. Create apps for each network you need
3. Copy the API keys and update `.env`:

```bash
POLYGON_RPC_URL=https://polygon-mainnet.g.alchemy.com/v2/YOUR_KEY
POLYGON_AMOY_RPC_URL=https://polygon-amoy.g.alchemy.com/v2/YOUR_KEY
ARBITRUM_RPC_URL=https://arb-mainnet.g.alchemy.com/v2/YOUR_KEY
ARBITRUM_SEPOLIA_RPC_URL=https://arb-sepolia.g.alchemy.com/v2/YOUR_KEY
```

#### Infura (Alternative)

1. Sign up at [infura.io](https://www.infura.io/)
2. Create projects for each network
3. Update `.env` with Infura URLs

## Deploying Contracts

### Local Development

Start a local Hardhat node:

```bash
npm run node
```

In another terminal, deploy:

```bash
npm run deploy:local
```

### Testnet Deployment

#### Polygon Amoy

```bash
npm run deploy:polygon-amoy
```

#### Arbitrum Sepolia

```bash
npm run deploy:arbitrum-sepolia
```

### Mainnet Deployment

!!! danger "Mainnet Warning"
    Mainnet deployments cost real money. Double-check:
    - Contract code is audited
    - You have enough tokens for gas
    - You're deploying to the correct network

#### Polygon Mainnet

```bash
npm run deploy:polygon
```

#### Arbitrum One

```bash
npm run deploy:arbitrum
```

## Contract Verification

Verification makes your contract source code publicly available on block explorers.

### Automatic Verification

Add `--verify` flag or set `VERIFY=true`:

```bash
# During deployment
npx hardhat run scripts/deploy-with-verify.js --network polygonAmoy --verify

# Or with environment variable
VERIFY=true npm run deploy:polygon-amoy
```

### Manual Verification

If automatic verification fails:

```bash
# Get contract address from deployments/{network}.json
npx hardhat verify --network polygonAmoy 0xYourContractAddress
```

### Check Verification Status

Visit the block explorer:

- **Polygon**: [polygonscan.com](https://polygonscan.com/)
- **Polygon Amoy**: [amoy.polygonscan.com](https://amoy.polygonscan.com/)
- **Arbitrum**: [arbiscan.io](https://arbiscan.io/)
- **Arbitrum Sepolia**: [sepolia.arbiscan.io](https://sepolia.arbiscan.io/)

## Deployment Tracking

Deployment information is saved in `blockchain/deployments/{network}.json`:

```json
{
  "address": "0x1234567890abcdef...",
  "network": "polygonAmoy",
  "chainId": 80002,
  "deployer": "0xYourWalletAddress...",
  "timestamp": "2024-02-09T12:34:56.789Z",
  "blockNumber": 12345678,
  "txHash": "0xTransactionHash...",
  "verified": true,
  "verifiedAt": "2024-02-09T12:35:30.123Z"
}
```

## Interacting with Deployed Contracts

Use the interact script with any network:

```bash
# Polygon Amoy
npm run interact:polygon-amoy

# Arbitrum Sepolia
npm run interact:arbitrum-sepolia

# Polygon Mainnet
npm run interact:polygon

# Arbitrum One
npm run interact:arbitrum
```

The script automatically:
1. Reads the deployed contract address from `deployments/{network}.json`
2. Connects to the existing contract
3. Runs example transactions (register provenance, verify, etc.)

## Network Comparison

| Network | Type | Chain ID | Avg Gas Price | Tx Cost* | Block Time | Finality |
|---------|------|----------|---------------|----------|------------|----------|
| **Polygon** | Mainnet L2 | 137 | ~30 gwei | ~$0.01 | 2s | 128 blocks (~4 min) |
| **Polygon Amoy** | Testnet | 80002 | Free | Free | 2s | ~30s |
| **Arbitrum One** | Mainnet L2 | 42161 | ~0.1 gwei | ~$0.01 | 0.25s | 1 block |
| **Arbitrum Sepolia** | Testnet | 421614 | Free | Free | 0.25s | ~30s |
| **Ethereum Mainnet** | Mainnet L1 | 1 | ~50 gwei | ~$5-50 | 12s | 15 blocks (~3 min) |

\* Approximate cost for registering a provenance record at current prices

## Cost Estimates

### Registration Transaction (~100,000 gas)

| Network | Gas Price | ETH Price | Cost per Tx | Cost per 1000 Tx |
|---------|-----------|-----------|-------------|------------------|
| Polygon | 30 gwei | $0.80 MATIC | $0.0024 | $2.40 |
| Arbitrum | 0.1 gwei | $2,000 ETH | $0.02 | $20 |
| Ethereum | 50 gwei | $2,000 ETH | $10 | $10,000 |

!!! tip "Cost Optimization"
    - **Use L2s**: Polygon and Arbitrum are 100-500x cheaper than Ethereum mainnet
    - **Batch operations**: Register multiple records in one transaction
    - **IPFS storage**: Store full metadata off-chain, only hash on-chain
    - **Monitor gas**: Deploy during low-traffic times

## Troubleshooting

### "Insufficient funds" Error

Make sure your wallet has:
- Enough tokens to pay for gas
- A small buffer (add 20% extra)

Check balance:
```bash
# Your wallet address is shown at deployment start
# Visit network block explorer and search for your address
```

### "Nonce too high" Error

Your local nonce is out of sync:

```bash
# Reset Hardhat's cached nonce
npx hardhat clean
rm -rf cache/ artifacts/
```

### "Invalid API Key" Error

Check your `.env` file:
- API keys are correct
- No extra spaces or quotes
- File is named `.env` (not `.env.example`)

### "Network not supported" Error

Ensure:
1. Network is configured in `hardhat.config.js`
2. You're using the correct network name
3. RPC URL is accessible (test with `curl`)

### RPC Connection Issues

Try these solutions:

1. **Use Alchemy/Infura**: Public RPCs can be unreliable
2. **Check rate limits**: Free tiers have request limits
3. **Wait and retry**: RPC might be temporarily down
4. **Switch RPC**: Try alternative public endpoints

## Best Practices

### Development Workflow

1. **Local First**: Test thoroughly on Hardhat Network
2. **Testnet Deploy**: Deploy to testnet (Amoy/Sepolia)
3. **Testnet Test**: Run full test suite on testnet
4. **Audit**: Get professional audit for mainnet
5. **Mainnet Deploy**: Deploy to production network

### Security Checklist

- [ ] Private key stored securely (never in code)
- [ ] Contract code audited by professionals
- [ ] Tests passing with 100% coverage
- [ ] Upgradability considered (if needed)
- [ ] Access controls properly configured
- [ ] Emergency pause mechanism tested
- [ ] Deployment wallet has minimal funds

### Gas Optimization

```solidity
// Good: Batch operations
function batchRegister(
    string[] calldata names,
    string[] calldata uris,
    bytes32[] calldata hashes
) external {
    for (uint i = 0; i < names.length; i++) {
        _registerProvenance(names[i], uris[i], hashes[i]);
    }
}

// Avoid: Individual transactions
// Each call costs base tx fee (~21,000 gas)
```

### Monitoring

After deployment, monitor:

1. **Transaction status**: Ensure confirmations
2. **Gas usage**: Track actual vs estimated costs
3. **Contract events**: Set up event listeners
4. **Error rates**: Monitor failed transactions

## Advanced Topics

### Multi-Sig Deployment

For production, use a multi-sig wallet:

1. Deploy Gnosis Safe on target network
2. Fund the Safe with deployment funds
3. Create deployment transaction in Safe
4. Collect required signatures
5. Execute deployment

### Upgradeable Contracts

Consider OpenZeppelin's upgradeable contracts:

```bash
npm install @openzeppelin/contracts-upgradeable
```

Use UUPS or Transparent Proxy pattern for upgradeability.

### Custom Networks

Add new networks in `hardhat.config.js`:

```javascript
networks: {
  customNetwork: {
    chainId: 12345,
    url: "https://rpc.custom.network",
    accounts: [process.env.PRIVATE_KEY]
  }
}
```

## Resources

### Documentation

- [Hardhat Docs](https://hardhat.org/docs)
- [Polygon Docs](https://docs.polygon.technology/)
- [Arbitrum Docs](https://docs.arbitrum.io/)
- [Ethers.js Docs](https://docs.ethers.org/)

### Tools

- [Hardhat VSCode Extension](https://marketplace.visualstudio.com/items?itemName=NomicFoundation.hardhat-solidity)
- [Remix IDE](https://remix.ethereum.org/) - Browser-based Solidity IDE
- [Tenderly](https://tenderly.co/) - Contract monitoring and debugging
- [OpenZeppelin Defender](https://www.openzeppelin.com/defender) - Operations platform

### Block Explorers

- [Polygonscan](https://polygonscan.com/) - Polygon mainnet
- [Amoy Polygonscan](https://amoy.polygonscan.com/) - Polygon Amoy testnet
- [Arbiscan](https://arbiscan.io/) - Arbitrum One
- [Arbiscan Sepolia](https://sepolia.arbiscan.io/) - Arbitrum Sepolia

### Faucets

- [Polygon Faucet](https://faucet.polygon.technology/)
- [Chainlink Faucet](https://faucets.chain.link/)
- [Alchemy Faucet](https://www.alchemy.com/faucets)

## Next Steps

- [API Reference](api-reference.md) - Detailed API documentation
- [Basic Usage](basic-usage.md) - How to use the provenance system
- [Examples](../examples/healthcare.md) - Real-world examples

## Support

- **GitHub Issues**: [Report bugs](https://github.com/Ricoledan/dta-provenance-demo/issues)
- **Discord**: Join our community for help
- **Documentation**: Full docs at [project site](https://ricoledan.github.io/dta-provenance-demo)
