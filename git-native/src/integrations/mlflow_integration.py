"""
MLflow integration for DTA provenance.

Bridges MLflow experiment tracking with DTA provenance metadata,
allowing you to track both ML experiments and compliance metadata together.
"""

from typing import Dict, Optional, Any, List
from pathlib import Path
import json

# Lazy import of MLflow - only required if using MLflow features
try:
    import mlflow
    import mlflow.tracking
    MLFLOW_AVAILABLE = True
except ImportError:
    MLFLOW_AVAILABLE = False


class MLflowProvenanceBridge:
    """Bridge between MLflow experiment tracking and DTA provenance tracking."""

    def __init__(self, repo_path: Path, tracking_uri: Optional[str] = None):
        """
        Initialize MLflow-Provenance bridge.

        Args:
            repo_path: Path to Git repository
            tracking_uri: MLflow tracking URI (optional, defaults to local)

        Raises:
            ImportError: If MLflow is not installed
        """
        if not MLFLOW_AVAILABLE:
            raise ImportError(
                "MLflow is not installed. Install with: pip install 'dta-provenance[mlflow]'"
            )

        self.repo_path = Path(repo_path)

        # Set tracking URI if provided
        if tracking_uri:
            mlflow.set_tracking_uri(tracking_uri)

    def log_provenance_to_mlflow(
        self,
        metadata: Dict[str, Any],
        run_id: Optional[str] = None
    ) -> str:
        """
        Log DTA provenance metadata to an MLflow run.

        This stores the complete provenance metadata as tags and params
        in MLflow for easy retrieval and querying.

        Args:
            metadata: DTA provenance metadata dict
            run_id: MLflow run ID (uses active run if None)

        Returns:
            MLflow run ID

        Raises:
            RuntimeError: If no active MLflow run and run_id not provided
        """
        # Get or use active run
        if run_id:
            run = mlflow.get_run(run_id)
        else:
            active_run = mlflow.active_run()
            if not active_run:
                raise RuntimeError(
                    "No active MLflow run. Start a run with mlflow.start_run() "
                    "or provide run_id parameter"
                )
            run = active_run
            run_id = run.info.run_id

        # Log provenance metadata as tags
        with mlflow.start_run(run_id=run_id):
            # Log source information
            if 'source' in metadata:
                source = metadata['source']
                if 'datasetName' in source:
                    mlflow.set_tag('dta.source.datasetName', source['datasetName'])
                if 'providerName' in source:
                    mlflow.set_tag('dta.source.providerName', source['providerName'])
                if 'datasetUrl' in source:
                    mlflow.set_tag('dta.source.datasetUrl', source['datasetUrl'])
                if 'license' in source:
                    mlflow.set_tag('dta.source.license', source['license'])

            # Log provenance information
            if 'provenance' in metadata:
                prov = metadata['provenance']
                if 'dataType' in prov:
                    mlflow.set_tag('dta.provenance.dataType', prov['dataType'])
                if 'dataFormat' in prov:
                    mlflow.set_tag('dta.provenance.dataFormat', prov['dataFormat'])
                if 'dataGenerationMethod' in prov:
                    mlflow.set_tag('dta.provenance.dataGenerationMethod',
                                 prov['dataGenerationMethod'])
                if 'dateDataGenerated' in prov:
                    mlflow.set_tag('dta.provenance.dateDataGenerated',
                                 prov['dateDataGenerated'])

            # Log use information
            if 'use' in metadata:
                use = metadata['use']
                if 'intendedUse' in use:
                    mlflow.set_tag('dta.use.intendedUse', use['intendedUse'])
                if 'sensitiveData' in use:
                    mlflow.set_tag('dta.use.sensitiveData', str(use['sensitiveData']))
                if 'legalRightsToUse' in use:
                    mlflow.set_tag('dta.use.legalRightsToUse', use['legalRightsToUse'])

            # Log complete metadata as artifact
            metadata_file = self.repo_path / '.mlflow_provenance_temp.json'
            with open(metadata_file, 'w') as f:
                json.dump(metadata, f, indent=2)

            mlflow.log_artifact(str(metadata_file), 'provenance')

            # Clean up temp file
            metadata_file.unlink()

            # Set provenance compliance tag
            mlflow.set_tag('dta.compliant', 'true')
            mlflow.set_tag('dta.version', '1.0.0')

        return run_id

    def commit_with_mlflow_tracking(
        self,
        file_paths: List[Path],
        metadata: Dict[str, Any],
        message: str,
        tracker: Any,
        experiment_name: Optional[str] = None,
        run_name: Optional[str] = None
    ) -> tuple[str, str]:
        """
        Create a Git commit with provenance and track in MLflow.

        This combines Git-native provenance tracking with MLflow experiment tracking,
        storing the MLflow run_id in the provenance metadata and the Git commit hash
        in MLflow tags.

        Args:
            file_paths: Files to commit
            metadata: DTA provenance metadata dict
            message: Commit message
            tracker: ProvenanceTracker instance
            experiment_name: MLflow experiment name (optional)
            run_name: MLflow run name (optional)

        Returns:
            Tuple of (commit_hash, mlflow_run_id)

        Raises:
            Exception: If commit or MLflow logging fails
        """
        # Set experiment if provided
        if experiment_name:
            mlflow.set_experiment(experiment_name)

        # Start MLflow run
        with mlflow.start_run(run_name=run_name) as run:
            run_id = run.info.run_id

            # Add MLflow run_id to metadata
            if 'metadata' not in metadata:
                metadata['metadata'] = {}
            metadata['metadata']['mlflow_run_id'] = run_id

            # Create Git commit with enriched metadata
            from ..provenance import ProvenanceMetadata
            prov_metadata = ProvenanceMetadata.from_dict(metadata)

            commit_hash = tracker.commit_with_provenance(
                file_paths=file_paths,
                metadata=prov_metadata,
                message=message
            )

            # Log provenance to MLflow
            self.log_provenance_to_mlflow(metadata, run_id)

            # Log Git commit hash to MLflow
            mlflow.set_tag('git.commit_hash', commit_hash)
            mlflow.set_tag('git.commit_message', message)

            # Log file paths
            for idx, file_path in enumerate(file_paths):
                mlflow.set_tag(f'git.file.{idx}', str(file_path))

        return commit_hash, run_id

    def read_mlflow_provenance(
        self,
        run_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Read DTA provenance metadata from an MLflow run.

        Args:
            run_id: MLflow run ID

        Returns:
            DTA provenance metadata dict if found, None otherwise
        """
        try:
            run = mlflow.get_run(run_id)

            # Check if this run has DTA provenance
            if 'dta.compliant' not in run.data.tags:
                return None

            # Reconstruct metadata from tags
            tags = run.data.tags
            metadata = {
                'source': {},
                'provenance': {},
                'use': {},
                'metadata': {}
            }

            # Extract source fields
            for key, value in tags.items():
                if key.startswith('dta.source.'):
                    field = key.replace('dta.source.', '')
                    metadata['source'][field] = value
                elif key.startswith('dta.provenance.'):
                    field = key.replace('dta.provenance.', '')
                    metadata['provenance'][field] = value
                elif key.startswith('dta.use.'):
                    field = key.replace('dta.use.', '')
                    # Convert string 'True'/'False' to boolean for sensitiveData
                    if field == 'sensitiveData':
                        metadata['use'][field] = value.lower() == 'true'
                    else:
                        metadata['use'][field] = value
                elif key.startswith('git.'):
                    field = key.replace('git.', '')
                    metadata['metadata'][field] = value

            # Try to get full metadata from artifact
            client = mlflow.tracking.MlflowClient()
            artifacts = client.list_artifacts(run_id, 'provenance')

            if artifacts:
                # Download the artifact
                artifact_path = client.download_artifacts(run_id, 'provenance')
                metadata_file = Path(artifact_path) / '.mlflow_provenance_temp.json'

                if metadata_file.exists():
                    with open(metadata_file) as f:
                        full_metadata = json.load(f)
                    return full_metadata

            return metadata

        except Exception:
            return None

    def get_mlflow_runs_by_dataset(
        self,
        dataset_name: str,
        experiment_ids: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Get all MLflow runs that used a specific dataset.

        Args:
            dataset_name: Dataset name to search for
            experiment_ids: Optional list of experiment IDs to search in

        Returns:
            List of run information dicts
        """
        client = mlflow.tracking.MlflowClient()

        # Build filter expression
        filter_string = f"tags.`dta.source.datasetName` = '{dataset_name}'"

        # Search runs
        runs = client.search_runs(
            experiment_ids=experiment_ids or [],
            filter_string=filter_string
        )

        return [
            {
                'run_id': run.info.run_id,
                'experiment_id': run.info.experiment_id,
                'status': run.info.status,
                'start_time': run.info.start_time,
                'end_time': run.info.end_time,
                'tags': run.data.tags,
                'params': run.data.params,
                'metrics': run.data.metrics
            }
            for run in runs
        ]


def is_mlflow_available() -> bool:
    """
    Check if MLflow is available in the environment.

    Returns:
        True if MLflow is installed, False otherwise
    """
    return MLFLOW_AVAILABLE
