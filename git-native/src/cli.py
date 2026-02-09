"""
CLI tool for Git-native provenance tracking.

Uses Click for command-line interface and Rich for beautiful terminal output.
"""

from pathlib import Path
from typing import List, Optional
import sys
import json

try:
    import click
except ImportError:
    print("Error: click is required. Install with: pip install click")
    sys.exit(1)

try:
    from rich.console import Console
    from rich.table import Table
    from rich.tree import Tree
    from rich.panel import Panel
    from rich.syntax import Syntax
    from rich import box
except ImportError:
    print("Error: rich is required. Install with: pip install rich")
    sys.exit(1)

import git

from .provenance import ProvenanceTracker, ProvenanceMetadata, load_provenance_file
from .verify import ProvenanceVerifier, validate_provenance_file

console = Console()


@click.group()
@click.version_option(version="1.0.0")
def cli():
    """
    DTA-compliant provenance tracking for data and AI.

    Track data provenance using Git commits with Data & Trust Alliance
    standards v1.0.0. Provides cryptographic integrity verification and
    comprehensive audit trails.
    """
    pass


@cli.command()
@click.argument('files', nargs=-1, type=click.Path(exists=True), required=True)
@click.option(
    '--metadata',
    '-m',
    required=True,
    type=click.Path(exists=True),
    help='Path to DTA provenance JSON file'
)
@click.option(
    '--message',
    '-M',
    required=True,
    help='Commit message'
)
@click.option(
    '--sign/--no-sign',
    default=False,
    help='GPG sign the commit (requires git config)'
)
@click.option(
    '--repo',
    type=click.Path(exists=True),
    default='.',
    help='Git repository path (default: current directory)'
)
def commit(files, metadata, message, sign, repo):
    """
    Commit files with provenance metadata.

    Creates a Git commit with DTA-compliant provenance metadata embedded
    in the commit message. The metadata is cryptographically hashed for
    integrity verification.

    Example:

        dta-provenance commit dataset.csv \\
            --metadata provenance.json \\
            --message "Add training data v1.0"
    """
    console.print("[bold blue]Committing with provenance...[/]")

    try:
        # Load and validate metadata
        with console.status("[yellow]Loading metadata...[/]"):
            prov_metadata = load_provenance_file(Path(metadata))

        console.print("✅ Metadata loaded and validated")

        # Initialize tracker
        tracker = ProvenanceTracker(Path(repo))

        # Convert file paths to Path objects
        file_paths = [Path(f).relative_to(repo) for f in files]

        # Create commit
        with console.status("[yellow]Creating commit...[/]"):
            commit_hash = tracker.commit_with_provenance(
                file_paths=file_paths,
                metadata=prov_metadata,
                message=message,
                sign=sign
            )

        # Display success
        panel = Panel(
            f"[green]Commit: {commit_hash[:12]}...[/]\n"
            f"[cyan]Dataset: {prov_metadata.source['datasetName']}[/]\n"
            f"[cyan]Files: {len(file_paths)}[/]",
            title="✅ Provenance Commit Created",
            border_style="green"
        )
        console.print(panel)

    except Exception as e:
        console.print(f"[red]Error: {e}[/]")
        sys.exit(1)


@cli.command()
@click.argument('commit_hash', default='HEAD')
@click.option(
    '--repo',
    type=click.Path(exists=True),
    default='.',
    help='Git repository path (default: current directory)'
)
def verify(commit_hash, repo):
    """
    Verify provenance integrity.

    Checks cryptographic integrity of provenance metadata in a commit.
    Verifies GPG signatures (if signed) and metadata hash consistency.

    Example:

        dta-provenance verify HEAD
        dta-provenance verify abc123def
    """
    console.print(f"[bold blue]Verifying provenance for {commit_hash}...[/]")

    try:
        tracker = ProvenanceTracker(Path(repo))
        is_valid, message = tracker.verify_integrity(commit_hash)

        if is_valid:
            console.print(f"[green]✅ {message}[/]")
        else:
            console.print(f"[red]❌ {message}[/]")
            sys.exit(1)

        # Display metadata if present
        metadata = tracker.read_provenance(commit_hash)
        if metadata:
            table = Table(title="Provenance Metadata", box=box.ROUNDED)
            table.add_column("Field", style="cyan")
            table.add_column("Value", style="white")

            table.add_row("Dataset", metadata.source.get("datasetName", "N/A"))
            table.add_row("Provider", metadata.source.get("providerName", "N/A"))
            table.add_row("Data Type", metadata.provenance.get("dataType", "N/A"))
            table.add_row(
                "Sensitive Data",
                "Yes" if metadata.use.get("sensitiveData") else "No"
            )

            console.print(table)

    except Exception as e:
        console.print(f"[red]Error: {e}[/]")
        sys.exit(1)


