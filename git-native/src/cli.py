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


if __name__ == '__main__':
    cli()
