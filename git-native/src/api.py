"""
FastAPI server for provenance queries.

Provides REST API endpoints for querying Git-native provenance metadata,
generating audit trails, and validating DTA compliance.
"""

from typing import Dict, Any, Optional, List
from pathlib import Path
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, validator
import json

from .provenance import ProvenanceTracker, ProvenanceMetadata, load_provenance_file
from .verify import ProvenanceVerifier, validate_provenance_file, ValidationReport


# Pydantic models for request/response validation
class HealthResponse(BaseModel):
    """Health check response."""
    status: str = Field(..., description="Service status")
    version: str = Field(..., description="API version")


class ProvenanceResponse(BaseModel):
    """Provenance metadata response."""
    commit_hash: str = Field(..., description="Git commit hash")
    metadata: Dict[str, Any] = Field(..., description="DTA provenance metadata")

    class Config:
        json_schema_extra = {
            "example": {
                "commit_hash": "abc123def456",
                "metadata": {
                    "source": {
                        "datasetName": "Customer Churn Dataset",
                        "providerName": "Analytics Team"
                    },
                    "provenance": {
                        "dataGenerationMethod": "SQL export",
                        "dataType": "Tabular"
                    },
                    "use": {
                        "intendedUse": "ML model training",
                        "sensitiveData": False
                    }
                }
            }
        }


class AuditTrailResponse(BaseModel):
    """Audit trail response."""
    file_path: str = Field(..., description="File path")
    commit_count: int = Field(..., description="Number of commits")
    audit_trail: List[Dict[str, Any]] = Field(..., description="Audit trail records")

    class Config:
        json_schema_extra = {
            "example": {
                "file_path": "data/dataset.csv",
                "commit_count": 3,
                "audit_trail": [
                    {
                        "commit_hash": "abc123",
                        "date": "2024-01-15T12:00:00Z",
                        "author": "user@example.com",
                        "message": "Initial dataset",
                        "provenance": {"source": {"datasetName": "Test"}}
                    }
                ]
            }
        }


