# DTA Provenance Dashboard

Frontend dashboard for visualizing and interacting with DTA-compliant data provenance tracking.

## Features

- **Provenance Lookup**: View detailed provenance metadata for any commit
- **Audit Trail**: Explore complete file history with timeline visualization
- **Lineage Graph**: Interactive D3-based DAG visualization of data lineage
- **Metadata Validator**: Validate DTA v1.0.0 compliance in real-time

## Prerequisites

- Node.js 20+ (for development)
- DTA Provenance API Server running on port 8000

## Development

### Install Dependencies

```bash
npm install
```

### Run Development Server

```bash
npm run dev
```

The dashboard will be available at http://localhost:3000

API requests to `/api/*` will be proxied to `http://localhost:8000`

### Build for Production

```bash
npm run build
```

Built files will be in the `dist/` directory.

### Preview Production Build

```bash
npm run preview
```

## Docker Deployment

### Build and Run with Docker Compose

From the root directory:

```bash
docker-compose up --build
```

Services:
- Dashboard: http://localhost:3000
- API: http://localhost:8000

### Build Docker Image Only

```bash
docker build -t dta-provenance-dashboard .
```

## Project Structure

```
dashboard/
├── index.html              # SPA shell
├── package.json            # Dependencies and scripts
├── vite.config.js          # Vite configuration
├── Dockerfile              # Multi-stage Docker build
├── nginx.conf              # Nginx configuration for production
├── src/
│   ├── main.js            # Application entry point
│   ├── style.css          # Global styles
│   └── components/
│       ├── provenance-viewer.js   # Provenance metadata display
│       ├── audit-trail.js         # Audit trail timeline
│       ├── lineage-graph.js       # D3 lineage visualization
│       └── validator.js           # Metadata validator form
```

## API Integration

The dashboard communicates with the DTA Provenance API Server using the following endpoints:

- `GET /api/health` - API health check
- `GET /api/provenance/:commit_hash` - Get provenance metadata
- `GET /api/audit-trail?file_path=<path>` - Get file audit trail
- `GET /api/lineage?file_path=<path>` - Get lineage graph
- `POST /api/validate` - Validate metadata

## Customization

### Theme Colors

Edit `src/style.css` CSS variables:

```css
:root {
  --primary: #5c6ac4;
  --secondary: #47c1bf;
  --success: #00c853;
  /* ... */
}
```

### API URL

For non-Docker deployments, update the API URL in `vite.config.js`:

```javascript
proxy: {
  '/api': {
    target: 'http://your-api-server:8000',
    // ...
  }
}
```

## Technology Stack

- **Vite** - Build tool and dev server
- **D3.js** - Graph visualization
- **Vanilla JavaScript** - No framework dependencies
- **Nginx** - Production web server

## License

MIT License - see [LICENSE](../LICENSE) for details.
