# DTA Provenance Standards Demo

<div class="grid cards" markdown>

-   :material-rocket-launch:{ .lg .middle } __Quick Start__

    ---

    Get up and running in 60 seconds with Git-native provenance tracking

    [:octicons-arrow-right-24: Quick Start](quickstart.md)

-   :material-book-open-variant:{ .lg .middle } __Documentation__

    ---

    Comprehensive guides, API reference, and examples

    [:octicons-arrow-right-24: Read the Docs](DTA_STANDARDS.md)

-   :material-docker:{ .lg .middle } __Docker Support__

    ---

    One-command setup with Docker Compose

    [:octicons-arrow-right-24: Docker Setup](docker-setup.md)

-   :material-github:{ .lg .middle } __Open Source__

    ---

    MIT licensed - contributions welcome!

    [:octicons-arrow-right-24: GitHub](https://github.com/Ricoledan/dta-provenance-demo)

</div>

## What is This?

A comprehensive demonstration of **data provenance tracking** using the official [Data & Trust Alliance standards v1.0.0](https://www.dtaalliance.org/work/data-provenance-standards).

Shows you **two complete implementations**:

1. **Git-Native Approach** - Cryptographic audit logs using Git commits
2. **Blockchain Approach** - Smart contracts on Ethereum/Polygon

Perfect for understanding when to use blockchain vs. traditional solutions for data provenance in AI/ML pipelines, supply chains, and regulated industries.

## Why This Project?

- ✅ **Official Standards** - Implements DTA v1.0.0 specification
- ✅ **Production Quality** - Comprehensive tests, CLI tools, extensive documentation
- ✅ **Real-World Examples** - Healthcare, ML training, IoT sensors, financial data
- ✅ **Educational** - Learn what works (and what doesn't) in provenance tracking
- ✅ **Honest Comparison** - Shows why most projects DON'T need blockchain

## Features

### Git-Native Implementation

```python
from src.provenance import ProvenanceTracker, ProvenanceMetadata

# Create DTA-compliant metadata
metadata = ProvenanceMetadata(
    source={"datasetName": "Training Data", "providerName": "ML Team"},
    provenance={"dataGenerationMethod": "SQL export", ...},
    use={"intendedUse": "Model training", ...}
)

# Commit with provenance
tracker = ProvenanceTracker("./my-project")
commit_hash = tracker.commit_with_provenance(
    ["dataset.csv"],
    metadata,
    "Add training data v1.0"
)

# Verify integrity
is_valid, message = tracker.verify_integrity(commit_hash)
```

### Blockchain Implementation

```solidity
// Register provenance on-chain
function registerProvenance(
    string memory _datasetName,
    string memory _metadataURI,  // IPFS/Arweave
    bytes32 _metadataHash
) public returns (bytes32 recordId)
```

### CLI Tools

```bash
# Validate DTA standards
dta-provenance validate metadata.json

# Commit with provenance
dta-provenance commit dataset.csv \
  --metadata provenance.json \
  --message "Add training data"

# Verify integrity
dta-provenance verify HEAD

# Generate audit trail
dta-provenance trace dataset.csv
```

## Use Cases

### Healthcare Imaging
Complete HIPAA-compliant provenance for medical imaging datasets with de-identification documentation.

[View Example →](examples/healthcare.md)

### ML Training Data
Track provenance of training datasets from HuggingFace with license compliance verification.

[View Example →](examples/ml-training.md)

### IoT Sensor Streams
Real-time environmental monitoring with sensor calibration and quality indicators.

[View Example →](examples/iot-sensors.md)

### Financial Transactions
Anonymized payment data with multi-layer privacy protection and risk assessment.

[View Example →](examples/financial.md)

## When to Use What?

| Scenario | Recommendation | Why? |
|----------|----------------|------|
| Internal ML pipeline | **Git-Native** ✅ | Fast, free, integrates with existing workflows |
| Cross-company supply chain | **Blockchain** (maybe) ⚠️ | Only if trust is issue AND you can't use APIs |
| Single organization | **Git-Native** ✅ | No need for blockchain's trust properties |
| Regulatory audit trail | **Either** ✅ | Both provide cryptographic integrity |
| High-frequency updates | **Git-Native** ✅ | No gas fees, instant commits |
| Public transparency | **Blockchain** ✅ | Immutable, publicly verifiable |

[Full Comparison →](COMPARISON.md)

## Quick Links

<div class="grid" markdown>

- [**Installation Guide**](installation.md)
- [**DTA Standards Explained**](DTA_STANDARDS.md)
- [**Architecture Overview**](ARCHITECTURE.md)
- [**API Reference**](tutorials/api-reference.md)
- [**Contributing Guidelines**](CONTRIBUTING.md)
- [**FAQ**](faq.md)

</div>

## Installation

=== "Nix (Recommended)"

    ```bash
    git clone https://github.com/Ricoledan/dta-provenance-demo.git
    cd dta-provenance-demo
    nix develop
    ```

=== "Docker"

    ```bash
    docker-compose up -d
    # Access Jupyter: http://localhost:8888
    # Blockchain RPC: http://localhost:8545
    ```

=== "Manual"

    ```bash
    # Git-native
    cd git-native
    pip install -r requirements.txt
    pip install -e .

    # Blockchain
    cd blockchain
    npm install
    ```

## Community

- **GitHub**: [Report issues](https://github.com/Ricoledan/dta-provenance-demo/issues)
- **DTA Alliance**: [Official Website](https://www.dtaalliance.org/)
- **Documentation**: [Full Docs](https://ricoledan.github.io/dta-provenance-demo)

## License

MIT License - see [LICENSE](license.md) for details.

The DTA standards are used under their original license. See [Credits](credits.md) for full attribution.

---

<div class="center" markdown>

**Ready to get started?** → [Quick Start Guide](quickstart.md)

</div>
