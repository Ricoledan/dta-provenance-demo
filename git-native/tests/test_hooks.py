"""
Tests for pre-commit hooks.
"""

import json
import pytest
from pathlib import Path
from src.hooks import validate_metadata_hook, check_trailers_hook


@pytest.fixture
def valid_provenance_json(tmp_path):
    """Create a valid DTA provenance JSON file."""
    metadata = {
        "source": {
            "datasetName": "Test Dataset",
            "providerName": "Test Provider"
        },
        "provenance": {
            "dataGenerationMethod": "Manual entry",
            "dateDataGenerated": "2024-01-15",
            "dataType": "Text",
            "dataFormat": "CSV"
        },
        "use": {
            "intendedUse": "Testing",
            "legalRightsToUse": "MIT License",
            "sensitiveData": False
        }
    }

    file_path = tmp_path / "valid_provenance.json"
    with open(file_path, 'w') as f:
        json.dump(metadata, f, indent=2)

    return file_path


@pytest.fixture
def invalid_provenance_json(tmp_path):
    """Create an invalid DTA provenance JSON file (missing required fields)."""
    metadata = {
        "source": {
            "datasetName": "Test Dataset"
            # Missing providerName
        },
        "provenance": {
            "dataGenerationMethod": "Manual entry",
            "dateDataGenerated": "2024-01-15",
            # Missing dataType and dataFormat
        },
        "use": {
            "intendedUse": "Testing"
            # Missing legalRightsToUse and sensitiveData
        }
    }

    file_path = tmp_path / "invalid_provenance.json"
    with open(file_path, 'w') as f:
        json.dump(metadata, f, indent=2)

    return file_path


@pytest.fixture
def non_provenance_json(tmp_path):
    """Create a non-provenance JSON file (should be ignored)."""
    data = {
        "name": "Some Config",
        "version": "1.0.0",
        "settings": {
            "debug": True
        }
    }

    file_path = tmp_path / "config.json"
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=2)

    return file_path


@pytest.fixture
def valid_commit_msg(tmp_path):
    """Create a valid commit message with DTA trailers."""
    message = """Add training dataset

DTA-Provenance-Version: 1.0.0
DTA-Provenance-Hash: abc123def456
DTA-Dataset-Name: Test Dataset
DTA-Provenance-Metadata: {"source":{"datasetName":"Test Dataset","providerName":"Test Provider"},"provenance":{"dataGenerationMethod":"Manual","dateDataGenerated":"2024-01-15","dataType":"Text","dataFormat":"CSV"},"use":{"intendedUse":"Testing","legalRightsToUse":"MIT","sensitiveData":false}}
"""

    file_path = tmp_path / "COMMIT_EDITMSG"
    with open(file_path, 'w') as f:
        f.write(message)

    return file_path


@pytest.fixture
def commit_msg_missing_trailers(tmp_path):
    """Create commit message with metadata but missing trailers."""
    message = """Add training dataset

DTA-Provenance-Metadata: {"source":{"datasetName":"Test"},"provenance":{"dataGenerationMethod":"Manual","dateDataGenerated":"2024-01-15","dataType":"Text","dataFormat":"CSV"},"use":{"intendedUse":"Testing","legalRightsToUse":"MIT","sensitiveData":false}}
"""

    file_path = tmp_path / "COMMIT_EDITMSG"
    with open(file_path, 'w') as f:
        f.write(message)

    return file_path


@pytest.fixture
def commit_msg_no_provenance(tmp_path):
    """Create regular commit message without provenance."""
    message = """Fix bug in parser

This commit fixes the parser logic for edge cases.
"""

    file_path = tmp_path / "COMMIT_EDITMSG"
    with open(file_path, 'w') as f:
        f.write(message)

    return file_path


class TestValidateMetadataHook:
    """Tests for validate_metadata_hook."""

    def test_valid_provenance_file(self, valid_provenance_json):
        """Valid provenance file should pass."""
        result = validate_metadata_hook([str(valid_provenance_json)])
        assert result == 0

    def test_invalid_provenance_file(self, invalid_provenance_json):
        """Invalid provenance file should fail."""
        result = validate_metadata_hook([str(invalid_provenance_json)])
        assert result == 1

    def test_non_provenance_json_ignored(self, non_provenance_json):
        """Non-provenance JSON files should be ignored."""
        result = validate_metadata_hook([str(non_provenance_json)])
        assert result == 0

    def test_mixed_files(self, valid_provenance_json, non_provenance_json):
        """Mix of provenance and non-provenance files."""
        result = validate_metadata_hook([
            str(valid_provenance_json),
            str(non_provenance_json)
        ])
        assert result == 0

    def test_empty_file_list(self):
        """Empty file list should pass."""
        result = validate_metadata_hook([])
        assert result == 0

    def test_non_json_file_ignored(self, tmp_path):
        """Non-JSON files should be ignored."""
        text_file = tmp_path / "readme.txt"
        text_file.write_text("This is not JSON")

        result = validate_metadata_hook([str(text_file)])
        assert result == 0

    def test_malformed_json(self, tmp_path):
        """Malformed JSON should fail."""
        bad_json = tmp_path / "bad.json"
        bad_json.write_text('{"source": {incomplete')

        result = validate_metadata_hook([str(bad_json)])
        assert result == 1


class TestCheckTrailersHook:
    """Tests for check_trailers_hook."""

    def test_valid_commit_with_trailers(self, valid_commit_msg):
        """Commit with all required trailers should pass."""
        result = check_trailers_hook([str(valid_commit_msg)])
        assert result == 0

    def test_commit_missing_trailers(self, commit_msg_missing_trailers):
        """Commit with metadata but missing trailers should fail."""
        result = check_trailers_hook([str(commit_msg_missing_trailers)])
        assert result == 1

    def test_commit_without_provenance(self, commit_msg_no_provenance):
        """Regular commit without provenance should pass."""
        result = check_trailers_hook([str(commit_msg_no_provenance)])
        assert result == 0

    def test_no_arguments(self):
        """No arguments should fail gracefully."""
        result = check_trailers_hook([])
        assert result == 1

    def test_nonexistent_file(self):
        """Non-existent file should fail gracefully."""
        result = check_trailers_hook(["/nonexistent/path/to/file"])
        assert result == 1

    def test_malformed_metadata_json(self, tmp_path):
        """Commit with malformed metadata JSON should fail."""
        message = """Add dataset

DTA-Provenance-Version: 1.0.0
DTA-Provenance-Hash: abc123
DTA-Dataset-Name: Test
DTA-Provenance-Metadata: {invalid json}
"""
        file_path = tmp_path / "COMMIT_EDITMSG"
        file_path.write_text(message)

        result = check_trailers_hook([str(file_path)])
        assert result == 1

    def test_incomplete_metadata_structure(self, tmp_path):
        """Commit with incomplete metadata structure should fail."""
        message = """Add dataset

DTA-Provenance-Version: 1.0.0
DTA-Provenance-Hash: abc123
DTA-Dataset-Name: Test
DTA-Provenance-Metadata: {"source":{"datasetName":"Test"}}
"""
        file_path = tmp_path / "COMMIT_EDITMSG"
        file_path.write_text(message)

        result = check_trailers_hook([str(file_path)])
        assert result == 1
