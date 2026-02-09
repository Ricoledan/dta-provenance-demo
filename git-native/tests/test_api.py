"""
Tests for FastAPI server.

Uses TestClient to test all API endpoints with valid and invalid inputs.
"""

import json
import pytest
from pathlib import Path
from typing import Generator
import tempfile
import shutil

import git

from src.provenance import ProvenanceTracker, ProvenanceMetadata


class TempGitRepo:
    """Container for temp repo path and commit hash."""
    def __init__(self, path: Path, commit_hash: str):
        self.path = path
        self.commit_hash = commit_hash


@pytest.fixture
def temp_git_repo() -> Generator[TempGitRepo, None, None]:
    """Create a temporary Git repository with test data."""
    temp_dir = Path(tempfile.mkdtemp())

    try:
        # Initialize git repo
        repo = git.Repo.init(temp_dir)

        # Configure git user
        with repo.config_writer() as config:
            config.set_value("user", "name", "Test User")
            config.set_value("user", "email", "test@example.com")

        # Create test file
        test_file = temp_dir / "data.csv"
        test_file.write_text("id,name,value\n1,test,100\n")

        # Create initial commit
        repo.index.add([str(test_file.relative_to(temp_dir))])
        repo.index.commit("Initial commit")

        # Create commit with provenance
        tracker = ProvenanceTracker(temp_dir)

        metadata = ProvenanceMetadata(
            source={
                "datasetName": "Test Dataset",
                "providerName": "Test Provider",
                "datasetVersion": "1.0"
            },
            provenance={
                "dataGenerationMethod": "Test generation",
                "dateDataGenerated": "2024-01-15T00:00:00Z",
                "dataType": "Tabular",
                "dataFormat": "CSV"
            },
            use={
                "intendedUse": "Testing",
                "legalRightsToUse": "Internal use only",
                "sensitiveData": False
            }
        )

        # Modify file and commit with provenance
        test_file.write_text("id,name,value\n1,test,100\n2,test2,200\n")

        commit_hash = tracker.commit_with_provenance(
            file_paths=[test_file.relative_to(temp_dir)],
            metadata=metadata,
            message="Add test data with provenance"
        )

        # Return container with both path and commit hash
        yield TempGitRepo(temp_dir, commit_hash)

    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def test_client(temp_git_repo: TempGitRepo):
    """Create FastAPI test client."""
    try:
        from fastapi.testclient import TestClient
    except ImportError:
        pytest.skip("FastAPI not installed")

    from src.api import create_app

    app = create_app(temp_git_repo.path)
    return TestClient(app)


class TestHealthEndpoint:
    """Test health check endpoint."""

    def test_health_check(self, test_client):
        """Test health endpoint returns healthy status."""
        response = test_client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["version"] == "1.0.0"


class TestProvenanceEndpoint:
    """Test provenance metadata endpoint."""

    def test_get_provenance_with_valid_commit(self, test_client, temp_git_repo: TempGitRepo):
        """Test retrieving provenance from valid commit."""
        commit_hash = temp_git_repo.commit_hash

        response = test_client.get(f"/provenance/{commit_hash}")

        assert response.status_code == 200
        data = response.json()

        assert data["commit_hash"] == commit_hash
        assert "metadata" in data

        metadata = data["metadata"]
        assert metadata["source"]["datasetName"] == "Test Dataset"
        assert metadata["provenance"]["dataType"] == "Tabular"
        assert metadata["use"]["sensitiveData"] is False

    def test_get_provenance_with_abbreviated_hash(self, test_client, temp_git_repo: TempGitRepo):
        """Test retrieving provenance with abbreviated commit hash."""
        commit_hash = temp_git_repo.commit_hash[:8]

        response = test_client.get(f"/provenance/{commit_hash}")

        assert response.status_code == 200
        data = response.json()
        assert "metadata" in data

    def test_get_provenance_with_head(self, test_client):
        """Test retrieving provenance using HEAD."""
        response = test_client.get("/provenance/HEAD")

        assert response.status_code == 200
        data = response.json()
        assert "metadata" in data

    def test_get_provenance_invalid_commit(self, test_client):
        """Test error handling for invalid commit hash."""
        response = test_client.get("/provenance/invalid_commit_hash_xyz")

        assert response.status_code == 404
        data = response.json()
        assert "detail" in data

    def test_get_provenance_no_metadata(self, test_client):
        """Test handling commit without provenance metadata."""
        # Use the initial commit which has no provenance
        response = test_client.get("/provenance/HEAD~1")

        assert response.status_code == 404
        data = response.json()
        assert "No provenance metadata found" in data["detail"]


