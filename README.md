<div align="center">

# DTA Provenance Standards Demo

**Production-quality implementations of Data & Trust Alliance provenance standards**

[![Tests](https://github.com/Ricoledan/dta-provenance-demo/actions/workflows/test.yml/badge.svg)](https://github.com/Ricoledan/dta-provenance-demo/actions/workflows/test.yml)
[![Documentation](https://github.com/Ricoledan/dta-provenance-demo/actions/workflows/docs.yml/badge.svg)](https://github.com/Ricoledan/dta-provenance-demo/actions/workflows/docs.yml)
[![Python](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Node](https://img.shields.io/badge/node-18%2B-brightgreen.svg)](https://nodejs.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![DTA Standards](https://img.shields.io/badge/DTA-v1.0.0-purple.svg)](https://github.com/Data-and-Trust-Alliance)

**[View Full Documentation](https://ricoledan.github.io/dta-provenance-demo)**

[Quick Start](#quick-start) • [Features](#features) • [Documentation](#documentation) • [Architecture](#architecture)

</div>

---

## Overview

A comprehensive demonstration of **data provenance tracking** using the official [Data & Trust Alliance standards v1.0.0](https://www.dtaalliance.org/work/data-provenance-standards). This project provides production-ready implementations across multiple platforms and tools, making it easy to understand when and how to implement provenance tracking in real-world applications.

### Two Complete Implementations

1. **Git-Native Approach** - Cryptographic audit logs using Git commits with trailers
2. **Blockchain Approach** - Immutable smart contracts on Ethereum-compatible networks

### Key Capabilities

- **Official DTA v1.0.0 Standards** - Full implementation of Data & Trust Alliance specifications
- **Production Quality** - 156 passing tests with 67% code coverage
- **Multiple Integration Points** - DVC, MLflow, SBOM, API server, VS Code extension
- **Real-World Examples** - Healthcare imaging, ML training, IoT sensors, financial transactions
- **Complete Documentation** - Comprehensive guides, API references, and tutorials
- **Honest Technical Comparison** - Detailed analysis of when blockchain is (and isn't) appropriate

> **Note:** The official DTA JSON Schema file is incomplete (missing closing brace). This project follows the DTA specification correctly, but automated schema validation against the official schema is not available. See [standards/official/README.md](standards/official/README.md) for details.

---

## Table of Contents

- [Quick Start](#quick-start)
- [Features](#features)
- [Architecture](#architecture)
- [Examples](#examples)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Running Tests](#running-tests)
- [Deployment](#deployment)
- [Contributing](#contributing)
- [License](#license)

---

## Quick Start

### Docker Compose (Recommended)

The fastest way to get started with all services:

```bash
# Clone the repository
git clone https://github.com/Ricoledan/dta-provenance-demo.git
cd dta-provenance-demo/git-native

# Start all services
docker-compose up -d

# Access services
# - API Server: http://localhost:8000
# - API Docs: http://localhost:8000/docs
# - Dashboard: http://localhost:3001
```

### Git-Native CLI

```bash
# Install Python package
cd git-native
pip install -e .

# Validate DTA compliance
dta-provenance validate ../standards/examples/healthcare-imaging.json

# Create test repository
mkdir my-project && cd my-project
git init

# Commit with provenance
echo "data" > dataset.csv
dta-provenance commit dataset.csv \
  --metadata ../standards/examples/healthcare-imaging.json \
  --message "Add training dataset"

# Verify integrity
dta-provenance verify HEAD

# Trace lineage
dta-provenance trace dataset.csv
```

### Blockchain Deployment

```bash
# Install dependencies
cd blockchain
npm install

# Start local Hardhat network
npx hardhat node

# Deploy contract (in another terminal)
npx hardhat run scripts/deploy.js --network localhost

# Run tests
npx hardhat test

# Deploy to Polygon testnet
cp .env.example .env  # Add your private key and RPC URL
npm run deploy:polygon-amoy
```

---

## Features

### Core Implementations

#### Git-Native Provenance Tracking

Python-based implementation using Git commits with structured trailers.

**Features:**
- DTA v1.0.0 compliant metadata storage in Git commit messages
- Cryptographic integrity verification using SHA-256 hashing
- Complete audit trail generation from Git history
- GPG/SSH signature support for commits
- CLI tool with rich terminal output
- Python library for programmatic access

**Commands:**
```bash
dta-provenance commit      # Create provenance-tracked commits
dta-provenance verify      # Verify cryptographic integrity
dta-provenance trace       # Generate audit trails
dta-provenance validate    # Check DTA compliance
dta-provenance show        # Display metadata from commits
```

#### Blockchain Provenance Registry

Solidity smart contract implementation for immutable provenance records.

**Features:**
- ERC-compliant smart contract on Ethereum/Polygon/Arbitrum
- On-chain metadata hash verification
- Provider-based access control
- Event emission for off-chain indexing
- Gas-optimized operations (~228K for registration)
- Multi-network deployment support

**Networks Supported:**
- Ethereum Mainnet
- Polygon (Mainnet & Amoy Testnet)
- Arbitrum One (Mainnet & Sepolia Testnet)
- Local Hardhat Network

### Advanced Integrations

#### 1. Pre-commit Hooks

Automated validation integrated with the pre-commit framework.

**Features:**
- Automatic metadata validation on file staging
- Commit message trailer verification
- DTA compliance checking before commits
- Configurable validation rules
- Works with existing pre-commit configurations

**Installation:**
```bash
pip install pre-commit
pre-commit install
pre-commit install --hook-type commit-msg
```

#### 2. DVC Integration

Bridge between DVC data versioning and DTA provenance metadata.

**Features:**
- Automatic DVC file tracking with provenance enrichment
- Metadata storage in `metadata.dvc` fields
- Hash verification across Git and DVC
- Support for remote storage backends (S3, GCS, Azure)
- CLI command for streamlined workflows

**Usage:**
```bash
pip install 'dta-provenance[dvc]'
dta-provenance dvc-track dataset.csv \
  --metadata provenance.json \
  --output enriched-metadata.json
```

#### 3. MLflow Integration

Bidirectional linking between Git commits and MLflow experiment runs.

**Features:**
- Git commits store `mlflow_run_id` in metadata
- MLflow runs store `git.commit_hash` in tags
- Complete DTA metadata logged as MLflow artifacts
- Query runs by dataset name
- Experiment tracking with provenance compliance

**Usage:**
```bash
pip install 'dta-provenance[mlflow]'
dta-provenance mlflow-log --metadata provenance.json
```

#### 4. SBOM Integration

Software Bill of Materials generation with CycloneDX format.

**Features:**
- Generate SBOMs from Python dependencies
- Link SBOM to provenance metadata
- Dependency analysis and license tracking
- Security scanning integration (Trivy, Grype)
- NTIA minimum elements compliance

**Usage:**
```bash
pip install 'dta-provenance[sbom]'
dta-provenance sbom-generate \
  --project-name my-ml-project \
  --metadata provenance.json
```

#### 5. REST API Server

FastAPI-based server for programmatic provenance queries.

**Features:**
- 5 RESTful endpoints for provenance operations
- OpenAPI/Swagger documentation
- CORS support for web applications
- Pydantic validation for type safety
- Docker deployment ready

**Endpoints:**
- `GET /health` - Health check
- `GET /provenance/{commit_hash}` - Retrieve metadata
- `GET /audit-trail/{file_path}` - Full audit history
- `POST /validate` - DTA compliance validation
- `GET /lineage/{file_path}` - Lineage graph data

**Usage:**
```bash
pip install 'dta-provenance[api]'
dta-provenance serve --host 0.0.0.0 --port 8000
```

#### 6. Frontend Dashboard

Interactive web application for provenance visualization and validation.

**Features:**
- Provenance metadata viewer with hierarchical display
- Audit trail timeline with CSV/JSON export
- Interactive D3.js lineage graph with force-directed layout
- Real-time DTA compliance validator
- Responsive design with Material theme
- Nginx-based production deployment

**Access:**
```bash
cd git-native
docker-compose up -d
# Open http://localhost:3001
```

#### 7. VS Code Extension

IDE integration for real-time validation and Git integration.

**Features:**
- Automatic validation on JSON file save
- Inline diagnostics for DTA compliance errors
- 5 code snippets for rapid development
- JSON Schema for IntelliSense support
- Git provenance history viewer
- Status bar with compliance scores
- Configurable validation strictness

**Installation:**
```bash
cd git-native/vscode-extension
npm install && npm run compile
vsce package
code --install-extension dta-provenance-validator-0.1.0.vsix
```

### Testing & Quality Assurance

- **Python Tests:** 121 tests covering all modules (pytest)
- **Blockchain Tests:** 35 tests for smart contracts (Hardhat)
- **Coverage:** 67% overall, 98%+ for integration modules
- **CI/CD:** GitHub Actions for automated testing
- **Linting:** Ruff, Black, MyPy for Python; ESLint for TypeScript
- **Documentation Tests:** MkDocs strict mode validation

---

## Architecture

### Git-Native Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Application Layer                        │
├─────────────────────────────────────────────────────────────────┤
│  CLI Tool  │  API Server  │  VS Code Extension  │  Dashboard   │
├─────────────────────────────────────────────────────────────────┤
│                      Core Library Layer                          │
├─────────────────────────────────────────────────────────────────┤
│  ProvenanceTracker  │  ProvenanceVerifier  │  Visualizer       │
├─────────────────────────────────────────────────────────────────┤
│                    Integration Layer                             │
├─────────────────────────────────────────────────────────────────┤
│  DVC Bridge  │  MLflow Bridge  │  SBOM Bridge                   │
├─────────────────────────────────────────────────────────────────┤
│                      Storage Layer                               │
├─────────────────────────────────────────────────────────────────┤
│  Git Repository  │  Filesystem  │  Remote Storage               │
└─────────────────────────────────────────────────────────────────┘
```

### Blockchain Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      Client Applications                         │
├─────────────────────────────────────────────────────────────────┤
│  Web3.js/Ethers.js  │  Frontend DApps  │  Scripts              │
├─────────────────────────────────────────────────────────────────┤
│                    Smart Contract Layer                          │
├─────────────────────────────────────────────────────────────────┤
│               ProvenanceRegistry.sol                             │
│  - registerProvenance()  - verifyRecord()                        │
│  - validateMetadata()    - updateMetadata()                      │
├─────────────────────────────────────────────────────────────────┤
│                    Blockchain Networks                           │
├─────────────────────────────────────────────────────────────────┤
│  Ethereum  │  Polygon  │  Arbitrum  │  Local Hardhat           │
└─────────────────────────────────────────────────────────────────┘
```

### Data Flow

**Git-Native Flow:**
1. User creates/modifies data files
2. DTA metadata prepared (JSON)
3. Files staged in Git
4. Provenance metadata embedded in commit message as trailers
5. SHA-256 hash computed for integrity
6. Commit signed (optional GPG/SSH)
7. Metadata retrievable from commit history

**Blockchain Flow:**
1. Data processed off-chain
2. Metadata hash computed (SHA-256)
3. Transaction submitted to smart contract
4. On-chain verification and storage
5. Event emitted for indexing
6. Metadata retrievable by record ID or provider

---

## Examples

### Healthcare Imaging Dataset

Tracking medical imaging data with HIPAA compliance requirements.

```json
{
  "source": {
    "datasetName": "Pneumonia X-ray Detection Dataset",
    "providerName": "University Hospital Medical Imaging",
    "datasetVersion": "2.1.0",
    "providerWebsite": "https://hospital.example.edu/imaging"
  },
  "provenance": {
    "dataGenerationMethod": "Chest X-ray DICOM to PNG conversion with radiologist annotations",
    "dateDataGenerated": "2023-11-15",
    "dataType": "Image",
    "dataFormat": "PNG with JSON annotations",
    "qualityIndicators": "Board-certified radiologist review, inter-rater agreement 0.94"
  },
  "use": {
    "intendedUse": "Training AI models for pneumonia detection in chest X-rays",
    "legalRightsToUse": "IRB-approved research protocol #2023-456",
    "sensitiveData": true,
    "sensitiveDataCategories": ["Health Information (HIPAA)"],
    "privacyMeasures": "De-identified per HIPAA Safe Harbor, face regions removed"
  }
}
```

**Full example:** [standards/examples/healthcare-imaging.json](standards/examples/healthcare-imaging.json)

### ML Training Pipeline

Tracking Hugging Face model training with experiment provenance.

```bash
# Track dataset with DVC
dta-provenance dvc-track train.csv --metadata train-provenance.json

# Log to MLflow during training
python train.py  # Internally uses MLflowProvenanceBridge

# Generate SBOM for dependencies
dta-provenance sbom-generate --project-name sentiment-model

# Create provenance-tracked commit
dta-provenance commit model.bin \
  --metadata enriched-provenance.json \
  --message "Fine-tuned BERT for sentiment analysis"
```

**Full example:** [standards/examples/ml-training-huggingface.json](standards/examples/ml-training-huggingface.json)

### IoT Sensor Stream

Real-time sensor data with temporal provenance tracking.

**Full example:** [standards/examples/iot-sensor-stream.json](standards/examples/iot-sensor-stream.json)

### Financial Transactions

Trading data with compliance and audit requirements.

**Full example:** [standards/examples/financial-transactions.json](standards/examples/financial-transactions.json)

---

## Project Structure

```
dta-provenance-demo/
├── .github/
│   └── workflows/              # CI/CD pipelines (test, docs, lint)
├── blockchain/
│   ├── contracts/              # Solidity smart contracts
│   │   └── ProvenanceRegistry.sol
│   ├── scripts/                # Deployment and interaction scripts
│   ├── test/                   # Hardhat test suite (35 tests)
│   ├── deployments/            # Network deployment records
│   ├── hardhat.config.js       # Multi-network configuration
│   └── .env.example            # Environment template
├── docs/
│   ├── tutorials/              # Step-by-step guides (10 tutorials)
│   │   ├── pre-commit-hooks.md
│   │   ├── dvc-integration.md
│   │   ├── mlflow-integration.md
│   │   ├── sbom-integration.md
│   │   ├── blockchain-networks.md
│   │   ├── api-server.md
│   │   ├── dashboard.md
│   │   └── vscode-extension.md
│   ├── examples/               # Real-world use cases
│   ├── ARCHITECTURE.md         # System design documentation
│   ├── DTA_STANDARDS.md        # Standards specification
│   └── COMPARISON.md           # Git vs Blockchain analysis
├── git-native/
│   ├── src/
│   │   ├── provenance.py       # Core tracking library
│   │   ├── verify.py           # Validation and verification
│   │   ├── cli.py              # Command-line interface (9 commands)
│   │   ├── api.py              # FastAPI REST server
│   │   ├── hooks.py            # Pre-commit integration
│   │   ├── visualize.py        # Graph generation
│   │   └── integrations/       # External tool bridges
│   │       ├── dvc_integration.py
│   │       ├── mlflow_integration.py
│   │       └── sbom_integration.py
│   ├── tests/                  # Comprehensive test suite (121 tests)
│   ├── dashboard/              # Vite + D3.js frontend
│   │   ├── src/
│   │   │   ├── components/     # UI components
│   │   │   │   ├── provenance-viewer.js
│   │   │   │   ├── audit-trail.js
│   │   │   │   ├── lineage-graph.js
│   │   │   │   └── validator.js
│   │   │   └── main.js
│   │   ├── Dockerfile          # Multi-stage build
│   │   └── nginx.conf          # Reverse proxy config
│   ├── vscode-extension/       # TypeScript IDE extension
│   │   ├── src/
│   │   │   ├── extension.ts    # Main activation
│   │   │   └── validator.ts    # Validation logic
│   │   ├── snippets/           # Code snippets (5 templates)
│   │   └── schemas/            # JSON Schema
│   ├── docker-compose.yml      # Multi-service orchestration
│   ├── pyproject.toml          # Python package configuration
│   └── requirements.txt        # Core dependencies
├── standards/
│   ├── official/               # DTA v1.0.0 schema and docs
│   └── examples/               # Reference implementations
│       ├── healthcare-imaging.json
│       ├── ml-training-huggingface.json
│       ├── iot-sensor-stream.json
│       └── financial-transactions.json
├── .pre-commit-config.yaml     # Automated validation hooks
├── mkdocs.yml                  # Documentation site configuration
├── docker-compose.yml          # Root-level service orchestration
└── README.md                   # This file
```

---

## Installation

### System Requirements

- **Python:** 3.9 or higher
- **Node.js:** 18 or higher
- **Git:** 2.30 or higher
- **Docker:** 20.10 or higher (optional, for containerized deployment)

### Python Package

```bash
cd git-native

# Core installation
pip install -e .

# With all integrations
pip install -e '.[all]'

# Specific integrations
pip install -e '.[dvc]'      # DVC support
pip install -e '.[mlflow]'   # MLflow support
pip install -e '.[sbom]'     # SBOM generation
pip install -e '.[api]'      # API server
```

### Blockchain

```bash
cd blockchain
npm install
```

### VS Code Extension

```bash
cd git-native/vscode-extension
npm install
npm run compile

# Package and install
npm install -g vsce
vsce package
code --install-extension dta-provenance-validator-0.1.0.vsix
```

### Dashboard

```bash
cd git-native/dashboard
npm install
npm run build

# Or use Docker
docker-compose up -d dashboard
```

---

## Running Tests

### Python Tests

```bash
cd git-native

# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/test_provenance.py

# Run specific test
pytest tests/test_provenance.py::test_metadata_hash_consistency
```

**Test Summary:**
- 121 total tests
- Core provenance: 20 tests
- Verification: 18 tests
- CLI: 19 tests
- API: 24 tests
- DVC integration: 13 tests
- MLflow integration: 16 tests
- SBOM integration: 12 tests
- Hooks: 14 tests

### Blockchain Tests

```bash
cd blockchain

# Run all tests
npx hardhat test

# Run with gas reporting
REPORT_GAS=true npx hardhat test

# Run specific test
npx hardhat test --grep "should register a new provenance record"
```

**Test Summary:**
- 35 total tests
- Deployment: 2 tests
- Registration: 7 tests
- Retrieval: 2 tests
- Verification: 4 tests
- Validation: 3 tests
- Updates: 5 tests
- Provider tracking: 3 tests
- Gas optimization: 2 tests

### Integration Tests

```bash
# API integration tests
cd git-native
pytest tests/test_api.py -v

# Full integration test
./scripts/integration-test.sh
```

---

## Deployment

### Docker Compose

Production-ready deployment with all services:

```bash
cd git-native
docker-compose up -d

# Services available:
# - API: http://localhost:8000
# - Dashboard: http://localhost:3001
# - Docs: http://localhost:8000/docs

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Blockchain Networks

#### Testnets (Free)

```bash
cd blockchain

# Configure environment
cp .env.example .env
# Add PRIVATE_KEY, RPC URLs, and API keys

# Deploy to Polygon Amoy testnet
npm run deploy:polygon-amoy

# Deploy to Arbitrum Sepolia testnet
npm run deploy:arbitrum-sepolia

# Interact with deployed contract
npm run interact:polygon-amoy
```

#### Mainnets (Costs Gas)

```bash
# Deploy to Polygon mainnet
npm run deploy:polygon

# Deploy to Arbitrum One mainnet
npm run deploy:arbitrum
```

**Cost Comparison:**
- Ethereum Mainnet: ~$50-200 per transaction
- Polygon Mainnet: ~$0.01 per transaction
- Arbitrum One: ~$0.01 per transaction
- Testnets: Free (faucet tokens)

### Production API

```bash
# Using systemd
sudo cp scripts/dta-api.service /etc/systemd/system/
sudo systemctl enable dta-api
sudo systemctl start dta-api

# Using Nginx reverse proxy
sudo cp scripts/nginx-api.conf /etc/nginx/sites-available/dta-api
sudo ln -s /etc/nginx/sites-available/dta-api /etc/nginx/sites-enabled/
sudo systemctl reload nginx
```

### Documentation Site

```bash
# Build locally
mkdocs build

# Serve locally
mkdocs serve

# Deploy to GitHub Pages
mkdocs gh-deploy
```

---

## Documentation

Comprehensive documentation is available at [https://ricoledan.github.io/dta-provenance-demo](https://ricoledan.github.io/dta-provenance-demo)

### Key Documentation Pages

**Getting Started:**
- [Quick Start Guide](https://ricoledan.github.io/dta-provenance-demo/quickstart/)
- [Installation Instructions](https://ricoledan.github.io/dta-provenance-demo/installation/)
- [Docker Setup](https://ricoledan.github.io/dta-provenance-demo/docker-setup/)
- [Nix Setup](https://ricoledan.github.io/dta-provenance-demo/nix-setup/)

**Technical Documentation:**
- [Architecture Overview](https://ricoledan.github.io/dta-provenance-demo/ARCHITECTURE/)
- [DTA Standards Specification](https://ricoledan.github.io/dta-provenance-demo/DTA_STANDARDS/)
- [Git vs Blockchain Comparison](https://ricoledan.github.io/dta-provenance-demo/COMPARISON/)

**Tutorials:**
- [Basic Usage](https://ricoledan.github.io/dta-provenance-demo/tutorials/basic-usage/)
- [Pre-commit Hooks](https://ricoledan.github.io/dta-provenance-demo/tutorials/pre-commit-hooks/)
- [DVC Integration](https://ricoledan.github.io/dta-provenance-demo/tutorials/dvc-integration/)
- [MLflow Integration](https://ricoledan.github.io/dta-provenance-demo/tutorials/mlflow-integration/)
- [SBOM Integration](https://ricoledan.github.io/dta-provenance-demo/tutorials/sbom-integration/)
- [Blockchain Networks](https://ricoledan.github.io/dta-provenance-demo/tutorials/blockchain-networks/)
- [API Server](https://ricoledan.github.io/dta-provenance-demo/tutorials/api-server/)
- [Frontend Dashboard](https://ricoledan.github.io/dta-provenance-demo/tutorials/dashboard/)
- [VS Code Extension](https://ricoledan.github.io/dta-provenance-demo/tutorials/vscode-extension/)

**Examples:**
- [Healthcare Imaging](https://ricoledan.github.io/dta-provenance-demo/examples/healthcare/)
- [ML Training](https://ricoledan.github.io/dta-provenance-demo/examples/ml-training/)
- [IoT Sensors](https://ricoledan.github.io/dta-provenance-demo/examples/iot-sensors/)
- [Financial Data](https://ricoledan.github.io/dta-provenance-demo/examples/financial/)

---

## When to Use Git vs Blockchain

### Use Git-Native When:

- You have a centralized authority or trust anchor
- Cost and performance are critical
- You need rich querying capabilities
- Your team is already familiar with Git
- Compliance requires audit trails but not decentralization
- Data privacy is a concern (on-chain data is public)

**Advantages:**
- Zero operational cost
- Instant operations (no mining/confirmation time)
- Flexible querying with Git tools
- Proven cryptographic security
- Works offline
- Private by default

### Use Blockchain When:

- Multiple untrusting parties need to verify provenance
- No single entity can be trusted as authority
- Immutability must be guaranteed by consensus
- Public verifiability is required
- Smart contract automation is valuable

**Advantages:**
- Truly decentralized trust model
- Censorship resistant
- Public verifiability
- Programmable via smart contracts
- Network effect and interoperability

### Cost Comparison

| Operation | Git-Native | Ethereum | Polygon | Arbitrum |
|-----------|------------|----------|---------|----------|
| Registration | Free | $50-200 | $0.01 | $0.01 |
| Verification | Free | $20-100 | $0.005 | $0.005 |
| Query | Free | $5-20 | $0.002 | $0.002 |
| Storage | Local disk | On-chain (expensive) | On-chain | On-chain |

**Conclusion:** For most ML and data science applications, Git-native provenance provides sufficient guarantees at zero cost. Blockchain adds value primarily when decentralization and public verifiability are strict requirements.

---

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Development Setup

```bash
# Clone the repository
git clone https://github.com/Ricoledan/dta-provenance-demo.git
cd dta-provenance-demo

# Install development dependencies
cd git-native
pip install -e '.[dev]'

# Run linters
ruff check src/
black --check src/
mypy src/

# Run tests
pytest

# Build documentation
cd ..
mkdocs serve
```

### Pull Request Process

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Make your changes with tests
4. Ensure all tests pass (`pytest` and `npx hardhat test`)
5. Update documentation as needed
6. Commit your changes (`git commit -m 'Add feature'`)
7. Push to the branch (`git push origin feature/your-feature`)
8. Open a Pull Request

### Code Standards

- Python: Follow PEP 8, use type hints, maintain >80% test coverage
- TypeScript: Follow ESLint rules, use strict mode
- Solidity: Follow Solidity style guide, optimize for gas
- Documentation: Use clear, concise language with code examples
- Commit messages: Use conventional commits format

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## Credits

### Standards

- [Data & Trust Alliance](https://www.dtaalliance.org/) - DTA Provenance Standards v1.0.0

### Technologies

- [GitPython](https://github.com/gitpython-developers/GitPython) - Git repository interaction
- [FastAPI](https://fastapi.tiangolo.com/) - Modern Python web framework
- [Hardhat](https://hardhat.org/) - Ethereum development environment
- [D3.js](https://d3js.org/) - Data visualization library
- [MkDocs Material](https://squidfunk.github.io/mkdocs-material/) - Documentation theme

### Contributors

See [CONTRIBUTING.md](CONTRIBUTING.md) for the list of contributors.

---

## Support

- **Documentation:** https://ricoledan.github.io/dta-provenance-demo
- **Issues:** https://github.com/Ricoledan/dta-provenance-demo/issues
- **Discussions:** https://github.com/Ricoledan/dta-provenance-demo/discussions

---

<div align="center">

**Built with production quality. Tested with real-world scenarios. Documented for clarity.**

[Get Started](https://ricoledan.github.io/dta-provenance-demo/quickstart/) • [View Examples](https://ricoledan.github.io/dta-provenance-demo/examples/healthcare/) • [Read the Docs](https://ricoledan.github.io/dta-provenance-demo/)

</div>