@cli.command()
@click.argument('file', type=click.Path(exists=True))
@click.option(
    '--format',
    type=click.Choice(['text', 'json'], case_sensitive=False),
    default='text',
    help='Output format'
)
@click.option(
    '--max-commits',
    type=int,
    default=10,
    help='Maximum number of commits to show'
)
@click.option(
    '--repo',
    type=click.Path(exists=True),
    default='.',
    help='Git repository path (default: current directory)'
)
def trace(file, format, max_commits, repo):
    """
    Trace data lineage.

    Shows the complete audit trail for a file, including all commits
    that modified it and their provenance metadata.

    Example:

        dta-provenance trace dataset.csv
        dta-provenance trace dataset.csv --format json
    """
    console.print(f"[bold blue]Tracing lineage for {file}...[/]")

    try:
        tracker = ProvenanceTracker(Path(repo))
        file_path = Path(file).relative_to(repo)

        audit_trail = tracker.generate_audit_trail(file_path, max_commits)

        if not audit_trail:
            console.print(f"[yellow]No commits found for {file}[/]")
            return

        if format == 'json':
            console.print_json(data=audit_trail)
        else:
            # Create tree visualization
            tree = Tree(f"📁 [bold]{file}[/] - {len(audit_trail)} commits")

            for record in audit_trail:
                commit_branch = tree.add(
                    f"[cyan]{record['commit_hash'][:8]}[/] - "
                    f"{record['date'][:10]} - "
                    f"[dim]{record['author']}[/]"
                )
                commit_branch.add(f"[white]{record['message']}[/]")

                if record['provenance']:
                    prov = record['provenance']
                    dataset_name = prov.get('source', {}).get('datasetName', 'Unknown')
                    commit_branch.add(f"[green]Dataset: {dataset_name}[/]")

            console.print(tree)

    except Exception as e:
        console.print(f"[red]Error: {e}[/]")
        sys.exit(1)


@cli.command()
@click.argument('metadata_file', type=click.Path(exists=True))
@click.option(
    '--schema',
    type=click.Path(exists=True),
    help='Path to DTA JSON schema (optional)'
)
def validate(metadata_file, schema):
    """
    Validate DTA compliance.

    Checks if a provenance JSON file complies with DTA v1.0.0 standards.
    Reports errors, warnings, and missing optional fields.

    Example:

        dta-provenance validate provenance.json
        dta-provenance validate provenance.json --schema dta-schema.json
    """
    console.print(f"[bold blue]Validating {metadata_file}...[/]")

    try:
        schema_path = Path(schema) if schema else None
        report = validate_provenance_file(Path(metadata_file), schema_path)

        # Display report
        console.print(str(report))

        if not report.is_valid:
            sys.exit(1)

    except Exception as e:
        console.print(f"[red]Error: {e}[/]")
        sys.exit(1)


