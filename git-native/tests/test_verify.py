"""
Tests for the verification module.
"""

import json
import tempfile
from pathlib import Path
import pytest
from git import Repo

from src.verify import ProvenanceVerifier, ValidationReport
from src.provenance import ProvenanceMetadata, ProvenanceTracker


@pytest.fixture
def temp_git_repo():
    """Create a temporary git repository for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        repo_path = Path(tmpdir)
        repo = Repo.init(repo_path)

        # Configure git user
        with repo.config_writer() as git_config:
            git_config.set_value("user", "name", "Test User")
            git_config.set_value("user", "email", "test@example.com")

        yield repo_path


@pytest.fixture
def valid_metadata():
    """Create valid DTA metadata for testing."""
    return {
        "source": {
            "datasetName": "Test Dataset",
            "providerName": "Test Provider",
            "datasetVersion": "1.0.0"
        },
        "provenance": {
            "dataGenerationMethod": "Manual testing",
            "dateDataGenerated": "2024-01-15T00:00:00Z",
            "dataType": "Tabular",
            "dataFormat": "CSV"
        },
        "use": {
            "intendedUse": "Testing purposes",
            "legalRightsToUse": "Test license",
            "sensitiveData": False
        }
    }


@pytest.fixture
def verifier():
    """Create a ProvenanceVerifier instance."""
    return ProvenanceVerifier()


class TestProvenanceVerifier:
    """Test suite for ProvenanceVerifier class."""

    def test_verifier_initialization(self, verifier):
        """Test that verifier initializes correctly."""
        assert verifier is not None
        assert verifier.schema is None  # No schema provided

    def test_validate_metadata_valid(self, verifier, valid_metadata):
        """Test validation of valid metadata."""
        report = verifier.validate_metadata(valid_metadata)

        assert isinstance(report, ValidationReport)
        assert report.is_valid is True
        assert len(report.errors) == 0
        assert report.score > 0.0

    def test_validate_metadata_missing_required_field(self, verifier, valid_metadata):
        """Test validation fails with missing required field."""
        # Remove required field
        del valid_metadata["source"]["datasetName"]

        report = verifier.validate_metadata(valid_metadata)

        assert report.is_valid is False
        assert len(report.errors) > 0
        assert any("datasetName" in error for error in report.errors)

    def test_validate_metadata_missing_source(self, verifier, valid_metadata):
        """Test validation fails with missing source section."""
        del valid_metadata["source"]

        report = verifier.validate_metadata(valid_metadata)

        assert report.is_valid is False
        assert len(report.errors) > 0

    def test_validate_metadata_missing_provenance(self, verifier, valid_metadata):
        """Test validation fails with missing provenance section."""
        del valid_metadata["provenance"]

        report = verifier.validate_metadata(valid_metadata)

        assert report.is_valid is False
        assert len(report.errors) > 0

    def test_validate_metadata_missing_use(self, verifier, valid_metadata):
        """Test validation fails with missing use section."""
        del valid_metadata["use"]

        report = verifier.validate_metadata(valid_metadata)

        assert report.is_valid is False
        assert len(report.errors) > 0

    def test_validate_metadata_sensitive_data_without_categories(self, verifier, valid_metadata):
        """Test validation warns when sensitive data lacks categories."""
        valid_metadata["use"]["sensitiveData"] = True
        # Don't add sensitiveDataCategories - should trigger warning

        report = verifier.validate_metadata(valid_metadata)

        # Should have warnings about missing sensitive data categories
        assert len(report.warnings) > 0 or not report.is_valid

    def test_validate_metadata_sensitive_data_without_privacy_measures(self, verifier, valid_metadata):
        """Test validation warns when sensitive data lacks privacy measures."""
        valid_metadata["use"]["sensitiveData"] = True
        valid_metadata["use"]["sensitiveDataCategories"] = ["PII"]
        # Don't add privacyMeasures - should trigger warning

        report = verifier.validate_metadata(valid_metadata)

        # Should have warnings about missing privacy measures
        assert len(report.warnings) > 0 or not report.is_valid

    def test_validate_metadata_with_optional_fields(self, verifier, valid_metadata):
        """Test validation with optional fields included."""
        valid_metadata["source"]["datasetURI"] = "https://example.com/dataset"
        valid_metadata["source"]["providerWebsite"] = "https://example.com"
        valid_metadata["provenance"]["qualityIndicators"] = {
            "completeness": 0.95,
            "accuracy": 0.98
        }

        report = verifier.validate_metadata(valid_metadata)

        assert report.is_valid is True
        assert report.score > 0.0

    def test_validate_metadata_empty_dict(self, verifier):
        """Test validation of empty metadata."""
        report = verifier.validate_metadata({})

        assert report.is_valid is False
        assert len(report.errors) > 0

    def test_validation_report_score_calculation(self, verifier, valid_metadata):
        """Test that validation score is calculated correctly."""
        report = verifier.validate_metadata(valid_metadata)

        assert 0.0 <= report.score <= 1.0
        assert report.score > 0.5  # Should be high for valid metadata

    def test_validation_report_string_representation(self, verifier, valid_metadata):
        """Test ValidationReport string representation."""
        report = verifier.validate_metadata(valid_metadata)
        report_str = str(report)

        assert "DTA Standards Validation" in report_str
        assert "Compliance Score" in report_str
        if report.is_valid:
            assert "✅ VALID" in report_str
        else:
            assert "❌ INVALID" in report_str

    def test_validation_report_with_errors(self, verifier, valid_metadata):
        """Test ValidationReport string includes errors."""
        del valid_metadata["source"]["datasetName"]
        report = verifier.validate_metadata(valid_metadata)
        report_str = str(report)

        if report.errors:
            assert "Errors:" in report_str
            assert "❌" in report_str

    def test_validation_report_with_warnings(self, verifier, valid_metadata):
        """Test ValidationReport string includes warnings."""
        valid_metadata["use"]["sensitiveData"] = True
        report = verifier.validate_metadata(valid_metadata)
        report_str = str(report)

        if report.warnings:
            assert "Warnings:" in report_str or "⚠️" in report_str

    def test_validation_report_with_missing_optional(self, verifier, valid_metadata):
        """Test ValidationReport string includes missing optional fields."""
        report = verifier.validate_metadata(valid_metadata)
        report_str = str(report)

        if report.missing_optional_fields:
            assert "Missing Optional Fields" in report_str or "ℹ️" in report_str

    def test_verify_git_commit_integrity(self, verifier, temp_git_repo, valid_metadata):
        """Test verification of git commit integrity."""
        # Create tracker and commit
        tracker = ProvenanceTracker(temp_git_repo)

        # Create a test file
        test_file = temp_git_repo / "data.csv"
        test_file.write_text("test,data\n1,2\n")

        metadata = ProvenanceMetadata(**valid_metadata)
        commit_hash = tracker.commit_with_provenance(
            [test_file],
            metadata,
            "Test commit"
        )

        # Verify the commit
        is_valid, message = verifier.verify_commit_integrity(temp_git_repo, commit_hash)

        assert is_valid is True
        assert "valid" in message.lower()

    def test_verify_nonexistent_commit(self, verifier, temp_git_repo):
        """Test verification of non-existent commit."""
        is_valid, message = verifier.verify_commit_integrity(
            temp_git_repo,
            "0" * 40  # Invalid commit hash
        )

        assert is_valid is False
        assert "not found" in message.lower() or "error" in message.lower()

    def test_validate_metadata_file(self, verifier, valid_metadata, tmp_path):
        """Test validation of metadata from file."""
        metadata_file = tmp_path / "metadata.json"
        metadata_file.write_text(json.dumps(valid_metadata))

        report = verifier.validate_metadata_file(metadata_file)

        assert isinstance(report, ValidationReport)
        assert report.is_valid is True

    def test_validate_metadata_file_invalid_json(self, verifier, tmp_path):
        """Test validation of invalid JSON file."""
        metadata_file = tmp_path / "invalid.json"
        metadata_file.write_text("{ invalid json }")

        with pytest.raises(json.JSONDecodeError):
            verifier.validate_metadata_file(metadata_file)

    def test_validate_metadata_file_not_found(self, verifier, tmp_path):
        """Test validation of non-existent file."""
        metadata_file = tmp_path / "nonexistent.json"

        with pytest.raises(FileNotFoundError):
            verifier.validate_metadata_file(metadata_file)


class TestValidationReport:
    """Test suite for ValidationReport class."""

    def test_validation_report_creation(self):
        """Test creating a ValidationReport."""
        report = ValidationReport(
            is_valid=True,
            errors=[],
            warnings=["Test warning"],
            missing_optional_fields=["datasetURI"],
            score=0.85
        )

        assert report.is_valid is True
        assert len(report.warnings) == 1
        assert len(report.missing_optional_fields) == 1
        assert report.score == 0.85

    def test_validation_report_invalid(self):
        """Test creating an invalid ValidationReport."""
        report = ValidationReport(
            is_valid=False,
            errors=["Missing required field"],
            warnings=[],
            missing_optional_fields=[],
            score=0.3
        )

        assert report.is_valid is False
        assert len(report.errors) == 1
        assert report.score == 0.3

    def test_validation_report_str_valid(self):
        """Test string representation of valid report."""
        report = ValidationReport(
            is_valid=True,
            errors=[],
            warnings=[],
            missing_optional_fields=[],
            score=0.95
        )

        report_str = str(report)
        assert "✅ VALID" in report_str
        assert "95.0%" in report_str

    def test_validation_report_str_invalid(self):
        """Test string representation of invalid report."""
        report = ValidationReport(
            is_valid=False,
            errors=["Critical error"],
            warnings=["Minor warning"],
            missing_optional_fields=["field1"],
            score=0.25
        )

        report_str = str(report)
        assert "❌ INVALID" in report_str
        assert "25.0%" in report_str
        assert "Critical error" in report_str

    def test_validation_report_perfect_score(self):
        """Test report with perfect score."""
        report = ValidationReport(
            is_valid=True,
            errors=[],
            warnings=[],
            missing_optional_fields=[],
            score=1.0
        )

        assert report.score == 1.0
        assert "100.0%" in str(report)

    def test_validation_report_zero_score(self):
        """Test report with zero score."""
        report = ValidationReport(
            is_valid=False,
            errors=["Multiple", "Critical", "Errors"],
            warnings=[],
            missing_optional_fields=[],
            score=0.0
        )

        assert report.score == 0.0
        assert "0.0%" in str(report)
