"""
Tests for MLflow integration.

Uses mocked MLflow operations to avoid requiring actual MLflow installation.
"""

import pytest
import json
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock, call


@pytest.fixture
def mock_mlflow_available():
    """Mock MLflow as available."""
    with patch('src.integrations.mlflow_integration.MLFLOW_AVAILABLE', True):
        yield


@pytest.fixture
def mlflow_repo(tmp_path, mock_mlflow_available):
    """Create a mock repository for MLflow integration."""
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
            "providerName": "Test Provider",
            "datasetUrl": "https://example.com/dataset",
            "license": "MIT"
        },
        "provenance": {
            "dataGenerationMethod": "Automated",
            "dateDataGenerated": "2024-01-15T00:00:00Z",
            "dataType": "Tabular",
            "dataFormat": "CSV"
        },
        "use": {
            "intendedUse": "ML Training",
            "legalRightsToUse": "MIT License",
            "sensitiveData": False
        }
    }


@pytest.fixture
def mock_mlflow(mock_mlflow_available):
    """Mock MLflow module."""
    # Create mock mlflow module
    mock = MagicMock()

    # Mock active run
    mock_run_info = Mock()
    mock_run_info.run_id = 'test-run-123'

    mock_run = Mock()
    mock_run.info = mock_run_info

    mock.active_run.return_value = mock_run
    mock.get_run.return_value = mock_run
    mock.start_run.return_value.__enter__ = Mock(return_value=mock_run)
    mock.start_run.return_value.__exit__ = Mock(return_value=False)

    # Patch mlflow module in the integration module
    with patch.dict('sys.modules', {'mlflow': mock, 'mlflow.tracking': Mock()}):
        import src.integrations.mlflow_integration
        src.integrations.mlflow_integration.mlflow = mock
        yield mock


