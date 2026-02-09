/**
 * Provenance Viewer Component
 * Renders provenance metadata as a structured card
 */
export class ProvenanceViewer {
  constructor(container, api) {
    this.container = container;
    this.api = api;
    this.currentCommit = null;
  }

  /**
   * Render the component
   */
  render() {
    this.container.innerHTML = `
      <div class="lookup-form">
        <input
          type="text"
          id="commit-input"
          placeholder="Enter commit hash (e.g., HEAD, abc123...)"
          class="input"
        />
        <button id="lookup-btn" class="btn btn-primary">Lookup</button>
      </div>
      <div id="provenance-result"></div>
    `;

    // Attach event listeners
    const lookupBtn = this.container.querySelector('#lookup-btn');
    const commitInput = this.container.querySelector('#commit-input');

    lookupBtn.addEventListener('click', () => this.lookupProvenance());
    commitInput.addEventListener('keypress', (e) => {
      if (e.key === 'Enter') {
        this.lookupProvenance();
      }
    });
  }

  /**
   * Lookup provenance for a commit
   */
  async lookupProvenance() {
    const commitInput = this.container.querySelector('#commit-input');
    const commitHash = commitInput.value.trim();

    if (!commitHash) {
      this.showError('Please enter a commit hash');
      return;
    }

    const resultDiv = this.container.querySelector('#provenance-result');
    resultDiv.innerHTML = '<div class="loading">Loading provenance data...</div>';

    try {
      const data = await this.api.getProvenance(commitHash);
      this.currentCommit = commitHash;
      this.displayProvenance(data);
    } catch (error) {
      this.showError(error.message);
    }
  }

  /**
   * Display provenance metadata
   * @param {Object} data - Provenance data
   */
  displayProvenance(data) {
    const resultDiv = this.container.querySelector('#provenance-result');

    if (!data.metadata) {
      resultDiv.innerHTML = `
        <div class="message warning">
          <strong>No Provenance Data Found</strong>
          <p>This commit does not contain DTA provenance metadata.</p>
        </div>
      `;
      return;
    }

    const metadata = data.metadata;

    resultDiv.innerHTML = `
      <div class="provenance-card">
        <div class="card-header">
          <h3>Provenance Metadata</h3>
          <span class="badge badge-success">DTA v1.0.0 Compliant</span>
        </div>

        <div class="metadata-section">
          <h4>Source Information</h4>
          ${this.renderSection(metadata.source)}
        </div>

        <div class="metadata-section">
          <h4>Provenance Details</h4>
          ${this.renderSection(metadata.provenance)}
        </div>

        <div class="metadata-section">
          <h4>Use & Rights</h4>
          ${this.renderSection(metadata.use)}
        </div>

        ${metadata.metadata ? `
          <div class="metadata-section">
            <h4>Additional Metadata</h4>
            ${this.renderSection(metadata.metadata)}
          </div>
        ` : ''}

        <div class="metadata-section">
          <h4>Commit Information</h4>
          <dl>
            <dt>Commit Hash:</dt>
            <dd><code>${data.commit_hash}</code></dd>
            <dt>Author:</dt>
            <dd>${data.author || 'N/A'}</dd>
            <dt>Date:</dt>
            <dd>${data.date || 'N/A'}</dd>
            <dt>Message:</dt>
            <dd>${data.message || 'N/A'}</dd>
          </dl>
        </div>
      </div>
    `;
  }

  /**
   * Render a metadata section
   * @param {Object} section - Section data
   * @returns {string} HTML string
   */
  renderSection(section) {
    if (!section || Object.keys(section).length === 0) {
      return '<p class="text-muted">No data available</p>';
    }

    const items = Object.entries(section)
      .map(([key, value]) => {
        const displayValue = typeof value === 'object'
          ? JSON.stringify(value, null, 2)
          : String(value);

        return `
          <dt>${this.formatKey(key)}:</dt>
          <dd>${this.escapeHtml(displayValue)}</dd>
        `;
      })
      .join('');

    return `<dl>${items}</dl>`;
  }

  /**
   * Format camelCase keys to Title Case
   * @param {string} key - Key to format
   * @returns {string} Formatted key
   */
  formatKey(key) {
    return key
      .replace(/([A-Z])/g, ' $1')
      .replace(/^./, (str) => str.toUpperCase());
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
    const resultDiv = this.container.querySelector('#provenance-result');
    resultDiv.innerHTML = `
      <div class="message error">
        <strong>Error:</strong> ${this.escapeHtml(message)}
      </div>
    `;
  }
}
