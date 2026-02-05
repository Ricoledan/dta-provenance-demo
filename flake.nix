{
  description = "DTA Provenance Standards Demo - Development Environment";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};

        pythonEnv = pkgs.python311.withPackages (ps: with ps; [
          # Core dependencies
          gitpython
          click
          rich
          jsonschema
          networkx

          # Development dependencies
          pytest
          pytest-cov
          black
          mypy
          ruff

          # Optional dependencies
          # pygraphviz  # Requires graphviz, uncomment if needed
          matplotlib
        ]);

      in
      {
        devShells.default = pkgs.mkShell {
          buildInputs = with pkgs; [
            # Python environment
            pythonEnv

            # Git
            git

            # Node.js for blockchain implementation
            nodejs_20
            nodePackages.npm

# Blockchain tools
             # Hardhat will be installed via npm in the blockchain directory

            # Optional: for graph visualization
            graphviz

            # Development tools
            jq
            curl

            # Shell utilities
            bashInteractive
          ];

          shellHook = ''
            echo "🚀 DTA Provenance Demo Development Environment"
            echo ""
            echo "Python: $(python --version)"
            echo "Node.js: $(node --version)"
            echo "Git: $(git --version)"
            echo ""
            echo "Available commands:"
            echo "  dta-provenance - CLI tool (after pip install -e git-native/)"
            echo "  npx hardhat    - Hardhat blockchain tools"
            echo "  pytest         - Run Python tests"
            echo ""
            echo "Quick start:"
            echo "  cd git-native && pip install -e ."
            echo "  cd blockchain && npm install"
            echo ""
            echo "Type 'exit' to leave the environment"
            echo ""

            # Set Python path to include git-native/src
            export PYTHONPATH="${toString ./.}/git-native:$PYTHONPATH"

            # Create virtual environment if it doesn't exist
            if [ ! -d .venv ]; then
              echo "Creating Python virtual environment..."
              python -m venv .venv
            fi

            # Activate virtual environment
            source .venv/bin/activate

            # Install git-native package in development mode if not already installed
            if [ -f git-native/pyproject.toml ]; then
              echo "Installing git-native package in development mode..."
              pip install -e git-native/ --quiet
            fi
          '';
        };

        # Optional: Package the Python library
        packages.default = pkgs.python311Packages.buildPythonPackage {
          pname = "dta-provenance";
          version = "1.0.0";
          src = ./git-native;

          propagatedBuildInputs = with pkgs.python311Packages; [
            gitpython
            click
            rich
            jsonschema
            networkx
          ];

          doCheck = true;
          checkInputs = with pkgs.python311Packages; [
            pytest
            pytest-cov
          ];
        };
      }
    );
}
