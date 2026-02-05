# Contributing to DTA Provenance Demo

Thank you for your interest in contributing to this project! We welcome contributions from the community.

## Ways to Contribute

- 🐛 **Report Bugs** - Found an issue? Let us know!
- 💡 **Suggest Features** - Have an idea? We'd love to hear it!
- 📝 **Improve Documentation** - Help make our docs clearer
- 🔧 **Submit Code** - Fix bugs or add features
- 🎨 **Design Assets** - Create diagrams, logos, or demos
- 📚 **Add Examples** - Share your use case

## Getting Started

### 1. Fork and Clone

```bash
# Fork on GitHub, then clone your fork
git clone https://github.com/YOUR_USERNAME/dta-provenance-demo.git
cd dta-provenance-demo

# Add upstream remote
git remote add upstream https://github.com/ORIGINAL_OWNER/dta-provenance-demo.git
```

### 2. Set Up Development Environment

**Python (Git-Native):**
```bash
cd git-native
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
pip install -e ".[dev]"
```

**Node.js (Blockchain):**
```bash
cd blockchain
npm install
```

### 3. Create a Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/your-bug-fix
```

## Development Workflow

### Python Development

**Run Tests:**
```bash
cd git-native
pytest                          # Run all tests
pytest -v                       # Verbose output
pytest --cov=src               # With coverage
pytest tests/test_provenance.py # Specific file
```

**Code Formatting:**
```bash
black src/ tests/               # Format code
ruff check src/ tests/          # Lint
mypy src/                       # Type check
```

**Manual Testing:**
```bash
dta-provenance --help
dta-provenance validate ../standards/examples/healthcare-imaging.json
```

### Blockchain Development

**Compile Contracts:**
```bash
cd blockchain
npx hardhat compile
```

**Run Tests:**
```bash
npx hardhat test
npx hardhat test --gas-report
```

**Deploy Locally:**
```bash
# Terminal 1
npx hardhat node

# Terminal 2
npx hardhat run scripts/deploy.js --network localhost
```

## Code Standards

### Python Code Style

- **Formatting:** Use `black` (line length 88)
- **Linting:** Pass `ruff` checks
- **Type Hints:** Add type hints to all functions
- **Docstrings:** Use Google-style docstrings

**Example:**
```python
def commit_with_provenance(
    self,
    file_paths: List[Path],
    metadata: ProvenanceMetadata,
    message: str,
    sign: bool = False
) -> str:
    """
    Create a Git commit with provenance metadata.

    Args:
        file_paths: Files to commit (relative to repo root)
        metadata: DTA-compliant provenance metadata
        message: Commit message
        sign: Whether to GPG/SSH sign the commit

    Returns:
        Commit SHA hash

    Raises:
        ValueError: If files don't exist or metadata is invalid
    """
    # Implementation
```

### Solidity Code Style

- **Version:** Solidity ^0.8.20
- **Comments:** NatSpec format for all public functions
- **Testing:** Add tests for all new contract functions
- **Gas Optimization:** Consider gas costs

**Example:**
```solidity
/**
 * @dev Register a new provenance record
 * @param _datasetName Human-readable name of the dataset
 * @param _metadataURI URI pointing to full DTA metadata
 * @param _metadataHash SHA-256 hash of the metadata
 * @return recordId Unique identifier for this record
 */
function registerProvenance(
    string memory _datasetName,
    string memory _metadataURI,
    bytes32 _metadataHash
) public returns (bytes32) {
    // Implementation
}
```

### Documentation Style

- **Markdown:** Use GitHub-flavored markdown
- **Examples:** Include code examples
- **Clear Headers:** Use proper heading hierarchy
- **Links:** Check all links work

## Testing Requirements

### Python Tests

All new code should have tests:

```python
def test_new_feature():
    """Test description."""
    # Arrange
    tracker = ProvenanceTracker(Path("."))

    # Act
    result = tracker.new_feature()

    # Assert
    assert result == expected_value
