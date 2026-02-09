"""
DVC (Data Version Control) integration for DTA provenance.

Bridges DVC's data versioning with DTA provenance metadata,
allowing you to track both data versions and compliance metadata together.
"""

from typing import Dict, Optional, Any
from pathlib import Path
import json
import subprocess
import sys

# Lazy import of DVC - only required if using DVC features
try:
    import dvc.api
    DVC_AVAILABLE = True
except ImportError:
    DVC_AVAILABLE = False


class DVCProvenanceBridge:
    """Bridge between DVC data versioning and DTA provenance tracking."""

    def __init__(self, repo_path: Path):
        """
        Initialize DVC-Provenance bridge.

        Args:
            repo_path: Path to Git repository (must be DVC-initialized)

        Raises:
            ImportError: If DVC is not installed
            RuntimeError: If DVC repo is not initialized
        """
        if not DVC_AVAILABLE:
            raise ImportError(
                "DVC is not installed. Install with: pip install 'dta-provenance[dvc]'"
            )

        self.repo_path = Path(repo_path)

        # Check if DVC is initialized
        dvc_dir = self.repo_path / '.dvc'
        if not dvc_dir.exists():
            raise RuntimeError(
                f"{repo_path} is not a DVC repository. "
                "Initialize with: dvc init"
            )

    def track_dvc_file(
        self,
        file_path: Path,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Add file to DVC tracking and enrich provenance metadata.

        This runs `dvc add` on the file and stores the DVC hash
        in the provenance metadata for full traceability.

        Args:
            file_path: File to track with DVC (relative to repo root)
            metadata: Existing provenance metadata dict (will be enriched)

        Returns:
            Enriched metadata with DVC information

        Raises:
            subprocess.CalledProcessError: If dvc add fails
        """
        if metadata is None:
            metadata = {}

        full_path = self.repo_path / file_path

        if not full_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        # Run dvc add
        result = subprocess.run(
            ['dvc', 'add', str(file_path)],
            cwd=self.repo_path,
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            raise subprocess.CalledProcessError(
                result.returncode,
                result.args,
                result.stdout,
                result.stderr
            )

        # Read the .dvc file to extract hash
        dvc_file = Path(str(full_path) + '.dvc')
        if dvc_file.exists():
            dvc_info = self._parse_dvc_file(dvc_file)

            # Enrich metadata with DVC information
            if 'metadata' not in metadata:
                metadata['metadata'] = {}

            metadata['metadata']['dvc'] = {
                'tracked': True,
                'dvc_file': str(dvc_file.relative_to(self.repo_path)),
                'md5': dvc_info.get('md5', ''),
                'size': dvc_info.get('size', ''),
                'path': str(file_path)
            }

        return metadata

    def enrich_metadata_from_dvc(
        self,
        file_path: Path,
        metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Enrich provenance metadata with DVC information for an already-tracked file.

        Args:
            file_path: DVC-tracked file (relative to repo root)
            metadata: Provenance metadata dict to enrich

        Returns:
            Enriched metadata with DVC hash and version info
        """
        full_path = self.repo_path / file_path
        dvc_file = Path(str(full_path) + '.dvc')

        if not dvc_file.exists():
            # File not tracked by DVC, return metadata unchanged
            return metadata

        # Read DVC file
        dvc_info = self._parse_dvc_file(dvc_file)

        # Enrich metadata
        if 'metadata' not in metadata:
            metadata['metadata'] = {}

        metadata['metadata']['dvc'] = {
            'tracked': True,
            'dvc_file': str(dvc_file.relative_to(self.repo_path)),
            'md5': dvc_info.get('md5', ''),
            'size': dvc_info.get('size', ''),
            'path': str(file_path)
        }

        return metadata

    def read_dvc_provenance(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """
        Read DVC metadata for a tracked file.

        Args:
            file_path: DVC-tracked file (relative to repo root)

        Returns:
            DVC metadata dict if file is tracked, None otherwise
        """
        full_path = self.repo_path / file_path
        dvc_file = Path(str(full_path) + '.dvc')

        if not dvc_file.exists():
            return None

        # Parse DVC file
        dvc_info = self._parse_dvc_file(dvc_file)

        return {
            'tracked': True,
            'dvc_file': str(dvc_file.relative_to(self.repo_path)),
            'metadata': dvc_info
        }

    def get_dvc_status(self) -> Dict[str, Any]:
        """
        Get DVC repository status.

        Returns:
            Dict with DVC status information (tracked files, cache stats, etc.)
        """
        result = subprocess.run(
            ['dvc', 'status'],
            cwd=self.repo_path,
            capture_output=True,
            text=True
        )

        # Parse output
        status = {
            'is_clean': 'No changes' in result.stdout or result.stdout.strip() == '',
            'output': result.stdout,
            'return_code': result.returncode
        }

        return status

    def _parse_dvc_file(self, dvc_file: Path) -> Dict[str, str]:
        """
        Parse a .dvc file to extract metadata.

        DVC files are YAML with an 'outs' list containing file metadata.

        Args:
            dvc_file: Path to .dvc file

        Returns:
            Dict with md5, size, and other metadata
        """
        dvc_info = {}
        with open(dvc_file) as f:
            content = f.read()
            lines = content.split('\n')

            # Simple YAML parser for DVC files
            # Format is typically:
            # outs:
            # - md5: <hash>
            #   size: <size>
            #   path: <path>
            in_outs = False
            for line in lines:
                stripped = line.strip()

                if stripped.startswith('outs:'):
                    in_outs = True
                    continue

                if in_outs and stripped.startswith('- '):
                    # Start of list item, extract key-value
                    if ':' in stripped:
                        key, value = stripped[2:].split(':', 1)
                        dvc_info[key.strip()] = value.strip()
                elif in_outs and stripped and not stripped.startswith('-'):
                    # Continuation of list item (indented)
                    if ':' in stripped:
                        key, value = stripped.split(':', 1)
                        dvc_info[key.strip()] = value.strip()

        return dvc_info


def is_dvc_available() -> bool:
    """
    Check if DVC is available in the environment.

    Returns:
        True if DVC is installed, False otherwise
    """
    return DVC_AVAILABLE
