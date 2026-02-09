"""
Tests for SBOM integration.

Uses mocked CycloneDX operations to avoid requiring actual CycloneDX installation.
"""

import pytest
import json
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock, create_autospec


# Mock CycloneDX modules before any imports
sys.modules['cyclonedx'] = MagicMock()
sys.modules['cyclonedx.model'] = MagicMock()
sys.modules['cyclonedx.model.bom'] = MagicMock()
sys.modules['cyclonedx.model.component'] = MagicMock()
sys.modules['cyclonedx.output'] = MagicMock()


@pytest.fixture
def mock_cyclonedx_available():
    """Mock CycloneDX as available."""
    with patch('src.integrations.sbom_integration.CYCLONEDX_AVAILABLE', True):
        yield


@pytest.fixture
def test_repo(tmp_path):
    """Create a test repository."""
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
def sample_sbom_data():
    """Sample SBOM file content."""
    return {
        "bomFormat": "CycloneDX",
        "specVersion": "1.5",
        "serialNumber": "urn:uuid:test-123",
        "version": 1,
        "components": [
            {
                "type": "library",
                "name": "requests",
                "version": "2.31.0",
                "licenses": [
                    {
                        "license": {
                            "id": "Apache-2.0"
                        }
                    }
                ]
            },
            {
                "type": "library",
                "name": "numpy",
                "version": "1.24.0",
                "licenses": [
                    {
                        "license": {
                            "id": "BSD-3-Clause"
                        }
                    }
                ]
            }
        ]
    }