@cli.command()
@click.argument('commit_hash', default='HEAD')
@click.option(
    '--repo',
    type=click.Path(exists=True),
    default='.',
    help='Git repository path (default: current directory)'
)
@click.option(
    '--output',
    '-o',
    type=click.Path(),
    help='Output file (default: print to console)'
)
def show(commit_hash, repo, output):
    """
    Show provenance metadata from a commit.

    Displays the complete DTA provenance metadata from a commit in
    formatted JSON.

    Example:

        dta-provenance show HEAD
        dta-provenance show abc123def --output metadata.json
    """
    try:
        tracker = ProvenanceTracker(Path(repo))
        metadata = tracker.read_provenance(commit_hash)

        if not metadata:
            console.print(f"[yellow]No provenance metadata found in {commit_hash}[/]")
            return

        metadata_dict = metadata.to_dict()

        if output:
            with open(output, 'w') as f:
                json.dump(metadata_dict, f, indent=2)
            console.print(f"[green]Metadata saved to {output}[/]")
        else:
            syntax = Syntax(
                json.dumps(metadata_dict, indent=2),
                "json",
                theme="monokai",
                line_numbers=True
            )
            console.print(syntax)

    except Exception as e:
        console.print(f"[red]Error: {e}[/]")
        sys.exit(1)


@cli.command()
@click.argument('files', nargs=-1, type=click.Path(exists=True), required=True)
@click.option(
    '--metadata',
    '-m',
    type=click.Path(exists=True),
    help='Path to DTA provenance JSON file (will be enriched with DVC info)'
)
@click.option(
    '--output',
    '-o',
    type=click.Path(),
    help='Output path for enriched metadata (default: print to console)'
)
@click.option(
    '--repo',
    type=click.Path(exists=True),
    default='.',
    help='Git repository path (default: current directory)'
)
def dvc_track(files, metadata, output, repo):
    """
    Track files with DVC and enrich provenance metadata.

    Adds files to DVC tracking and enriches DTA provenance metadata with
    DVC hashes and version information for complete traceability.

    Requires DVC to be installed: pip install 'dta-provenance[dvc]'

    Example:

        dta-provenance dvc-track dataset.csv \\
            --metadata provenance.json \\
            --output provenance-with-dvc.json
    """
    console.print("[bold blue]Tracking files with DVC...[/]")

    try:
        # Lazy import DVC integration
        from .integrations.dvc_integration import DVCProvenanceBridge
    except ImportError as e:
        console.print(f"[red]Error: {e}[/]")
        console.print("[yellow]Install with: pip install 'dta-provenance[dvc]'[/]")
        sys.exit(1)

    try:
        bridge = DVCProvenanceBridge(Path(repo))

        # Load existing metadata if provided
        if metadata:
            prov_metadata = load_provenance_file(Path(metadata))
            metadata_dict = prov_metadata.to_dict()
        else:
            metadata_dict = {}

        # Track each file
        for file_path in files:
            relative_path = Path(file_path).relative_to(repo)
            console.print(f"[yellow]Tracking {relative_path} with DVC...[/]")

            metadata_dict = bridge.track_dvc_file(relative_path, metadata_dict)
            console.print(f"[green]✅ {relative_path} tracked[/]")

        # Output enriched metadata
        if output:
            with open(output, 'w') as f:
                json.dump(metadata_dict, f, indent=2)
            console.print(f"[green]Enriched metadata saved to {output}[/]")
        else:
            syntax = Syntax(
                json.dumps(metadata_dict, indent=2),
                "json",
                theme="monokai",
                line_numbers=True
            )
            console.print(syntax)

        console.print("\n[green]✅ DVC tracking complete[/]")
        console.print("[cyan]Next steps:[/]")
        console.print("  1. git add .dvc/config data.csv.dvc .gitignore")
        console.print("  2. git commit -m 'Add DVC tracking'")

    except Exception as e:
        console.print(f"[red]Error: {e}[/]")
        sys.exit(1)


