# Pre-commit Hooks

Automated validation of DTA provenance metadata using [pre-commit](https://pre-commit.com/).

## Overview

The DTA Provenance Standards Demo includes two pre-commit hooks for automated validation:

1. **`dta-validate-metadata`** - Validates JSON provenance files against DTA v1.0.0 standards
2. **`dta-check-trailers`** - Ensures commits with provenance metadata have required Git trailers

These hooks prevent invalid provenance metadata from being committed to your repository.

## Installation

### 1. Install pre-commit

```bash
pip install pre-commit
```

### 2. Install the DTA provenance package

```bash
cd git-native
pip install -e .
```

### 3. Install the pre-commit hooks

From the repository root:

```bash
pre-commit install
pre-commit install --hook-type commit-msg
```

The first command installs hooks that run on `git add`, and the second installs hooks that run on `git commit`.

## Configuration

The repository includes a `.pre-commit-config.yaml` file with the DTA hooks pre-configured:

```yaml
repos:
  - repo: local
    hooks:
      # Validate DTA provenance JSON files
      - id: dta-validate-metadata
        name: Validate DTA Provenance Metadata
        entry: dta-provenance-validate-metadata
        language: system
        files: \.json$
        pass_filenames: true

      # Check commit messages for DTA trailers
      - id: dta-check-trailers
        name: Check DTA Commit Trailers
        entry: dta-provenance-check-trailers
        language: system
        stages: [commit-msg]
        pass_filenames: true
```

## Usage

### Automatic Validation

Once installed, the hooks run automatically:

**When staging files:**

```bash
git add provenance.json
```

If the file contains DTA provenance metadata, it will be validated. Non-provenance JSON files are ignored.

**When creating commits:**

```bash
git commit -m "Add training data"
```

If the commit message includes DTA trailers, they will be validated for completeness.

### Manual Validation

You can run the hooks manually on all files:

```bash
# Run all hooks on all files
pre-commit run --all-files

# Run only the metadata validation hook
pre-commit run dta-validate-metadata --all-files

# Run only the trailer check (requires a commit message file)
echo "Test commit\n\nDTA-Provenance-Metadata: {...}" > /tmp/msg
dta-provenance-check-trailers /tmp/msg
```

## Example Output

### Valid Provenance File

```bash
$ git add provenance/dataset-v1.json
Validate DTA Provenance Metadata.....................................Passed
```

### Invalid Provenance File

```bash
$ git add provenance/invalid.json
Validate DTA Provenance Metadata.....................................Failed
- hook id: dta-validate-metadata
- exit code: 1

❌ Validation failed: provenance/invalid.json
DTA Standards Validation: ❌ INVALID
Compliance Score: 60.0%

Errors:
  ❌ Missing required field: source.providerName
  ❌ Missing required field: provenance.dataType
  ❌ Missing required field: use.sensitiveData

❌ 1 file(s) failed validation
```

### Commit with Missing Trailers

```bash
$ git commit -m "Add data" -m "DTA-Provenance-Metadata: {...}"
Check DTA Commit Trailers............................................Failed
- hook id: dta-check-trailers
- exit code: 1

❌ Commit message has provenance metadata but missing required trailers:
  - DTA-Provenance-Version
  - DTA-Provenance-Hash
  - DTA-Dataset-Name

Use 'dta-provenance commit' to create properly formatted commits.
```

### Valid Commit with Provenance

```bash
$ dta-provenance commit dataset.csv -m provenance.json -M "Add training data"
$ git commit --amend  # Hooks run automatically
Check DTA Commit Trailers............................................Passed
```

## Hook Behavior

### Metadata Validation Hook

- **Runs on:** File staging (`git add`)
- **Validates:** JSON files with `source`, `provenance`, and `use` sections
- **Ignores:** Non-JSON files, JSON files without provenance structure
- **Checks:**
    - Required fields are present
    - Data types are valid
    - Semantic rules (e.g., `sensitiveDataCategories` when `sensitiveData=true`)

### Trailer Check Hook

- **Runs on:** Commit creation (`git commit`)
- **Validates:** Commits with `DTA-Provenance-Metadata` trailer
- **Ignores:** Regular commits without provenance
- **Checks:**
    - All required trailers present (`Version`, `Hash`, `Dataset-Name`, `Metadata`)
    - Metadata JSON is well-formed
    - Metadata has required structure

## Bypassing Hooks (Not Recommended)

In rare cases, you may need to bypass the hooks:

```bash
# Skip all pre-commit hooks
git commit --no-verify -m "Emergency fix"

# Skip specific hook
SKIP=dta-validate-metadata git commit -m "Temporary bypass"
```

**Warning:** Bypassing hooks can result in invalid provenance metadata in your repository.

## Integration with CI/CD

Run the hooks in your CI pipeline to ensure validation even if developers bypass local hooks:

```yaml
# .github/workflows/validate.yml
name: Validate Provenance

on: [push, pull_request]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          pip install pre-commit
          cd git-native && pip install -e .
      - name: Run pre-commit hooks
        run: pre-commit run --all-files
```

## Troubleshooting

### "command not found: dta-provenance-validate-metadata"

The entry points are not installed. Reinstall the package:

```bash
cd git-native
pip install -e .
```

### "pre-commit hook failed but file is valid"

The hook may be using a different Python environment. Check that pre-commit uses the same environment where the package is installed:

```bash
pre-commit run --verbose dta-validate-metadata --all-files
```

### "Hook runs on every JSON file"

This is expected. The hook automatically detects DTA provenance files and ignores others. There's no performance impact on non-provenance JSON files.

## Best Practices

1. **Always use `dta-provenance commit`** for commits with provenance metadata to ensure proper formatting
2. **Run hooks locally** before pushing to catch issues early
3. **Don't bypass hooks** except in emergencies
4. **Keep hooks up to date** with `pre-commit autoupdate`
5. **Use in CI/CD** as a safety net for validation

## Related Commands

- [`dta-provenance validate`](../cli-reference.md#validate) - Manual validation without hooks
- [`dta-provenance commit`](../cli-reference.md#commit) - Create properly formatted commits
- [Pre-commit framework documentation](https://pre-commit.com/)
