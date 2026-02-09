# DVC Integration

Integrate DTA provenance tracking with [DVC (Data Version Control)](https://dvc.org/) for complete data lineage.

## Overview

DVC is a version control system for data files, ML models, and datasets. By combining DVC with DTA provenance metadata, you get:

- **Data versioning** - Track large data files outside Git
- **Content-addressable storage** - Immutable data identified by hash
- **DTA compliance** - Provenance metadata for regulatory requirements
- **Complete lineage** - Know exactly which data version was used

## Installation

```bash
# Install with DVC support
pip install 'dta-provenance[dvc]'

# Or install manually
pip install dvc>=3.0
```

## Quick Start

### 1. Initialize DVC in your repository

```bash
git init
dvc init
```

### 2. Track a file with DVC and provenance

```bash
# Create your provenance metadata
cat > provenance.json <<EOF
{
  "source": {
    "datasetName": "Customer Data Q1 2024",
    "providerName": "Internal CRM"
  },
  "provenance": {
    "dataGenerationMethod": "Exported from CRM system",
    "dateDataGenerated": "2024-01-15",
    "dataType": "Tabular",
    "dataFormat": "CSV"
  },
  "use": {
    "intendedUse": "Customer analytics",
    "legalRightsToUse": "Internal use only",
    "sensitiveData": true,
    "sensitiveDataCategories": ["PII", "Financial"]
  }
}
EOF

# Track file with DVC and enrich metadata
dta-provenance dvc-track customers.csv \\
    --metadata provenance.json \\
    --output provenance-with-dvc.json
```

### 3. Commit with enriched provenance

```bash
git add customers.csv.dvc .gitignore provenance-with-dvc.json
dta-provenance commit customers.csv.dvc provenance-with-dvc.json \\
    --metadata provenance-with-dvc.json \\
    --message "Add Q1 customer data with DVC tracking"
```

## How It Works

### DVC Metadata Enrichment

When you use `dvc-track`, the DTA provenance metadata is enriched with DVC-specific fields:

```json
{
  "source": { ... },
  "provenance": { ... },
  "use": { ... },
  "metadata": {
    "dvc": {
      "tracked": true,
      "dvc_file": "customers.csv.dvc",
      "md5": "abc123def456...",
      "size": "1048576",
      "path": "customers.csv"
    }
  }
}
```

This allows you to:

- **Verify data integrity** - Compare MD5 hashes
- **Track file versions** - DVC file changes are tracked in Git
- **Reconstruct exact state** - Use DVC checkout with commit hash
- **Audit compliance** - Full provenance + version history

### DVC File Structure

DVC creates `.dvc` files that are tracked in Git:

```yaml
# customers.csv.dvc
outs:
- md5: abc123def456
  size: 1048576
  path: customers.csv
```

The actual data is stored in `.dvc/cache/` and can be pushed to remote storage (S3, GCS, Azure, etc.).

## Usage Examples

### Track Multiple Files

```bash
dta-provenance dvc-track train.csv test.csv \\
    --metadata provenance.json \\
    --output provenance-enriched.json
```

### Track Without Existing Metadata

If you don't have provenance metadata yet, you can still track with DVC and create metadata later:

```bash
# Track with DVC first
dta-provenance dvc-track dataset.csv

# Creates enriched metadata with DVC info only
# Add full DTA provenance fields later
```

### Check DVC Status Programmatically

```python
from pathlib import Path
from src.integrations.dvc_integration import DVCProvenanceBridge

# Initialize bridge
bridge = DVCProvenanceBridge(Path('.'))

# Get DVC status
status = bridge.get_dvc_status()
print(f"Clean: {status['is_clean']}")

# Read DVC metadata for a file
dvc_info = bridge.read_dvc_provenance(Path('data.csv'))
if dvc_info:
    print(f"MD5: {dvc_info['metadata']['md5']}")
```

### Enrich Existing Metadata

If you already have DVC-tracked files and want to add provenance:

```python
from pathlib import Path
from src.integrations.dvc_integration import DVCProvenanceBridge
from src.provenance import load_provenance_file

# Load existing provenance
metadata = load_provenance_file(Path('provenance.json'))
metadata_dict = metadata.to_dict()

# Enrich with DVC info
bridge = DVCProvenanceBridge(Path('.'))
enriched = bridge.enrich_metadata_from_dvc(Path('data.csv'), metadata_dict)

# Save enriched metadata
import json
with open('provenance-with-dvc.json', 'w') as f:
    json.dump(enriched, f, indent=2)
```

## Workflow: Data Science Project

Complete workflow for a data science project with DVC + DTA:

```bash
# 1. Initialize project
git init
dvc init

# 2. Add raw data with provenance
dta-provenance dvc-track raw_data.csv \\
    --metadata raw_data_provenance.json \\
    --output raw_data_enriched.json

git add raw_data.csv.dvc raw_data_enriched.json .gitignore
git commit -m "Add raw data with provenance"

# 3. Process data (creates processed_data.csv)
python process_data.py

# 4. Track processed data with updated provenance
cat > processed_provenance.json <<EOF
{
  "source": {
    "datasetName": "Processed Customer Data",
    "providerName": "Internal CRM",
    "datasetVersion": "1.0-processed"
  },
  "provenance": {
    "dataGenerationMethod": "Cleaned and normalized from raw CRM export",
    "dateDataGenerated": "2024-01-16",
    "dataType": "Tabular",
    "dataFormat": "CSV",
    "qualityIndicators": "Removed duplicates, normalized dates"
  },
  "use": {
    "intendedUse": "ML model training",
    "legalRightsToUse": "Internal use only",
    "sensitiveData": true,
    "sensitiveDataCategories": ["PII"],
    "privacyMeasures": "Anonymized customer IDs"
  }
}
EOF

dta-provenance dvc-track processed_data.csv \\
    --metadata processed_provenance.json \\
    --output processed_enriched.json

git add processed_data.csv.dvc processed_enriched.json
dta-provenance commit processed_data.csv.dvc \\
    --metadata processed_enriched.json \\
    --message "Add processed data"

# 5. Push data to remote storage
dvc remote add -d storage s3://my-bucket/dvc-cache
dvc push

git push
```

## Remote Storage

DVC supports multiple remote storage backends:

```bash
# Amazon S3
dvc remote add -d storage s3://mybucket/dvcstore

# Google Cloud Storage
dvc remote add -d storage gs://mybucket/dvcstore

# Azure Blob Storage
dvc remote add -d storage azure://mycontainer/dvcstore

# SSH/SFTP
dvc remote add -d storage ssh://user@server/path

# Local or network filesystem
dvc remote add -d storage /mnt/dvc-storage
```

Push and pull data:

```bash
# Push local data to remote
dvc push

# Pull data from remote
dvc pull

# Get specific version
git checkout abc123
dvc checkout
```

## Benefits

### Data Scientists

- Track large datasets without bloating Git
- Reproduce exact results from any commit
- Share data efficiently with team
- Meet compliance requirements automatically

### MLOps Engineers

- Immutable data artifacts with cryptographic hashes
- Audit trail of all data transformations
- Integration with CI/CD pipelines
- Consistent environments across team

### Compliance Officers

- Complete provenance metadata per DTA standards
- Cryptographic proof of data integrity
- Full audit trail in Git history
- Evidence for regulatory audits

## Limitations

- **DVC required** - Both locally and in CI/CD
- **Storage costs** - Need remote storage for team collaboration
- **Initial setup** - Requires DVC initialization and remote configuration
- **Learning curve** - Team must understand DVC commands

## Troubleshooting

### "DVC is not installed"

```bash
pip install 'dta-provenance[dvc]'
# or
pip install dvc>=3.0
```

### "Not a DVC repository"

```bash
# Initialize DVC first
dvc init
git commit -m "Initialize DVC"
```

### "File is not DVC-tracked"

Ensure the file has been added with `dvc add` or use `dvc-track` command which does it automatically.

### "DVC command failed"

Check DVC installation and configuration:

```bash
dvc version
dvc status
dvc remote list
```

## Best Practices

1. **Always enrich metadata** - Don't track with DVC alone; add provenance metadata
2. **Commit .dvc files** - Always commit `.dvc` files and `.gitignore` to Git
3. **Use remote storage** - Configure DVC remote for team collaboration
4. **Version processed data** - Track both raw and processed datasets
5. **Document transformations** - Update provenance metadata when processing data
6. **Test data integrity** - Verify MD5 hashes after pulling data

## Related Resources

- [`dta-provenance dvc-track` command](../cli-reference.md#dvc-track)
- [DVC Documentation](https://dvc.org/doc)
- [DTA Standards](../DTA_STANDARDS.md)
- [MLflow Integration](mlflow-integration.md) - Track experiments with provenance