class TestMLflowProvenanceBridge:
    """Tests for MLflowProvenanceBridge class."""

    def test_init_success(self, mlflow_repo, mock_mlflow):
        """Initialize bridge successfully."""
        from src.integrations.mlflow_integration import MLflowProvenanceBridge

        bridge = MLflowProvenanceBridge(mlflow_repo)
        assert bridge.repo_path == mlflow_repo

    def test_init_with_tracking_uri(self, mlflow_repo, mock_mlflow):
        """Initialize bridge with custom tracking URI."""
        from src.integrations.mlflow_integration import MLflowProvenanceBridge

        tracking_uri = "http://mlflow-server:5000"
        bridge = MLflowProvenanceBridge(mlflow_repo, tracking_uri=tracking_uri)

        mock_mlflow.set_tracking_uri.assert_called_once_with(tracking_uri)

    def test_init_mlflow_not_available(self, mlflow_repo):
        """Initialize bridge when MLflow is not installed."""
        with patch('src.integrations.mlflow_integration.MLFLOW_AVAILABLE', False):
            from src.integrations.mlflow_integration import MLflowProvenanceBridge

            with pytest.raises(ImportError, match="MLflow is not installed"):
                MLflowProvenanceBridge(mlflow_repo)

    def test_log_provenance_to_mlflow(self, mlflow_repo, mock_mlflow, sample_metadata):
        """Log provenance metadata to MLflow run."""
        from src.integrations.mlflow_integration import MLflowProvenanceBridge

        bridge = MLflowProvenanceBridge(mlflow_repo)
        run_id = bridge.log_provenance_to_mlflow(sample_metadata)

        assert run_id == 'test-run-123'

        # Verify tags were set
        mock_mlflow.set_tag.assert_any_call('dta.source.datasetName', 'Test Dataset')
        mock_mlflow.set_tag.assert_any_call('dta.source.providerName', 'Test Provider')
        mock_mlflow.set_tag.assert_any_call('dta.provenance.dataType', 'Tabular')
        mock_mlflow.set_tag.assert_any_call('dta.provenance.dataFormat', 'CSV')
        mock_mlflow.set_tag.assert_any_call('dta.use.intendedUse', 'ML Training')
        mock_mlflow.set_tag.assert_any_call('dta.use.sensitiveData', 'False')
        mock_mlflow.set_tag.assert_any_call('dta.compliant', 'true')
        mock_mlflow.set_tag.assert_any_call('dta.version', '1.0.0')

        # Verify artifact was logged
        mock_mlflow.log_artifact.assert_called_once()

    def test_log_provenance_with_run_id(self, mlflow_repo, mock_mlflow, sample_metadata):
        """Log provenance to specific run ID."""
        from src.integrations.mlflow_integration import MLflowProvenanceBridge

        bridge = MLflowProvenanceBridge(mlflow_repo)
        run_id = bridge.log_provenance_to_mlflow(sample_metadata, run_id='custom-run-456')

        assert run_id == 'custom-run-456'
        mock_mlflow.get_run.assert_called_once_with('custom-run-456')

    def test_log_provenance_no_active_run(self, mlflow_repo, mock_mlflow, sample_metadata):
        """Log provenance when no active run and no run_id provided."""
        from src.integrations.mlflow_integration import MLflowProvenanceBridge

        mock_mlflow.active_run.return_value = None

        bridge = MLflowProvenanceBridge(mlflow_repo)

        with pytest.raises(RuntimeError, match="No active MLflow run"):
            bridge.log_provenance_to_mlflow(sample_metadata)

    def test_commit_with_mlflow_tracking(self, mlflow_repo, mock_mlflow, sample_metadata):
        """Create commit with MLflow tracking."""
        from src.integrations.mlflow_integration import MLflowProvenanceBridge

        # Mock tracker
        mock_tracker = Mock()
        mock_tracker.commit_with_provenance.return_value = 'abc123def456'

        bridge = MLflowProvenanceBridge(mlflow_repo)

        commit_hash, run_id = bridge.commit_with_mlflow_tracking(
            file_paths=[Path('data.csv')],
            metadata=sample_metadata.copy(),
            message='Test commit',
            tracker=mock_tracker
        )

        assert commit_hash == 'abc123def456'
        assert run_id == 'test-run-123'

        # Verify tracker was called
        mock_tracker.commit_with_provenance.assert_called_once()

        # Verify MLflow tags were set
        mock_mlflow.set_tag.assert_any_call('git.commit_hash', 'abc123def456')
        mock_mlflow.set_tag.assert_any_call('git.commit_message', 'Test commit')

    def test_commit_with_experiment_name(self, mlflow_repo, mock_mlflow, sample_metadata):
        """Create commit with MLflow experiment name."""
        from src.integrations.mlflow_integration import MLflowProvenanceBridge

        mock_tracker = Mock()
        mock_tracker.commit_with_provenance.return_value = 'abc123'

        bridge = MLflowProvenanceBridge(mlflow_repo)

        bridge.commit_with_mlflow_tracking(
            file_paths=[Path('data.csv')],
            metadata=sample_metadata,
            message='Test commit',
            tracker=mock_tracker,
            experiment_name='test-experiment',
            run_name='test-run'
        )

        mock_mlflow.set_experiment.assert_called_once_with('test-experiment')

    def test_read_mlflow_provenance(self, mlflow_repo, mock_mlflow):
        """Read provenance metadata from MLflow run."""
        from src.integrations.mlflow_integration import MLflowProvenanceBridge

        # Mock run with DTA tags
        mock_run_data = Mock()
        mock_run_data.tags = {
            'dta.compliant': 'true',
            'dta.version': '1.0.0',
            'dta.source.datasetName': 'Test Dataset',
            'dta.source.providerName': 'Test Provider',
            'dta.provenance.dataType': 'Tabular',
            'dta.provenance.dataFormat': 'CSV',
            'dta.use.intendedUse': 'ML Training',
            'dta.use.sensitiveData': 'False',
            'git.commit_hash': 'abc123'
        }

        mock_run = Mock()
        mock_run.data = mock_run_data
        mock_mlflow.get_run.return_value = mock_run

        # Mock client with empty artifacts
        mock_client = Mock()
        mock_client.list_artifacts.return_value = []

        with patch('src.integrations.mlflow_integration.mlflow.tracking.MlflowClient',
                   return_value=mock_client):
            bridge = MLflowProvenanceBridge(mlflow_repo)
            metadata = bridge.read_mlflow_provenance('test-run-123')

        assert metadata is not None
        assert metadata['source']['datasetName'] == 'Test Dataset'
        assert metadata['provenance']['dataType'] == 'Tabular'
        assert metadata['use']['sensitiveData'] is False
        assert metadata['metadata']['commit_hash'] == 'abc123'

    def test_read_mlflow_provenance_not_compliant(self, mlflow_repo, mock_mlflow):
        """Read provenance from run without DTA metadata."""
        from src.integrations.mlflow_integration import MLflowProvenanceBridge

        # Mock run without DTA tags
        mock_run_data = Mock()
        mock_run_data.tags = {}

        mock_run = Mock()
        mock_run.data = mock_run_data
        mock_mlflow.get_run.return_value = mock_run

        bridge = MLflowProvenanceBridge(mlflow_repo)
        metadata = bridge.read_mlflow_provenance('test-run-123')

        assert metadata is None

    def test_read_mlflow_provenance_with_artifact(self, mlflow_repo, mock_mlflow, sample_metadata):
        """Read provenance with full metadata from artifact."""
        from src.integrations.mlflow_integration import MLflowProvenanceBridge

        # Mock run
        mock_run_data = Mock()
        mock_run_data.tags = {'dta.compliant': 'true'}
        mock_run = Mock()
        mock_run.data = mock_run_data
        mock_mlflow.get_run.return_value = mock_run

        # Create temp metadata file
        artifact_dir = mlflow_repo / 'artifacts'
        artifact_dir.mkdir()
        metadata_file = artifact_dir / '.mlflow_provenance_temp.json'
        with open(metadata_file, 'w') as f:
            json.dump(sample_metadata, f)

        # Mock client with artifacts
        mock_artifact = Mock()
        mock_client = Mock()
        mock_client.list_artifacts.return_value = [mock_artifact]
        mock_client.download_artifacts.return_value = str(artifact_dir)

        with patch('src.integrations.mlflow_integration.mlflow.tracking.MlflowClient',
                   return_value=mock_client):
            bridge = MLflowProvenanceBridge(mlflow_repo)
            metadata = bridge.read_mlflow_provenance('test-run-123')

        assert metadata is not None
        assert metadata['source']['datasetName'] == 'Test Dataset'
        assert metadata['provenance']['dataType'] == 'Tabular'

    def test_read_mlflow_provenance_error(self, mlflow_repo, mock_mlflow):
        """Handle errors when reading provenance."""
        from src.integrations.mlflow_integration import MLflowProvenanceBridge

        mock_mlflow.get_run.side_effect = Exception("MLflow error")

        bridge = MLflowProvenanceBridge(mlflow_repo)
        metadata = bridge.read_mlflow_provenance('test-run-123')

        assert metadata is None

    def test_get_mlflow_runs_by_dataset(self, mlflow_repo, mock_mlflow):
        """Get all runs that used a specific dataset."""
        from src.integrations.mlflow_integration import MLflowProvenanceBridge

        # Mock runs
        mock_run_info = Mock()
        mock_run_info.run_id = 'run-1'
        mock_run_info.experiment_id = 'exp-1'
        mock_run_info.status = 'FINISHED'
        mock_run_info.start_time = 1000
        mock_run_info.end_time = 2000

        mock_run_data = Mock()
        mock_run_data.tags = {'dta.source.datasetName': 'Test Dataset'}
        mock_run_data.params = {'param1': 'value1'}
        mock_run_data.metrics = {'accuracy': 0.95}

        mock_run = Mock()
        mock_run.info = mock_run_info
        mock_run.data = mock_run_data

        # Mock client
        mock_client = Mock()
        mock_client.search_runs.return_value = [mock_run]

        with patch('src.integrations.mlflow_integration.mlflow.tracking.MlflowClient',
                   return_value=mock_client):
            bridge = MLflowProvenanceBridge(mlflow_repo)
            runs = bridge.get_mlflow_runs_by_dataset('Test Dataset')

        assert len(runs) == 1
        assert runs[0]['run_id'] == 'run-1'
        assert runs[0]['experiment_id'] == 'exp-1'
        assert runs[0]['tags']['dta.source.datasetName'] == 'Test Dataset'

        # Verify filter was used
        mock_client.search_runs.assert_called_once()
        call_kwargs = mock_client.search_runs.call_args[1]
        assert 'Test Dataset' in call_kwargs['filter_string']


def test_is_mlflow_available_true():
    """Test MLflow availability check when installed."""
    with patch('src.integrations.mlflow_integration.MLFLOW_AVAILABLE', True):
        from src.integrations.mlflow_integration import is_mlflow_available
        assert is_mlflow_available() is True


def test_is_mlflow_available_false():
    """Test MLflow availability check when not installed."""
    with patch('src.integrations.mlflow_integration.MLFLOW_AVAILABLE', False):
        from src.integrations.mlflow_integration import is_mlflow_available
        assert is_mlflow_available() is False


def test_import_without_mlflow():
    """Test that module can be imported even without MLflow."""
    with patch('src.integrations.mlflow_integration.MLFLOW_AVAILABLE', False):
        from src.integrations.mlflow_integration import MLflowProvenanceBridge

        # Should be importable but fail on instantiation
        with pytest.raises(ImportError, match="MLflow is not installed"):
            MLflowProvenanceBridge(Path('/tmp'))
