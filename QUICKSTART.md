# Quick Start Guide

Get up and running with DTA Provenance Standards in 5 minutes.

---

## Prerequisites

- Python 3.9 or higher
- Git 2.30 or higher
- Node.js 18+ (only for blockchain implementation)

Check your versions:
```bash
python --version  # Should be 3.9+
git --version     # Should be 2.30+
node --version    # Should be 18+ (optional)
```

---

## Option 1: Git-Native (Recommended - 5 minutes)

### Step 1: Install the Package

```bash
cd git-native
pip install -r requirements.txt
pip install -e .
```

### Step 2: Verify Installation

```bash
dta-provenance --version
dta-provenance --help
```

You should see:
```
Usage: dta-provenance [OPTIONS] COMMAND [ARGS]...

  DTA-compliant provenance tracking for data and AI.
...
```

### Step 3: Validate an Example

```bash
dta-provenance validate ../standards/examples/healthcare-imaging.json
```

You should see:
```
Validating ../standards/examples/healthcare-imaging.json...
DTA Standards Validation: ✅ VALID
Compliance Score: 100.0%
```

> **Note:** The validation uses our custom validator since the official DTA JSON Schema file contains invalid JSON. Our validator checks all required fields and provides compliance scoring. See `standards/official/README.md` for details.

### Step 4: Try It in a Real Repository

```bash
# Create a test project
mkdir ~/my-test-project
cd ~/my-test-project
git init
git config user.name "Your Name"
git config user.email "your.email@example.com"

# Create a sample dataset
echo "id,value\n1,100\n2,200" > dataset.csv

# Create provenance metadata
cat > provenance.json <<EOF
{
  "source": {
    "datasetName": "Test Dataset",
    "datasetVersion": "1.0.0",
    "providerName": "Test Provider"
  },
  "provenance": {
    "dataGenerationMethod": "Manual creation for testing",
    "dateDataGenerated": "2024-01-15T00:00:00Z",
    "dataType": "Tabular",
    "dataFormat": "CSV"
  },
  "use": {
    "intendedUse": "Testing DTA provenance",
    "legalRightsToUse": "Public domain",
    "sensitiveData": false,
    "sensitiveDataCategories": []
  }
}
EOF

# Commit with provenance
dta-provenance commit dataset.csv \
  --metadata provenance.json \
  --message "Add test dataset"

# Verify integrity
dta-provenance verify HEAD

# Show provenance
dta-provenance show HEAD
```

**Success!** You've created your first provenance-tracked commit.

---

## Option 2: Blockchain (Advanced - 15 minutes)

### Step 1: Install Dependencies

```bash
cd blockchain
npm install
```

### Step 2: Compile Smart Contract

```bash
npx hardhat compile
```

You should see:
```
Compiled 1 Solidity file successfully
```

### Step 3: Start Local Blockchain (Terminal 1)

```bash
npx hardhat node
```

Keep this running. You should see:
```
Started HTTP and WebSocket JSON-RPC server at http://127.0.0.1:8545/
```

### Step 4: Deploy Contract (Terminal 2)

```bash
npx hardhat run scripts/deploy.js --network localhost
```

You should see:
```
✅ ProvenanceRegistry deployed to: 0x5FbDB2315678afecb367f032d93F642f64180aa3
```

### Step 5: Interact with Contract

```bash
npx hardhat run scripts/interact.js --network localhost
```

You should see a complete demo with:
- Provenance record registration
- Metadata validation
- Gas cost analysis

**Success!** You've deployed and interacted with the provenance smart contract.

---

## What's Next?

### Learn the Standards

Read the comprehensive guide to all 22 DTA fields:
```bash
open docs/DTA_STANDARDS.md
```

Or view online: [DTA Standards Guide](docs/DTA_STANDARDS.md)

### Compare Approaches

See the detailed Git vs. Blockchain comparison:
```bash
open docs/COMPARISON.md
```

Or view online: [Comparison Guide](docs/COMPARISON.md)

### Try Real Examples

Explore the example datasets:
- Healthcare: `standards/examples/healthcare-imaging.json`
- ML Training: `standards/examples/ml-training-huggingface.json`
- IoT Sensors: `standards/examples/iot-sensor-stream.json`
- Financial: `standards/examples/financial-transactions.json`

