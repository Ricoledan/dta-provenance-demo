# Official DTA Standards

This directory contains attribution and references to the official Data & Trust Alliance Data Provenance Standards v1.0.0.

## About the JSON Schema

**Note:** The official JSON Schema file published by the Data & Trust Alliance is incomplete and contains invalid JSON (as of February 2024). The file is missing one closing brace `}` and has 105 opening braces but only 104 closing braces.

https://github.com/Data-and-Trust-Alliance/json-metadata/blob/main/data-provenance-standards-1.0.0.schema.json

**Error:** `Expecting ',' delimiter: line 433 column 1 (char 13839)` - the file ends prematurely

### Impact

This does **not** affect the validity of the DTA standards or this implementation:

- ✅ The DTA v1.0.0 **specification** is valid and well-documented
- ✅ Our examples follow the official specification correctly
- ✅ All 22 required and optional fields are properly implemented
- ✅ Our custom validator still works for structural validation
- ❌ We cannot use `jsonschema.validate()` against the official schema file

### Workarounds

1. **Use the specification documentation** - Manually validate against the [official DTA specification](https://github.com/Data-and-Trust-Alliance/DPS)

2. **Use our validator** - The `ProvenanceVerifier` class provides validation:
   ```python
   from src.verify import validate_provenance_file

   report = validate_provenance_file('metadata.json')
   print(report)  # Shows compliance score and missing fields
   ```

3. **Report the issue** - Consider opening an issue at: https://github.com/Data-and-Trust-Alliance/json-metadata/issues

## References

- **Specification:** https://github.com/Data-and-Trust-Alliance/DPS
- **Website:** https://www.dtaalliance.org/
- **JSON Metadata Repo:** https://github.com/Data-and-Trust-Alliance/json-metadata

See [ATTRIBUTION.md](ATTRIBUTION.md) for full credits.