class TestAuditTrailEndpoint:
    """Test audit trail endpoint."""

    def test_get_audit_trail(self, test_client):
        """Test retrieving audit trail for file."""
        response = test_client.get("/audit-trail/data.csv")

        assert response.status_code == 200
        data = response.json()

        assert data["file_path"] == "data.csv"
        assert data["commit_count"] >= 1
        assert len(data["audit_trail"]) >= 1

        # Verify audit trail structure
        record = data["audit_trail"][0]
        assert "commit_hash" in record
        assert "date" in record
        assert "author" in record
        assert "message" in record

    def test_get_audit_trail_with_max_commits(self, test_client):
        """Test audit trail with max_commits parameter."""
        response = test_client.get("/audit-trail/data.csv?max_commits=1")

        assert response.status_code == 200
        data = response.json()

        assert len(data["audit_trail"]) <= 1

    def test_get_audit_trail_nonexistent_file(self, test_client):
        """Test error handling for nonexistent file."""
        response = test_client.get("/audit-trail/nonexistent.csv")

        assert response.status_code == 404
        data = response.json()
        assert "detail" in data

    def test_get_audit_trail_nested_path(self, test_client, temp_git_repo: TempGitRepo):
        """Test audit trail with nested file path."""
        # Create nested directory
        nested_dir = temp_git_repo.path / "subdir"
        nested_dir.mkdir()
        nested_file = nested_dir / "nested.csv"
        nested_file.write_text("test")

        # Commit file
        repo = git.Repo(temp_git_repo.path)
        repo.index.add(["subdir/nested.csv"])
        repo.index.commit("Add nested file")

        response = test_client.get("/audit-trail/subdir/nested.csv")

        assert response.status_code == 200
        data = response.json()
        assert data["file_path"] == "subdir/nested.csv"


class TestValidateEndpoint:
    """Test metadata validation endpoint."""

    def test_validate_valid_metadata(self, test_client):
        """Test validation with valid metadata."""
        valid_metadata = {
            "source": {
                "datasetName": "Test Dataset",
                "providerName": "Test Provider"
            },
            "provenance": {
                "dataGenerationMethod": "Manual",
                "dateDataGenerated": "2024-01-15T00:00:00Z",
                "dataType": "Tabular",
                "dataFormat": "CSV"
            },
            "use": {
                "intendedUse": "Testing",
                "legalRightsToUse": "Internal",
                "sensitiveData": False
            }
        }

        response = test_client.post(
            "/validate",
            json={"metadata": valid_metadata}
        )

        assert response.status_code == 200
        data = response.json()

        assert data["is_valid"] is True
        assert len(data["errors"]) == 0
        assert data["score"] > 0.0

    def test_validate_missing_required_fields(self, test_client):
        """Test validation with missing required fields."""
        invalid_metadata = {
            "source": {
                "datasetName": "Test Dataset"
                # Missing providerName
            },
            "provenance": {
                "dataGenerationMethod": "Manual"
                # Missing other required fields
            },
            "use": {
                "intendedUse": "Testing"
            }
        }

        response = test_client.post(
            "/validate",
            json={"metadata": invalid_metadata}
        )

        assert response.status_code == 200
        data = response.json()

        assert data["is_valid"] is False
        assert len(data["errors"]) > 0

    def test_validate_empty_metadata(self, test_client):
        """Test validation with empty metadata."""
        response = test_client.post(
            "/validate",
            json={"metadata": {}}
        )

        assert response.status_code == 200
        data = response.json()

        assert data["is_valid"] is False
        assert len(data["errors"]) > 0

    def test_validate_malformed_request(self, test_client):
        """Test error handling for malformed request."""
        response = test_client.post(
            "/validate",
            json={"invalid": "data"}
        )

        assert response.status_code == 422  # Unprocessable Entity

    def test_validate_with_warnings(self, test_client):
        """Test validation that produces warnings."""
        metadata_with_warnings = {
            "source": {
                "datasetName": "Test Dataset",
                "providerName": "Test Provider",
                "datasetVersion": "1.0"
            },
            "provenance": {
                "dataGenerationMethod": "Manual",
                "dateDataGenerated": "2024-01-15T00:00:00Z",
                "dataType": "Tabular",
                "dataFormat": "CSV"
            },
            "use": {
                "intendedUse": "Testing",
                "legalRightsToUse": "Internal",
                "sensitiveData": False
            }
            # Missing some optional fields
        }

        response = test_client.post(
            "/validate",
            json={"metadata": metadata_with_warnings}
        )

        assert response.status_code == 200
        data = response.json()

        assert data["is_valid"] is True
        # May have missing optional fields
        assert isinstance(data["missing_optional_fields"], list)


