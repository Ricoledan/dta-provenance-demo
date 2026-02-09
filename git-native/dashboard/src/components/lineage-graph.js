import * as d3 from 'd3';

/**
 * Lineage Graph Component
 * D3-based DAG visualization from /lineage endpoint
 */
export class LineageGraph {
  constructor(container, api) {
    this.container = container;
    this.api = api;
    this.svg = null;
    this.simulation = null;
  }

  /**
   * Render the component
   */
  render() {
    this.container.innerHTML = `
      <div class="lookup-form">
        <input
          type="text"
          id="lineage-file-input"
          placeholder="Enter file path (e.g., data/dataset.csv)"
          class="input"
        />
        <button id="lineage-btn" class="btn btn-primary">Generate Lineage Graph</button>
      </div>
      <div id="lineage-result"></div>
    `;

    // Attach event listeners
    const lineageBtn = this.container.querySelector('#lineage-btn');
    const fileInput = this.container.querySelector('#lineage-file-input');

    lineageBtn.addEventListener('click', () => this.generateLineage());
    fileInput.addEventListener('keypress', (e) => {
      if (e.key === 'Enter') {
        this.generateLineage();
      }
    });
  }

  /**
   * Generate lineage graph
   */
  async generateLineage() {
    const fileInput = this.container.querySelector('#lineage-file-input');
    const filePath = fileInput.value.trim();

    if (!filePath) {
      this.showError('Please enter a file path');
      return;
    }

    const resultDiv = this.container.querySelector('#lineage-result');
    resultDiv.innerHTML = '<div class="loading">Generating lineage graph...</div>';

    try {
      const lineageData = await this.api.getLineage(filePath);
      this.displayGraph(lineageData);
    } catch (error) {
      this.showError(error.message);
    }
  }

  /**
   * Display lineage graph
   * @param {Object} lineageData - Lineage data with nodes and edges
   */
  displayGraph(lineageData) {
    const resultDiv = this.container.querySelector('#lineage-result');

    if (!lineageData.nodes || lineageData.nodes.length === 0) {
      resultDiv.innerHTML = `
        <div class="message warning">
          <strong>No Lineage Data Found</strong>
          <p>No lineage information available for this file.</p>
        </div>
      `;
      return;
    }

    // Clear previous graph
    resultDiv.innerHTML = '<div id="graph-container"></div>';
    const graphContainer = resultDiv.querySelector('#graph-container');

    // Create SVG
    const width = graphContainer.clientWidth || 800;
    const height = 600;

    const svg = d3.select(graphContainer)
      .append('svg')
      .attr('width', width)
      .attr('height', height)
      .attr('viewBox', [0, 0, width, height]);

    // Create graph data structure
    const nodes = lineageData.nodes.map(node => ({
      id: node.id,
      label: node.label || node.id,
      type: node.type || 'commit',
      ...node
    }));

    const links = lineageData.edges.map(edge => ({
      source: edge.source,
      target: edge.target,
      ...edge
    }));

    // Create force simulation
    const simulation = d3.forceSimulation(nodes)
      .force('link', d3.forceLink(links).id(d => d.id).distance(100))
      .force('charge', d3.forceManyBody().strength(-300))
      .force('center', d3.forceCenter(width / 2, height / 2))
      .force('collision', d3.forceCollide().radius(50));

    // Create arrow markers
    svg.append('defs')
      .append('marker')
      .attr('id', 'arrowhead')
      .attr('viewBox', '0 -5 10 10')
      .attr('refX', 25)
      .attr('refY', 0)
      .attr('markerWidth', 6)
      .attr('markerHeight', 6)
      .attr('orient', 'auto')
      .append('path')
      .attr('d', 'M0,-5L10,0L0,5')
      .attr('fill', '#5c6ac4');

    // Create links
    const link = svg.append('g')
      .selectAll('line')
      .data(links)
      .join('line')
      .attr('stroke', '#5c6ac4')
      .attr('stroke-width', 2)
      .attr('marker-end', 'url(#arrowhead)');

    // Create nodes
    const node = svg.append('g')
      .selectAll('g')
      .data(nodes)
      .join('g')
      .call(this.drag(simulation));

    // Add circles to nodes
    node.append('circle')
      .attr('r', 20)
      .attr('fill', d => this.getNodeColor(d.type))
      .attr('stroke', '#fff')
      .attr('stroke-width', 2);

    // Add labels to nodes
    node.append('text')
      .text(d => d.label.substring(0, 8))
      .attr('font-size', '10px')
      .attr('text-anchor', 'middle')
      .attr('dy', 35)
      .attr('fill', '#333');

    // Add tooltips
    node.append('title')
      .text(d => `${d.type}: ${d.label}\n${d.message || ''}`);

    // Update positions on simulation tick
    simulation.on('tick', () => {
      link
        .attr('x1', d => d.source.x)
        .attr('y1', d => d.source.y)
        .attr('x2', d => d.target.x)
        .attr('y2', d => d.target.y);

      node
        .attr('transform', d => `translate(${d.x},${d.y})`);
    });

    this.svg = svg;
    this.simulation = simulation;

    // Add legend
    this.addLegend(resultDiv);

    // Add export button
    this.addExportButton(resultDiv);
  }

