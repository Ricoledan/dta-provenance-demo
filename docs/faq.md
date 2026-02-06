# Frequently Asked Questions

## General Questions

### What is data provenance?

Data provenance is the documentation of data's origin, movement, and transformations throughout its lifecycle. It answers questions like:
- Where did this data come from?
- How was it collected or generated?
- What transformations were applied?
- Who has access to it?
- How should it be used?

### Why does data provenance matter?

Data provenance is increasingly critical for:

1. **Regulatory Compliance**
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

### What are the Data & Trust Alliance (DTA) standards?

The DTA standards v1.0.0 define 22 fields organized into three categories:
- **SOURCE** (8 fields): Where data came from
- **PROVENANCE** (6 fields): How data was created
- **USE** (8 fields): How data should be used

See [DTA Standards Guide](DTA_STANDARDS.md) for full details.

## Technical Questions

### Do I need blockchain for data provenance?

**Almost certainly not.** The Git-native approach works for 95% of use cases.

**Use Git-native when:**
- ✅ Single organization controls the data
- ✅ Internal ML pipelines
- ✅ Privacy-sensitive data
- ✅ High-frequency updates
- ✅ Cost matters

**Only use blockchain when ALL of these apply:**
- ⚠️ Multiple untrusting parties
- ⚠️ No central authority can be trusted
- ⚠️ Automated settlement needed (smart contracts)
- ⚠️ Public transparency valuable
- ⚠️ Update frequency low enough

See [detailed comparison](COMPARISON.md).

### Is this production-ready?

**Git-native implementation:** Yes, production-quality with:
- ✅ Comprehensive test coverage
- ✅ CLI tools
- ✅ Error handling
- ✅ Documentation

**Blockchain implementation:** Educational/demo quality. Would need:
- ⚠️ Access control improvements
- ⚠️ Gas optimization
- ⚠️ Security audit
- ⚠️ Deployment infrastructure

### Can I use this with my existing ML pipeline?

Yes! The Python library integrates easily with:
- MLflow
- DVC (Data Version Control)
- Jupyter notebooks
- Standard Python ML tools

See the [ML Training example](examples/ml-training.md).

### What about IPFS/Arweave for decentralized storage?

These are great for immutable file storage and complement either approach:
- Store full datasets on IPFS/Arweave
- Store provenance metadata hash on-chain (blockchain) or in Git
- Reference IPFS/Arweave URIs in metadata

The blockchain implementation shows this pattern with `metadataURI` fields.

### How does this compare to DVC (Data Version Control)?

**DVC:**
- Focuses on versioning large files efficiently
- Handles data storage and retrieval
- Integrates with cloud storage (S3, GCS, Azure)

**This project:**
- Focuses on metadata and provenance tracking
- Implements DTA standards compliance
- Provides cryptographic integrity verification

They're **complementary** - you can use both together:
- DVC for efficient file versioning
- DTA provenance for metadata tracking

## Compliance Questions

### Does this meet GDPR requirements?

The DTA standards align with GDPR requirements, specifically:
- Article 5(1)(a): Lawfulness, fairness, and transparency
- Article 5(2): Accountability
- Article 30: Records of processing activities

This project helps you document:
- Legal basis for processing (`legalRightsToUse`)
- Privacy measures (`privacyMeasures`)
- Data categories (`sensitiveDataCategories`)
- Processing locations (`dataProcessingLocation`)

**However**, this is a documentation tool, not a complete GDPR compliance solution. Consult legal counsel for full compliance.

### What about the EU AI Act?

The EU AI Act requires training data provenance for high-risk AI systems. The DTA standards cover:
- Data sources and origins
- Collection methodology
- Quality indicators
- Bias assessment
- Privacy measures

See [DTA Standards Guide](DTA_STANDARDS.md) for regulatory mapping.

### Can this be used for FDA submissions?

The provenance tracking provides documentation useful for FDA AI/ML submissions:
- Data collection procedures
- Quality controls
- Version tracking
- Audit trails

**However**, FDA compliance requires additional documentation beyond provenance. Use this as part of a broader quality management system.

## Usage Questions

### How do I get started?

1. [Install](installation.md) the tools (Nix, Docker, or manual)
2. Follow the [Quick Start Guide](quickstart.md)
3. Try the [Interactive Jupyter Notebook](https://github.com/Ricoledan/dta-provenance-demo/blob/main/DTA_Provenance_Demo.ipynb)
4. Explore [real-world examples](examples/healthcare.md)

### Can I modify the DTA standards?

The DTA standards are extensible - you can add custom fields while maintaining core compliance:

```python
metadata = ProvenanceMetadata(
    source={"datasetName": "...", ...},  # Required DTA fields
    provenance={"dataGenerationMethod": "...", ...},
    use={"intendedUse": "...", ...},
    # Add custom fields
    custom={
        "internalTrackingId": "12345",
        "departmentCode": "ML-RESEARCH",
        "customQualityMetrics": {...}
    }
)
```

### How do I validate my metadata?

```bash
# CLI
dta-provenance validate my-metadata.json

# Python
from src.verify import validate_provenance_file
report = validate_provenance_file("my-metadata.json")
print(report)
```

### Can I use this in a CI/CD pipeline?

Yes! The GitHub Actions workflow shows integration:

```yaml
- name: Validate provenance
  run: |
    dta-provenance validate metadata.json
    if [ $? -ne 0 ]; then
      echo "Provenance validation failed"
      exit 1
    fi
```

See [GitHub Actions workflow](https://github.com/Ricoledan/dta-provenance-demo/blob/main/.github/workflows/test.yml).

## Community Questions

### How can I contribute?

See the [Contributing Guide](CONTRIBUTING.md) for:
- Code contributions
- Documentation improvements
- Bug reports
- Feature requests
- Examples and use cases

### Who maintains this project?

This is an open-source educational project demonstrating DTA standards implementation. Contributions welcome!

### Where can I get help?

- **GitHub Issues**: [Report bugs or ask questions](https://github.com/Ricoledan/dta-provenance-demo/issues)
- **Documentation**: [Full documentation site](https://ricoledan.github.io/dta-provenance-demo)
- **DTA Alliance**: [Official website](https://www.dtaalliance.org/)

## Blockchain-Specific Questions

### What blockchain networks are supported?

The demo supports:
- Hardhat local network (for testing)
- Ethereum mainnet/testnets
- Polygon (with configuration)
- Any EVM-compatible network

See `blockchain/hardhat.config.js` for network configuration.

### What are the gas costs?

From our tests:
- Registration: ~228,000 gas (~$5-20 depending on network)
- Verification: ~29,000 gas (~$0.50-5)

**This is why Git-native is recommended for most use cases** - no gas fees!

### Can I use a private blockchain?

Yes! Deploy to:
- Hyperledger Besu
- Quorum
- Polygon Supernets
- Other private EVM networks

Private blockchains offer lower costs but lose the public transparency benefit.

## Still Have Questions?

- Open an issue: [GitHub Issues](https://github.com/Ricoledan/dta-provenance-demo/issues)
- Read the docs: [Full Documentation](https://ricoledan.github.io/dta-provenance-demo)
- Check examples: [Real-world Examples](examples/healthcare.md)
