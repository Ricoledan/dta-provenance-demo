"""
SBOM (Software Bill of Materials) integration for DTA provenance.

Generates CycloneDX-format SBOMs and links them to provenance metadata
for complete software supply chain tracking.
"""

from typing import Dict, Optional, Any, List
from pathlib import Path
import json
import subprocess
import sys

# Lazy import of CycloneDX - only required if using SBOM features
try:
    from cyclonedx.model.bom import Bom
    from cyclonedx.model.component import Component, ComponentType
    from cyclonedx.output import OutputFormat, get_instance
    from cyclonedx.model import XsUri
    CYCLONEDX_AVAILABLE = True
except ImportError:
    CYCLONEDX_AVAILABLE = False


class SBOMProvenanceBridge:
    """Bridge between SBOM generation and DTA provenance tracking."""

    def __init__(self, repo_path: Path):
        """
        Initialize SBOM-Provenance bridge.

        Args:
            repo_path: Path to repository root

        Raises:
            ImportError: If CycloneDX is not installed
        """
        if not CYCLONEDX_AVAILABLE:
            raise ImportError(
                "cyclonedx-bom is not installed. "
                "Install with: pip install 'dta-provenance[sbom]'"
            )

        self.repo_path = Path(repo_path)

    def generate_sbom(
        self,
        project_name: str,
        project_version: str = "1.0.0",
        output_path: Optional[Path] = None
    ) -> Path:
        """
        Generate SBOM for Python project.

        Uses pip to extract installed packages and generates a CycloneDX SBOM.

        Args:
            project_name: Name of the project
            project_version: Version of the project
            output_path: Where to save SBOM (default: sbom.json in repo root)

        Returns:
            Path to generated SBOM file

        Raises:
            subprocess.CalledProcessError: If pip fails
        """
        if output_path is None:
            output_path = self.repo_path / 'sbom.json'

        # Get installed packages
        result = subprocess.run(
            [sys.executable, '-m', 'pip', 'list', '--format=json'],
            capture_output=True,
            text=True,
            check=True
        )

        packages = json.loads(result.stdout)

        # Create BOM
        bom = Bom()

        # Add components for each package
        components = []
        for pkg in packages:
            component = Component(
                name=pkg['name'],
                version=pkg['version'],
                component_type=ComponentType.LIBRARY
            )
            components.append(component)

        bom.components.update(components)

        # Write SBOM to file
        outputter = get_instance(bom=bom, output_format=OutputFormat.JSON)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w') as f:
            f.write(outputter.output_as_string())

        return output_path

    def link_sbom_to_provenance(
        self,
        sbom_path: Path,
        metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Link SBOM file to provenance metadata.

        Enriches provenance metadata with SBOM reference and key dependency info.

        Args:
            sbom_path: Path to SBOM file (relative to repo root)
            metadata: Provenance metadata dict to enrich

        Returns:
            Enriched metadata with SBOM reference
        """
        full_path = self.repo_path / sbom_path

        if not full_path.exists():
            raise FileNotFoundError(f"SBOM file not found: {sbom_path}")

        # Read SBOM to extract summary info
        with open(full_path) as f:
            sbom_data = json.load(f)

        # Extract component count and key dependencies
        components = sbom_data.get('components', [])
        dependency_count = len(components)

        # Enrich metadata
        if 'metadata' not in metadata:
            metadata['metadata'] = {}

        metadata['metadata']['sbom'] = {
            'format': 'CycloneDX',
            'version': sbom_data.get('specVersion', 'unknown'),
            'sbom_file': str(sbom_path),
            'dependency_count': dependency_count,
            'serial_number': sbom_data.get('serialNumber', '')
        }

        return metadata

    def extract_dependency_info(self, sbom_path: Path) -> Dict[str, Any]:
        """
        Extract dependency information from SBOM.

        Args:
            sbom_path: Path to SBOM file (relative to repo root)

        Returns:
            Dict with dependency information (counts, licenses, etc.)
        """
        full_path = self.repo_path / sbom_path

        if not full_path.exists():
            raise FileNotFoundError(f"SBOM file not found: {sbom_path}")

        with open(full_path) as f:
            sbom_data = json.load(f)

        components = sbom_data.get('components', [])

        # Analyze dependencies
        info = {
            'total_dependencies': len(components),
            'dependencies': [],
            'licenses': set(),
            'by_type': {}
        }

        for component in components:
            dep = {
                'name': component.get('name', 'unknown'),
                'version': component.get('version', 'unknown'),
                'type': component.get('type', 'library')
            }

            info['dependencies'].append(dep)

            # Track component types
            comp_type = component.get('type', 'library')
            info['by_type'][comp_type] = info['by_type'].get(comp_type, 0) + 1

            # Track licenses
            licenses = component.get('licenses', [])
            for lic in licenses:
                if isinstance(lic, dict) and 'license' in lic:
                    lic_info = lic['license']
                    if isinstance(lic_info, dict) and 'id' in lic_info:
                        info['licenses'].add(lic_info['id'])

        info['licenses'] = sorted(list(info['licenses']))

        return info

    def generate_and_link(
        self,
        project_name: str,
        project_version: str,
        metadata: Dict[str, Any],
        sbom_output: Optional[Path] = None
    ) -> tuple[Path, Dict[str, Any]]:
        """
        Generate SBOM and link to provenance in one step.

        Args:
            project_name: Name of the project
            project_version: Version of the project
            metadata: Provenance metadata to enrich
            sbom_output: Where to save SBOM (optional)

        Returns:
            Tuple of (sbom_path, enriched_metadata)
        """
        # Generate SBOM
        sbom_path = self.generate_sbom(
            project_name,
            project_version,
            sbom_output
        )

        # Link to provenance
        relative_sbom = sbom_path.relative_to(self.repo_path)
        enriched = self.link_sbom_to_provenance(relative_sbom, metadata)

        return sbom_path, enriched


def is_cyclonedx_available() -> bool:
    """
    Check if CycloneDX is available in the environment.

    Returns:
        True if CycloneDX is installed, False otherwise
    """
    return CYCLONEDX_AVAILABLE