class ValidateRequest(BaseModel):
    """Validation request body."""
    metadata: Dict[str, Any] = Field(..., description="DTA provenance metadata to validate")

    class Config:
        json_schema_extra = {
            "example": {
                "metadata": {
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
            }
        }


class ValidationResponse(BaseModel):
    """Validation response."""
    is_valid: bool = Field(..., description="Whether metadata is valid")
    errors: List[str] = Field(default_factory=list, description="Validation errors")
    warnings: List[str] = Field(default_factory=list, description="Validation warnings")
    missing_optional_fields: List[str] = Field(
        default_factory=list,
        description="Missing optional fields"
    )
    score: float = Field(..., description="Compliance score (0.0 to 1.0)")

    class Config:
        json_schema_extra = {
            "example": {
                "is_valid": True,
                "errors": [],
                "warnings": [],
                "missing_optional_fields": ["datasetVersion", "lastModifiedDate"],
                "score": 0.85
            }
        }


class LineageNode(BaseModel):
    """Lineage graph node."""
    id: str = Field(..., description="Node identifier")
    label: str = Field(..., description="Node label")
    node_type: str = Field(..., description="Node type (commit, file)")


class LineageEdge(BaseModel):
    """Lineage graph edge."""
    source: str = Field(..., description="Source node ID")
    target: str = Field(..., description="Target node ID")
    label: Optional[str] = Field(None, description="Edge label")


class LineageResponse(BaseModel):
    """Lineage graph response."""
    file_path: str = Field(..., description="File path")
    nodes: List[LineageNode] = Field(..., description="Graph nodes")
    edges: List[LineageEdge] = Field(..., description="Graph edges")

    class Config:
        json_schema_extra = {
            "example": {
                "file_path": "data/dataset.csv",
                "nodes": [
                    {"id": "commit_abc123", "label": "abc123", "node_type": "commit"},
                    {"id": "file_dataset", "label": "dataset.csv", "node_type": "file"}
                ],
                "edges": [
                    {"source": "commit_abc123", "target": "file_dataset", "label": "modified"}
                ]
            }
        }


class ErrorResponse(BaseModel):
    """Error response."""
    detail: str = Field(..., description="Error message")


def create_app(repo_path: Path) -> FastAPI:
    """
    Create FastAPI application instance.

    Args:
        repo_path: Path to Git repository

    Returns:
        Configured FastAPI application
    """
    app = FastAPI(
        title="DTA Provenance API",
        description="REST API for querying Git-native provenance metadata",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # In production, specify allowed origins
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Initialize provenance tracker and verifier
    tracker = ProvenanceTracker(repo_path)
    verifier = ProvenanceVerifier()

    @app.get(
        "/health",
        response_model=HealthResponse,
        tags=["health"],
        summary="Health check",
        description="Check if the API server is running and healthy."
    )
    async def health_check() -> HealthResponse:
        """Health check endpoint."""
        return HealthResponse(status="healthy", version="1.0.0")

    @app.get(
        "/provenance/{commit_hash}",
        response_model=ProvenanceResponse,
        responses={
            404: {"model": ErrorResponse, "description": "Commit not found or no provenance metadata"},
            500: {"model": ErrorResponse, "description": "Internal server error"}
        },
        tags=["provenance"],
        summary="Get provenance metadata",
        description="Retrieve DTA provenance metadata from a specific Git commit."
    )
    async def get_provenance(commit_hash: str) -> ProvenanceResponse:
        """
        Get provenance metadata from a commit.

        Args:
            commit_hash: Git commit hash (full or abbreviated)

        Returns:
            Provenance metadata

        Raises:
            HTTPException: If commit not found or no metadata available
        """
        try:
            metadata = tracker.read_provenance(commit_hash)

            if not metadata:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"No provenance metadata found in commit {commit_hash}"
                )

            return ProvenanceResponse(
                commit_hash=commit_hash,
                metadata=metadata.to_dict()
            )

        except HTTPException:
            raise
        except Exception as e:
            error_msg = str(e).lower()
            if "not found" in error_msg or "does not exist" in error_msg or "invalid" in error_msg:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Commit {commit_hash} not found"
                )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )

    @app.get(
        "/audit-trail/{file_path:path}",
        response_model=AuditTrailResponse,
        responses={
            404: {"model": ErrorResponse, "description": "File not found"},
            500: {"model": ErrorResponse, "description": "Internal server error"}
        },
        tags=["audit"],
        summary="Get audit trail",
        description="Retrieve complete audit trail for a file, including all commits and provenance metadata."
    )
    async def get_audit_trail(
        file_path: str,
        max_commits: Optional[int] = None
    ) -> AuditTrailResponse:
        """
        Get audit trail for a file.

        Args:
            file_path: Relative path to file in repository
            max_commits: Maximum number of commits to return (default: all)

        Returns:
            Audit trail with all commits that modified the file

        Raises:
            HTTPException: If file not found or error occurs
        """
        try:
            path = Path(file_path)
            audit_trail = tracker.generate_audit_trail(path, max_commits)

            if not audit_trail:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"No commits found for file {file_path}"
                )

            return AuditTrailResponse(
                file_path=file_path,
                commit_count=len(audit_trail),
                audit_trail=audit_trail
            )

        except HTTPException:
            raise
        except Exception as e:
            error_msg = str(e).lower()
            if "not found" in error_msg or "does not exist" in error_msg or "unknown" in error_msg:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"File {file_path} not found"
                )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )

    @app.post(
        "/validate",
        response_model=ValidationResponse,
        responses={
            400: {"model": ErrorResponse, "description": "Invalid request body"},
            500: {"model": ErrorResponse, "description": "Internal server error"}
        },
        tags=["validation"],
        summary="Validate provenance metadata",
        description="Validate DTA provenance metadata against v1.0.0 standards."
    )
    async def validate_metadata(request: ValidateRequest) -> ValidationResponse:
        """
        Validate DTA provenance metadata.

        Args:
            request: Validation request with metadata

        Returns:
            Validation report with errors, warnings, and compliance score

        Raises:
            HTTPException: If validation fails
        """
        try:
            # Validate metadata
            report = verifier.validate_dta_compliance(request.metadata)

            return ValidationResponse(
                is_valid=report.is_valid,
                errors=report.errors,
                warnings=report.warnings,
                missing_optional_fields=report.missing_optional_fields,
                score=report.score
            )

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )

    @app.get(
        "/lineage/{file_path:path}",
        response_model=LineageResponse,
        responses={
            404: {"model": ErrorResponse, "description": "File not found"},
            500: {"model": ErrorResponse, "description": "Internal server error"}
        },
        tags=["lineage"],
        summary="Get lineage graph",
        description="Generate lineage graph data for a file showing commit relationships."
    )
    async def get_lineage(file_path: str) -> LineageResponse:
        """
        Get lineage graph for a file.

        Args:
            file_path: Relative path to file in repository

        Returns:
            Lineage graph with nodes and edges

        Raises:
            HTTPException: If file not found or error occurs
        """
        try:
            path = Path(file_path)

            # Try to generate lineage graph
            graph = verifier.trace_lineage(path, tracker.repo)

            if not graph:
                # Fallback: generate simple lineage from audit trail
                audit_trail = tracker.generate_audit_trail(path)

                if not audit_trail:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"No commits found for file {file_path}"
                    )

                # Create simple linear graph
                nodes = []
                edges = []

                # Add file node
                nodes.append(LineageNode(
                    id=f"file_{path.name}",
                    label=path.name,
                    node_type="file"
                ))

                # Add commit nodes and edges
                for i, record in enumerate(audit_trail):
                    commit_id = f"commit_{record['commit_hash'][:8]}"
                    nodes.append(LineageNode(
                        id=commit_id,
                        label=record['commit_hash'][:8],
                        node_type="commit"
                    ))

                    # Edge from commit to file
                    edges.append(LineageEdge(
                        source=commit_id,
                        target=f"file_{path.name}",
                        label="modified"
                    ))

                    # Edge to next commit (parent relationship)
                    if i < len(audit_trail) - 1:
                        next_commit_id = f"commit_{audit_trail[i + 1]['commit_hash'][:8]}"
                        edges.append(LineageEdge(
                            source=commit_id,
                            target=next_commit_id,
                            label="parent"
                        ))

                return LineageResponse(
                    file_path=file_path,
                    nodes=nodes,
                    edges=edges
                )

            # Convert networkx graph to API format
            nodes = []
            edges = []

            for node in graph.nodes():
                node_data = graph.nodes[node]
                nodes.append(LineageNode(
                    id=str(node),
                    label=node_data.get("label", str(node)),
                    node_type=node_data.get("type", "unknown")
                ))

            for source, target in graph.edges():
                edge_data = graph.edges[source, target]
                edges.append(LineageEdge(
                    source=str(source),
                    target=str(target),
                    label=edge_data.get("label")
                ))

            return LineageResponse(
                file_path=file_path,
                nodes=nodes,
                edges=edges
            )

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )

    return app
