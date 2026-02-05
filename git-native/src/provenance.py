"""
DTA-compliant provenance tracking using Git.

This module provides a production-quality library for tracking data provenance
using Git commits with DTA Alliance metadata standards.
"""

from typing import Dict, Optional, List, Any
from pathlib import Path
from dataclasses import dataclass, asdict, field
from datetime import datetime
import json
import hashlib
import subprocess

try:
    import git
except ImportError:
    raise ImportError(
        "GitPython is required. Install with: pip install GitPython"
    )


@dataclass
class ProvenanceMetadata:
    """
    Represents DTA v1.0.0 provenance metadata.

    Attributes:
        source: Origin and provider information (8 fields)
        provenance: Data generation and processing information (6 fields)
        use: Usage rights and restrictions (8 fields)
    """

    source: Dict[str, Any]
    provenance: Dict[str, Any]
    use: Dict[str, Any]
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Validate required fields."""
        # Required source fields
        required_source = ["datasetName", "providerName"]
        for field_name in required_source:
            if field_name not in self.source:
                raise ValueError(f"Missing required source field: {field_name}")

        # Required provenance fields
        required_provenance = [
            "dataGenerationMethod",
            "dateDataGenerated",
            "dataType",
            "dataFormat"
        ]
        for field_name in required_provenance:
            if field_name not in self.provenance:
                raise ValueError(f"Missing required provenance field: {field_name}")

        # Required use fields
        required_use = ["intendedUse", "legalRightsToUse", "sensitiveData"]
        for field_name in required_use:
            if field_name not in self.use:
                raise ValueError(f"Missing required use field: {field_name}")

        # If sensitiveData is True, require sensitiveDataCategories
        if self.use.get("sensitiveData") and not self.use.get("sensitiveDataCategories"):
            raise ValueError(
                "sensitiveDataCategories is required when sensitiveData is True"
            )

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "source": self.source,
            "provenance": self.provenance,
            "use": self.use,
            **self.metadata
        }

    def compute_hash(self) -> str:
        """
        Compute SHA-256 hash of metadata for integrity verification.

        Returns:
            Hex-encoded SHA-256 hash string
        """
        json_str = json.dumps(self.to_dict(), sort_keys=True)
        return hashlib.sha256(json_str.encode()).hexdigest()

    @classmethod
    def from_dict(cls, data: Dict) -> "ProvenanceMetadata":
        """Create ProvenanceMetadata from dictionary."""
        source = data.get("source", {})
        provenance = data.get("provenance", {})
        use = data.get("use", {})

        # Extract any additional metadata fields
        metadata = {
            k: v for k, v in data.items()
            if k not in ["source", "provenance", "use"]
        }

        return cls(
            source=source,
            provenance=provenance,
            use=use,
            metadata=metadata
        )

    @classmethod
    def from_json_file(cls, file_path: Path) -> "ProvenanceMetadata":
        """Load ProvenanceMetadata from JSON file."""
        with open(file_path, 'r') as f:
            data = json.load(f)
        return cls.from_dict(data)


class ProvenanceTracker:
    """Main class for Git-native provenance tracking."""

    def __init__(self, repo_path: Path):
        """
        Initialize tracker with Git repository path.

        Args:
            repo_path: Path to Git repository (must be initialized)

        Raises:
            git.exc.InvalidGitRepositoryError: If path is not a Git repo
        """
        self.repo_path = Path(repo_path)
        try:
            self.repo = git.Repo(self.repo_path)
        except git.exc.InvalidGitRepositoryError:
            raise git.exc.InvalidGitRepositoryError(
                f"{repo_path} is not a Git repository. "
                "Initialize with: git init"
            )

    def commit_with_provenance(
        self,
        file_paths: List[Path],
        metadata: ProvenanceMetadata,
        message: str,
        sign: bool = False
    ) -> str:
        """
        Create a Git commit with provenance metadata.

        The provenance metadata is stored in the commit message using
        Git trailers (https://git-scm.com/docs/git-interpret-trailers).

        Args:
            file_paths: Files to commit (relative to repo root)
            metadata: DTA-compliant provenance metadata
            message: Commit message
            sign: Whether to GPG/SSH sign the commit (requires git config)

        Returns:
            Commit SHA hash

        Raises:
            ValueError: If files don't exist or metadata is invalid
            git.exc.GitCommandError: If git commit fails
        """
        # Validate files exist
        for file_path in file_paths:
            full_path = self.repo_path / file_path
            if not full_path.exists():
                raise ValueError(f"File not found: {file_path}")

        # Stage files
        for file_path in file_paths:
            self.repo.index.add([str(file_path)])

        # Compute metadata hash for integrity
        metadata_hash = metadata.compute_hash()

        # Build commit message with Git trailers
        commit_message = f"{message}\n\n"
        commit_message += f"DTA-Provenance-Version: 1.0.0\n"
        commit_message += f"DTA-Provenance-Hash: {metadata_hash}\n"
        commit_message += f"DTA-Dataset-Name: {metadata.source['datasetName']}\n"

        # Add compact JSON representation
        metadata_json = json.dumps(metadata.to_dict(), separators=(',', ':'))
        commit_message += f"DTA-Provenance-Metadata: {metadata_json}\n"

        # Create commit
        commit_kwargs = {"message": commit_message}
        if sign:
            commit_kwargs["gpg_sign"] = True

        commit = self.repo.index.commit(**commit_kwargs)

        return commit.hexsha

    def read_provenance(self, commit_hash: str) -> Optional[ProvenanceMetadata]:
        """
        Extract provenance metadata from a commit.

        Args:
            commit_hash: Git commit SHA or reference (HEAD, branch, tag)

        Returns:
            ProvenanceMetadata if found, None otherwise

        Raises:
            git.exc.BadName: If commit reference doesn't exist
        """
        try:
            commit = self.repo.commit(commit_hash)
        except git.exc.BadName:
            raise git.exc.BadName(f"Commit not found: {commit_hash}")

        # Parse commit message for DTA trailers
        message = commit.message

        # Look for DTA-Provenance-Metadata trailer
        for line in message.split('\n'):
            if line.startswith('DTA-Provenance-Metadata:'):
                metadata_json = line.split(':', 1)[1].strip()
                try:
                    data = json.loads(metadata_json)
                    return ProvenanceMetadata.from_dict(data)
                except json.JSONDecodeError:
                    return None

        return None

    def generate_audit_trail(
        self,
        file_path: Path,
        max_commits: Optional[int] = None
    ) -> List[Dict]:
        """
        Generate complete audit trail from Git history.

        Returns all commits that modified the specified file, with their
        provenance metadata if available.

        Args:
            file_path: File to trace (relative to repo root)
            max_commits: Maximum number of commits to return (None = all)

        Returns:
            List of audit records with commit info and provenance
        """
        audit_trail = []

        try:
            commits = list(self.repo.iter_commits(paths=str(file_path)))
        except git.exc.GitCommandError:
            return []

        if max_commits:
            commits = commits[:max_commits]

        for commit in commits:
            record = {
                "commit_hash": commit.hexsha,
                "author": str(commit.author),
                "date": commit.committed_datetime.isoformat(),
                "message": commit.message.split('\n')[0],  # First line only
                "provenance": None
            }

            # Try to extract provenance metadata
            metadata = self.read_provenance(commit.hexsha)
            if metadata:
                record["provenance"] = metadata.to_dict()

            audit_trail.append(record)

        return audit_trail

    def verify_integrity(self, commit_hash: str) -> tuple[bool, str]:
        """
        Verify integrity of provenance metadata in a commit.

        Checks that:
        1. Commit signature is valid (if signed)
        2. Metadata hash matches computed hash

        Args:
            commit_hash: Git commit SHA or reference

        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            commit = self.repo.commit(commit_hash)
        except git.exc.BadName:
            return False, f"Commit not found: {commit_hash}"

        # Check GPG signature if present
        if hasattr(commit, 'gpgsig') and commit.gpgsig:
            try:
                # Verify GPG signature using git verify-commit
                result = subprocess.run(
                    ["git", "verify-commit", commit_hash],
                    cwd=self.repo_path,
                    capture_output=True,
                    text=True
                )
                if result.returncode != 0:
                    return False, "GPG signature verification failed"
            except FileNotFoundError:
                return False, "git command not found"

        # Extract and verify metadata hash
        metadata = self.read_provenance(commit_hash)
        if not metadata:
            return True, "No provenance metadata found (not an error)"

        # Find stored hash in commit message
        stored_hash = None
        for line in commit.message.split('\n'):
            if line.startswith('DTA-Provenance-Hash:'):
                stored_hash = line.split(':', 1)[1].strip()
                break

        if not stored_hash:
            return False, "Provenance metadata found but hash missing"

        # Compute current hash and compare
        computed_hash = metadata.compute_hash()
        if stored_hash != computed_hash:
            return False, "Metadata hash mismatch (data tampered?)"

        return True, "Provenance integrity verified"


def save_provenance_file(
    metadata: ProvenanceMetadata,
    output_path: Path
) -> None:
    """
    Save provenance metadata to JSON file.

    Args:
        metadata: ProvenanceMetadata to save
        output_path: Where to save the JSON file
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w') as f:
        json.dump(metadata.to_dict(), f, indent=2)


def load_provenance_file(file_path: Path) -> ProvenanceMetadata:
    """
    Load provenance metadata from JSON file.

    Args:
        file_path: Path to JSON file

    Returns:
        ProvenanceMetadata object
    """
    return ProvenanceMetadata.from_json_file(file_path)
