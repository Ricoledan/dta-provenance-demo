"""
Tests for DVC integration.

Uses mocked DVC operations to avoid requiring actual DVC installation.
"""

import pytest
import json
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import subprocess


@pytest.fixture
def mock_dvc_available():
    """Mock DVC as available."""
    with patch('src.integrations.dvc_integration.DVC_AVAILABLE', True):
        yield


@pytest.fixture
def dvc_repo(tmp_path, mock_dvc_available):
    """Create a mock DVC repository."""
    # Create .dvc directory
    dvc_dir = tmp_path / '.dvc'
    dvc_dir.mkdir()
    (dvc_dir / 'config').touch()

    # Create .git directory
    git_dir = tmp_path / '.git'
    git_dir.mkdir()

    return tmp_path


@pytest.fixture
def sample_metadata():
    """Sample DTA provenance metadata."""
    return {
        "source": {
            "datasetName": "Test Dataset",
            "providerName": "Test Provider"
        },
        "provenance": {
            "dataGenerationMethod": "Automated",
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


@pytest.fixture
def dvc_file_content():
    """Sample .dvc file content."""
    return """outs:
- md5: abc123def456
  size: 1024
  path: data.csv
"""


class TestDVCProvenanceBridge:
    """Tests for DVCProvenanceBridge class."""

    def test_init_success(self, dvc_repo):
        """Initialize bridge with valid DVC repo."""
        from src.integrations.dvc_integration import DVCProvenanceBridge

        bridge = DVCProvenanceBridge(dvc_repo)
        assert bridge.repo_path == dvc_repo

    def test_init_no_dvc(self, tmp_path, mock_dvc_available):
        """Initialize bridge with non-DVC repo should fail."""
        from src.integrations.dvc_integration import DVCProvenanceBridge

        # Create git dir but no .dvc
        (tmp_path / '.git').mkdir()

        with pytest.raises(RuntimeError, match="not a DVC repository"):
            DVCProvenanceBridge(tmp_path)

    @patch('subprocess.run')
    def test_track_dvc_file(self, mock_run, dvc_repo, sample_metadata, dvc_file_content):
        """Track a file with DVC and enrich metadata."""
        from src.integrations.dvc_integration import DVCProvenanceBridge

        # Create test file
        test_file = dvc_repo / 'data.csv'
        test_file.write_text('test,data\n1,2\n')

        # Mock successful dvc add
        mock_run.return_value = Mock(returncode=0, stdout='', stderr='')

        # Create .dvc file
        dvc_file = dvc_repo / 'data.csv.dvc'
        dvc_file.write_text(dvc_file_content)

        bridge = DVCProvenanceBridge(dvc_repo)
        enriched = bridge.track_dvc_file(Path('data.csv'), sample_metadata)

        # Verify dvc add was called
        mock_run.assert_called_once()
        assert 'dvc' in mock_run.call_args[0][0]
        assert 'add' in mock_run.call_args[0][0]

        # Verify metadata enrichment
        assert 'metadata' in enriched
        assert 'dvc' in enriched['metadata']
        assert enriched['metadata']['dvc']['tracked'] is True
        assert enriched['metadata']['dvc']['md5'] == 'abc123def456'
        assert enriched['metadata']['dvc']['size'] == '1024'

    @patch('subprocess.run')
    def test_track_dvc_file_failure(self, mock_run, dvc_repo):
        """Track file with DVC when dvc add fails."""
        from src.integrations.dvc_integration import DVCProvenanceBridge

        # Create test file
        test_file = dvc_repo / 'data.csv'
        test_file.write_text('test,data\n')

        # Mock failed dvc add
        mock_run.return_value = Mock(
            returncode=1,
            stdout='',
            stderr='Error: dvc add failed'
        )

        bridge = DVCProvenanceBridge(dvc_repo)

        with pytest.raises(subprocess.CalledProcessError):
            bridge.track_dvc_file(Path('data.csv'))

    def test_track_nonexistent_file(self, dvc_repo):
        """Track nonexistent file should fail."""
        from src.integrations.dvc_integration import DVCProvenanceBridge

        bridge = DVCProvenanceBridge(dvc_repo)

        with pytest.raises(FileNotFoundError):
            bridge.track_dvc_file(Path('nonexistent.csv'))

    def test_enrich_metadata_from_dvc(self, dvc_repo, sample_metadata, dvc_file_content):
        """Enrich metadata from existing DVC tracking."""
        from src.integrations.dvc_integration import DVCProvenanceBridge

        # Create test file and .dvc file
        test_file = dvc_repo / 'data.csv'
        test_file.write_text('test,data\n')

        dvc_file = dvc_repo / 'data.csv.dvc'
        dvc_file.write_text(dvc_file_content)

        bridge = DVCProvenanceBridge(dvc_repo)
        enriched = bridge.enrich_metadata_from_dvc(Path('data.csv'), sample_metadata)

        # Verify enrichment
        assert 'metadata' in enriched
        assert 'dvc' in enriched['metadata']
        assert enriched['metadata']['dvc']['tracked'] is True
        assert enriched['metadata']['dvc']['md5'] == 'abc123def456'

    def test_enrich_metadata_no_dvc_file(self, dvc_repo, sample_metadata):
        """Enrich metadata when file is not DVC-tracked."""
        from src.integrations.dvc_integration import DVCProvenanceBridge

        # Create test file without .dvc
        test_file = dvc_repo / 'data.csv'
        test_file.write_text('test,data\n')

        bridge = DVCProvenanceBridge(dvc_repo)
        enriched = bridge.enrich_metadata_from_dvc(Path('data.csv'), sample_metadata)

        # Should return unchanged
        assert enriched == sample_metadata

    def test_read_dvc_provenance(self, dvc_repo, dvc_file_content):
        """Read DVC metadata for tracked file."""
        from src.integrations.dvc_integration import DVCProvenanceBridge

        # Create test file and .dvc file
        test_file = dvc_repo / 'data.csv'
        test_file.write_text('test,data\n')

        dvc_file = dvc_repo / 'data.csv.dvc'
        dvc_file.write_text(dvc_file_content)

        bridge = DVCProvenanceBridge(dvc_repo)
        dvc_metadata = bridge.read_dvc_provenance(Path('data.csv'))

        assert dvc_metadata is not None
        assert dvc_metadata['tracked'] is True
        assert 'metadata' in dvc_metadata
        assert dvc_metadata['metadata']['md5'] == 'abc123def456'

    def test_read_dvc_provenance_not_tracked(self, dvc_repo):
        """Read DVC metadata for non-tracked file."""
        from src.integrations.dvc_integration import DVCProvenanceBridge

        # Create test file without .dvc
        test_file = dvc_repo / 'data.csv'
        test_file.write_text('test,data\n')

        bridge = DVCProvenanceBridge(dvc_repo)
        dvc_metadata = bridge.read_dvc_provenance(Path('data.csv'))

        assert dvc_metadata is None

    @patch('subprocess.run')
    def test_get_dvc_status(self, mock_run, dvc_repo):
        """Get DVC status."""
        from src.integrations.dvc_integration import DVCProvenanceBridge

        # Mock dvc status output
        mock_run.return_value = Mock(
            returncode=0,
            stdout='No changes',
            stderr=''
        )

        bridge = DVCProvenanceBridge(dvc_repo)
        status = bridge.get_dvc_status()

        assert status['is_clean'] is True
        assert status['return_code'] == 0
        mock_run.assert_called_once()


def test_is_dvc_available_true():
    """Test DVC availability check when installed."""
    with patch('src.integrations.dvc_integration.DVC_AVAILABLE', True):
        from src.integrations.dvc_integration import is_dvc_available
        assert is_dvc_available() is True


def test_is_dvc_available_false():
    """Test DVC availability check when not installed."""
    with patch('src.integrations.dvc_integration.DVC_AVAILABLE', False):
        from src.integrations.dvc_integration import is_dvc_available
        assert is_dvc_available() is False


def test_import_without_dvc():
    """Test that module can be imported even without DVC."""
    with patch('src.integrations.dvc_integration.DVC_AVAILABLE', False):
        from src.integrations.dvc_integration import DVCProvenanceBridge

        # Should be importable but fail on instantiation
        with pytest.raises(ImportError, match="DVC is not installed"):
            DVCProvenanceBridge(Path('/tmp'))
