# VS Code Extension Tutorial

This guide shows you how to use the DTA Provenance Validator VS Code extension for validating and managing DTA v1.0.0 provenance metadata.

## Installation

### From Source (Development)

1. **Navigate to extension directory:**
   ```bash
   cd git-native/vscode-extension
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Compile TypeScript:**
   ```bash
   npm run compile
   ```

4. **Package the extension:**
   ```bash
   npm install -g vsce
   vsce package
   ```

5. **Install in VS Code:**
   ```bash
   code --install-extension dta-provenance-validator-0.1.0.vsix
   ```

### From VS Code Marketplace (Future)

Once published:
1. Open VS Code
2. Press `Cmd+Shift+X` (Extensions)
3. Search for "DTA Provenance Validator"
4. Click Install

## Features

### 1. Automatic Validation

The extension automatically validates DTA provenance metadata files when you save them.

**Supported file patterns:**
- `**/provenance*.json`
- `**/dta-metadata.json`
- Any JSON file with "provenance" or "metadata" in the name

**What it validates:**
- All required fields (source, provenance, use)
- Recommended optional fields
- Data type values
- Date formats (ISO 8601)
- Semantic rules (e.g., sensitiveDataCategories when sensitiveData=true)

**Example:**

Create `provenance.json`:
```json
{
  "source": {
    "datasetName": "Customer Data",
    "providerName": "Analytics Team"
  },
  "provenance": {
    "dataGenerationMethod": "SQL export",
    "dateDataGenerated": "2024-01-15T00:00:00Z",
    "dataType": "Tabular",
    "dataFormat": "CSV"
  },
  "use": {
    "intendedUse": "ML training",
    "legalRightsToUse": "Internal",
    "sensitiveData": false
  }
}
```

Save the file (Cmd+S) and see:
- ✅ Validation results in the output panel
- Status bar showing compliance score
- Inline diagnostics for any issues

### 2. Manual Validation

Validate any file on demand:

1. Open a JSON file
2. Press `Cmd+Shift+P`
3. Type "DTA: Validate Provenance Metadata"
4. Press Enter

Results appear in:
- Output panel (DTA Provenance channel)
- Status bar (compliance score)
- Inline diagnostics (red/yellow squiggles)

### 3. Code Snippets

Speed up metadata creation with snippets:

#### Complete Template

1. Type `dta-template`
2. Press `Tab`
3. Fill in the placeholders

```json
{
  "source": {
    "datasetName": "Dataset Name",    // Tab to next field
    "datasetVersion": "1.0.0",
    "providerName": "Provider Name",
    ...
  },
  ...
}
```

#### Minimal Template

For quick setup with required fields only:

1. Type `dta-minimal`
2. Press `Tab`

#### Section Templates

Add individual sections:
- `dta-source` - Source metadata
- `dta-provenance` - Provenance metadata
- `dta-use` - Use metadata

### 4. JSON Schema Integration

The extension provides JSON schema support for:

**IntelliSense:**
- Field name auto-completion
- Value suggestions (e.g., dataType values)
- Hover documentation

**Usage:**

1. Open a provenance JSON file
2. Start typing a field name
3. Press `Ctrl+Space` for suggestions

Example:
```json
{
  "source": {
    "data[Ctrl+Space]  // Shows: datasetName, datasetVersion, etc.
  }
}
```

### 5. Git Provenance History

View DTA provenance metadata from Git commits:

1. Open any file in a Git repository
2. Press `Cmd+Shift+P`
3. Type "DTA: Show Git Provenance"
4. Press Enter

**What you see:**
- Commits containing DTA provenance metadata
- Complete metadata from each commit
- Full commit history for the file
- Author, date, and commit message

**Example Git commit with provenance:**

```bash
git commit -m "$(cat <<'EOF'
Add training dataset

