# DTA Provenance Validator for VS Code

A Visual Studio Code extension for validating Data & Trust Alliance (DTA) v1.0.0 provenance metadata with Git integration.

## Features

### Automatic Validation
- **On-Save Validation**: Automatically validates DTA provenance metadata when you save JSON files
- **Real-time Diagnostics**: Shows errors and warnings inline in your editor
- **Status Bar Integration**: Quick compliance score display

### DTA v1.0.0 Compliance
- Validates all required fields (source, provenance, use)
- Checks recommended fields
- Semantic validation (e.g., sensitiveDataCategories when sensitiveData=true)
- Data type validation against standard types
- ISO 8601 date format validation

### Git Integration
- **Show Provenance History**: View DTA provenance metadata from Git commits
- **Commit Tracking**: Extract and display provenance metadata stored in Git trailers
- **Audit Trail**: Complete history of all commits affecting a file

### Code Snippets
- `dta-template` - Complete DTA v1.0.0 template
- `dta-minimal` - Minimal template with required fields only
- `dta-source` - Source metadata section
- `dta-provenance` - Provenance metadata section
- `dta-use` - Use metadata section

### JSON Schema
- Built-in JSON schema for IntelliSense and validation
- Auto-completion for DTA fields
- Hover documentation

## Usage

### Validate a File

1. Open a JSON file containing DTA provenance metadata
2. The extension automatically validates files matching:
   - `**/provenance*.json`
   - `**/dta-metadata.json`
   - Any JSON file with "provenance" or "metadata" in the name
3. Or run: `Cmd+Shift+P` → "DTA: Validate Provenance Metadata"

### View Git Provenance

1. Open any file in your Git repository
2. Run: `Cmd+Shift+P` → "DTA: Show Git Provenance"
3. View commits with DTA provenance metadata

### Use Snippets

1. In a JSON file, type `dta-` and press `Ctrl+Space`
2. Select a snippet:
   - `dta-template` for complete template
   - `dta-minimal` for minimal required fields
   - `dta-source`, `dta-provenance`, `dta-use` for individual sections

## Configuration

Access settings via `Cmd+,` → Search "DTA"

- `dta.validateOnSave` (default: `true`) - Automatically validate on file save
- `dta.showStatusBar` (default: `true`) - Show compliance score in status bar
- `dta.strictValidation` (default: `false`) - Treat warnings as errors

## Example

Create a new file `provenance.json`:

```json
{
  "source": {
    "datasetName": "Customer Churn Data",
    "providerName": "Analytics Team"
  },
  "provenance": {
    "dataGenerationMethod": "SQL export from production database",
    "dateDataGenerated": "2024-01-15T00:00:00Z",
    "dataType": "Tabular",
    "dataFormat": "CSV"
  },
  "use": {
    "intendedUse": "ML model training for churn prediction",
    "legalRightsToUse": "Internal use only",
    "sensitiveData": false
  }
}
```

The extension will:
- Validate required fields
- Show warnings for missing recommended fields
- Display compliance score in status bar
- Provide IntelliSense for field names

## Requirements

- VS Code 1.70.0 or higher
- Git (for provenance history features)

## Commands

| Command | Description |
|---------|-------------|
| `DTA: Validate Provenance Metadata` | Validate current file |
| `DTA: Show Git Provenance` | Show Git provenance history |

## Validation Rules

### Required Fields

**source:**
- `datasetName` - Name of the dataset
- `providerName` - Data provider name

**provenance:**
- `dataGenerationMethod` - How data was generated
- `dateDataGenerated` - When data was generated (ISO 8601)
- `dataType` - Type of data (Text, Image, Audio, Video, Time series, Tabular, Graph, Geospatial, Multi-modal)
- `dataFormat` - Format (CSV, JSON, Parquet, etc.)

**use:**
- `intendedUse` - Purpose of the data
- `legalRightsToUse` - Legal basis for use
- `sensitiveData` - Boolean indicating if data is sensitive

### Semantic Rules

- If `sensitiveData` is `true`, `sensitiveDataCategories` is required
- Dates should be in ISO 8601 format
- `dataType` should be one of the standard types

## Extension Development

### Building

```bash
cd vscode-extension
npm install
npm run compile
```

### Testing

```bash
npm test
```

### Packaging

```bash
npm install -g vsce
vsce package
```

This creates a `.vsix` file you can install with:
```bash
code --install-extension dta-provenance-validator-0.1.0.vsix
```

## Integration with Python Library

This extension complements the Python library:

```bash
# Install Python library
pip install dta-provenance

# Use CLI
dta-provenance validate provenance.json

# Create Git commits with provenance
dta-provenance commit dataset.csv --metadata provenance.json
```

## Links

- [DTA Provenance Standards v1.0.0](https://www.dtaalliance.org/work/data-provenance-standards)
- [Project Repository](https://github.com/Ricoledan/dta-provenance-demo)
- [Documentation](https://ricoledan.github.io/dta-provenance-demo)

## License

MIT License - see [LICENSE](../LICENSE) for details.

## Credits

Implements the official [Data & Trust Alliance](https://www.dtaalliance.org/) Data Provenance Standards v1.0.0.
