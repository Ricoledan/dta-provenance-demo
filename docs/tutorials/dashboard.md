# Frontend Dashboard

The DTA Provenance Dashboard provides a web-based interface for visualizing and interacting with data provenance information tracked in your Git repository.

## Overview

The dashboard is a modern single-page application (SPA) built with Vite and vanilla JavaScript, featuring:

- **Provenance Lookup**: View detailed DTA metadata for any commit
- **Audit Trail**: Explore complete file history with timeline visualization
- **Lineage Graph**: Interactive D3-based DAG visualization of data dependencies
- **Metadata Validator**: Real-time validation of DTA v1.0.0 compliance

## Prerequisites

- Node.js 20 or higher (for development)
- DTA Provenance API Server running on port 8000
- Modern web browser (Chrome, Firefox, Safari, Edge)

## Quick Start

### Using Docker Compose (Recommended)

The easiest way to run both the API server and dashboard:

```bash
# From the git-native directory
docker-compose up --build

# Access the dashboard
open http://localhost:3000
```

This will start:
- API Server on port 8000
- Dashboard on port 3000

### Manual Development Setup

```bash
# Navigate to dashboard directory
cd dashboard

# Install dependencies
npm install

# Start development server
npm run dev

# Dashboard available at http://localhost:3000
```

The development server includes hot module replacement (HMR) for instant updates during development.

## Features

### 1. Provenance Lookup

View complete provenance metadata for any Git commit.

**Usage:**
1. Navigate to the "Provenance Lookup" section
2. Enter a commit hash (full or abbreviated) or use `HEAD` for the latest commit
3. Click "Lookup"

**Example:**
```
Commit: HEAD
or
Commit: a1b2c3d
```

The viewer displays:
- Source information (dataset name, provider, URL)
- Provenance details (generation method, date, type, format)
- Use and rights (intended use, legal rights, sensitive data flags)
- Additional metadata
- Git commit information (author, date, message)

### 2. Audit Trail

Explore the complete history of a file as a visual timeline.

**Usage:**
1. Navigate to the "Audit Trail" section
2. Enter the file path (relative to repository root)
3. Optionally specify maximum number of commits
4. Click "Get Audit Trail"

**Example:**
```
File: data/dataset.csv
Max commits: 10
```

The timeline shows:
- Commit hash and message
- Author and timestamp
- Provenance metadata indicators
- Chronological ordering

**Export Options:**
- Export as CSV for spreadsheet analysis
- Export as JSON for programmatic processing

### 3. Lineage Graph

Visualize data dependencies and relationships as an interactive graph.

**Usage:**
1. Navigate to the "Lineage Graph" section
2. Enter the file path
3. Click "Generate Lineage Graph"

**Features:**
- Interactive node dragging
- Color-coded node types (commits, files, datasets)
- Directed edges showing dependencies
- Tooltips with detailed information
- SVG export capability

**Node Types:**
- **Purple** - Commits with provenance metadata
- **Teal** - Data files
- **Indigo** - Datasets

**Interactions:**
- Drag nodes to rearrange
- Hover for tooltips
- Export as SVG for documentation

### 4. Metadata Validator

Validate DTA v1.0.0 compliance before committing.

**Usage:**
1. Navigate to the "Metadata Validator" section
2. Paste or type JSON metadata
3. Click "Validate Metadata"

**Features:**
- Real-time JSON syntax validation
- DTA v1.0.0 schema compliance checking
- Missing required field detection
- Field coverage statistics
- Example metadata template

**Example Workflow:**
```javascript
// Click "Load Example" to see valid metadata
// Modify as needed
// Click "Validate" to check compliance
```

## API Integration

The dashboard communicates with the API server using these endpoints:

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/health` | GET | API health check |
| `/api/provenance/:hash` | GET | Get provenance metadata |
| `/api/audit-trail` | GET | Get file history |
| `/api/lineage` | GET | Get lineage graph |
| `/api/validate` | POST | Validate metadata |

## Configuration

### Development Proxy

The Vite development server proxies API requests to avoid CORS issues:

```javascript
// vite.config.js
proxy: {
  '/api': {
    target: 'http://localhost:8000',
    changeOrigin: true,
  }
}
```

### Production Nginx Proxy

In production, nginx proxies API requests:

```nginx
# nginx.conf
location /api {
    proxy_pass http://api:8000;
    # ... proxy headers
}
```

## Deployment

### Docker Production Build

```bash
# Build dashboard image
docker build -t dta-provenance-dashboard ./dashboard

# Run with docker-compose
docker-compose up -d
```

### Manual Production Build

```bash
# Build static files
npm run build