@cli.command()
@click.option(
    '--host',
    default='127.0.0.1',
    help='Host to bind the server (default: 127.0.0.1)'
)
@click.option(
    '--port',
    default=8000,
    type=int,
    help='Port to bind the server (default: 8000)'
)
@click.option(
    '--reload',
    is_flag=True,
    help='Enable auto-reload for development'
)
@click.option(
    '--repo',
    type=click.Path(exists=True),
    default='.',
    help='Git repository path (default: current directory)'
)
def serve(host, port, reload, repo):
    """
    Start the FastAPI server for provenance queries.

    Runs a REST API server that provides endpoints for querying provenance
    metadata, generating audit trails, and validating DTA compliance.

    Requires FastAPI and uvicorn: pip install 'dta-provenance[api]'

    Example:

        # Start server on default port 8000
        dta-provenance serve

        # Start with custom host and port
        dta-provenance serve --host 0.0.0.0 --port 8080

        # Start with auto-reload for development
        dta-provenance serve --reload
    """
    console.print("[bold blue]Starting DTA Provenance API server...[/]")

    try:
        # Lazy import FastAPI and uvicorn
        try:
            import uvicorn
            from .api import create_app
        except ImportError:
            console.print("[red]Error: FastAPI and uvicorn are required[/]")
            console.print("[yellow]Install with: pip install 'dta-provenance[api]'[/]")
            sys.exit(1)

        # Create app
        app = create_app(Path(repo))

        # Display server info
        panel = Panel(
            f"[cyan]Host: {host}[/]\n"
            f"[cyan]Port: {port}[/]\n"
            f"[cyan]Repository: {Path(repo).absolute()}[/]\n"
            f"[cyan]Docs: http://{host}:{port}/docs[/]\n"
            f"[cyan]ReDoc: http://{host}:{port}/redoc[/]",
            title="🚀 API Server Configuration",
            border_style="blue"
        )
        console.print(panel)

        # Run server
        uvicorn.run(
            app,
            host=host,
            port=port,
            reload=reload,
            log_level="info"
        )

    except KeyboardInterrupt:
        console.print("\n[yellow]Server stopped[/]")
    except Exception as e:
        console.print(f"[red]Error: {e}[/]")
        sys.exit(1)


@cli.command()
@click.option(
    '--project-name',
    '-n',
    required=True,
    help='Name of the project'
)
@click.option(
    '--project-version',
    '-v',
    default='1.0.0',
    help='Version of the project (default: 1.0.0)'
)
@click.option(
    '--metadata',
    '-m',
    type=click.Path(exists=True),
    help='Path to DTA provenance JSON file (will be enriched with SBOM info)'
)
@click.option(
    '--output',
    '-o',
    type=click.Path(),
    help='Output path for SBOM file (default: sbom.json in repo root)'
)
@click.option(
    '--repo',
    type=click.Path(exists=True),
    default='.',
    help='Git repository path (default: current directory)'
)
def sbom_generate(project_name, project_version, metadata, output, repo):
    """
    Generate SBOM and link to provenance metadata.

    Creates a CycloneDX-format Software Bill of Materials (SBOM) for the
    project's Python dependencies and enriches DTA provenance metadata with
    SBOM reference and dependency information.

    Requires CycloneDX to be installed: pip install 'dta-provenance[sbom]'

    Example:

        dta-provenance sbom-generate \\
            --project-name my-ml-project \\
            --project-version 1.0.0 \\
            --metadata provenance.json \\
            --output sbom.json
    """
    console.print("[bold blue]Generating SBOM...[/]")

    try:
        # Lazy import SBOM integration
        from .integrations.sbom_integration import SBOMProvenanceBridge
    except ImportError as e:
        console.print(f"[red]Error: {e}[/]")
        console.print("[yellow]Install with: pip install 'dta-provenance[sbom]'[/]")
        sys.exit(1)

    try:
        bridge = SBOMProvenanceBridge(Path(repo))

        # Load existing metadata if provided
        if metadata:
            prov_metadata = load_provenance_file(Path(metadata))
            metadata_dict = prov_metadata.to_dict()
        else:
            metadata_dict = {}

        # Set output path
        output_path = Path(output) if output else None

        # Generate SBOM and link to provenance
        with console.status("[yellow]Generating SBOM from installed packages...[/]"):
            sbom_path, enriched = bridge.generate_and_link(
                project_name,
                project_version,
                metadata_dict,
                output_path
            )

        console.print(f"[green]✅ SBOM generated: {sbom_path}[/]")

        # Extract and display dependency info
        dep_info = bridge.extract_dependency_info(sbom_path.relative_to(Path(repo)))

        # Display summary
        table = Table(title="SBOM Summary", box=box.ROUNDED)
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="white")

        table.add_row("Total Dependencies", str(dep_info['total_dependencies']))
        table.add_row("Licenses Found", str(len(dep_info['licenses'])))
        table.add_row("SBOM Format", "CycloneDX")
        table.add_row("SBOM File", str(sbom_path.relative_to(Path(repo))))

        console.print(table)

        # Save enriched metadata if output was specified
        if metadata:
            enriched_output = Path(repo) / 'provenance-with-sbom.json'
            with open(enriched_output, 'w') as f:
                json.dump(enriched, f, indent=2)
            console.print(f"[green]Enriched metadata saved to {enriched_output}[/]")
        else:
            # Just display the enriched metadata
            syntax = Syntax(
                json.dumps(enriched, indent=2),
                "json",
                theme="monokai",
                line_numbers=True
            )
            console.print("\n[bold]Enriched Metadata:[/]")
            console.print(syntax)

        console.print("\n[green]✅ SBOM generation complete[/]")
        console.print("[cyan]Next steps:[/]")
        console.print(f"  1. git add {sbom_path.relative_to(Path(repo))}")
        if metadata:
            console.print(f"  2. git add provenance-with-sbom.json")
            console.print("  3. git commit -m 'Add SBOM and provenance'")
        else:
            console.print("  2. git commit -m 'Add SBOM'")

    except Exception as e:
        console.print(f"[red]Error: {e}[/]")
        sys.exit(1)


