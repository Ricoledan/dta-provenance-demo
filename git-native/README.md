# Git-Native DTA Provenance Tracking

Production-quality Python library and CLI tool for tracking data provenance using Git commits with DTA Alliance standards v1.0.0.

## Features

- ✅ **DTA v1.0.0 Compliant** - Implements all 22 required and optional fields
- ✅ **Git Integration** - Uses Git commits for cryptographic integrity
- ✅ **CLI Tool** - Beautiful terminal interface with Rich
- ✅ **Python Library** - Importable for integration with ML pipelines
- ✅ **REST API Server** - FastAPI server for provenance queries
- ✅ **Web Dashboard** - Interactive UI for visualization and validation
- ✅ **Verification** - Cryptographic integrity checking
- ✅ **Audit Trails** - Complete lineage tracking
- ✅ **Visualization** - Generate provenance graphs with D3.js
- ✅ **Type Hints** - Full type annotations for IDE support
- ✅ **Tested** - Comprehensive test coverage

## Quick Start

### Installation

```bash
# Install from PyPI (when published)
pip install dta-provenance

# Or install from source
git clone https://github.com/yourusername/dta-provenance-demo.git
cd dta-provenance-demo/git-native
pip install -e .
```

### CLI Usage

```bash
# Validate DTA metadata
dta-provenance validate metadata.json

# Commit with provenance
dta-provenance commit dataset.csv \
  --metadata provenance.json \
  --message "Add training dataset v1.0"

# Verify integrity
dta-provenance verify HEAD

# Trace lineage
dta-provenance trace dataset.csv

# Show provenance metadata
dta-provenance show HEAD

# Start API server
dta-provenance serve --port 8000
```

### Python Library Usage

```python
from pathlib import Path
from src.provenance import ProvenanceTracker, ProvenanceMetadata

# Create metadata
metadata = ProvenanceMetadata(
    source={
        "datasetName": "Customer Churn Dataset",
        "providerName": "Analytics Team"
    },
    provenance={
        "dataGenerationMethod": "SQL export",
        "dateDataGenerated": "2024-01-15T00:00:00Z",
        "dataType": "Tabular",
        "dataFormat": "CSV"
    },
    use={
        "intendedUse": "ML model training",
        "legalRightsToUse": "Internal use",
        "sensitiveData": False
    }
)

# Initialize tracker
tracker = ProvenanceTracker(Path("."))

# Commit with provenance
commit_hash = tracker.commit_with_provenance(
    file_paths=[Path("data/churn.csv")],
    metadata=metadata,
    message="Add churn prediction dataset"
)

# Verify integrity
is_valid, message = tracker.verify_integrity(commit_hash)
print(f"Integrity: {message}")

# Generate audit trail
audit_trail = tracker.generate_audit_trail(
    Path("data/churn.csv")
)
```

## Requirements

- Python 3.9 or higher
- Git 2.30 or higher

## Dependencies

- `GitPython` - Git repository interaction
- `click` - CLI framework
- `rich` - Beautiful terminal output
- `jsonschema` - DTA schema validation
- `networkx` - Lineage graph generation

## Development

### Running Tests

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# View coverage report
open htmlcov/index.html
```

### Code Quality

```bash
# Format code
black src/ tests/

# Lint
ruff check src/ tests/

# Type check
mypy src/
```

## Documentation

- [DTA Standards Guide](../docs/DTA_STANDARDS.md) - Complete guide to all 22 fields
- [Comparison](../docs/COMPARISON.md) - Git vs. Blockchain analysis
- [Frontend Dashboard](../docs/tutorials/dashboard.md) - Web UI for visualization
- [API Server](../docs/tutorials/api-server.md) - REST API documentation
- [Examples](../standards/examples/) - Real-world provenance examples

## Integration Examples

### With MLflow

```python
import mlflow
from pathlib import Path
from src.provenance import ProvenanceTracker, load_provenance_file
from src.integrations.mlflow_integration import MLflowProvenanceBridge

# Load provenance metadata
metadata = load_provenance_file(Path('provenance.json'))

# Initialize tracking
tracker = ProvenanceTracker(Path("."))
bridge = MLflowProvenanceBridge(Path("."))

