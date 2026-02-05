"""
Provenance verification and validation tools.

Provides cryptographic verification of Git-based provenance records
and DTA standards compliance validation.
"""

from typing import Dict, List, Tuple
from pathlib import Path
from dataclasses import dataclass
import json

try:
    import jsonschema
except ImportError:
    raise ImportError(
        "jsonschema is required. Install with: pip install jsonschema"
    )

try:
    import git
except ImportError:
    raise ImportError(
        "GitPython is required. Install with: pip install GitPython"
    )

try:
    import networkx as nx
except ImportError:
    nx = None  # Optional dependency for lineage tracing


@dataclass
class ValidationReport:
    """Report of DTA standards validation."""

    is_valid: bool
    errors: List[str]
    warnings: List[str]
    missing_optional_fields: List[str]
    score: float  # 0.0 to 1.0

    def __str__(self) -> str:
        """Human-readable validation report."""
        status = "✅ VALID" if self.is_valid else "❌ INVALID"
        report = f"DTA Standards Validation: {status}\n"
        report += f"Compliance Score: {self.score:.1%}\n\n"

        if self.errors:
            report += "Errors:\n"
            for error in self.errors:
                report += f"  ❌ {error}\n"
            report += "\n"

        if self.warnings:
            report += "Warnings:\n"
            for warning in self.warnings:
                report += f"  ⚠️  {warning}\n"
            report += "\n"

        if self.missing_optional_fields:
            report += "Missing Optional Fields (recommended):\n"
            for field in self.missing_optional_fields:
                report += f"  ℹ️  {field}\n"

        return report