class TestLineageEndpoint:
    """Test lineage graph endpoint."""

    def test_get_lineage(self, test_client):
        """Test retrieving lineage graph."""
        response = test_client.get("/lineage/data.csv")

        assert response.status_code == 200
        data = response.json()

        assert data["file_path"] == "data.csv"
        assert "nodes" in data
        assert "edges" in data
        assert len(data["nodes"]) > 0

        # Verify node structure
        if data["nodes"]:
            node = data["nodes"][0]
            assert "id" in node
            assert "label" in node
            assert "node_type" in node

        # Verify edge structure
        if data["edges"]:
            edge = data["edges"][0]
            assert "source" in edge
            assert "target" in edge

    def test_get_lineage_nonexistent_file(self, test_client):
        """Test lineage for nonexistent file."""
        response = test_client.get("/lineage/nonexistent.csv")

        assert response.status_code == 404
        data = response.json()
        assert "detail" in data

    def test_get_lineage_nested_path(self, test_client, temp_git_repo: TempGitRepo):
        """Test lineage with nested file path."""
        # Create nested directory
        nested_dir = temp_git_repo.path / "subdir"
        nested_dir.mkdir()
        nested_file = nested_dir / "nested.csv"
        nested_file.write_text("test")

        # Commit file
        repo = git.Repo(temp_git_repo.path)
        repo.index.add(["subdir/nested.csv"])
        repo.index.commit("Add nested file")

        response = test_client.get("/lineage/subdir/nested.csv")

        assert response.status_code == 200
        data = response.json()
        assert data["file_path"] == "subdir/nested.csv"


class TestAPIDocumentation:
    """Test API documentation endpoints."""

    def test_openapi_schema(self, test_client):
        """Test OpenAPI schema is available."""
        response = test_client.get("/openapi.json")

        assert response.status_code == 200
        schema = response.json()

        assert schema["info"]["title"] == "DTA Provenance API"
        assert schema["info"]["version"] == "1.0.0"
        assert "paths" in schema

    def test_swagger_ui(self, test_client):
        """Test Swagger UI is available."""
        response = test_client.get("/docs")

        assert response.status_code == 200
        assert "swagger" in response.text.lower() or "openapi" in response.text.lower()

    def test_redoc(self, test_client):
        """Test ReDoc is available."""
        response = test_client.get("/redoc")

        assert response.status_code == 200


class TestCORS:
    """Test CORS middleware."""

    def test_cors_headers(self, test_client):
        """Test CORS headers are present."""
        response = test_client.options(
            "/health",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "GET"
            }
        )

        # CORS headers should be present
        assert "access-control-allow-origin" in response.headers


class TestErrorHandling:
    """Test error handling."""

    def test_404_not_found(self, test_client):
        """Test 404 error for non-existent endpoint."""
        response = test_client.get("/nonexistent-endpoint")

        assert response.status_code == 404

    def test_method_not_allowed(self, test_client):
        """Test method not allowed error."""
        response = test_client.post("/health")

        assert response.status_code == 405  # Method Not Allowed
