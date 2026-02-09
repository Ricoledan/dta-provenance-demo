# Dashboard Quick Start

Get the DTA Provenance Dashboard running in 5 minutes.

## Option 1: Docker Compose (Recommended)

```bash
# From git-native directory
cd /path/to/dta-provenance-demo/git-native

# Start both API and Dashboard
docker-compose up --build

# Access dashboard
open http://localhost:3000
```

That's it! The dashboard is now running with the API server.

## Option 2: Local Development

### Prerequisites
- Node.js 20+
- API server running on port 8000

### Steps

```bash
# Navigate to dashboard
cd dashboard

# Install dependencies
npm install

# Start dev server
npm run dev

# Open browser
open http://localhost:3000
```

## First Steps

1. **Test Provenance Lookup**
   - Enter `HEAD` in the commit input
   - Click "Lookup"
   - View provenance metadata (if commit has metadata)

2. **Explore Audit Trail**
   - Enter a file path (e.g., `data/dataset.csv`)
   - Click "Get Audit Trail"
   - See the timeline of changes

3. **Generate Lineage Graph**
   - Enter a file path
   - Click "Generate Lineage Graph"
   - Explore the interactive visualization

4. **Validate Metadata**
   - Click "Load Example" to see valid metadata
   - Modify the JSON
   - Click "Validate Metadata"

## Troubleshooting

### "API not available" error

Check if API server is running:
```bash
curl http://localhost:8000/api/health
```

If not running:
```bash
# Start API server
dta-provenance serve --port 8000

# Or use Docker
docker-compose up api
```

### Port 3000 already in use

Change the port in `vite.config.js`:
```javascript
server: {
  port: 3001,  // Changed from 3000
  // ...
}
```

## Next Steps

- Read [Full Dashboard Documentation](../../docs/tutorials/dashboard.md)
- Learn about [API Endpoints](../../docs/tutorials/api-server.md)
- Explore [DTA Standards](../../docs/DTA_STANDARDS.md)