class TestSBOMProvenanceBridge:
    """Tests for SBOMProvenanceBridge class."""

    def test_init_success(self, test_repo, mock_cyclonedx_available):
        """Initialize bridge successfully."""
        from src.integrations.sbom_integration import SBOMProvenanceBridge

        bridge = SBOMProvenanceBridge(test_repo)
        assert bridge.repo_path == test_repo

    def test_init_no_cyclonedx(self, test_repo):
        """Initialize bridge without CycloneDX should fail."""
        with patch('src.integrations.sbom_integration.CYCLONEDX_AVAILABLE', False):
            from src.integrations.sbom_integration import SBOMProvenanceBridge

            with pytest.raises(ImportError, match="cyclonedx-bom is not installed"):
                SBOMProvenanceBridge(test_repo)

    @patch('subprocess.run')
    def test_generate_sbom(self, mock_run, test_repo, mock_cyclonedx_available):
        """Generate SBOM for Python project."""
        from src.integrations.sbom_integration import SBOMProvenanceBridge

        # Mock pip list output
        mock_run.return_value = Mock(
            returncode=0,
            stdout=json.dumps([
                {"name": "requests", "version": "2.31.0"},
                {"name": "numpy", "version": "1.24.0"}
            ]),
            stderr=''
        )

        # Mock BOM and outputter
        from cyclonedx.model.bom import Bom
        from cyclonedx.output import get_instance

        mock_bom_instance = MagicMock()
        mock_bom_instance.components = MagicMock()
        Bom.return_value = mock_bom_instance

        mock_outputter = MagicMock()
        mock_outputter.output_as_string.return_value = '{"bomFormat": "CycloneDX"}'
        get_instance.return_value = mock_outputter

        bridge = SBOMProvenanceBridge(test_repo)
        sbom_path = bridge.generate_sbom("test-project", "1.0.0")

        # Verify subprocess was called
        mock_run.assert_called_once()
        assert 'pip' in mock_run.call_args[0][0]
        assert 'list' in mock_run.call_args[0][0]

        # Verify output file exists
        assert sbom_path.exists()
        assert sbom_path == test_repo / 'sbom.json'

    def test_link_sbom_to_provenance(
        self,
        test_repo,
        sample_metadata,
        sample_sbom_data,
        mock_cyclonedx_available
    ):
        """Link SBOM file to provenance metadata."""
        from src.integrations.sbom_integration import SBOMProvenanceBridge

        # Create SBOM file
        sbom_file = test_repo / 'sbom.json'
        sbom_file.write_text(json.dumps(sample_sbom_data))

        bridge = SBOMProvenanceBridge(test_repo)
        enriched = bridge.link_sbom_to_provenance(Path('sbom.json'), sample_metadata)

        # Verify enrichment
        assert 'metadata' in enriched
        assert 'sbom' in enriched['metadata']
        assert enriched['metadata']['sbom']['format'] == 'CycloneDX'
        assert enriched['metadata']['sbom']['version'] == '1.5'
        assert enriched['metadata']['sbom']['sbom_file'] == 'sbom.json'
        assert enriched['metadata']['sbom']['dependency_count'] == 2
        assert enriched['metadata']['sbom']['serial_number'] == 'urn:uuid:test-123'

    def test_link_sbom_nonexistent_file(
        self,
        test_repo,
        sample_metadata,
        mock_cyclonedx_available
    ):
        """Link SBOM when file doesn't exist should fail."""
        from src.integrations.sbom_integration import SBOMProvenanceBridge

        bridge = SBOMProvenanceBridge(test_repo)

        with pytest.raises(FileNotFoundError, match="SBOM file not found"):
            bridge.link_sbom_to_provenance(Path('nonexistent.json'), sample_metadata)

    def test_extract_dependency_info(
        self,
        test_repo,
        sample_sbom_data,
        mock_cyclonedx_available
    ):
        """Extract dependency information from SBOM."""
        from src.integrations.sbom_integration import SBOMProvenanceBridge

        # Create SBOM file
        sbom_file = test_repo / 'sbom.json'
        sbom_file.write_text(json.dumps(sample_sbom_data))

        bridge = SBOMProvenanceBridge(test_repo)
        info = bridge.extract_dependency_info(Path('sbom.json'))

        # Verify extracted info
        assert info['total_dependencies'] == 2
        assert len(info['dependencies']) == 2

        # Check first dependency
        assert info['dependencies'][0]['name'] == 'requests'
        assert info['dependencies'][0]['version'] == '2.31.0'
        assert info['dependencies'][0]['type'] == 'library'

        # Check licenses
        assert 'Apache-2.0' in info['licenses']
        assert 'BSD-3-Clause' in info['licenses']

        # Check by_type
        assert info['by_type']['library'] == 2

    def test_extract_dependency_info_nonexistent(
        self,
        test_repo,
        mock_cyclonedx_available
    ):
        """Extract dependency info from nonexistent file should fail."""
        from src.integrations.sbom_integration import SBOMProvenanceBridge

        bridge = SBOMProvenanceBridge(test_repo)

        with pytest.raises(FileNotFoundError, match="SBOM file not found"):
            bridge.extract_dependency_info(Path('nonexistent.json'))

    @patch('subprocess.run')
    def test_generate_and_link(
        self,
        mock_run,
        test_repo,
        sample_metadata,
        sample_sbom_data,
        mock_cyclonedx_available
    ):
        """Generate SBOM and link to provenance in one step."""
        from src.integrations.sbom_integration import SBOMProvenanceBridge

        # Mock pip list output
        mock_run.return_value = Mock(
            returncode=0,
            stdout=json.dumps([
                {"name": "requests", "version": "2.31.0"}
            ]),
            stderr=''
        )

        # Mock BOM and outputter
        from cyclonedx.model.bom import Bom
        from cyclonedx.output import get_instance

        mock_bom_instance = MagicMock()
        mock_bom_instance.components = MagicMock()
        Bom.return_value = mock_bom_instance

        mock_outputter = MagicMock()
        mock_outputter.output_as_string.return_value = json.dumps(sample_sbom_data)
        get_instance.return_value = mock_outputter

        bridge = SBOMProvenanceBridge(test_repo)
        sbom_path, enriched = bridge.generate_and_link(
            "test-project",
            "1.0.0",
            sample_metadata
        )

        # Verify SBOM was created
        assert sbom_path.exists()

        # Verify metadata was enriched
        assert 'metadata' in enriched
        assert 'sbom' in enriched['metadata']
        assert enriched['metadata']['sbom']['format'] == 'CycloneDX'

    @patch('subprocess.run')
    def test_generate_sbom_custom_output(
        self,
        mock_run,
        test_repo,
        mock_cyclonedx_available
    ):
        """Generate SBOM with custom output path."""
        from src.integrations.sbom_integration import SBOMProvenanceBridge

        # Setup mocks
        mock_run.return_value = Mock(
            returncode=0,
            stdout=json.dumps([{"name": "test", "version": "1.0"}]),
            stderr=''
        )

        # Mock BOM and outputter
        from cyclonedx.model.bom import Bom
        from cyclonedx.output import get_instance

        mock_bom_instance = MagicMock()
        mock_bom_instance.components = MagicMock()
        Bom.return_value = mock_bom_instance

        mock_outputter = MagicMock()
        mock_outputter.output_as_string.return_value = '{}'
        get_instance.return_value = mock_outputter

        bridge = SBOMProvenanceBridge(test_repo)
        custom_output = test_repo / 'custom' / 'sbom.json'
        sbom_path = bridge.generate_sbom(
            "test-project",
            "1.0.0",
            custom_output
        )

        assert sbom_path == custom_output
        assert sbom_path.exists()


def test_is_cyclonedx_available_true():
    """Test CycloneDX availability check when installed."""
    with patch('src.integrations.sbom_integration.CYCLONEDX_AVAILABLE', True):
        from src.integrations.sbom_integration import is_cyclonedx_available
        assert is_cyclonedx_available() is True


def test_is_cyclonedx_available_false():
    """Test CycloneDX availability check when not installed."""
    with patch('src.integrations.sbom_integration.CYCLONEDX_AVAILABLE', False):
        from src.integrations.sbom_integration import is_cyclonedx_available
        assert is_cyclonedx_available() is False


def test_import_without_cyclonedx():
    """Test that module can be imported even without CycloneDX."""
    with patch('src.integrations.sbom_integration.CYCLONEDX_AVAILABLE', False):
        from src.integrations.sbom_integration import SBOMProvenanceBridge

        # Should be importable but fail on instantiation
        with pytest.raises(ImportError, match="cyclonedx-bom is not installed"):
            SBOMProvenanceBridge(Path('/tmp'))
