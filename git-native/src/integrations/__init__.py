"""
Integration modules for external tools.

This sub-package provides bridges between DTA provenance tracking and
popular data science and MLOps tools like DVC, MLflow, and SBOM generators.

Each integration module is designed with optional dependencies using
lazy imports and graceful degradation.
"""

__all__ = []

# Integrations are lazy-loaded to avoid requiring all dependencies
