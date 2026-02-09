# SBOM Integration

Integrate DTA provenance tracking with [CycloneDX SBOM](https://cyclonedx.org/) for complete software supply chain transparency.

## Overview

A Software Bill of Materials (SBOM) is a comprehensive inventory of all software components, libraries, and dependencies in a project. By combining SBOM generation with DTA provenance metadata, you get:

- **Dependency transparency** - Know exactly what packages are used
- **License compliance** - Track all licenses across dependencies
- **Vulnerability management** - Identify security issues in dependencies
- **Supply chain security** - Complete audit trail of software components
- **DTA compliance** - Provenance metadata for regulatory requirements

## What is CycloneDX?

CycloneDX is an industry-standard format for Software Bill of Materials (SBOM). It's widely supported by security tools and is recommended by:

- CISA (US Cybersecurity & Infrastructure Security Agency)
- NTIA (National Telecommunications and Information Administration)
- OWASP (Open Web Application Security Project)

## Installation

```bash
# Install with SBOM support
pip install 'dta-provenance[sbom]'

# Or install manually
pip install cyclonedx-bom>=4.0
```

## Quick Start

### 1. Generate SBOM for your project

```bash
# Basic SBOM generation
dta-provenance sbom-generate \\
    --project-name my-ml-project \\
    --project-version 1.0.0
```

This creates a `sbom.json` file in your repository root containing all Python dependencies.

### 2. Generate SBOM with provenance metadata

```bash
# Create your provenance metadata
cat > provenance.json <<EOF
{
  "source": {
    "datasetName": "ML Training Pipeline",
    "providerName": "Data Science Team"
  },
  "provenance": {
    "dataGenerationMethod": "Automated ML pipeline",
    "dateDataGenerated": "2024-01-15",
    "dataType": "Code",
    "dataFormat": "Python 3.11"
  },
  "use": {
    "intendedUse": "Model training and inference",
    "legalRightsToUse": "Internal use only",
    "sensitiveData": false
  }
}
EOF

# Generate SBOM and enrich metadata
dta-provenance sbom-generate \\
    --project-name my-ml-project \\
    --project-version 1.0.0 \\
    --metadata provenance.json \\
    --output sbom.json
```

### 3. Commit with enriched provenance

```bash
git add sbom.json provenance-with-sbom.json
dta-provenance commit sbom.json provenance-with-sbom.json \\
    --metadata provenance-with-sbom.json \\
    --message "Add SBOM and provenance tracking"
```

## How It Works

### SBOM Metadata Enrichment

When you use `sbom-generate`, the DTA provenance metadata is enriched with SBOM-specific fields:

```json
{
  "source": { ... },
  "provenance": { ... },
  "use": { ... },
  "metadata": {
    "sbom": {
      "format": "CycloneDX",
      "version": "1.5",
      "sbom_file": "sbom.json",
      "dependency_count": 42,
      "serial_number": "urn:uuid:3e671687-395b-41f5-a30f-a58921a69b79"
    }
  }
}
```

This allows you to:

- **Track dependencies over time** - See how dependencies change across commits
- **Verify software integrity** - Compare SBOM hashes
- **Audit compliance** - Full provenance + dependency tracking
- **Identify security issues** - Know which versions are in use

### CycloneDX SBOM Structure

The generated SBOM follows CycloneDX 1.5 specification:

```json
{
  "bomFormat": "CycloneDX",
  "specVersion": "1.5",
  "serialNumber": "urn:uuid:...",
  "version": 1,
  "metadata": {
    "component": {
      "type": "application",
      "name": "my-ml-project",
      "version": "1.0.0"
    }
  },
  "components": [
    {
      "type": "library",
      "name": "numpy",
      "version": "1.24.0",
      "purl": "pkg:pypi/numpy@1.24.0",
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
```

## Usage Examples

### Generate SBOM with Custom Output

```bash
dta-provenance sbom-generate \\
    --project-name analytics-platform \\
    --project-version 2.1.0 \\
    --output artifacts/sbom.json
```

### Extract Dependency Information

```python
from pathlib import Path
from src.integrations.sbom_integration import SBOMProvenanceBridge

# Initialize bridge
bridge = SBOMProvenanceBridge(Path('.'))

# Extract dependency info
dep_info = bridge.extract_dependency_info(Path('sbom.json'))

print(f"Total dependencies: {dep_info['total_dependencies']}")
print(f"Licenses found: {len(dep_info['licenses'])}")

# List all dependencies
for dep in dep_info['dependencies']:
    print(f"  {dep['name']} {dep['version']}")

# List all licenses
print("\nLicenses:")
for license in dep_info['licenses']:
    print(f"  - {license}")
```

### Generate and Link Programmatically

```python
from pathlib import Path
from src.integrations.sbom_integration import SBOMProvenanceBridge
from src.provenance import load_provenance_file

# Load existing provenance
metadata = load_provenance_file(Path('provenance.json'))
metadata_dict = metadata.to_dict()

# Initialize bridge
bridge = SBOMProvenanceBridge(Path('.'))

# Generate SBOM and link to provenance
sbom_path, enriched = bridge.generate_and_link(
    project_name="ml-pipeline",
    project_version="1.0.0",
    metadata=metadata_dict,
    sbom_output=Path('artifacts/sbom.json')
)

print(f"SBOM created: {sbom_path}")
print(f"Dependencies tracked: {enriched['metadata']['sbom']['dependency_count']}")

# Save enriched metadata
import json
with open('provenance-with-sbom.json', 'w') as f:
    json.dump(enriched, f, indent=2)
```

## Workflow: ML Project with SBOM

Complete workflow for an ML project with SBOM tracking:

```bash
# 1. Initialize project
git init
python -m venv venv
source venv/bin/activate

# 2. Install dependencies
pip install numpy pandas scikit-learn

# 3. Create provenance metadata
cat > provenance.json <<EOF
{
  "source": {
    "datasetName": "Customer Churn Model v1",
    "datasetVersion": "1.0.0",
    "providerName": "ML Team"
  },
  "provenance": {
    "dataGenerationMethod": "Scikit-learn pipeline with preprocessor",
    "dateDataGenerated": "2024-01-15T10:00:00Z",
    "dataType": "Code",
    "dataFormat": "Python 3.11 with scikit-learn 1.3.0"
  },
  "use": {
    "intendedUse": "Predicting customer churn",
    "legalRightsToUse": "Internal use only",
    "sensitiveData": false
  }
}
EOF

# 4. Generate SBOM with provenance
dta-provenance sbom-generate \\
    --project-name customer-churn-model \\
    --project-version 1.0.0 \\
    --metadata provenance.json \\
    --output sbom.json

# 5. Commit everything
git add sbom.json provenance-with-sbom.json
dta-provenance commit sbom.json provenance-with-sbom.json \\
    --metadata provenance-with-sbom.json \\
    --message "Initial model with SBOM tracking"

# 6. Update dependencies later
pip install --upgrade scikit-learn

# 7. Regenerate SBOM
dta-provenance sbom-generate \\
    --project-name customer-churn-model \\
    --project-version 1.1.0 \\
    --metadata provenance-with-sbom.json \\
    --output sbom.json

# 8. Commit updated SBOM
git add sbom.json
git commit -m "Update dependencies - scikit-learn 1.4.0"
```

## Security Use Cases

### Vulnerability Scanning

SBOM files can be used with security scanning tools:

```bash
# Generate SBOM
dta-provenance sbom-generate -n my-app -v 1.0.0

# Scan with OWASP Dependency-Check
dependency-check --scan sbom.json --format JSON

# Scan with Trivy
trivy sbom sbom.json

# Scan with Grype
grype sbom:sbom.json
```

### License Compliance

```python
from pathlib import Path
from src.integrations.sbom_integration import SBOMProvenanceBridge

bridge = SBOMProvenanceBridge(Path('.'))
dep_info = bridge.extract_dependency_info(Path('sbom.json'))

# Check for problematic licenses
problematic = ['GPL-3.0', 'AGPL-3.0']
found_issues = [lic for lic in dep_info['licenses'] if lic in problematic]

if found_issues:
    print(f"⚠️  Found problematic licenses: {found_issues}")
else:
    print("✅ All licenses are compliant")

# List all unique licenses
print("\nLicenses in use:")
for license in sorted(dep_info['licenses']):
    count = sum(1 for dep in dep_info['dependencies']
                if any(lic.get('license', {}).get('id') == license
                      for lic in dep.get('licenses', [])))
    print(f"  {license}: {count} packages")
```

### Supply Chain Auditing

```bash
# Generate SBOM for audit
dta-provenance sbom-generate \\
    --project-name production-system \\
    --project-version 3.2.1 \\
    --output audit/sbom-2024-01-15.json

# Compare with previous SBOM
diff audit/sbom-2024-01-01.json audit/sbom-2024-01-15.json

# Track SBOM in Git for history
git add audit/sbom-2024-01-15.json
git commit -m "SBOM snapshot for Q1 2024 audit"
```

## Integration with CI/CD

### GitHub Actions Example

```yaml
name: Generate SBOM

on:
  push:
    branches: [main]
  release:
    types: [published]

jobs:
  sbom:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install -e .
          pip install 'dta-provenance[sbom]'

      - name: Generate SBOM
        run: |
          dta-provenance sbom-generate \\
            --project-name ${{ github.event.repository.name }} \\
            --project-version ${{ github.sha }} \\
            --output sbom.json

      - name: Upload SBOM
        uses: actions/upload-artifact@v3
        with:
          name: sbom
          path: sbom.json

      - name: Attach SBOM to release
        if: github.event_name == 'release'
        uses: actions/upload-release-asset@v1
        with:
          upload_url: ${{ github.event.release.upload_url }}
          asset_path: sbom.json
          asset_name: sbom.json
          asset_content_type: application/json
```

## Benefits

### For Developers

- Automated dependency tracking
- No manual SBOM creation needed
- Integrates with existing Git workflow
- Works with standard Python tools (pip)

### For Security Teams

- Complete dependency visibility
- Vulnerability scanning integration
- License compliance tracking
- Supply chain risk management

### For Compliance Officers

- Software inventory for audits
- Regulatory compliance (SBOM requirements)
- Full provenance + dependency tracking
- Cryptographic proof in Git history

## Limitations

- **Python-only** - Currently only generates SBOMs for Python projects
- **Pip-based** - Uses `pip list` to discover dependencies
- **Runtime dependencies** - Captures installed packages, not just declared dependencies
- **No transitive analysis** - Lists direct dependencies only (CycloneDX supports transitive, but requires additional tooling)

## Troubleshooting

### "cyclonedx-bom is not installed"

```bash
pip install 'dta-provenance[sbom]'
# or
pip install cyclonedx-bom>=4.0
```

### "SBOM file not found"

Ensure the SBOM was generated before trying to link it:

```bash
# Generate first
dta-provenance sbom-generate -n my-project -v 1.0.0

# Then link or extract
dta-provenance sbom-generate -n my-project -v 1.0.0 --metadata provenance.json
```

### Empty or incomplete SBOM

This can happen if pip is not in the correct environment:

```bash
# Ensure you're in the right virtual environment
which pip
pip list

# Then generate SBOM
dta-provenance sbom-generate -n my-project -v 1.0.0
```

### License information missing

Not all packages declare licenses properly. The SBOM will include packages without license info:

```python
dep_info = bridge.extract_dependency_info(Path('sbom.json'))

# Find packages without licenses
unlicensed = [dep for dep in dep_info['dependencies']
              if not dep.get('licenses')]
print(f"Packages without license info: {len(unlicensed)}")
```

## Best Practices

1. **Generate SBOM on release** - Create SBOM for every release/deployment
2. **Track in Git** - Commit SBOM files for historical tracking
3. **Automate in CI/CD** - Generate SBOM automatically in pipelines
4. **Scan regularly** - Use security tools to scan SBOM for vulnerabilities
5. **Review licenses** - Check licenses before adding new dependencies
6. **Document changes** - Update provenance metadata when dependencies change
7. **Keep SBOM updated** - Regenerate after dependency updates

## Regulatory Context

### Executive Order 14028 (US)

Requires SBOM for software sold to federal government.

### EU Cyber Resilience Act

Proposes SBOM requirements for products with digital elements.

### NTIA Minimum Elements

CycloneDX format meets NTIA minimum elements for SBOM:

- ✅ Author Name (project metadata)
- ✅ Component Name (package names)
- ✅ Version String (package versions)
- ✅ Unique Identifier (PURL, serial number)
- ✅ Dependency Relationship (component structure)
- ✅ Timestamp (generated in metadata)

## Related Resources

- [SBOM CLI Reference](../cli-reference.md#sbom-generate)
- [CycloneDX Specification](https://cyclonedx.org/specification/overview/)
- [DTA Standards](../DTA_STANDARDS.md)
- [DVC Integration](dvc-integration.md) - Version control for data
- [NTIA SBOM Resources](https://www.ntia.gov/sbom)
- [CISA SBOM Resources](https://www.cisa.gov/sbom)
