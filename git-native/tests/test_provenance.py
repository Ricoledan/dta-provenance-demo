"""
Test suite for provenance tracking.

Uses pytest with fixtures and parametrization for thorough coverage.
"""

import pytest
from pathlib import Path
import json
import tempfile
import shutil

import git

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.provenance import (
    ProvenanceTracker,
    ProvenanceMetadata,
    save_provenance_file,
    load_provenance_file
)


@pytest.fixture
def sample_metadata():
    """Fixture providing valid DTA metadata."""
    return ProvenanceMetadata(
        source={
            "datasetName": "Test Dataset",
            "datasetVersion": "1.0.0",
            "providerName": "Test Provider",
            "providerWebsite": "https://example.com",
        },
        provenance={
            "dataGenerationMethod": "Test method",
            "dateDataGenerated": "2024-01-01T00:00:00Z",
            "dataType": "Tabular",
            "dataFormat": "CSV",
            "dataSubjectivity": "Objective"
        },
        use={
            "intendedUse": "Testing purposes",
            "legalRightsToUse": "Test license",
            "sensitiveData": False,
            "sensitiveDataCategories": []
        }
    )


@pytest.fixture
def temp_git_repo(tmp_path):
    """Fixture providing temporary Git repository."""
    repo_path = tmp_path / "test_repo"
    repo_path.mkdir()

    # Initialize git repo
    repo = git.Repo.init(repo_path)

    # Configure git (required for commits)
    with repo.config_writer() as config:
        config.set_value("user", "name", "Test User")
        config.set_value("user", "email", "test@example.com")

    # Create initial commit
    test_file = repo_path / "README.md"
    test_file.write_text("# Test Repository")
    repo.index.add(["README.md"])
    repo.index.commit("Initial commit")

    yield repo_path

    # Cleanup is automatic with tmp_path


def test_provenance_metadata_creation(sample_metadata):
    """Test creating ProvenanceMetadata."""
    assert sample_metadata.source["datasetName"] == "Test Dataset"
    assert sample_metadata.provenance["dataType"] == "Tabular"
    assert sample_metadata.use["sensitiveData"] is False


def test_provenance_metadata_required_fields():
    """Test validation fails for missing required fields."""
    # Missing required source field
    with pytest.raises(ValueError, match="Missing required source field"):
        ProvenanceMetadata(
            source={"providerName": "Test"},  # Missing datasetName
            provenance={
                "dataGenerationMethod": "Test",
                "dateDataGenerated": "2024-01-01T00:00:00Z",
                "dataType": "Tabular",
                "dataFormat": "CSV"
            },
            use={
                "intendedUse": "Test",
                "legalRightsToUse": "Test",
                "sensitiveData": False
            }
        )


def test_provenance_metadata_sensitive_data_validation():
    """Test validation requires categories when sensitiveData=True."""
    with pytest.raises(ValueError, match="sensitiveDataCategories"):
        ProvenanceMetadata(
            source={"datasetName": "Test", "providerName": "Test"},
            provenance={
                "dataGenerationMethod": "Test",
                "dateDataGenerated": "2024-01-01T00:00:00Z",
                "dataType": "Tabular",
                "dataFormat": "CSV"
            },
            use={
                "intendedUse": "Test",
                "legalRightsToUse": "Test",
                "sensitiveData": True  # Missing sensitiveDataCategories
            }
        )


def test_metadata_hash_consistency(sample_metadata):
    """Test that metadata hash is deterministic."""
    hash1 = sample_metadata.compute_hash()
    hash2 = sample_metadata.compute_hash()
    assert hash1 == hash2
    assert len(hash1) == 64  # SHA-256 hex digest length


def test_metadata_hash_uniqueness(sample_metadata):
    """Test that different metadata produces different hashes."""
    hash1 = sample_metadata.compute_hash()

    # Modify metadata
    sample_metadata.source["datasetVersion"] = "2.0.0"
    hash2 = sample_metadata.compute_hash()

    assert hash1 != hash2


def test_metadata_to_dict(sample_metadata):
    """Test converting metadata to dictionary."""
    data = sample_metadata.to_dict()

    assert "source" in data
    assert "provenance" in data
    assert "use" in data
    assert data["source"]["datasetName"] == "Test Dataset"


def test_metadata_from_dict(sample_metadata):
    """Test creating metadata from dictionary."""
    data = sample_metadata.to_dict()
    metadata = ProvenanceMetadata.from_dict(data)

    assert metadata.source["datasetName"] == sample_metadata.source["datasetName"]
    assert metadata.provenance["dataType"] == sample_metadata.provenance["dataType"]


def test_save_and_load_provenance_file(sample_metadata, tmp_path):
    """Test saving and loading provenance JSON files."""
    file_path = tmp_path / "provenance.json"

    # Save
    save_provenance_file(sample_metadata, file_path)
    assert file_path.exists()

    # Load
    loaded_metadata = load_provenance_file(file_path)
    assert loaded_metadata.source["datasetName"] == sample_metadata.source["datasetName"]


def test_tracker_initialization(temp_git_repo):
    """Test ProvenanceTracker initialization."""
    tracker = ProvenanceTracker(temp_git_repo)
    assert tracker.repo_path == temp_git_repo
    assert isinstance(tracker.repo, git.Repo)


def test_tracker_initialization_invalid_repo(tmp_path):
    """Test tracker fails with non-git directory."""
    non_repo = tmp_path / "not_a_repo"
    non_repo.mkdir()

    with pytest.raises(git.exc.InvalidGitRepositoryError):
        ProvenanceTracker(non_repo)


