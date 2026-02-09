/**
 * Validator Component
 * Form for JSON validation via POST /validate
 */
export class Validator {
  constructor(container, api) {
    this.container = container;
    this.api = api;
  }

  /**
   * Render the component
   */
  render() {
    this.container.innerHTML = `
      <div class="validator-form">
        <div class="form-group">
          <label for="metadata-input">Paste DTA Metadata JSON:</label>
          <textarea
            id="metadata-input"
            class="textarea"
            rows="15"
            placeholder='{\n  "source": {\n    "datasetName": "Example Dataset",\n    "providerName": "Analytics Team"\n  },\n  "provenance": {\n    "dataGenerationMethod": "SQL export",\n    "dateDataGenerated": "2024-01-15T00:00:00Z",\n    "dataType": "Tabular",\n    "dataFormat": "CSV"\n  },\n  "use": {\n    "intendedUse": "ML training",\n    "legalRightsToUse": "Internal use",\n    "sensitiveData": false\n  }\n}'
          ></textarea>
        </div>
        <div class="form-actions">
          <button id="validate-btn" class="btn btn-primary">Validate Metadata</button>
          <button id="clear-btn" class="btn btn-secondary">Clear</button>
          <button id="load-example-btn" class="btn btn-secondary">Load Example</button>
        </div>
      </div>
      <div id="validation-result"></div>
    `;

    // Attach event listeners
    const validateBtn = this.container.querySelector('#validate-btn');
    const clearBtn = this.container.querySelector('#clear-btn');
    const loadExampleBtn = this.container.querySelector('#load-example-btn');

    validateBtn.addEventListener('click', () => this.validateMetadata());
    clearBtn.addEventListener('click', () => this.clearForm());
    loadExampleBtn.addEventListener('click', () => this.loadExample());
  }

  /**
   * Validate metadata
   */
  async validateMetadata() {
    const metadataInput = this.container.querySelector('#metadata-input');
    const metadataText = metadataInput.value.trim();

    if (!metadataText) {
      this.showError('Please enter metadata JSON');
      return;
    }

    // Parse JSON
    let metadata;
    try {
      metadata = JSON.parse(metadataText);
    } catch (error) {
      this.showError(`Invalid JSON: ${error.message}`);
      return;
    }

    const resultDiv = this.container.querySelector('#validation-result');
    resultDiv.innerHTML = '<div class="loading">Validating metadata...</div>';

    try {
      const result = await this.api.validateMetadata(metadata);
      this.displayValidationResult(result);
    } catch (error) {
      this.showError(error.message);
    }
  }

  /**
   * Display validation result
   * @param {Object} result - Validation result
   */
  displayValidationResult(result) {
    const resultDiv = this.container.querySelector('#validation-result');

    if (result.valid) {
      resultDiv.innerHTML = `
        <div class="message success">
          <h3>✓ Validation Successful</h3>
          <p>The metadata is compliant with DTA v1.0.0 standards.</p>
          ${result.warnings && result.warnings.length > 0 ? `
            <div class="warnings">
              <h4>Warnings:</h4>
              <ul>
                ${result.warnings.map(w => `<li>${this.escapeHtml(w)}</li>`).join('')}
              </ul>
            </div>
          ` : ''}
        </div>
        ${this.renderFieldSummary(result)}
      `;
    } else {
      resultDiv.innerHTML = `
        <div class="message error">
          <h3>✗ Validation Failed</h3>
          <p>The metadata does not comply with DTA v1.0.0 standards.</p>
          ${result.errors && result.errors.length > 0 ? `
            <div class="errors">
              <h4>Errors:</h4>
              <ul>
                ${result.errors.map(e => `<li>${this.escapeHtml(e.message || e)}</li>`).join('')}
              </ul>
            </div>
          ` : ''}
          ${result.missing_required && result.missing_required.length > 0 ? `
            <div class="missing-fields">
              <h4>Missing Required Fields:</h4>
              <ul>
                ${result.missing_required.map(f => `<li><code>${this.escapeHtml(f)}</code></li>`).join('')}
              </ul>
            </div>
          ` : ''}
        </div>
      `;
    }
  }

  /**
   * Render field summary
   * @param {Object} result - Validation result
   * @returns {string} HTML string
   */
  renderFieldSummary(result) {
    if (!result.field_summary) return '';

    const summary = result.field_summary;

    return `
      <div class="field-summary">
        <h4>Field Summary</h4>
        <div class="summary-stats">
          <div class="stat">
            <span class="stat-label">Required Fields:</span>
            <span class="stat-value">${summary.required_present || 0} / ${summary.required_total || 0}</span>
          </div>
          <div class="stat">
            <span class="stat-label">Optional Fields:</span>
            <span class="stat-value">${summary.optional_present || 0} / ${summary.optional_total || 0}</span>
          </div>
          <div class="stat">
            <span class="stat-label">Total Fields:</span>
            <span class="stat-value">${summary.total_present || 0} / ${summary.total_fields || 0}</span>
          </div>
        </div>
      </div>
    `;
  }

  /**
   * Clear form
   */
  clearForm() {
    const metadataInput = this.container.querySelector('#metadata-input');
    const resultDiv = this.container.querySelector('#validation-result');
    metadataInput.value = '';
    resultDiv.innerHTML = '';
  }

  /**
   * Load example metadata
   */
  loadExample() {
    const metadataInput = this.container.querySelector('#metadata-input');
    const example = {
      source: {
        datasetName: "Customer Churn Dataset",
        providerName: "Analytics Team",
        sourceURL: "https://example.com/datasets/churn"
      },
      provenance: {
        dataGenerationMethod: "SQL export from production database",
        dateDataGenerated: "2024-01-15T00:00:00Z",
        dataType: "Tabular",
        dataFormat: "CSV",
        dataSchema: {
          columns: ["customer_id", "churn", "tenure", "monthly_charges"],
          types: ["string", "boolean", "integer", "float"]
        }
      },
      use: {
        intendedUse: "Machine learning model training for churn prediction",
        legalRightsToUse: "Internal use only - covered under data processing agreement",
        sensitiveData: false,
        restrictions: "Do not share externally without legal approval"
      },
      metadata: {
        version: "1.0.0",
        created: "2024-01-15T10:30:00Z",
        creator: "data-team@example.com",
        description: "Historical customer data for training churn prediction models"
      }
    };

    metadataInput.value = JSON.stringify(example, null, 2);
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
    const resultDiv = this.container.querySelector('#validation-result');
    resultDiv.innerHTML = `
      <div class="message error">
        <strong>Error:</strong> ${this.escapeHtml(message)}
      </div>
    `;
  }
}
