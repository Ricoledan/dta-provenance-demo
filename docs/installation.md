# Installation Guide

This guide covers all installation methods for the DTA Provenance Demo.

## Requirements

### Git-Native Implementation
- Python 3.9 or higher
- Git 2.30 or higher
- pip package manager

### Blockchain Implementation
- Node.js 18 or higher
- npm 9 or higher

## Installation Methods

### Option 1: Nix (Recommended)

Nix provides a fully reproducible development environment:

```bash
# Install Nix (if not already installed)
curl -L https://nixos.org/nix/install | sh

# Clone repository
git clone https://github.com/Ricoledan/dta-provenance-demo.git
cd dta-provenance-demo

# Enter development environment
nix develop

# Everything is ready!
dta-provenance --help
```

**Benefits:**
- ✅ Reproducible environment
- ✅ All dependencies managed
- ✅ No conflicts with system packages
- ✅ Easy to set up and teardown

See [Nix Setup Guide](nix-setup.md) for detailed instructions.

### Option 2: Docker

Docker provides isolated containers for each component:

```bash
# Clone repository
git clone https://github.com/Ricoledan/dta-provenance-demo.git
cd dta-provenance-demo

# Start all services
docker-compose up -d

# Access services
# Jupyter: http://localhost:8888
# Blockchain RPC: http://localhost:8545

# Use CLI
docker-compose exec git-native dta-provenance --help
```

**Benefits:**
- ✅ One-command setup
- ✅ Isolated environments
- ✅ Production-ready
- ✅ Easy deployment

See [Docker Setup Guide](docker-setup.md) for detailed instructions.

### Option 3: Manual Installation

#### Git-Native (Python)

```bash
# Clone repository
git clone https://github.com/Ricoledan/dta-provenance-demo.git
cd dta-provenance-demo

# Install Python dependencies
cd git-native
pip install -r requirements.txt
pip install -e .

# Verify installation
dta-provenance --version
dta-provenance --help
```

#### Blockchain (Node.js)

```bash
# From project root
cd blockchain

# Install dependencies
npm install

# Verify installation
npx hardhat --version

# Run tests
npx hardhat test
```

## Verification

### Verify Git-Native Installation

```bash
# Check CLI is available
dta-provenance --version

# Validate an example
dta-provenance validate standards/examples/healthcare-imaging.json

# Run tests
cd git-native
pytest
```

### Verify Blockchain Installation

```bash
# Check Hardhat is working
cd blockchain
npx hardhat --version

# Compile contracts
npx hardhat compile

# Run tests
npx hardhat test

# Start local node (optional)
npx hardhat node
```

## Troubleshooting

### Python Version Issues

If you encounter Python version errors:

```bash
# Check Python version
python --version

# Use pyenv to manage Python versions
pyenv install 3.11
pyenv local 3.11
```

### Node Version Issues

If you encounter Node version errors:

```bash
# Check Node version
node --version

# Use nvm to manage Node versions
nvm install 20
nvm use 20
```

### Permission Issues

If you encounter permission errors:

```bash
# Use a virtual environment (Python)
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Fix npm permissions
npm config set prefix ~/.npm-global
export PATH=~/.npm-global/bin:$PATH
```

### Git Configuration

The provenance tracker requires Git user configuration:

```bash
# Set Git user (if not already set)
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

## Development Setup

For active development:

```bash
# Install development dependencies
cd git-native
pip install -r requirements.txt
pip install pytest pytest-cov black flake8 isort

# Install pre-commit hooks (optional)
pip install pre-commit
pre-commit install

# Run linting
black src/ tests/
flake8 src/ tests/
isort src/ tests/

# Run tests with coverage
pytest --cov=src --cov-report=html
```

## IDE Integration

### VS Code

Recommended extensions:
- Python (ms-python.python)
- Jupyter (ms-toolsai.jupyter)
- Solidity (juanblanco.solidity)
- Docker (ms-azuretools.vscode-docker)

### PyCharm

Configure Python interpreter to use the virtual environment or Nix shell.

## Next Steps

- [Quick Start Guide](quickstart.md)
- [DTA Standards Overview](DTA_STANDARDS.md)
- [Basic Usage Tutorial](tutorials/basic-usage.md)
- [API Reference](tutorials/api-reference.md)

## Getting Help

- **Issues**: [GitHub Issues](https://github.com/Ricoledan/dta-provenance-demo/issues)
- **Documentation**: [Full Documentation](https://ricoledan.github.io/dta-provenance-demo)
- **Contributing**: [Contributing Guide](CONTRIBUTING.md)