```

**Coverage Target:** 80%+ for new code

### Solidity Tests

```javascript
describe("ProvenanceRegistry", function () {
  it("Should register provenance record", async function () {
    const registry = await ProvenanceRegistry.deploy();

    const tx = await registry.registerProvenance(
      "Test Dataset",
      "ipfs://Qm...",
      ethers.utils.randomBytes(32)
    );

    await expect(tx).to.emit(registry, "RecordCreated");
  });
});
```

## Commit Message Guidelines

Follow conventional commits:

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation only
- `style`: Formatting, missing semicolons, etc.
- `refactor`: Code restructuring
- `test`: Adding tests
- `chore`: Maintenance tasks

**Examples:**
```
feat(cli): add --output option to show command

Add ability to export provenance metadata to file:
  dta-provenance show HEAD --output metadata.json

Closes #123
```

```
fix(provenance): handle missing metadata fields gracefully

Previously crashed with KeyError when optional fields missing.
Now returns default values and logs warning.

Fixes #456
```

## Pull Request Process

### 1. Update Your Branch

```bash
git fetch upstream
git rebase upstream/main
```

### 2. Run All Checks

```bash
# Python
cd git-native
pytest
black --check src/ tests/
ruff check src/ tests/
mypy src/

# Blockchain
cd blockchain
npx hardhat compile
npx hardhat test
```

### 3. Push to Your Fork

```bash
git push origin feature/your-feature-name
```

### 4. Create Pull Request

Go to GitHub and create a PR with:

**Title:** Clear, descriptive title

**Description:**
```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Tests pass locally
- [ ] Added new tests for changes
- [ ] Coverage maintained or improved

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No new warnings

## Related Issues
Fixes #123
```

### 5. Code Review

- Address review comments
- Push updates to same branch
- Request re-review when ready

### 6. Merge

Once approved, maintainer will merge your PR.

## Types of Contributions

### Bug Reports

**Good Bug Report:**
```markdown
**Description**
Clear description of the bug

**To Reproduce**
Steps to reproduce:
1. Run command '...'
2. See error

**Expected Behavior**
What should happen

**Actual Behavior**
What actually happens

**Environment**
- OS: macOS 13.0
- Python: 3.11
- Git: 2.39

**Error Messages**
```
Full error traceback here
```
```

### Feature Requests

**Good Feature Request:**
```markdown
**Problem**
Describe the problem this feature solves

**Proposed Solution**
Describe your proposed solution

**Alternatives Considered**
What alternatives did you consider?

**Use Case**
How would you use this feature?
```

### Adding Examples

We welcome new DTA-compliant example datasets!

**Requirements:**
- All 22 fields properly documented
- Real-world or realistic use case
- Inline comments explaining choices
- README section explaining the example

**Example PR:**
```markdown
Add satellite imagery dataset example

- Complete DTA metadata for Earth observation data
- Includes geospatial provenance details
- Documents ESA licensing terms
- Explains privacy considerations for location data
```

## Areas Needing Help

### High Priority
- [ ] Blockchain test suite (test/ProvenanceRegistry.test.js)
- [ ] CI/CD workflows (.github/workflows/)
- [ ] Screen recording GIF demo
- [ ] Architecture diagrams (SVG)

### Medium Priority
- [ ] Jupyter notebook tutorial
- [ ] MLflow integration example
- [ ] DVC integration example
- [ ] GitHub Action for provenance validation
- [ ] Additional real-world examples

### Low Priority
- [ ] VS Code extension
- [ ] Frontend dashboard
- [ ] Docker containers
- [ ] Multi-blockchain support

## Community

### Communication

- **Issues:** Use GitHub Issues for bugs and features
- **Discussions:** Use GitHub Discussions for questions
- **Security:** Email security@example.com for vulnerabilities

### Code of Conduct

Be respectful and inclusive. We follow the [Contributor Covenant](https://www.contributor-covenant.org/).

### Recognition

Contributors are recognized in:
- README.md contributors section (when added)
- Git commit history
- Release notes

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

## Questions?

Not sure where to start? Open a GitHub Discussion and we'll help you find a good first issue!

---

Thank you for contributing! 🎉