```bash
dta-provenance validate standards/examples/healthcare-imaging.json
dta-provenance validate standards/examples/ml-training-huggingface.json
```

### Integrate with Your Project

```python
# In your Python project
from pathlib import Path
from src.provenance import ProvenanceTracker, ProvenanceMetadata

# Initialize tracker
tracker = ProvenanceTracker(Path("."))

# Create metadata from your data
metadata = ProvenanceMetadata(
    source={"datasetName": "My Dataset", "providerName": "My Team"},
    provenance={
        "dataGenerationMethod": "...",
        "dateDataGenerated": "2024-01-15T00:00:00Z",
        "dataType": "Tabular",
        "dataFormat": "CSV"
    },
    use={
        "intendedUse": "...",
        "legalRightsToUse": "...",
        "sensitiveData": False
    }
)

# Commit with provenance
commit_hash = tracker.commit_with_provenance(
    file_paths=[Path("my_data.csv")],
    metadata=metadata,
    message="Add dataset v1"
)
```

---

## Troubleshooting

### Python: "Module not found"

Make sure you installed in editable mode:
```bash
cd git-native
pip install -e .
```

### Git: "Not a git repository"

Initialize Git first:
```bash
git init
git config user.name "Your Name"
git config user.email "your@email.com"
```

### Blockchain: "Error connecting to network"

Make sure Hardhat node is running:
```bash
# Terminal 1
npx hardhat node
```

### CLI: "Command not found: dta-provenance"

The package might not be in your PATH. Try:
```bash
python -m src.cli --help
```

Or reinstall:
```bash
pip uninstall dta-provenance
pip install -e .
```

---

## Common Commands Reference

### Git-Native CLI

```bash
# Validate DTA metadata file
dta-provenance validate metadata.json

# Commit with provenance
dta-provenance commit file.csv --metadata metadata.json --message "Description"

# Verify a commit
dta-provenance verify HEAD
dta-provenance verify <commit-hash>

# Show provenance metadata
dta-provenance show HEAD
dta-provenance show <commit-hash> --output metadata.json

# Trace data lineage
dta-provenance trace file.csv
dta-provenance trace file.csv --format json
dta-provenance trace file.csv --max-commits 50

# Get help
dta-provenance --help
dta-provenance <command> --help
```

### Blockchain (Hardhat)

```bash
# Compile contracts
npx hardhat compile

# Run tests
npx hardhat test
npx hardhat test --gas-report

# Start local node
npx hardhat node

# Deploy to local network
npx hardhat run scripts/deploy.js --network localhost

# Run interaction demo
npx hardhat run scripts/interact.js --network localhost

# Clean build artifacts
npx hardhat clean
```

---

## Running Tests

### Python Tests

```bash
cd git-native

# Run all tests
pytest

# Run with verbose output
pytest -v

# Run with coverage
pytest --cov=src --cov-report=html

# View coverage report
open htmlcov/index.html

# Run specific test file
pytest tests/test_provenance.py

# Run specific test
pytest tests/test_provenance.py::test_commit_with_provenance -v
```

### Solidity Tests (when implemented)

```bash
cd blockchain

# Run all tests
npx hardhat test

# Run with gas reporting
REPORT_GAS=true npx hardhat test

# Run specific test file
npx hardhat test test/ProvenanceRegistry.test.js
```

---

## Next Steps

1. ✅ **You've completed the quick start!**

2. **Learn More:**
   - Read [DTA Standards Guide](docs/DTA_STANDARDS.md)
   - Read [Comparison Guide](docs/COMPARISON.md)
   - Explore [Real Examples](standards/examples/)

3. **Integrate:**
   - Use in your ML pipeline
   - Add to your data workflows
   - Customize for your use case

4. **Contribute:**
   - Report issues on GitHub
   - Submit improvements
   - Share your use case

---

## Need Help?

- **Documentation:** See [README.md](README.md) for comprehensive docs
- **Examples:** Check `standards/examples/` for real-world use cases
- **Issues:** Report bugs or ask questions on GitHub Issues
- **DTA Standards:** Visit https://www.dtaalliance.org/

---

**Congratulations!** 🎉

You're now tracking data provenance with DTA standards. Start with Git-native for most use cases, and explore blockchain only if you need trustless multi-party verification.