  /**
   * Add legend to the graph
   * @param {HTMLElement} container - Container element
   */
  addLegend(container) {
    const legend = document.createElement('div');
    legend.className = 'graph-legend';
    legend.innerHTML = `
      <h4>Legend</h4>
      <div class="legend-items">
        <div class="legend-item">
          <span class="legend-color" style="background-color: ${this.getNodeColor('commit')}"></span>
          <span>Commit</span>
        </div>
        <div class="legend-item">
          <span class="legend-color" style="background-color: ${this.getNodeColor('file')}"></span>
          <span>File</span>
        </div>
        <div class="legend-item">
          <span class="legend-color" style="background-color: ${this.getNodeColor('dataset')}"></span>
          <span>Dataset</span>
        </div>
      </div>
    `;
    container.appendChild(legend);
  }

  /**
   * Add export button
   * @param {HTMLElement} container - Container element
   */
  addExportButton(container) {
    const exportBtn = document.createElement('button');
    exportBtn.textContent = 'Export as SVG';
    exportBtn.className = 'btn btn-secondary';
    exportBtn.style.marginTop = '10px';
    exportBtn.addEventListener('click', () => this.exportAsSVG());
    container.appendChild(exportBtn);
  }

  /**
   * Export graph as SVG
   */
  exportAsSVG() {
    if (!this.svg) return;

    const svgData = this.svg.node().outerHTML;
    const blob = new Blob([svgData], { type: 'image/svg+xml' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'lineage-graph.svg';
    a.click();
    URL.revokeObjectURL(url);
  }

  /**
   * Get node color based on type
   * @param {string} type - Node type
   * @returns {string} Color code
   */
  getNodeColor(type) {
    const colors = {
      commit: '#5c6ac4',
      file: '#47c1bf',
      dataset: '#7e57c2',
      default: '#9e9e9e'
    };
    return colors[type] || colors.default;
  }

  /**
   * Drag behavior for nodes
   * @param {Object} simulation - D3 simulation
   * @returns {Function} Drag behavior
   */
  drag(simulation) {
    function dragstarted(event) {
      if (!event.active) simulation.alphaTarget(0.3).restart();
      event.subject.fx = event.subject.x;
      event.subject.fy = event.subject.y;
    }

    function dragged(event) {
      event.subject.fx = event.x;
      event.subject.fy = event.y;
    }

    function dragended(event) {
      if (!event.active) simulation.alphaTarget(0);
      event.subject.fx = null;
      event.subject.fy = null;
    }

    return d3.drag()
      .on('start', dragstarted)
      .on('drag', dragged)
      .on('end', dragended);
  }

  /**
   * Escape HTML to prevent XSS
   * @param {string} text - Text to escape
   * @returns {string} Escaped text
   */
  escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }

  /**
   * Show error message
   * @param {string} message - Error message
   */
  showError(message) {
    const resultDiv = this.container.querySelector('#lineage-result');
    resultDiv.innerHTML = `
      <div class="message error">
        <strong>Error:</strong> ${this.escapeHtml(message)}
      </div>
    `;
  }
}