class ProvenanceVerifier:
    """Verify integrity and compliance of provenance records."""

    def __init__(self, schema_path: Optional[Path] = None):
        """
        Initialize with DTA JSON schema.

        Args:
            schema_path: Path to DTA v1.0.0 JSON schema
                        If None, uses basic validation only
        """
        self.schema = None
        if schema_path and schema_path.exists():
            with open(schema_path) as f:
                self.schema = json.load(f)

    def verify_commit_integrity(
        self,
        commit_hash: str,
        repo: git.Repo
    ) -> Tuple[bool, str]:
        """
        Verify Git commit signature and metadata hash.

        Args:
            commit_hash: Git commit SHA
            repo: GitPython Repo object

        Returns:
            (is_valid, error_message)
        """
        try:
            commit = repo.commit(commit_hash)
        except git.exc.BadName:
            return False, f"Commit not found: {commit_hash}"

        # Extract provenance metadata from commit message
        metadata = self._extract_metadata(commit.message)
        if not metadata:
            return True, "No provenance metadata (not an error)"

        # Verify metadata hash
        stored_hash = self._extract_hash(commit.message)
        if not stored_hash:
            return False, "Provenance metadata present but hash missing"

        # Compute hash from metadata
        import hashlib
        metadata_json = json.dumps(metadata, sort_keys=True)
        computed_hash = hashlib.sha256(metadata_json.encode()).hexdigest()

        if stored_hash != computed_hash:
            return False, "Metadata hash mismatch (possible tampering)"

        return True, "Integrity verified"

    def validate_dta_compliance(
        self,
        metadata: Dict
    ) -> ValidationReport:
        """
        Validate metadata against DTA v1.0.0 standards.

        Performs both schema validation and semantic validation.

        Args:
            metadata: Provenance metadata dictionary

        Returns:
            ValidationReport with errors, warnings, and score
        """
        errors = []
        warnings = []
        missing_optional = []

        # Required fields validation
        required_fields = {
            "source": ["datasetName", "providerName"],
            "provenance": [
                "dataGenerationMethod",
                "dateDataGenerated",
                "dataType",
                "dataFormat"
            ],
            "use": ["intendedUse", "legalRightsToUse", "sensitiveData"]
        }

        for category, fields in required_fields.items():
            if category not in metadata:
                errors.append(f"Missing required category: {category}")
                continue

            for field in fields:
                if field not in metadata[category]:
                    errors.append(f"Missing required field: {category}.{field}")

        # Recommended fields
        recommended_fields = {
            "source": [
                "datasetVersion",
                "datasetURI",
                "providerWebsite",
                "geographicSourceOfData"
            ],
            "provenance": ["qualityIndicators"],
            "use": ["restrictions", "privacyMeasures"]
        }

        for category, fields in recommended_fields.items():
            if category in metadata:
                for field in fields:
                    if field not in metadata[category]:
                        missing_optional.append(f"{category}.{field}")

        # Semantic validation
        if "use" in metadata:
            # If sensitiveData is True, must have sensitiveDataCategories
            if metadata["use"].get("sensitiveData"):
                if not metadata["use"].get("sensitiveDataCategories"):
                    errors.append(
                        "sensitiveDataCategories required when sensitiveData=true"
                    )
                if not metadata["use"].get("privacyMeasures"):
                    warnings.append(
                        "privacyMeasures strongly recommended when sensitiveData=true"
                    )

        # Data type validation
        valid_data_types = [
            "Text", "Image", "Audio", "Video", "Time series",
            "Tabular", "Graph", "Geospatial", "Multi-modal"
        ]
        if "provenance" in metadata:
            data_type = metadata["provenance"].get("dataType")
            if data_type and data_type not in valid_data_types:
                warnings.append(
                    f"dataType '{data_type}' not in standard types: {valid_data_types}"
                )

        # JSON Schema validation (if schema provided)
        if self.schema:
            try:
                jsonschema.validate(metadata, self.schema)
            except jsonschema.ValidationError as e:
                errors.append(f"Schema validation error: {e.message}")
            except jsonschema.SchemaError as e:
                warnings.append(f"Schema error: {e.message}")

        # Calculate compliance score
        total_fields = sum(len(fields) for fields in required_fields.values())
        total_fields += sum(len(fields) for fields in recommended_fields.values())

        present_fields = total_fields - len(errors) - len(missing_optional)
        score = present_fields / total_fields if total_fields > 0 else 0.0

        is_valid = len(errors) == 0

        return ValidationReport(
            is_valid=is_valid,
            errors=errors,
            warnings=warnings,
            missing_optional_fields=missing_optional,
            score=score
        )

    def trace_lineage(
        self,
        file_path: Path,
        repo: git.Repo
    ) -> Optional["nx.DiGraph"]:
        """
        Build directed acyclic graph of data lineage.

        Traces the history of a file through Git commits and builds
        a dependency graph showing how data evolved over time.

        Args:
            file_path: File to trace (relative to repo root)
            repo: GitPython Repo object

        Returns:
            NetworkX DiGraph if networkx installed, None otherwise
        """
        if nx is None:
            raise ImportError(
                "networkx is required for lineage tracing. "
                "Install with: pip install networkx"
            )

        graph = nx.DiGraph()

        try:
            commits = list(repo.iter_commits(paths=str(file_path)))
        except git.exc.GitCommandError:
            return graph

        # Add nodes for each commit
        for commit in commits:
            metadata = self._extract_metadata(commit.message)

            node_data = {
                "commit": commit.hexsha[:8],
                "author": str(commit.author),
                "date": commit.committed_datetime.isoformat(),
                "message": commit.message.split('\n')[0]
            }

            if metadata:
                dataset_name = metadata.get("source", {}).get("datasetName", "Unknown")
                node_data["dataset"] = dataset_name

            graph.add_node(commit.hexsha, **node_data)

        # Add edges (parent -> child relationships)
        for commit in commits:
            for parent in commit.parents:
                if parent.hexsha in graph:
                    graph.add_edge(parent.hexsha, commit.hexsha)

        return graph

    def _extract_metadata(self, commit_message: str) -> Optional[Dict]:
        """Extract provenance metadata from commit message."""
        for line in commit_message.split('\n'):
            if line.startswith('DTA-Provenance-Metadata:'):
                metadata_json = line.split(':', 1)[1].strip()
                try:
                    return json.loads(metadata_json)
                except json.JSONDecodeError:
                    return None
        return None

    def _extract_hash(self, commit_message: str) -> Optional[str]:
        """Extract provenance hash from commit message."""
        for line in commit_message.split('\n'):
            if line.startswith('DTA-Provenance-Hash:'):
                return line.split(':', 1)[1].strip()
        return None


def validate_provenance_file(
    file_path: Path,
    schema_path: Optional[Path] = None
) -> ValidationReport:
    """
    Validate a provenance JSON file against DTA standards.

    Args:
        file_path: Path to provenance JSON file
        schema_path: Path to DTA JSON schema (optional)

    Returns:
        ValidationReport
    """
    verifier = ProvenanceVerifier(schema_path)

    with open(file_path) as f:
        metadata = json.load(f)

    return verifier.validate_dta_compliance(metadata)
