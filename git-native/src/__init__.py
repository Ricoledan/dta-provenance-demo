"""
DTA-compliant provenance tracking using Git.

This package provides production-quality tools for tracking data provenance
using Git commits with Data & Trust Alliance metadata standards v1.0.0.
"""

from .provenance import ProvenanceTracker, ProvenanceMetadata
from .verify import ProvenanceVerifier, ValidationReport

__version__ = "1.0.0"
__all__ = [
    "ProvenanceTracker",
    "ProvenanceMetadata",
    "ProvenanceVerifier",
    "ValidationReport",
]
