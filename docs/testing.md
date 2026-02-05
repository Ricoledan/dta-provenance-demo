# Running Tests

This guide covers running tests for both Git-native and blockchain implementations.

## Git-Native Tests (Python)

### Run All Tests

```bash
cd git-native
pytest
```

### Run with Verbose Output

```bash
pytest -v
```

### Run Specific Test File

```bash
pytest tests/test_provenance.py -v
```

### Run Specific Test

```bash
pytest tests/test_provenance.py::test_commit_with_provenance -v
```

### Run with Coverage

```bash
# Generate coverage report
pytest --cov=src --cov-report=html --cov-report=term

# Open HTML report
open htmlcov/index.html
```

### Expected Results

```
======================== test session starts =========================
collected 24 items

tests/test_provenance.py::test_provenance_metadata_creation PASSED
tests/test_provenance.py::test_commit_with_provenance PASSED
...
======================== 24 passed in 1.00s ==========================

Coverage: 43%+
```

## Blockchain Tests (JavaScript)

### Run All Tests

```bash
cd blockchain
npx hardhat test
```

### Run with Gas Reporting

```bash
npx hardhat test --gas-report
```

### Run Specific Test File

```bash
npx hardhat test test/ProvenanceRegistry.test.js
```

### Expected Results

```
  ProvenanceRegistry
    Deployment
      ✔ Should deploy with zero total records (45ms)
      ✔ Should have correct contract address
    Register Provenance
      ✔ Should register a new provenance record (123ms)
      ✔ Should emit RecordCreated event (89ms)
      ...

  35 passing (375ms)

Gas costs:
  - Registration: ~228,000 gas
  - Verification: ~29,000 gas
```

## Integration Tests

Run both test suites:

```bash
# From project root
cd git-native && pytest && cd ../blockchain && npx hardhat test
```

### Docker Testing

```bash
# Run all tests in Docker
docker-compose up -d
docker-compose exec git-native pytest
docker-compose exec blockchain npx hardhat test
```

## CI/CD Testing

Tests run automatically on every push via GitHub Actions. See [`.github/workflows/test.yml`](../.github/workflows/test.yml).

### Test Matrix

- **Python**: 3.9, 3.10, 3.11, 3.12
- **Node.js**: 18.x, 20.x, 22.x

## Test Coverage Goals

### Git-Native (Python)

- **Target**: 80%+ overall coverage
- **Current**: 43%+
- **Core modules**: 85%+ coverage

### Blockchain (Solidity)

- **Target**: 100% for smart contracts
- **Current**: 100% (35/35 tests passing)

## Writing Tests

### Python Test Example

```python
def test_commit_with_provenance(temp_git_repo, valid_metadata):
    """Test committing files with provenance metadata."""
    tracker = ProvenanceTracker(temp_git_repo)

    # Create test file
    test_file = temp_git_repo / "data.csv"
    test_file.write_text("test,data\n")

    # Commit with provenance
    commit_hash = tracker.commit_with_provenance(
        [test_file],
        valid_metadata,
        "Test commit"
    )

    assert commit_hash is not None
    assert len(commit_hash) == 40  # Git SHA-1 hash
```

### JavaScript Test Example

```javascript
it("Should register a new provenance record", async function () {
    const tx = await provenanceRegistry.registerProvenance(
        "Test Dataset",
        "ipfs://QmTest",
        metadataHash
    );

    const receipt = await tx.wait();
    expect(receipt.status).to.equal(1);
});
```

## Debugging Tests

### Python Debugging

```bash
# Run tests with pdb on failure
pytest --pdb

# Show print statements
pytest -s

# Show local variables in traceback
pytest -l
```

### JavaScript Debugging

```bash
# Run with stack traces
npx hardhat test --show-stack-traces

# Run with verbose logging
npx hardhat test --verbose
```

## Performance Testing

### Git-Native Performance

```bash
# Time test execution
time pytest

# Profile slow tests
pytest --durations=10
```

### Blockchain Gas Profiling

```bash
# Detailed gas report
npx hardhat test --gas-report

# Gas report with USD estimates
COINMARKETCAP_API_KEY=xxx npx hardhat test --gas-report
```

## Continuous Testing

### Watch Mode (Python)

```bash
# Install pytest-watch
pip install pytest-watch

# Run tests on file changes
ptw
```

### Watch Mode (JavaScript)

```bash
# Run tests on file changes
npx hardhat watch test
```

## Test Organization

### Git-Native Tests

```
git-native/tests/
├── test_provenance.py    # Core provenance tracking
├── test_verify.py        # Verification and validation
├── test_cli.py           # CLI commands
└── conftest.py           # Shared fixtures
```

### Blockchain Tests

```
blockchain/test/
└── ProvenanceRegistry.test.js  # Smart contract tests
```

## Best Practices

1. **Write tests first** (TDD approach)
2. **Keep tests independent** (no shared state)
3. **Use descriptive test names**
4. **Test edge cases and errors**
5. **Maintain high coverage**
6. **Run tests before committing**

## Troubleshooting

### Tests Fail Locally But Pass in CI

- Check Python/Node versions match CI
- Verify all dependencies installed
- Check for OS-specific issues

### Slow Tests

- Use `pytest --durations=10` to find slow tests
- Mock external dependencies
- Use test fixtures efficiently

### Flaky Tests

- Avoid time-dependent tests
- Use fixed seeds for randomness
- Properly clean up resources

## Next Steps

- [Contributing Guide](contributing.md) - How to contribute
- [Coverage Report](coverage.md) - View detailed coverage
- [CI/CD Workflow](../.github/workflows/test.yml) - See automation