def test_commit_with_provenance(temp_git_repo, sample_metadata):
    """Test creating commits with provenance metadata."""
    tracker = ProvenanceTracker(temp_git_repo)

    # Create a test file
    test_file = temp_git_repo / "dataset.csv"
    test_file.write_text("col1,col2\n1,2\n3,4\n")

    # Commit with provenance
    commit_hash = tracker.commit_with_provenance(
        file_paths=[Path("dataset.csv")],
        metadata=sample_metadata,
        message="Add test dataset"
    )

    assert len(commit_hash) == 40  # Git SHA-1 hash length
    assert commit_hash == tracker.repo.head.commit.hexsha


def test_commit_with_nonexistent_file(temp_git_repo, sample_metadata):
    """Test committing nonexistent file fails."""
    tracker = ProvenanceTracker(temp_git_repo)

    with pytest.raises(ValueError, match="File not found"):
        tracker.commit_with_provenance(
            file_paths=[Path("nonexistent.csv")],
            metadata=sample_metadata,
            message="This should fail"
        )


def test_read_provenance(temp_git_repo, sample_metadata):
    """Test reading provenance from commits."""
    tracker = ProvenanceTracker(temp_git_repo)

    # Create commit with provenance
    test_file = temp_git_repo / "dataset.csv"
    test_file.write_text("data")
    commit_hash = tracker.commit_with_provenance(
        file_paths=[Path("dataset.csv")],
        metadata=sample_metadata,
        message="Test commit"
    )

    # Read back
    read_metadata = tracker.read_provenance(commit_hash)
    assert read_metadata is not None
    assert read_metadata.source["datasetName"] == sample_metadata.source["datasetName"]


def test_read_provenance_no_metadata(temp_git_repo):
    """Test reading from commit without provenance."""
    tracker = ProvenanceTracker(temp_git_repo)

    # Use initial commit (has no provenance)
    initial_commit = tracker.repo.head.commit
    metadata = tracker.read_provenance(initial_commit.hexsha)

    assert metadata is None


def test_verify_integrity(temp_git_repo, sample_metadata):
    """Test integrity verification."""
    tracker = ProvenanceTracker(temp_git_repo)

    # Create commit with provenance
    test_file = temp_git_repo / "dataset.csv"
    test_file.write_text("data")
    commit_hash = tracker.commit_with_provenance(
        file_paths=[Path("dataset.csv")],
        metadata=sample_metadata,
        message="Test commit"
    )

    # Verify
    is_valid, message = tracker.verify_integrity(commit_hash)
    assert is_valid
    assert "verified" in message.lower()


def test_generate_audit_trail(temp_git_repo, sample_metadata):
    """Test generating audit trail."""
    tracker = ProvenanceTracker(temp_git_repo)

    # Create multiple commits
    test_file = temp_git_repo / "dataset.csv"

    for version in ["v1", "v2", "v3"]:
        test_file.write_text(f"data_{version}")
        sample_metadata.source["datasetVersion"] = version
        tracker.commit_with_provenance(
            file_paths=[Path("dataset.csv")],
            metadata=sample_metadata,
            message=f"Update to {version}"
        )

    # Generate audit trail
    trail = tracker.generate_audit_trail(Path("dataset.csv"))

    assert len(trail) == 3
    assert all("commit_hash" in record for record in trail)
    assert all("provenance" in record for record in trail)
    assert all("author" in record for record in trail)


def test_audit_trail_max_commits(temp_git_repo, sample_metadata):
    """Test audit trail respects max_commits parameter."""
    tracker = ProvenanceTracker(temp_git_repo)

    test_file = temp_git_repo / "dataset.csv"

    # Create 5 commits
    for i in range(5):
        test_file.write_text(f"data_{i}")
        tracker.commit_with_provenance(
            file_paths=[Path("dataset.csv")],
            metadata=sample_metadata,
            message=f"Commit {i}"
        )

    # Get only 3
    trail = tracker.generate_audit_trail(Path("dataset.csv"), max_commits=3)
    assert len(trail) == 3


@pytest.mark.parametrize("field,category", [
    ("datasetName", "source"),
    ("providerName", "source"),
    ("dataGenerationMethod", "provenance"),
    ("dataType", "provenance"),
    ("intendedUse", "use"),
])
def test_required_fields_validation(field, category):
    """Test validation fails for missing required fields."""
    valid_data = {
        "source": {
            "datasetName": "Test",
            "providerName": "Test"
        },
        "provenance": {
            "dataGenerationMethod": "Test",
            "dateDataGenerated": "2024-01-01T00:00:00Z",
            "dataType": "Tabular",
            "dataFormat": "CSV"
        },
        "use": {
            "intendedUse": "Test",
            "legalRightsToUse": "Test",
            "sensitiveData": False
        }
    }

    # Remove the field
    del valid_data[category][field]

    with pytest.raises(ValueError, match=f"Missing required.*{field}"):
        ProvenanceMetadata.from_dict(valid_data)


def test_metadata_with_extra_fields(sample_metadata):
    """Test metadata handles extra fields gracefully."""
    data = sample_metadata.to_dict()
    data["customField"] = "customValue"

    metadata = ProvenanceMetadata.from_dict(data)
    assert metadata.metadata.get("customField") == "customValue"


def test_commit_message_format(temp_git_repo, sample_metadata):
    """Test commit message contains DTA trailers."""
    tracker = ProvenanceTracker(temp_git_repo)

    test_file = temp_git_repo / "dataset.csv"
    test_file.write_text("data")
    commit_hash = tracker.commit_with_provenance(
        file_paths=[Path("dataset.csv")],
        metadata=sample_metadata,
        message="Test message"
    )

    commit = tracker.repo.commit(commit_hash)
    message = commit.message

    assert "DTA-Provenance-Version: 1.0.0" in message
    assert "DTA-Provenance-Hash:" in message
    assert "DTA-Dataset-Name:" in message
    assert "DTA-Provenance-Metadata:" in message
