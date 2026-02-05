"""
Provenance graph visualization.

Generates SVG/PNG diagrams of data lineage using Graphviz.
"""

from pathlib import Path
from typing import Optional

try:
    import networkx as nx
except ImportError:
    raise ImportError(
        "networkx is required. Install with: pip install networkx"
    )

try:
    from networkx.drawing.nx_agraph import to_agraph
    HAS_PYGRAPHVIZ = True
except ImportError:
    HAS_PYGRAPHVIZ = False


def generate_provenance_graph(
    lineage_dag: nx.DiGraph,
    output_path: Path,
    format: str = 'svg',
    title: Optional[str] = None
) -> None:
    """
    Generate visual diagram of provenance DAG.

    Args:
        lineage_dag: NetworkX directed acyclic graph from trace_lineage()
        output_path: Where to save the diagram
        format: Output format - 'svg', 'png', 'pdf', or 'dot'
        title: Optional title for the graph

    Raises:
        ImportError: If pygraphviz is not installed
        ValueError: If format is not supported
    """
    if not HAS_PYGRAPHVIZ:
        raise ImportError(
            "pygraphviz is required for graph visualization. "
            "Install with: pip install pygraphviz\n"
            "Note: On macOS, you may need: brew install graphviz"
        )

    supported_formats = ['svg', 'png', 'pdf', 'dot']
    if format not in supported_formats:
        raise ValueError(
            f"Unsupported format: {format}. "
            f"Supported: {supported_formats}"
        )

    # Convert NetworkX graph to pygraphviz
    agraph = to_agraph(lineage_dag)

    # Set graph attributes for better visualization
    agraph.graph_attr.update({
        'rankdir': 'TB',  # Top to bottom
        'bgcolor': 'white',
        'fontname': 'Arial',
        'fontsize': '12',
        'label': title or 'Data Provenance Lineage',
        'labelloc': 't',
        'labeljust': 'c'
    })

    # Set node attributes
    agraph.node_attr.update({
        'shape': 'box',
        'style': 'rounded,filled',
        'fillcolor': '#E3F2FD',
        'fontname': 'Arial',
        'fontsize': '10',
        'margin': '0.2,0.1'
    })

    # Set edge attributes
    agraph.edge_attr.update({
        'color': '#666666',
        'arrowsize': '0.7'
    })

    # Customize individual nodes
    for node in agraph.nodes():
        node_data = lineage_dag.nodes[node.name]

        # Build label
        label_parts = []

        if 'commit' in node_data:
            label_parts.append(f"Commit: {node_data['commit']}")

        if 'dataset' in node_data:
            label_parts.append(f"Dataset: {node_data['dataset']}")

        if 'date' in node_data:
            date_str = node_data['date'][:10]  # Just the date part
            label_parts.append(f"Date: {date_str}")

        if 'author' in node_data:
            label_parts.append(f"Author: {node_data['author']}")

        if 'message' in node_data:
            # Truncate long messages
            message = node_data['message']
            if len(message) > 50:
                message = message[:47] + "..."
            label_parts.append(f"{message}")

        node.attr['label'] = '\\n'.join(label_parts)

    # Render to file
    output_path.parent.mkdir(parents=True, exist_ok=True)
    agraph.draw(output_path, format=format, prog='dot')


def generate_simple_graph(
    lineage_dag: nx.DiGraph,
    output_path: Path
) -> None:
    """
    Generate simple ASCII art representation of lineage.

    Fallback when pygraphviz is not available.

    Args:
        lineage_dag: NetworkX directed acyclic graph
        output_path: Where to save the text file
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w') as f:
        f.write("Data Provenance Lineage\n")
        f.write("=" * 50 + "\n\n")

        # Topological sort for proper ordering
        try:
            sorted_nodes = list(nx.topological_sort(lineage_dag))
        except nx.NetworkXError:
            # Not a DAG, just use any order
            sorted_nodes = list(lineage_dag.nodes())

        for node in sorted_nodes:
            node_data = lineage_dag.nodes[node]

            f.write(f"Commit: {node_data.get('commit', node[:8])}\n")

            if 'dataset' in node_data:
                f.write(f"  Dataset: {node_data['dataset']}\n")

            if 'date' in node_data:
                f.write(f"  Date: {node_data['date'][:10]}\n")

            if 'author' in node_data:
                f.write(f"  Author: {node_data['author']}\n")

            if 'message' in node_data:
                f.write(f"  Message: {node_data['message']}\n")

            # Show descendants
            successors = list(lineage_dag.successors(node))
            if successors:
                f.write(f"  → Leads to: ")
                successor_commits = [
                    lineage_dag.nodes[s].get('commit', s[:8])
                    for s in successors
                ]
                f.write(", ".join(successor_commits))
                f.write("\n")

            f.write("\n")


def create_lineage_summary(lineage_dag: nx.DiGraph) -> str:
    """
    Create text summary of lineage graph.

    Args:
        lineage_dag: NetworkX directed acyclic graph

    Returns:
        Human-readable summary string
    """
    summary = []

    num_commits = lineage_dag.number_of_nodes()
    num_edges = lineage_dag.number_of_edges()

    summary.append(f"Provenance Lineage Summary")
    summary.append(f"=" * 50)
    summary.append(f"Total commits: {num_commits}")
    summary.append(f"Total relationships: {num_edges}")
    summary.append("")

    # Find root nodes (no predecessors)
    roots = [n for n in lineage_dag.nodes() if lineage_dag.in_degree(n) == 0]
    summary.append(f"Root commits (original data): {len(roots)}")

    # Find leaf nodes (no successors)
    leaves = [n for n in lineage_dag.nodes() if lineage_dag.out_degree(n) == 0]
    summary.append(f"Leaf commits (latest versions): {len(leaves)}")

    # Longest path (if DAG)
    try:
        longest_path = nx.dag_longest_path_length(lineage_dag)
        summary.append(f"Maximum lineage depth: {longest_path}")
    except nx.NetworkXError:
        pass

    # Datasets involved
    datasets = set()
    for node in lineage_dag.nodes():
        node_data = lineage_dag.nodes[node]
        if 'dataset' in node_data:
            datasets.add(node_data['dataset'])

    if datasets:
        summary.append(f"\nDatasets involved: {len(datasets)}")
        for dataset in sorted(datasets):
            summary.append(f"  - {dataset}")

    return "\n".join(summary)
