<div align="center">

# DTA Provenance Standards Demo

**Production-quality implementations of Data & Trust Alliance provenance standards**

[![Tests](https://github.com/Ricoledan/dta-provenance-demo/actions/workflows/test.yml/badge.svg)](https://github.com/Ricoledan/dta-provenance-demo/actions/workflows/test.yml)
[![Documentation](https://github.com/Ricoledan/dta-provenance-demo/actions/workflows/docs.yml/badge.svg)](https://github.com/Ricoledan/dta-provenance-demo/actions/workflows/docs.yml)
[![Python](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Node](https://img.shields.io/badge/node-18%2B-brightgreen.svg)](https://nodejs.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![DTA Standards](https://img.shields.io/badge/DTA-v1.0.0-purple.svg)](https://github.com/Data-and-Trust-Alliance)

📚 **[View Full Documentation](https://ricoledan.github.io/dta-provenance-demo)**

[Quick Start](#quick-start) • [Documentation](#documentation) • [Examples](#examples) • [Comparison](#comparison)

</div>

---

## What is This?

A comprehensive demonstration of **data provenance tracking** using the official [Data & Trust Alliance standards v1.0.0](https://www.dtaalliance.org/work/data-provenance-standards). Shows you **two complete implementations**:

1. **Git-Native Approach** - Cryptographic audit logs using Git commits
2. **Blockchain Approach** - Smart contracts on Ethereum/Polygon

Perfect for understanding when to use blockchain vs. traditional solutions for data provenance in AI/ML pipelines, supply chains, and regulated industries.

## Why This Project?

- ✅ **Official Standards** - Implements DTA v1.0.0 specification from Data & Trust Alliance
- ✅ **Production Quality** - Comprehensive test coverage, CLI tools, and extensive documentation
- ✅ **Real-World Examples** - Healthcare, ML training data, IoT sensors, financial data
- ✅ **Educational** - Learn what works (and what doesn't) in provenance tracking
- ✅ **Honest Comparison** - Shows why most projects DON'T need blockchain

> **Note:** The official DTA JSON Schema file is incomplete (missing closing brace). This project follows the DTA specification correctly, but automated schema validation against the official schema is not available. See [standards/official/README.md](standards/official/README.md) for details.

---

## Table of Contents

- [Quick Start](#quick-start)
  - [Git-Native Implementation](#git-native-implementation-60-seconds)
  - [Blockchain Implementation](#blockchain-implementation-local)
- [Examples](#examples)
- [Comparison: When to Use What?](#comparison-when-to-use-what)
- [Documentation](#documentation)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Running Tests](#running-tests)
- [Contributing](#contributing)
- [Credits](#credits)
- [License](#license)

---

## Quick Start

### Option 1: Nix (Recommended for Reproducible Environment)

```bash
# Clone the repository
git clone https://github.com/yourusername/dta-provenance-demo.git
cd dta-provenance-demo

# Enter the development environment (installs everything)
nix develop

# That's it! Everything is ready:
dta-provenance --help
```

**See [NIX_SETUP.md](NIX_SETUP.md) for detailed Nix instructions and non-Nix alternatives.**

### Option 2: Manual Setup (Git-Native - 60 seconds)

```bash
# Clone the repository
git clone https://github.com/yourusername/dta-provenance-demo.git
cd dta-provenance-demo

# Install the Git-native package
cd git-native
pip install -r requirements.txt
pip install -e .

# Try the CLI tool
dta-provenance --help

# Use an example provenance file
dta-provenance validate ../standards/examples/healthcare-imaging.json

# Initialize a test repository
mkdir my-test-project && cd my-test-project
git init

# Create a sample dataset
echo "patient_id,diagnosis,confidence\n1,pneumonia,0.95\n2,normal,0.99" > dataset.csv

# Commit with provenance
dta-provenance commit dataset.csv \
  --metadata ../standards/examples/healthcare-imaging.json \
  --message "Add pneumonia detection training data"

# Verify integrity
dta-provenance verify HEAD

# Trace lineage
dta-provenance trace dataset.csv
```

### Blockchain Implementation (Local)

```bash
# Install dependencies
cd blockchain
npm install

# Start local blockchain (Terminal 1)
npx hardhat node

# Deploy contract (Terminal 2)
npx hardhat run scripts/deploy.js --network localhost

# Run tests
npx hardhat test

# View gas costs
npx hardhat test --gas-report
```

---

## Examples

### Healthcare Imaging Dataset

See [`standards/examples/healthcare-imaging.json`](standards/examples/healthcare-imaging.json) for a complete DTA-compliant provenance record for medical imaging data with HIPAA de-identification.

**Key Features:**
- Full de-identification per HIPAA Safe Harbor
- Inter-rater agreement metrics (κ=0.89)
- Equipment specifications and protocols
- IRB approval documentation
- Quality indicators and processing steps

### ML Training Data (HuggingFace)

See [`standards/examples/ml-training-huggingface.json`](standards/examples/ml-training-huggingface.json) for public dataset provenance from code repositories.

**Key Features:**
- License compliance verification (MIT, Apache 2.0, BSD)
- PII detection and removal
- Deduplication methodology (MinHash LSH)
- GitHub API scraping documentation
- Fair use justification for ML training

### IoT Sensor Stream

See [`standards/examples/iot-sensor-stream.json`](standards/examples/iot-sensor-stream.json) for real-time environmental monitoring data.

**Key Features:**
- Sensor specifications and calibration
- Location privacy protection (100m grid aggregation)
- Data quality indicators (97.3% uptime)
- Processing pipeline documentation
- Retention policies (90 days raw, indefinite aggregated)

### Financial Transactions

See [`standards/examples/financial-transactions.json`](standards/examples/financial-transactions.json) for anonymized payment data with advanced privacy techniques.

**Key Features:**
- Multi-layer anonymization (PCA, k-anonymity, differential privacy)
- GDPR Article 6(1)(f) legal basis
- Re-identification risk assessment (< 0.001%)
- PCI-DSS compliance documentation
- Class imbalance handling (0.172% fraud rate)

---

## Comparison: When to Use What?

| Scenario | Recommendation | Why? |
|----------|----------------|------|
| Internal ML pipeline | **Git-Native** ✅ | Fast, free, integrates with existing workflows |
| Cross-company supply chain | **Blockchain** (maybe) ⚠️ | Only if trust is issue AND you can't use APIs |
| Single organization | **Git-Native** ✅ | No need for blockchain's trust properties |
| Needs automated settlement | **Blockchain** ✅ | Smart contracts enable trustless execution |
| Regulatory audit trail | **Either** ✅ | Both provide cryptographic integrity |
| High-frequency updates | **Git-Native** ✅ | No gas fees, instant commits |
| Public transparency | **Blockchain** ✅ | Immutable, publicly verifiable |
| Privacy-sensitive data | **Git-Native** ✅ | Better access control, no public ledger |

### Detailed Feature Comparison

| Feature | Git-Native | Blockchain |
|---------|-----------|------------|
| **Setup Complexity** | Minimal (Git + Python) | Moderate (Node.js, Hardhat, wallet) |
| **Cost** | Free | Gas fees (local: free, mainnet: $$) |
| **Speed** | Instant | Block confirmation time (~10s to 10m) |
| **Immutability** | Cryptographic commits | Smart contract storage |
| **Multi-party Trust** | Requires central Git host | Trustless verification |
| **Scalability** | Unlimited | Limited by block size/gas limits |
| **Privacy** | Repo access control | Public blockchain (pseudo-anonymous) |
| **Query Performance** | Git log (very fast) | Blockchain indexing required |
| **Best Use Case** | Internal ML pipelines | Cross-org supply chain (rare) |

**Read Full Comparison:** See [`docs/COMPARISON.md`](docs/COMPARISON.md) for detailed analysis with code examples.

---

## Documentation

### 📚 Comprehensive Guides

- **[Nix Setup](NIX_SETUP.md)** - Reproducible development environment with Nix
- **[Architecture](docs/ARCHITECTURE.md)** - System architecture diagrams with Mermaid
- **[DTA Standards Deep Dive](docs/DTA_STANDARDS.md)** - All 22 fields explained with examples
- **[Comparison Guide](docs/COMPARISON.md)** - Git vs. Blockchain technical analysis
- **[Contributing](docs/CONTRIBUTING.md)** - How to contribute

### 🎓 Learning Resources

The DTA standards define **22 fields** organized into 3 categories:

#### 1. SOURCE (8 fields) - Where the data came from
- `datasetName` (required) - Human-readable identifier
- `datasetVersion` - Semantic versioning
- `datasetURI` - Direct link or identifier (S3, IPFS, DOI)
- `providerName` (required) - Organization/individual
- `providerWebsite` - Contact and documentation
- `geographicSourceOfData` - Geographic origin
- `dataOriginCountry` - ISO country codes
- `locationDataGenerated` - Physical collection location

#### 2. PROVENANCE (6 fields) - How the data was created
- `dataGenerationMethod` (required) - Collection methodology
- `dateDataGenerated` (required) - ISO 8601 timestamp
- `dataType` (required) - Image, Text, Tabular, etc.
- `dataFormat` (required) - Technical format and schema
- `dataSubjectivity` - Objective, Subjective, or Mixed
- `qualityIndicators` - Metrics and quality measures

#### 3. USE (8 fields) - How the data should be used
- `intendedUse` (required) - Purpose and applications
- `restrictions` - Legal and practical limitations
- `legalRightsToUse` (required) - Legal basis (consent, legitimate interest, etc.)
- `privacyMeasures` (required if sensitive) - De-identification techniques
- `sensitiveData` (required) - Boolean flag
- `sensitiveDataCategories` (required if sensitive) - PII, PHI, financial, etc.
- `dataProcessingLocation` - Geographic processing locations

**Read More:** See the [DTA Standards Guide](docs/DTA_STANDARDS.md) for comprehensive documentation with regulatory context.

---

## Project Structure

```
dta-provenance-demo/
├── standards/                              # DTA standards and examples
│   ├── official/
│   │   └── ATTRIBUTION.md                 # Credit to Data & Trust Alliance
│   └── examples/
│       ├── healthcare-imaging.json        # Medical imaging dataset
│       ├── ml-training-huggingface.json   # HuggingFace dataset
│       ├── iot-sensor-stream.json         # IoT sensor data
│       └── financial-transactions.json    # Financial data
├── git-native/                            # Git-based implementation
│   ├── src/
│   │   ├── provenance.py                  # Core library
│   │   ├── verify.py                      # Verification & validation
│   │   ├── cli.py                         # Command-line interface
│   │   └── visualize.py                   # Graph visualization
│   ├── tests/
│   │   └── test_provenance.py             # Comprehensive tests
│   ├── requirements.txt
│   └── pyproject.toml                     # Modern Python packaging
├── blockchain/                            # Blockchain implementation
│   ├── contracts/
│   │   └── ProvenanceRegistry.sol         # Main smart contract
│   ├── scripts/
│   │   └── deploy.js                      # Deployment script
│   ├── test/
│   │   └── ProvenanceRegistry.test.js     # Unit tests
│   ├── hardhat.config.js
│   └── package.json
├── docs/                                  # Documentation
│   ├── DTA_STANDARDS.md                   # Deep dive into 22 fields
│   ├── COMPARISON.md                      # Git vs. Blockchain comparison
│   ├── CASE_STUDIES.md                    # Real-world examples
│   └── ARCHITECTURE.md                    # Technical architecture
└── README.md                              # This file
```

---

## Installation

### Git-Native Implementation

**Requirements:**
- Python 3.9 or higher
- Git 2.30 or higher

**Install:**
```bash
cd git-native
pip install -r requirements.txt
pip install -e .
```

**Verify Installation:**
```bash
dta-provenance --version
dta-provenance --help
```

### Blockchain Implementation

**Requirements:**
- Node.js 18 or higher
- npm 9 or higher

**Install:**
```bash
cd blockchain
npm install
```

**Verify Installation:**
```bash
npx hardhat --version
npx hardhat test
```

---

## Running Tests

### Git-Native Tests

```bash
cd git-native

# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/test_provenance.py -v

# Run specific test
pytest tests/test_provenance.py::test_commit_with_provenance -v
```

**Expected Coverage:** 80%+ for production quality

### Blockchain Tests

```bash
cd blockchain

# Run all tests
npx hardhat test

# Run with gas reporting
npx hardhat test --gas-report

# Run specific test file
npx hardhat test test/ProvenanceRegistry.test.js
```

---

## Usage Examples

### Python Library Usage

```python
from pathlib import Path
from src.provenance import ProvenanceTracker, ProvenanceMetadata

# Initialize tracker
tracker = ProvenanceTracker(Path("./my-project"))

# Create metadata
metadata = ProvenanceMetadata(
    source={
        "datasetName": "Customer Churn Dataset",
        "datasetVersion": "1.0.0",
        "providerName": "Marketing Analytics Team"
    },
    provenance={
        "dataGenerationMethod": "SQL export from production database",
        "dateDataGenerated": "2024-01-15T00:00:00Z",
        "dataType": "Tabular",
        "dataFormat": "CSV with 12 columns: customer_id, age, tenure, ..."
    },
    use={
        "intendedUse": "Training ML model for churn prediction",
        "legalRightsToUse": "Internal business data",
        "sensitiveData": True,
        "sensitiveDataCategories": ["PII", "Customer behavior data"],
        "privacyMeasures": "Customer IDs pseudonymized, names removed"
    }
)

# Commit with provenance
commit_hash = tracker.commit_with_provenance(
    file_paths=[Path("data/customer_churn.csv")],
    metadata=metadata,
    message="Add training data for churn model v1",
    sign=False
)

print(f"Committed: {commit_hash}")

# Verify integrity
is_valid, message = tracker.verify_integrity(commit_hash)
print(f"Verification: {message}")

# Generate audit trail
audit_trail = tracker.generate_audit_trail(
    Path("data/customer_churn.csv"),
    max_commits=10
)
```

### CLI Tool Usage

```bash
# Validate provenance file
dta-provenance validate my-metadata.json

# Commit with provenance
dta-provenance commit dataset.csv \
  --metadata provenance.json \
  --message "Add training data" \
  --sign  # Optional: GPG sign the commit

# Verify a commit
dta-provenance verify HEAD
dta-provenance verify abc123def

# Show provenance metadata
dta-provenance show HEAD --output metadata.json

# Trace data lineage
dta-provenance trace dataset.csv --format text
dta-provenance trace dataset.csv --format json > lineage.json

# Get help
dta-provenance --help
dta-provenance commit --help
```

---

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](docs/CONTRIBUTING.md) for guidelines.

**Quick Start for Contributors:**

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes
4. Run tests: `pytest` (Python) or `npx hardhat test` (Solidity)
5. Commit your changes: `git commit -m 'Add amazing feature'`
6. Push to the branch: `git push origin feature/amazing-feature`
7. Open a Pull Request

---

## Credits

### Data & Trust Alliance

This project uses the **Data Provenance Standards v1.0.0** developed by the [Data & Trust Alliance](https://www.dtaalliance.org/).

**Standards Development Team:**
The standards were co-developed by 19 organizations including:
- AARP
- IBM
- Mastercard
- Deloitte
- Nike
- Pfizer
- Walmart

Developed through 150+ sessions with 50+ organizations testing and validating.

**See Full Attribution:** [standards/official/ATTRIBUTION.md](standards/official/ATTRIBUTION.md)

### Official Resources

- **Schema:** https://github.com/Data-and-Trust-Alliance/json-metadata
- **Specification:** https://github.com/Data-and-Trust-Alliance/DPS
- **Website:** https://www.dtaalliance.org/

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

**Note:** The DTA standards schema is used under its original license. See [standards/official/ATTRIBUTION.md](standards/official/ATTRIBUTION.md) for details.

---

## Learn More

### Why Data Provenance Matters

Data provenance is increasingly critical due to:

1. **Regulatory Requirements**
   - EU AI Act requires training data documentation
   - GDPR mandates data processing records
   - FDA requires provenance for AI/ML medical devices

2. **Trust & Transparency**
   - Users want to know where AI training data comes from
   - Researchers need reproducible data pipelines
   - Auditors require complete audit trails

3. **Risk Management**
   - Identify data biases early
   - Detect privacy issues before deployment
   - Track data quality issues to source

### When NOT to Use Blockchain

Most projects don't need blockchain for provenance. Use Git-native approach if:

- ✅ Single organization controls the data
- ✅ Trust exists between parties (APIs work fine)
- ✅ Privacy is a concern (blockchain is public)
- ✅ High-frequency updates needed
- ✅ Cost matters (gas fees add up)

### When Blockchain Makes Sense

Consider blockchain only if ALL of these apply:

- ⚠️ Multiple untrusting parties need shared records
- ⚠️ No central authority can be trusted
- ⚠️ Automated settlement/execution needed (smart contracts)
- ⚠️ Public transparency is valuable
- ⚠️ Update frequency is low enough

**Famous Failures:**
- IBM Food Trust (2023) - Shut down, moved to SaaS
- TradeLens (2022) - Maersk/IBM blockchain closed
- Winding Tree (2023) - Travel blockchain bankrupt

**Why They Failed:** Blockchain didn't solve the trust problem—it just made coordination harder. APIs and databases work fine when you have business relationships.

---

## Roadmap

### ✅ Completed

- [x] **GitHub Pages documentation site** - Live at [ricoledan.github.io/dta-provenance-demo](https://ricoledan.github.io/dta-provenance-demo)
- [x] **Interactive Jupyter notebook demo** - Complete tutorial with real-world examples
- [x] **GitHub Action for automated provenance checks** - Full CI/CD with tests, linting, and deployment
- [x] **Docker containers for easy deployment** - Docker Compose setup with Git-native, Blockchain, and Jupyter
- [x] **Comprehensive test coverage** - 59 tests across Python and Solidity with automated CI
- [x] **Documentation linting and preview tools** - Local preview with `mkdocs serve` and automated link checking

### 🚧 Future Enhancements

- [ ] MLflow integration example
- [ ] VS Code extension for provenance validation
- [ ] Additional blockchain networks (Polygon, Arbitrum)
- [ ] Frontend dashboard for visualization
- [ ] Integration with DVC (Data Version Control)
- [ ] SBOM (Software Bill of Materials) integration
- [ ] Pre-commit hooks for automated validation
- [ ] API server for provenance queries

---

## FAQ

**Q: Do I need blockchain for data provenance?**
A: Almost certainly not. The Git-native approach works for 95% of use cases. Only consider blockchain if you have multiple untrusting parties and no central authority.

**Q: Is this production-ready?**
A: The Git-native implementation is production-quality and can be used in real projects. The blockchain implementation is for educational purposes and would need additional security hardening for production.

**Q: What about IPFS/Arweave for decentralized storage?**
A: Those are great for immutable file storage and can complement either approach. The blockchain implementation references IPFS URIs for full metadata storage.

**Q: Can I use this with my existing ML pipeline?**
A: Yes! The Python library integrates easily with MLflow, DVC, and other ML tools. See the examples directory.

**Q: How does this compare to DVC (Data Version Control)?**
A: DVC focuses on versioning large files efficiently. This project focuses on metadata and provenance tracking. They're complementary—you can use both together.

**Q: What about the EU AI Act?**
A: The DTA standards align well with EU AI Act requirements for high-risk AI systems. See [docs/DTA_STANDARDS.md](docs/DTA_STANDARDS.md) for regulatory mapping.

---
