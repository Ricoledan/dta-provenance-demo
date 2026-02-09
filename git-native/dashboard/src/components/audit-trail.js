/**
 * Audit Trail Component
 * Renders audit trail as timeline/table
 */
export class AuditTrail {
  constructor(container, api) {
    this.container = container;
    this.api = api;
    this.currentFile = null;
  }

  /**
   * Render the component
   */
  render() {
    this.container.innerHTML = `
      <div class="lookup-form">
        <input
          type="text"
          id="file-input"
          placeholder="Enter file path (e.g., data/dataset.csv)"
          class="input"
        />
        <input
          type="number"
          id="max-commits-input"
          placeholder="Max commits (optional)"
          class="input input-small"
          min="1"
        />
        <button id="trail-btn" class="btn btn-primary">Get Audit Trail</button>
      </div>
      <div id="trail-result"></div>
    `;

    // Attach event listeners
    const trailBtn = this.container.querySelector('#trail-btn');
    const fileInput = this.container.querySelector('#file-input');

    trailBtn.addEventListener('click', () => this.getAuditTrail());
    fileInput.addEventListener('keypress', (e) => {
      if (e.key === 'Enter') {
        this.getAuditTrail();
      }
    });
  }

  /**
   * Get audit trail for a file
   */
  async getAuditTrail() {
    const fileInput = this.container.querySelector('#file-input');
    const maxCommitsInput = this.container.querySelector('#max-commits-input');

    const filePath = fileInput.value.trim();
    const maxCommits = maxCommitsInput.value ? parseInt(maxCommitsInput.value) : null;

    if (!filePath) {
      this.showError('Please enter a file path');
      return;
    }

    const resultDiv = this.container.querySelector('#trail-result');
    resultDiv.innerHTML = '<div class="loading">Loading audit trail...</div>';

    try {
      const trail = await this.api.getAuditTrail(filePath, maxCommits);
      this.currentFile = filePath;
      this.displayTrail(trail);
    } catch (error) {
      this.showError(error.message);
    }
  }

  /**
   * Display audit trail
   * @param {Array} trail - Audit trail data
   */
  displayTrail(trail) {
    const resultDiv = this.container.querySelector('#trail-result');

    if (!trail || trail.length === 0) {
      resultDiv.innerHTML = `
        <div class="message warning">
          <strong>No Audit Trail Found</strong>
          <p>No commits found for this file path.</p>
        </div>
      `;
      return;
    }

    // Create timeline view
    const timelineHTML = trail.map((entry, index) => `
      <div class="timeline-item">
        <div class="timeline-marker">${index + 1}</div>
        <div class="timeline-content">
          <div class="timeline-header">
            <strong>${this.escapeHtml(entry.message || 'No commit message')}</strong>
            <span class="timestamp">${this.formatDate(entry.timestamp)}</span>
          </div>
          <div class="timeline-details">
            <div class="detail-row">
              <span class="label">Commit:</span>
              <code>${entry.commit_hash.substring(0, 8)}</code>
            </div>
            <div class="detail-row">
              <span class="label">Author:</span>
              <span>${this.escapeHtml(entry.author || 'Unknown')}</span>
            </div>
            ${entry.has_provenance ? `
              <div class="detail-row">
                <span class="badge badge-success">Has Provenance</span>
              </div>
            ` : ''}
          </div>
        </div>
      </div>
    `).join('');

    resultDiv.innerHTML = `
      <div class="audit-trail-header">
        <h3>Audit Trail for: <code>${this.escapeHtml(this.currentFile)}</code></h3>
        <span class="badge">${trail.length} commit(s)</span>
      </div>
      <div class="timeline">
        ${timelineHTML}
      </div>
      <div class="trail-actions">
        <button id="export-csv-btn" class="btn btn-secondary">Export as CSV</button>
        <button id="export-json-btn" class="btn btn-secondary">Export as JSON</button>
      </div>
    `;

    // Attach export handlers
    resultDiv.querySelector('#export-csv-btn').addEventListener('click', () => {
      this.exportAsCSV(trail);
    });
    resultDiv.querySelector('#export-json-btn').addEventListener('click', () => {
      this.exportAsJSON(trail);
    });
  }

  /**
   * Format date string
   * @param {string} dateStr - ISO date string
   * @returns {string} Formatted date
   */
  formatDate(dateStr) {
    if (!dateStr) return 'Unknown date';
    const date = new Date(dateStr);
    return date.toLocaleString();
  }

  /**
   * Export audit trail as CSV
   * @param {Array} trail - Audit trail data
   */
  exportAsCSV(trail) {
    const headers = ['Commit Hash', 'Timestamp', 'Author', 'Message', 'Has Provenance'];
    const rows = trail.map(entry => [
      entry.commit_hash,
      entry.timestamp || '',
      entry.author || '',
      (entry.message || '').replace(/"/g, '""'),
      entry.has_provenance ? 'Yes' : 'No'
    ]);

    const csv = [
      headers.join(','),
      ...rows.map(row => row.map(cell => `"${cell}"`).join(','))
    ].join('\n');

    this.downloadFile(csv, `audit-trail-${this.currentFile.replace(/\//g, '-')}.csv`, 'text/csv');
  }

  /**
   * Export audit trail as JSON
   * @param {Array} trail - Audit trail data
   */
  exportAsJSON(trail) {
    const json = JSON.stringify(trail, null, 2);
    this.downloadFile(json, `audit-trail-${this.currentFile.replace(/\//g, '-')}.json`, 'application/json');
  }

  /**
   * Download file
   * @param {string} content - File content
   * @param {string} filename - File name
   * @param {string} mimeType - MIME type
   */
  downloadFile(content, filename, mimeType) {
    const blob = new Blob([content], { type: mimeType });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    a.click();
    URL.revokeObjectURL(url);
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
    const resultDiv = this.container.querySelector('#trail-result');
    resultDiv.innerHTML = `
      <div class="message error">
        <strong>Error:</strong> ${this.escapeHtml(message)}
      </div>
    `;
  }
}
