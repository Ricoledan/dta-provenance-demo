# Nix Development Environment Setup

This project provides a Nix flake for reproducible development environments.

## For Nix Users (Recommended)

### Prerequisites

- [Nix](https://nixos.org/download.html) with flakes enabled
- Optional: [direnv](https://direnv.net/) for automatic environment loading

### Enable Flakes

If you haven't already, enable flakes in your Nix configuration:

```bash
# Add to ~/.config/nix/nix.conf or /etc/nix/nix.conf
experimental-features = nix-command flakes
```

### Quick Start

```bash
# Clone the repository
git clone https://github.com/yourusername/dta-provenance-demo.git
cd dta-provenance-demo

# Enter the development environment
nix develop

# Everything is now set up! Try:
dta-provenance --help
cd blockchain && npm install
npx hardhat compile
```

### With direnv (Automatic)

If you have direnv installed:

```bash
cd dta-provenance-demo

# Allow direnv to load the environment
direnv allow

# Environment loads automatically whenever you cd into the directory!
```

### What's Included

The Nix environment provides:

- ✅ **Python 3.11** with all dependencies
  - GitPython, Click, Rich, jsonschema, networkx
  - pytest, pytest-cov, black, mypy, ruff
- ✅ **Node.js 20** with npm
- ✅ **Git 2.30+**
- ✅ **Hardhat** for blockchain development
- ✅ **Graphviz** for graph visualization
- ✅ **Development tools** (jq, curl)

### Development Workflow

```bash
# Enter environment
nix develop

# Git-native development
cd git-native
pytest                    # Tests auto-run
dta-provenance --help    # CLI available

# Blockchain development
cd blockchain
npm install              # Install JS dependencies
npx hardhat compile     # Compile contracts
npx hardhat test        # Run tests

# Leave environment
exit
```

### Installing Packages

The git-native package is automatically installed in development mode when you enter the environment.

For additional Python packages:

```bash
# Inside nix develop
pip install package-name
```

For additional Node packages:

```bash
cd blockchain
npm install package-name
```

### Updating Dependencies

Edit `flake.nix` and run:

```bash
nix flake update
nix develop
```

---

## For Non-Nix Users

If you don't use Nix, follow these manual setup instructions:

### Prerequisites

Install these manually:

1. **Python 3.9+**
   ```bash
   # macOS
   brew install python@3.11

   # Ubuntu/Debian
   sudo apt install python3.11 python3.11-venv python3-pip

   # Windows
   # Download from https://www.python.org/downloads/
   ```

2. **Node.js 18+**
   ```bash
   # macOS
   brew install node@20

   # Ubuntu/Debian
   curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
   sudo apt install nodejs

   # Windows
   # Download from https://nodejs.org/
   ```

3. **Git 2.30+**
   ```bash
   # macOS
   brew install git

   # Ubuntu/Debian
   sudo apt install git

   # Windows
   # Download from https://git-scm.com/
   ```

### Git-Native Setup

```bash
cd git-native

# Create virtual environment
python -m venv venv

# Activate virtual environment
source venv/bin/activate  # macOS/Linux
# or
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Install in development mode
pip install -e .

# Verify installation
dta-provenance --help

# Run tests
pytest -v
```

### Blockchain Setup

```bash
cd blockchain

# Install dependencies
npm install

# Compile contracts
npx hardhat compile

# Run tests (when implemented)
npx hardhat test

# Start local blockchain
npx hardhat node
```

### Optional: Graphviz (for visualization)

```bash
# macOS
brew install graphviz
pip install pygraphviz

# Ubuntu/Debian
sudo apt install graphviz libgraphviz-dev
pip install pygraphviz

# Windows
# Download from https://graphviz.org/download/
# Then: pip install pygraphviz
```

---

## Comparing Approaches

### Nix Advantages

✅ **Reproducible** - Exact same environment on any machine
✅ **Declarative** - All dependencies in one file
✅ **Isolated** - Doesn't pollute your system
✅ **Automatic** - Everything installs with one command
✅ **Version pinning** - No "works on my machine" issues

### Manual Advantages

✅ **Familiar** - Uses standard tools (pip, npm)
✅ **Flexible** - Easy to modify for your needs
✅ **No learning curve** - Standard development workflow

---

## Troubleshooting

### Nix: "experimental-features" error

Enable flakes:
```bash
mkdir -p ~/.config/nix
echo "experimental-features = nix-command flakes" >> ~/.config/nix/nix.conf
```

### Nix: Building takes too long

Use the binary cache:
```bash
# Add to nix.conf
substituters = https://cache.nixos.org
trusted-public-keys = cache.nixos.org-1:6NCHdD59X431o0gWypbMrAURkbJ16ZPMQFGspcDShjY=
```

### Manual: "command not found: dta-provenance"

Make sure you:
1. Activated the virtual environment
2. Ran `pip install -e git-native/`

### Manual: Python version issues

Check your version:
```bash
python --version  # Should be 3.9+
```

If too old, install a newer Python or use pyenv:
```bash
# Install pyenv
curl https://pyenv.run | bash

# Install Python 3.11
pyenv install 3.11.7
pyenv local 3.11.7
```

---

## Why Nix?

Nix provides **reproducible development environments**. Instead of:

```bash
# Hope these work on your machine
pip install -r requirements.txt
npm install
brew install this that other
```

You get:

```bash
# Guaranteed to work exactly the same everywhere
nix develop
```

**Benefits:**
- New contributors get running in seconds
- No version conflicts
- Works identically on macOS, Linux, and WSL
- Easy to update all dependencies at once
- Rollback to previous versions if something breaks

**Learn more:** https://nixos.org/

---

## Quick Reference

### Nix Commands

```bash
nix develop              # Enter development shell
nix develop --command bash  # Enter with bash
nix flake update        # Update all dependencies
nix flake check         # Check flake validity
nix build               # Build the package
```

### With direnv

```bash
direnv allow            # Allow environment loading
direnv reload           # Reload environment
direnv deny             # Disable auto-loading
```

### Manual Commands

```bash
# Python environment
source venv/bin/activate
deactivate

# Install packages
pip install -e git-native/
npm install

# Run tools
dta-provenance --help
pytest -v
npx hardhat test
```

---

## Contributing

If you add new dependencies:

**For Nix users:**
- Update `flake.nix` with new packages
- Run `nix flake update`
- Test with `nix develop`

**For non-Nix users:**
- Update `git-native/requirements.txt` or `blockchain/package.json`
- Update `NIX_SETUP.md` with any new system dependencies

Both environments should stay in sync!
