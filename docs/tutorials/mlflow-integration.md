# MLflow Integration

Integrate DTA provenance tracking with [MLflow](https://mlflow.org/) for complete ML experiment and data lineage.

## Overview

MLflow is an open-source platform for managing the ML lifecycle, including experimentation, reproducibility, and deployment. By combining MLflow with DTA provenance metadata, you get:

- **Experiment tracking** - Track ML experiments with full data provenance
- **Reproducibility** - Link model runs to exact data versions
- **DTA compliance** - Provenance metadata for regulatory requirements
- **Complete lineage** - Know exactly which data was used for each model

## Installation

```bash
# Install with MLflow support
pip install 'dta-provenance[mlflow]'

# Or install manually
pip install mlflow>=2.0
```

## Quick Start

### 1. Set up MLflow tracking

```bash
# Use local tracking (default)
export MLFLOW_TRACKING_URI=file:./mlruns

# Or use remote tracking server
export MLFLOW_TRACKING_URI=http://mlflow-server:5000
```

### 2. Log provenance to MLflow

```bash
# Create your provenance metadata
cat > provenance.json <<EOF
{
  "source": {
    "datasetName": "Customer Churn Dataset Q1 2024",
    "providerName": "Internal CRM",
    "datasetUrl": "s3://data-bucket/customer-churn-q1.csv",
    "license": "Internal Use Only"
  },
  "provenance": {
    "dataGenerationMethod": "Exported from CRM system with SQL query",
    "dateDataGenerated": "2024-01-15T00:00:00Z",
    "dataType": "Tabular",
    "dataFormat": "CSV"
  },
  "use": {
    "intendedUse": "ML model training for churn prediction",
    "legalRightsToUse": "Internal use only",
    "sensitiveData": true,
    "sensitiveDataCategories": ["PII", "Behavioral"]
  }
}
EOF

# Log provenance to active MLflow run
# (requires an active MLflow run)
mlflow run start
dta-provenance mlflow-log --metadata provenance.json
```

### 3. Use in Python with MLflow

```python
import mlflow
from pathlib import Path
from src.provenance import ProvenanceTracker, load_provenance_file
from src.integrations.mlflow_integration import MLflowProvenanceBridge

# Load provenance metadata
metadata = load_provenance_file(Path('provenance.json'))

# Initialize bridge
bridge = MLflowProvenanceBridge(Path('.'))
tracker = ProvenanceTracker(Path('.'))

# Start MLflow run with provenance tracking
with mlflow.start_run(run_name='churn-model-v1'):
    # Train model
    model = train_model(data)

    # Log model metrics
    mlflow.log_metric('accuracy', 0.95)
    mlflow.log_metric('f1_score', 0.92)

    # Create Git commit with MLflow tracking
    commit_hash, run_id = bridge.commit_with_mlflow_tracking(
        file_paths=[Path('data/training_data.csv')],
        metadata=metadata.to_dict(),
        message='Training data for churn model v1',
        tracker=tracker,
        experiment_name='churn-prediction'
    )

    print(f"Git commit: {commit_hash}")
    print(f"MLflow run: {run_id}")
```

## How It Works

### Provenance Metadata in MLflow

When you use `mlflow-log`, the DTA provenance metadata is stored in MLflow as tags:

```python
# Tags stored in MLflow run
{
  "dta.compliant": "true",
  "dta.version": "1.0.0",
  "dta.source.datasetName": "Customer Churn Dataset Q1 2024",
  "dta.source.providerName": "Internal CRM",
  "dta.provenance.dataType": "Tabular",
  "dta.provenance.dataFormat": "CSV",
  "dta.use.intendedUse": "ML model training for churn prediction",
  "dta.use.sensitiveData": "True",
  "git.commit_hash": "abc123def456...",
  "git.commit_message": "Training data for churn model v1"
}
```

Additionally, the complete provenance metadata is stored as an artifact for full detail.

### Bidirectional Linking

The integration creates bidirectional links between Git and MLflow:

- **Git → MLflow**: Git commit metadata includes `mlflow_run_id`
- **MLflow → Git**: MLflow run tags include `git.commit_hash`

This allows you to:

- **Start from Git**: Find which MLflow runs used a specific commit
- **Start from MLflow**: Find which Git commit contains the data for a run
- **Audit trail**: Complete bidirectional traceability

## Usage Examples

### Log to Specific Run

```bash
# Log to specific MLflow run ID
dta-provenance mlflow-log \\
    --metadata provenance.json \\
    --run-id abc123-run-id
```

### Use Custom Tracking URI

```bash
# Log to remote MLflow server
dta-provenance mlflow-log \\
    --metadata provenance.json \\
    --tracking-uri http://mlflow-server:5000
```

### Query Runs by Dataset

```python
from pathlib import Path
from src.integrations.mlflow_integration import MLflowProvenanceBridge

# Initialize bridge
bridge = MLflowProvenanceBridge(Path('.'))

# Find all runs that used a specific dataset
runs = bridge.get_mlflow_runs_by_dataset('Customer Churn Dataset Q1 2024')

for run in runs:
    print(f"Run ID: {run['run_id']}")
    print(f"Status: {run['status']}")
    print(f"Metrics: {run['metrics']}")
```

### Read Provenance from MLflow

```python
from pathlib import Path
from src.integrations.mlflow_integration import MLflowProvenanceBridge

bridge = MLflowProvenanceBridge(Path('.'))

# Read provenance metadata from MLflow run
metadata = bridge.read_mlflow_provenance('run-id-123')

if metadata:
    print(f"Dataset: {metadata['source']['datasetName']}")
    print(f"Data Type: {metadata['provenance']['dataType']}")
    print(f"Sensitive: {metadata['use']['sensitiveData']}")
```

## Workflow: ML Model Development

Complete workflow for ML model development with MLflow + DTA:

```python
import mlflow
from pathlib import Path
from src.provenance import ProvenanceTracker, ProvenanceMetadata
from src.integrations.mlflow_integration import MLflowProvenanceBridge

# 1. Create provenance metadata
metadata = ProvenanceMetadata(
    source={
        "datasetName": "Customer Churn Training Set",
        "providerName": "Data Engineering Team",
        "datasetUrl": "s3://data-lake/churn/train.csv"
    },
    provenance={
        "dataGenerationMethod": "Stratified sampling from CRM database",
        "dateDataGenerated": "2024-01-15T00:00:00Z",
        "dataType": "Tabular",
        "dataFormat": "CSV"
    },
    use={
        "intendedUse": "Train churn prediction model",
        "legalRightsToUse": "Internal use only",
        "sensitiveData": True,
        "sensitiveDataCategories": ["PII", "Behavioral"]
    }
)

# 2. Initialize tracking
tracker = ProvenanceTracker(Path('.'))
bridge = MLflowProvenanceBridge(Path('.'))

# 3. Train model with full tracking
mlflow.set_experiment('churn-prediction')

with mlflow.start_run(run_name='random-forest-v1') as run:
    # Log parameters
    mlflow.log_param('model_type', 'RandomForest')
    mlflow.log_param('n_estimators', 100)

    # Train model
    model = train_random_forest(data, n_estimators=100)

    # Log metrics
    accuracy = evaluate_model(model, test_data)
    mlflow.log_metric('accuracy', accuracy)

    # Create Git commit with MLflow tracking
    commit_hash, run_id = bridge.commit_with_mlflow_tracking(
        file_paths=[Path('data/train.csv')],
        metadata=metadata.to_dict(),
        message=f'Training data for RandomForest v1 (accuracy: {accuracy:.3f})',
        tracker=tracker
    )

    # Log model
    mlflow.sklearn.log_model(model, 'model')

    print(f"Model trained and logged!")
    print(f"Git commit: {commit_hash}")
    print(f"MLflow run: {run_id}")

# 4. Later: retrieve full lineage
lineage = bridge.read_mlflow_provenance(run_id)
print(f"Model was trained on: {lineage['source']['datasetName']}")
```

## Advanced Features

### Experiment Organization

```python
# Organize by project
mlflow.set_experiment('customer-analytics/churn-prediction')

# Organize by model type
mlflow.set_experiment('models/classification')

# Organize by data version
mlflow.set_experiment('data-v2/experiments')
```

### Comparing Runs

```python
from src.integrations.mlflow_integration import MLflowProvenanceBridge

bridge = MLflowProvenanceBridge(Path('.'))

# Get all runs for a dataset
runs = bridge.get_mlflow_runs_by_dataset('Customer Churn Dataset')

# Compare metrics across runs
for run in runs:
    print(f"Run {run['run_id']}: accuracy={run['metrics'].get('accuracy', 'N/A')}")
```

### CI/CD Integration

```yaml
# .github/workflows/train-model.yml
name: Train Model

on: [push]

jobs:
  train:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'

      - name: Install dependencies
        run: |
          pip install dta-provenance[mlflow]
          pip install -r requirements.txt

      - name: Train model with provenance
        env:
          MLFLOW_TRACKING_URI: ${{ secrets.MLFLOW_TRACKING_URI }}
        run: |
          python train_model.py

      - name: Log provenance to MLflow
        run: |
          dta-provenance mlflow-log --metadata provenance.json
```

## Benefits

### Data Scientists

- Track which data version produced which model
- Reproduce exact results from any experiment
- Compare models trained on different datasets
- Meet compliance requirements automatically

### MLOps Engineers

- Immutable audit trail of all experiments
- Bidirectional Git ↔ MLflow linking
- Integration with CI/CD pipelines
- Automated compliance metadata

### Compliance Officers

- Complete provenance metadata per DTA standards
- Cryptographic proof via Git commits
- Query which data was used for which models
- Evidence for regulatory audits

## Remote Tracking Server

Set up a remote MLflow tracking server for team collaboration:

```bash
# Start MLflow server
mlflow server \\
    --backend-store-uri postgresql://user:pass@localhost/mlflow \\
    --default-artifact-root s3://mlflow-artifacts \\
    --host 0.0.0.0 \\
    --port 5000

# Configure clients to use remote server
export MLFLOW_TRACKING_URI=http://mlflow-server:5000

# Or in Python
import mlflow
mlflow.set_tracking_uri('http://mlflow-server:5000')
```

## Limitations

- **MLflow required** - Both locally and in CI/CD
- **Active run needed** - Must have MLflow run context for logging
- **Network access** - Remote tracking server requires network connectivity
- **Storage costs** - Remote artifact storage (S3, Azure, GCS) costs apply

## Troubleshooting

### "MLflow is not installed"

```bash
pip install 'dta-provenance[mlflow]'
# or
pip install mlflow>=2.0
```

### "No active MLflow run"

Start an MLflow run before logging:

```python
import mlflow

with mlflow.start_run():
    # Now you can log provenance
    bridge.log_provenance_to_mlflow(metadata)
```

Or provide run_id explicitly:

```bash
dta-provenance mlflow-log --metadata provenance.json --run-id abc123
```

### "Cannot connect to tracking server"

Check MLflow tracking URI:

```bash
echo $MLFLOW_TRACKING_URI

# Test connection
mlflow experiments list
```

### "Artifact logging failed"

Ensure artifact storage is configured and accessible:

```bash
# Check MLflow configuration
mlflow server --help

# Test artifact logging
mlflow artifacts log-artifact test.txt
```

## Best Practices

1. **Always log provenance** - Don't train models without data provenance
2. **Use experiments** - Organize runs into meaningful experiments
3. **Bidirectional linking** - Use `commit_with_mlflow_tracking` for automatic linking
4. **Query by dataset** - Track which datasets are most effective
5. **Version everything** - Version code (Git), data (DVC/Git), and experiments (MLflow)
6. **Document assumptions** - Include data quality notes in provenance metadata

## Related Resources

- [`dta-provenance mlflow-log` command](../cli-reference.md#mlflow-log)
- [MLflow Documentation](https://mlflow.org/docs/latest/index.html)
- [DTA Standards](../DTA_STANDARDS.md)
- [DVC Integration](dvc-integration.md) - Version data files with DVC