@cli.command()
@click.option(
    '--metadata',
    '-m',
    required=True,
    type=click.Path(exists=True),
    help='Path to DTA provenance JSON file'
)
@click.option(
    '--run-id',
    type=str,
    help='MLflow run ID (uses active run if not provided)'
)
@click.option(
    '--tracking-uri',
    type=str,
    help='MLflow tracking URI (optional)'
)
@click.option(
    '--repo',
    type=click.Path(exists=True),
    default='.',
    help='Git repository path (default: current directory)'
)
def mlflow_log(metadata, run_id, tracking_uri, repo):
    """
    Log provenance metadata to MLflow.

    Stores DTA provenance metadata in an MLflow run as tags and artifacts
    for easy tracking and querying of data lineage in ML experiments.

    Requires MLflow to be installed: pip install 'dta-provenance[mlflow]'

    Example:

        # Log to active MLflow run
        dta-provenance mlflow-log --metadata provenance.json

        # Log to specific run
        dta-provenance mlflow-log \\
            --metadata provenance.json \\
            --run-id abc123
    """
    console.print("[bold blue]Logging provenance to MLflow...[/]")

    try:
        # Lazy import MLflow integration
        from .integrations.mlflow_integration import MLflowProvenanceBridge
    except ImportError as e:
        console.print(f"[red]Error: {e}[/]")
        console.print("[yellow]Install with: pip install 'dta-provenance[mlflow]'[/]")
        sys.exit(1)

    try:
        # Load metadata
        with console.status("[yellow]Loading metadata...[/]"):
            prov_metadata = load_provenance_file(Path(metadata))
            metadata_dict = prov_metadata.to_dict()

        console.print("✅ Metadata loaded and validated")

        # Initialize bridge
        bridge = MLflowProvenanceBridge(Path(repo), tracking_uri=tracking_uri)

        # Log to MLflow
        with console.status("[yellow]Logging to MLflow...[/]"):
            logged_run_id = bridge.log_provenance_to_mlflow(
                metadata_dict,
                run_id=run_id
            )

        # Display success
        panel = Panel(
            f"[green]MLflow Run: {logged_run_id}[/]\n"
            f"[cyan]Dataset: {prov_metadata.source['datasetName']}[/]\n"
            f"[cyan]Provider: {prov_metadata.source.get('providerName', 'N/A')}[/]",
            title="✅ Provenance Logged to MLflow",
            border_style="green"
        )
        console.print(panel)

        console.print("\n[cyan]View in MLflow UI or query with:[/]")
        console.print(f"  mlflow runs show {logged_run_id}")

    except Exception as e:
        console.print(f"[red]Error: {e}[/]")
        sys.exit(1)


if __name__ == '__main__':
    cli()
