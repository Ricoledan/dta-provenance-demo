# Test Coverage

Current test coverage for the DTA Provenance Demo.

## Git-Native (Python)

### Overall Coverage

```
Module               Stmts   Miss  Cover
----------------------------------------
src/__init__.py         4      0   100%
src/provenance.py     137     66    52%
src/verify.py         146     66    55%
src/cli.py            136     69    49%
src/visualize.py       96     96     0%
----------------------------------------
TOTAL                 519    297    43%
```

### Coverage Goals

- **Current**: 43% overall
- **Target**: 80%+ overall
- **Core modules**: 85%+ (provenance.py currently at 52%)

### What's Tested

✅ **Provenance Tracking** (52% coverage)
- Metadata creation and validation
- Git commit integration
- Hash computation
- File tracking

✅ **Verification** (55% coverage)
- DTA compliance checking
- Commit integrity verification
- Metadata validation

✅ **CLI** (49% coverage)
- Command parsing
- Basic commands
- Error handling

❌ **Visualization** (0% coverage)
- Graph generation (needs tests)
- Lineage tracing visualization

### Improving Coverage

Priority areas for improvement:

1. **CLI Module** (currently 49%)
   - Add end-to-end CLI tests
   - Test all commands
   - Test error scenarios

2. **Visualization Module** (currently 0%)
   - Add graph generation tests
   - Test different output formats
   - Test edge cases

3. **Core Modules** (currently 52-55%)
   - Test error paths
   - Test edge cases
   - Add integration tests

### Running Coverage Reports

```bash
cd git-native

# Terminal report
pytest --cov=src --cov-report=term-missing

# HTML report
pytest --cov=src --cov-report=html
open htmlcov/index.html

# XML report (for CI)
pytest --cov=src --cov-report=xml
```

## Blockchain (Solidity)

### Overall Coverage

```
Contract                Lines   Statements   Branches   Coverage
-----------------------------------------------------------------
ProvenanceRegistry        215       100%        100%      100%
```

### Test Statistics

- **Total Tests**: 35
- **Passing**: 35 (100%)
- **Test Files**: 1
- **Test Suites**: 8

### What's Tested

✅ **Contract Deployment**
- Initialization
- State variables

✅ **Provenance Registration**
- Record creation
- Validation
- Event emission
- Multi-provider scenarios

✅ **Record Verification**
- Verification process
- Access control
- Event emission

✅ **Metadata Validation**
- Hash validation
- Integrity checks

✅ **Metadata Updates**
- Update permissions
- Event emission
- State changes

✅ **Provider Records**
- Record tracking
- Count queries
- Multi-record scenarios

✅ **Record Existence**
- Existence checks
- Non-existent records

✅ **Gas Optimization**
- Gas cost benchmarking
- Performance metrics

### Gas Costs

From test execution:

| Operation | Gas Used | Est. Cost (50 gwei) |
|-----------|----------|---------------------|
| Register provenance | ~228,000 | ~$5-20 |
| Verify record | ~29,000 | ~$0.50-5 |
| Update metadata | ~45,000 | ~$1-10 |

### Running Coverage

```bash
cd blockchain

# Run all tests
npx hardhat test

# With gas reporting
npx hardhat test --gas-report

# With coverage (requires solidity-coverage)
npm install --save-dev solidity-coverage
npx hardhat coverage
```

## CI/CD Coverage

### GitHub Actions

Coverage is automatically:
- Collected on every push
- Reported in PR comments
- Uploaded to Codecov (optional)

See [`.github/workflows/test.yml`](../.github/workflows/test.yml).

### Coverage Badges

Add badges to README.md:

```markdown
[![Coverage Status](https://codecov.io/gh/Ricoledan/dta-provenance-demo/branch/main/graph/badge.svg)](https://codecov.io/gh/Ricoledan/dta-provenance-demo)
```

## Coverage Trends

### Historical Trends

| Date | Python Coverage | Blockchain Coverage |
|------|----------------|---------------------|
| 2024-02-05 | 43% | 100% |
| 2024-02-04 | 28% | 0% (tests added) |
| Initial | 28% | N/A |

### Improvement Plan

**Phase 1: Core Coverage** (Target: 60%)
- [x] Add verify module tests
- [x] Add CLI basic tests
- [ ] Complete CLI coverage
- [ ] Add error path tests

**Phase 2: Feature Coverage** (Target: 80%)
- [ ] Add visualization tests
- [ ] Add integration tests
- [ ] Test edge cases

**Phase 3: Excellence** (Target: 90%+)
- [ ] Property-based testing
- [ ] Performance tests
- [ ] Security tests

## Contributing to Coverage

### Adding Tests

1. Identify untested code:
   ```bash
   pytest --cov=src --cov-report=html
   open htmlcov/index.html
   ```

2. Write tests for red/yellow lines

3. Run tests locally:
   ```bash
   pytest tests/test_your_module.py -v
   ```

4. Verify coverage improved:
   ```bash
   pytest --cov=src --cov-report=term
   ```

### Coverage Requirements

For new code:
- Core functionality: 90%+
- CLI commands: 80%+
- Utility functions: 70%+

### Pull Request Checks

PRs must:
- Not decrease overall coverage
- Include tests for new features
- Test error conditions

## Resources

- [pytest-cov Documentation](https://pytest-cov.readthedocs.io/)
- [Coverage.py Documentation](https://coverage.readthedocs.io/)
- [Solidity Coverage](https://github.com/sc-forks/solidity-coverage)

---

**Help improve coverage!** See [Contributing Guide](contributing.md).