with mlflow.start_run():
    # Train model
    model = train_model(data)

    # Create Git commit with MLflow tracking (bidirectional linking)
    commit_hash, run_id = bridge.commit_with_mlflow_tracking(
        file_paths=[Path("data/training_data.csv")],
        metadata=metadata.to_dict(),
        message=f"Training data for model v1",
        tracker=tracker,
        experiment_name="churn-prediction"
    )

    print(f"Git commit: {commit_hash}")
    print(f"MLflow run: {run_id}")

# Or use CLI
# dta-provenance mlflow-log --metadata provenance.json
```

### With DVC (Data Version Control)

```python
# Track large files with DVC
!dvc add data/large_dataset.parquet

# Track provenance with DTA
tracker = ProvenanceTracker(Path("."))
tracker.commit_with_provenance(
    file_paths=[Path("data/large_dataset.parquet.dvc")],
    metadata=metadata,
    message="Add large dataset (tracked with DVC)"
)
```

### Web Dashboard

Run the complete stack with Docker Compose:

```bash
# Start API server + Dashboard
docker-compose up --build

# Access dashboard at http://localhost:3000
# API available at http://localhost:8000
```

Features:
- **Provenance Lookup** - View metadata for any commit
- **Audit Trail** - Timeline visualization of file history
- **Lineage Graph** - Interactive D3-based DAG visualization
- **Validator** - Real-time DTA v1.0.0 compliance checking

See [Dashboard Documentation](../docs/tutorials/dashboard.md) for details.

### In CI/CD Pipeline

```yaml
# .github/workflows/validate-provenance.yml
name: Validate Provenance

on: [push]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'

      - name: Install dependencies
        run: pip install dta-provenance

      - name: Validate provenance metadata
        run: |
          dta-provenance validate data/provenance.json

      - name: Verify latest commit
        run: |
          dta-provenance verify HEAD
```

## API Reference

### ProvenanceMetadata

```python
class ProvenanceMetadata:
    """DTA v1.0.0 compliant metadata."""

    def __init__(
        self,
        source: Dict[str, Any],
        provenance: Dict[str, Any],
        use: Dict[str, Any],
        metadata: Dict[str, Any] = {}
    )

    def to_dict(self) -> Dict
    def compute_hash(self) -> str

    @classmethod
    def from_dict(cls, data: Dict) -> "ProvenanceMetadata"

    @classmethod
    def from_json_file(cls, file_path: Path) -> "ProvenanceMetadata"
```

### ProvenanceTracker

```python
class ProvenanceTracker:
    """Main class for Git-native provenance tracking."""

    def __init__(self, repo_path: Path)

    def commit_with_provenance(
        self,
        file_paths: List[Path],
        metadata: ProvenanceMetadata,
        message: str,
        sign: bool = False
    ) -> str

    def read_provenance(self, commit_hash: str) -> Optional[ProvenanceMetadata]

    def generate_audit_trail(
        self,
        file_path: Path,
        max_commits: Optional[int] = None
    ) -> List[Dict]

    def verify_integrity(self, commit_hash: str) -> Tuple[bool, str]
```

### ProvenanceVerifier

```python
class ProvenanceVerifier:
    """Verify integrity and compliance."""

    def __init__(self, schema_path: Optional[Path] = None)

    def verify_commit_integrity(
        self,
        commit_hash: str,
        repo: git.Repo
    ) -> Tuple[bool, str]

    def validate_dta_compliance(
        self,
        metadata: Dict
    ) -> ValidationReport

    def trace_lineage(
        self,
        file_path: Path,
        repo: git.Repo
    ) -> Optional[nx.DiGraph]
```

## License

MIT License - see [LICENSE](../LICENSE) for details.

## Credits

Uses the official [Data & Trust Alliance](https://www.dtaalliance.org/) Data Provenance Standards v1.0.0.

See [ATTRIBUTION](../standards/official/ATTRIBUTION.md) for full credits.

## Contributing

Contributions welcome! Please see [CONTRIBUTING.md](../docs/CONTRIBUTING.md) for guidelines.

## Support

- **Issues:** [GitHub Issues](https://github.com/yourusername/dta-provenance-demo/issues)
- **Documentation:** [Project Docs](../docs/)
- **Examples:** [Real-world examples](../standards/examples/)
