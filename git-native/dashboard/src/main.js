import './style.css';
import { ProvenanceViewer } from './components/provenance-viewer.js';
import { AuditTrail } from './components/audit-trail.js';
import { LineageGraph } from './components/lineage-graph.js';
import { Validator } from './components/validator.js';

/**
 * API Client for DTA Provenance API
 */
class APIClient {
  constructor(baseURL = '/api') {
    this.baseURL = baseURL;
  }

  /**
   * Fetch provenance metadata for a commit
   * @param {string} commitHash - Git commit hash
   * @returns {Promise<Object>}
   */
  async getProvenance(commitHash) {
    const response = await fetch(`${this.baseURL}/provenance/${commitHash}`);
    if (!response.ok) {
      throw new Error(`Failed to fetch provenance: ${response.statusText}`);
    }
    return response.json();
  }

  /**
   * Fetch audit trail for a file
   * @param {string} filePath - Path to the file
   * @param {number} maxCommits - Maximum number of commits to retrieve
   * @returns {Promise<Array>}
   */
  async getAuditTrail(filePath, maxCommits = null) {
    const params = new URLSearchParams({ file_path: filePath });
    if (maxCommits) {
      params.append('max_commits', maxCommits);
    }
    const response = await fetch(`${this.baseURL}/audit-trail?${params}`);
    if (!response.ok) {
      throw new Error(`Failed to fetch audit trail: ${response.statusText}`);
    }
    return response.json();
  }

  /**
   * Fetch lineage graph for a file
   * @param {string} filePath - Path to the file
   * @returns {Promise<Object>}
   */
  async getLineage(filePath) {
    const params = new URLSearchParams({ file_path: filePath });
    const response = await fetch(`${this.baseURL}/lineage?${params}`);
    if (!response.ok) {
      throw new Error(`Failed to fetch lineage: ${response.statusText}`);
    }
    return response.json();
  }

  /**
   * Validate DTA metadata
   * @param {Object} metadata - Metadata object to validate
   * @returns {Promise<Object>}
   */
  async validateMetadata(metadata) {
    const response = await fetch(`${this.baseURL}/validate`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(metadata),
    });
    if (!response.ok) {
      throw new Error(`Failed to validate metadata: ${response.statusText}`);
    }
    return response.json();
  }

  /**
   * Get health status of the API
   * @returns {Promise<Object>}
   */
  async getHealth() {
    const response = await fetch(`${this.baseURL}/health`);
    if (!response.ok) {
      throw new Error(`API health check failed: ${response.statusText}`);
    }
    return response.json();
  }
}

/**
 * Application class
 */
class App {
  constructor() {
    this.api = new APIClient();
    this.components = {};
  }

  /**
   * Initialize the application
   */
  async init() {
    console.log('Initializing DTA Provenance Dashboard...');

    // Check API health
    try {
      const health = await this.api.getHealth();
      console.log('API Status:', health);
    } catch (error) {
      console.error('API not available:', error);
      this.showError('API server is not available. Please ensure the API server is running on port 8000.');
      return;
    }

    // Initialize components
    this.components.provenanceViewer = new ProvenanceViewer(
      document.getElementById('provenance-viewer'),
      this.api
    );

    this.components.auditTrail = new AuditTrail(
      document.getElementById('audit-trail'),
      this.api
    );

    this.components.lineageGraph = new LineageGraph(
      document.getElementById('lineage-graph'),
      this.api
    );

    this.components.validator = new Validator(
      document.getElementById('validator'),
      this.api
    );

    // Render all components
    this.components.provenanceViewer.render();
    this.components.auditTrail.render();
    this.components.lineageGraph.render();
    this.components.validator.render();

    console.log('Dashboard initialized successfully');
  }

  /**
   * Display error message
   * @param {string} message - Error message
   */
  showError(message) {
    const app = document.getElementById('app');
    const errorDiv = document.createElement('div');
    errorDiv.className = 'error-banner';
    errorDiv.innerHTML = `
      <div class="container">
        <strong>Error:</strong> ${message}
      </div>
    `;
    app.insertBefore(errorDiv, app.firstChild);
  }
}

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
  const app = new App();
  app.init();
});