DTA-Provenance-Version: 1.0.0
DTA-Provenance-Hash: abc123...
DTA-Dataset-Name: Customer Churn Data
DTA-Provenance-Metadata: {"source":{...},"provenance":{...},"use":{...}}
EOF
)"
```

The extension extracts and displays this metadata in a readable format.

## Configuration

### Settings

Access via `Cmd+,` → Search "DTA"

**dta.validateOnSave** (default: `true`)
- Automatically validate when saving files
- Disable for manual validation only

**dta.showStatusBar** (default: `true`)
- Show compliance score in status bar
- Disable to hide status bar item

**dta.strictValidation** (default: `false`)
- Treat warnings as errors
- Useful for CI/CD pipelines

### Example Configuration

`.vscode/settings.json`:
```json
{
  "dta.validateOnSave": true,
  "dta.showStatusBar": true,
  "dta.strictValidation": false
}
```

## Validation Examples

### Valid Metadata

```json
{
  "source": {
    "datasetName": "Healthcare Imaging Dataset",
    "datasetVersion": "2.1.0",
    "providerName": "City Hospital Research Dept",
    "providerWebsite": "https://hospital.example.com/research"
  },
  "provenance": {
    "dataGenerationMethod": "CT scans from clinical imaging systems",
    "dateDataGenerated": "2023-06-01T00:00:00Z",
    "dataType": "Image",
    "dataFormat": "DICOM",
    "qualityIndicators": {
      "completeness": 0.98,
      "deIdentificationScore": 1.0
    }
  },
  "use": {
    "intendedUse": "Training ML models for disease detection",
    "legalRightsToUse": "Institutional approval with consent",
    "restrictions": ["No commercial use", "Research only"],
    "sensitiveData": true,
    "sensitiveDataCategories": ["Health/Medical"],
    "privacyMeasures": ["De-identification", "HIPAA compliance"],
    "retentionPolicy": "10 years per IRB requirements",
    "attribution": "City Hospital Research Department, 2023"
  }
}
```

**Result:** ✅ 100% compliance

### Missing Required Fields

```json
{
  "source": {
    "datasetName": "My Dataset"
    // Missing: providerName
  },
  "provenance": {
    "dataGenerationMethod": "Manual entry"
    // Missing: dateDataGenerated, dataType, dataFormat
  },
  "use": {
    "intendedUse": "Analysis"
    // Missing: legalRightsToUse, sensitiveData
  }
}
```

**Result:** ❌ Errors
- Missing required field: source.providerName
- Missing required field: provenance.dateDataGenerated
- Missing required field: provenance.dataType
- Missing required field: provenance.dataFormat
- Missing required field: use.legalRightsToUse
- Missing required field: use.sensitiveData

### Semantic Validation Error

```json
{
  "source": {
    "datasetName": "Patient Records",
    "providerName": "Hospital"
  },
  "provenance": {
    "dataGenerationMethod": "EHR export",
    "dateDataGenerated": "2024-01-15T00:00:00Z",
    "dataType": "Tabular",
    "dataFormat": "CSV"
  },
  "use": {
    "intendedUse": "Research",
    "legalRightsToUse": "IRB approved",
    "sensitiveData": true
    // Missing: sensitiveDataCategories (required when sensitiveData=true)
  }
}
```

**Result:** ❌ Error
- sensitiveDataCategories is required when sensitiveData is true

⚠️ Warning:
- privacyMeasures strongly recommended when sensitiveData is true

## Integration with Python CLI

The VS Code extension complements the Python CLI tool:

### Workflow Example

**1. Create metadata in VS Code:**

Use snippets to create `provenance.json`, validate with extension.

**2. Commit with Python CLI:**

```bash
dta-provenance commit dataset.csv \
  --metadata provenance.json \
  --message "Add customer dataset v1.0"
```

**3. View in VS Code:**

Open `dataset.csv`, run "DTA: Show Git Provenance" to see metadata.

**4. Verify integrity:**

```bash
dta-provenance verify HEAD
```

### CI/CD Integration

Use strict validation in CI:

```yaml
# .github/workflows/validate.yml
- name: Validate metadata
  run: |
    code --install-extension dta-provenance-validator-*.vsix
    # Run validation tests
```

Or use Python CLI:
```yaml
- name: Validate metadata
  run: dta-provenance validate data/provenance.json
```

## Troubleshooting

### Extension Not Activating

**Check:**
1. File is `.json` format
2. Filename contains "provenance" or "metadata"
3. Open Command Palette: "Developer: Show Running Extensions"

**Fix:**
- Reload VS Code: `Cmd+Shift+P` → "Developer: Reload Window"

### Validation Not Working

**Check:**
1. Settings: `dta.validateOnSave` is enabled
2. No JSON syntax errors (must parse as valid JSON first)
3. Check Output panel: "DTA Provenance" channel

**Fix:**
- Run manual validation: `Cmd+Shift+P` → "DTA: Validate"
- Check for JSON parse errors first

### Git Provenance Not Showing

**Check:**
1. File is in a Git repository
2. File has commit history
3. Git is installed and in PATH

**Fix:**
```bash
# Verify Git is working
git --version
git log --oneline
```

## Advanced Usage

### Custom File Patterns

Edit `.vscode/settings.json`:

```json
{
  "files.associations": {
    "**/my-custom-metadata.json": "json",
    "**/datasets/*.meta": "json"
  }
}
```

### Workspace Recommendations

Create `.vscode/extensions.json`:

```json
{
  "recommendations": [
    "dta-provenance-demo.dta-provenance-validator"
  ]
}
```

Team members get prompted to install the extension.

### Multi-root Workspaces

Configure per-folder:

```json
{
  "folders": [
    {
      "path": "project1",
      "settings": {
        "dta.strictValidation": true
      }
    },
    {
      "path": "project2",
      "settings": {
        "dta.strictValidation": false
      }
    }
  ]
}
```

## Next Steps

- **Tutorial:** [Pre-commit Hooks](pre-commit-hooks.md) - Automate validation
- **Tutorial:** [DVC Integration](dvc-integration.md) - Large file tracking
- **Tutorial:** [MLflow Integration](mlflow-integration.md) - ML experiment tracking
- **Reference:** [API Reference](api-reference.md) - Python library API

## Additional Resources

- [VS Code Extension API](https://code.visualstudio.com/api)
- [DTA Standards v1.0.0](https://www.dtaalliance.org/)
- [Extension Source Code](../../git-native/vscode-extension/)