# Files output to dist/
# Serve with any static web server
```

### Nginx Example

```nginx
server {
    listen 80;
    root /var/www/dashboard/dist;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /api {
        proxy_pass http://api-server:8000;
    }
}
```

## Customization

### Theme Colors

Edit CSS variables in `src/style.css`:

```css
:root {
  --primary: #5c6ac4;        /* Main brand color */
  --secondary: #47c1bf;      /* Accent color */
  --success: #00c853;        /* Success states */
  --warning: #ff9800;        /* Warning states */
  --error: #f44336;          /* Error states */
}
```

### Component Modifications

Each component is self-contained in `src/components/`:

- `provenance-viewer.js` - Metadata display logic
- `audit-trail.js` - Timeline rendering
- `lineage-graph.js` - D3 graph visualization
- `validator.js` - Validation form

Modify these files to customize behavior.

## Troubleshooting

### Dashboard Loads But Shows "API Not Available"

**Problem:** API server is not running or not accessible

**Solution:**
```bash
# Check API server is running
curl http://localhost:8000/api/health

# If using Docker, check container status
docker-compose ps

# View API server logs
docker-compose logs api
```

### Lineage Graph Not Rendering

**Problem:** Missing or invalid lineage data

**Solution:**
- Ensure the file has commit history
- Verify API server returns valid graph data
- Check browser console for JavaScript errors

### Validation Always Fails

**Problem:** JSON syntax errors or schema issues

**Solution:**
- Click "Load Example" to see valid format
- Use JSON validator to check syntax
- Review DTA v1.0.0 field requirements

### CORS Errors in Development

**Problem:** Direct API calls blocked by browser

**Solution:**
- Ensure Vite dev server is running (port 3000)
- Don't access dashboard directly on file:// protocol
- Use the proxy configuration in vite.config.js

## Architecture

### Technology Stack

- **Vite** - Fast build tool with HMR
- **D3.js v7** - Graph visualization library
- **Vanilla JavaScript** - No framework dependencies
- **ES Modules** - Modern module system
- **Nginx** - Production web server

### Project Structure

```
dashboard/
├── index.html              # HTML shell
├── package.json            # Dependencies
├── vite.config.js          # Build configuration
├── Dockerfile              # Multi-stage build
├── nginx.conf              # Production server config
└── src/
    ├── main.js            # App initialization
    ├── style.css          # Global styles
    └── components/
        ├── provenance-viewer.js
        ├── audit-trail.js
        ├── lineage-graph.js
        └── validator.js
```

### API Client

The `APIClient` class in `main.js` wraps all API interactions:

```javascript
class APIClient {
  async getProvenance(commitHash)
  async getAuditTrail(filePath, maxCommits)
  async getLineage(filePath)
  async validateMetadata(metadata)
  async getHealth()
}
```

## Performance

### Optimization Features

- **Gzip compression** enabled in nginx
- **Static asset caching** with 1-year expiry
- **Code splitting** via Vite
- **Minification** in production builds
- **Source maps** for debugging

### Best Practices

- Limit audit trail queries to reasonable commit counts
- Export large lineage graphs as SVG for offline viewing
- Use browser caching for repeated lookups
- Consider pagination for very large datasets

## Security

### Implemented Protections

- **XSS Prevention**: HTML escaping on all user inputs
- **CORS**: Configured in nginx and Vite
- **Security Headers**: X-Frame-Options, X-Content-Type-Options, X-XSS-Protection
- **Read-Only API**: Dashboard only reads, never modifies data

### Recommendations

- Deploy behind HTTPS in production
- Implement authentication if exposing publicly
- Regularly update dependencies (`npm audit`)
- Review nginx security headers

## Examples

### Example 1: Verify Dataset Provenance

```bash
# 1. Start services
docker-compose up -d

# 2. Open dashboard
open http://localhost:3000

# 3. In Provenance Lookup section:
#    - Enter commit hash where dataset was added
#    - Click "Lookup"
#    - Review provenance metadata

# 4. Verify DTA compliance
#    - Check for required fields
#    - Review data generation method
#    - Confirm intended use matches actual use
```

### Example 2: Audit Model Training Data

```bash
# 1. In Audit Trail section:
#    - Enter: data/training_data.csv
#    - Max commits: 20
#    - Click "Get Audit Trail"

# 2. Review timeline:
#    - Identify when dataset was created
#    - Track modifications over time
#    - Find commits with provenance metadata

# 3. Export results:
#    - Click "Export as CSV"
#    - Share with compliance team
```

### Example 3: Visualize Data Pipeline

```bash
# 1. In Lineage Graph section:
#    - Enter: data/final_dataset.parquet
#    - Click "Generate Lineage Graph"

# 2. Explore graph:
#    - Identify upstream dependencies
#    - Trace data transformations
#    - Find source datasets

# 3. Export for documentation:
#    - Click "Export as SVG"
#    - Include in technical documentation
```

## Next Steps

- [API Server Documentation](api-server.md) - Learn about API endpoints
- [Pre-commit Hooks](pre-commit-hooks.md) - Automate metadata validation
- [MLflow Integration](mlflow-integration.md) - Connect ML experiments
- [DTA Standards](../DTA_STANDARDS.md) - Understand compliance requirements

## Resources

- [Vite Documentation](https://vitejs.dev/)
- [D3.js Documentation](https://d3js.org/)
- [DTA Alliance](https://www.dtaalliance.org/)
- [Source Code](https://github.com/yourusername/dta-provenance-demo)
