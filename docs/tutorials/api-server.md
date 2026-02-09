# API Server

The DTA Provenance API server provides REST endpoints for querying provenance metadata, generating audit trails, and validating DTA compliance.

## Quick Start

### Installation

Install with API dependencies:

```bash
pip install 'dta-provenance[api]'
```

Or install all optional dependencies:

```bash
pip install -e '.[api]'  # From source
```

### Starting the Server

Start the API server from your Git repository:

```bash
# Start on default port 8000
dta-provenance serve

# Start on custom host and port
dta-provenance serve --host 0.0.0.0 --port 8080

# Start with auto-reload for development
dta-provenance serve --reload --repo /path/to/repo
```

The server will start and display:

```
🚀 API Server Configuration
┌────────────────────────────────────┐
│ Host: 127.0.0.1                    │
│ Port: 8000                         │
│ Repository: /path/to/repo          │
│ Docs: http://127.0.0.1:8000/docs   │
│ ReDoc: http://127.0.0.1:8000/redoc │
└────────────────────────────────────┘
```

### Interactive Documentation

Access the interactive API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI Schema**: http://localhost:8000/openapi.json

## API Endpoints

### Health Check

Check if the API server is running.

**Endpoint**: `GET /health`

**Response**:
```json
{
  "status": "healthy",
  "version": "1.0.0"
}
```

**Example**:
```bash
curl http://localhost:8000/health
```

### Get Provenance Metadata

Retrieve DTA provenance metadata from a Git commit.

**Endpoint**: `GET /provenance/{commit_hash}`

**Parameters**:
- `commit_hash`: Git commit hash (full or abbreviated) or `HEAD`

**Response**:
```json
{
  "commit_hash": "abc123def456",
  "metadata": {
    "source": {
      "datasetName": "Customer Churn Dataset",
      "providerName": "Analytics Team",
      "datasetVersion": "1.0"
    },
    "provenance": {
      "dataGenerationMethod": "SQL export",
      "dateDataGenerated": "2024-01-15T00:00:00Z",
      "dataType": "Tabular",
      "dataFormat": "CSV"
    },
    "use": {
      "intendedUse": "ML model training",
      "legalRightsToUse": "Internal use only",
      "sensitiveData": false
    }
  }
}
```

**Examples**:
```bash
# Get metadata from latest commit
curl http://localhost:8000/provenance/HEAD

# Get metadata from specific commit
curl http://localhost:8000/provenance/abc123def

# Get metadata from full commit hash
curl http://localhost:8000/provenance/abc123def456789...
```

**Error Responses**:
- `404 Not Found`: Commit not found or no provenance metadata
- `500 Internal Server Error`: Server error

### Get Audit Trail

Retrieve complete audit trail for a file.

**Endpoint**: `GET /audit-trail/{file_path:path}`

**Parameters**:
- `file_path`: Relative path to file in repository
- `max_commits` (optional): Maximum number of commits to return

**Response**:
```json
{
  "file_path": "data/dataset.csv",
  "commit_count": 3,
  "audit_trail": [
    {
      "commit_hash": "abc123def",
      "date": "2024-01-15T12:00:00Z",
      "author": "user@example.com",
      "message": "Update dataset",
      "provenance": {
        "source": {
          "datasetName": "Customer Churn Dataset"
        }
      }
    },
    {
      "commit_hash": "def456ghi",
      "date": "2024-01-10T10:00:00Z",
      "author": "user@example.com",
      "message": "Initial dataset",
      "provenance": null
    }
  ]
}
```

**Examples**:
```bash
# Get full audit trail
curl http://localhost:8000/audit-trail/data/dataset.csv

# Get last 5 commits only
curl http://localhost:8000/audit-trail/data/dataset.csv?max_commits=5

# Get audit trail for nested file
curl http://localhost:8000/audit-trail/subdir/nested/file.csv
```

**Error Responses**:
- `404 Not Found`: File not found or no commits
- `500 Internal Server Error`: Server error

### Validate Metadata

Validate DTA provenance metadata against v1.0.0 standards.

**Endpoint**: `POST /validate`

**Request Body**:
```json
{
  "metadata": {
    "source": {
      "datasetName": "Test Dataset",
      "providerName": "Test Provider"
    },
    "provenance": {
      "dataGenerationMethod": "Manual",
      "dateDataGenerated": "2024-01-15T00:00:00Z",
      "dataType": "Tabular",
      "dataFormat": "CSV"
    },
    "use": {
      "intendedUse": "Testing",
      "legalRightsToUse": "Internal",
      "sensitiveData": false
    }
  }
}
```

**Response**:
```json
{
  "is_valid": true,
  "errors": [],
  "warnings": [],
  "missing_optional_fields": [
    "datasetVersion",
    "lastModifiedDate"
  ],
  "score": 0.85
}
```

**Examples**:
```bash
# Validate metadata from file
curl -X POST http://localhost:8000/validate \
  -H "Content-Type: application/json" \
  -d @provenance.json

# Validate metadata inline
curl -X POST http://localhost:8000/validate \
  -H "Content-Type: application/json" \
  -d '{
    "metadata": {
      "source": {"datasetName": "Test", "providerName": "Provider"},
      "provenance": {
        "dataGenerationMethod": "Manual",
        "dateDataGenerated": "2024-01-15T00:00:00Z",
        "dataType": "Tabular",
        "dataFormat": "CSV"
      },
      "use": {
        "intendedUse": "Testing",
        "legalRightsToUse": "Internal",
        "sensitiveData": false
      }
    }
  }'
```

**Error Responses**:
- `422 Unprocessable Entity`: Invalid request body
- `500 Internal Server Error`: Server error

### Get Lineage Graph

Generate lineage graph data for a file.

**Endpoint**: `GET /lineage/{file_path:path}`

**Parameters**:
- `file_path`: Relative path to file in repository

**Response**:
```json
{
  "file_path": "data/dataset.csv",
  "nodes": [
    {
      "id": "commit_abc123",
      "label": "abc123",
      "node_type": "commit"
    },
    {
      "id": "file_dataset",
      "label": "dataset.csv",
      "node_type": "file"
    }
  ],
  "edges": [
    {
      "source": "commit_abc123",
      "target": "file_dataset",
      "label": "modified"
    }
  ]
}
```

**Examples**:
```bash
# Get lineage graph
curl http://localhost:8000/lineage/data/dataset.csv

# Visualize with jq
curl http://localhost:8000/lineage/data/dataset.csv | jq .
```

**Error Responses**:
- `404 Not Found`: File not found
- `500 Internal Server Error`: Server error

## Docker Usage

### Using Docker Compose

The API server is included in the Docker Compose configuration.

Start all services:
```bash
docker-compose up -d
```

The API will be available at http://localhost:8000

View logs:
```bash
docker-compose logs -f api
```

Access API container:
```bash
docker-compose exec api /bin/bash
```

### Standalone Docker

Build the Docker image:
```bash
docker build -f Dockerfile.git-native -t dta-provenance:api .
```

Run the API server:
```bash
docker run -d \
  -p 8000:8000 \
  -v $(pwd)/git-native:/app/git-native \
  --name dta-api \
  dta-provenance:api \
  sh -c "pip install -e '.[api]' && dta-provenance serve --host 0.0.0.0 --port 8000"
```

Access the API:
```bash
curl http://localhost:8000/health
```

## Integration Examples

### Python Client

```python
import httpx

# Create client
client = httpx.Client(base_url="http://localhost:8000")

# Check health
response = client.get("/health")
print(response.json())

# Get provenance
response = client.get("/provenance/HEAD")
metadata = response.json()
print(f"Dataset: {metadata['metadata']['source']['datasetName']}")

# Get audit trail
response = client.get("/audit-trail/data/dataset.csv")
audit = response.json()
print(f"Found {audit['commit_count']} commits")

# Validate metadata
metadata_to_validate = {
    "source": {"datasetName": "Test", "providerName": "Provider"},
    "provenance": {
        "dataGenerationMethod": "Manual",
        "dateDataGenerated": "2024-01-15T00:00:00Z",
        "dataType": "Tabular",
        "dataFormat": "CSV"
    },
    "use": {
        "intendedUse": "Testing",
        "legalRightsToUse": "Internal",
        "sensitiveData": False
    }
}

response = client.post("/validate", json={"metadata": metadata_to_validate})
report = response.json()
print(f"Valid: {report['is_valid']}, Score: {report['score']}")
```

### JavaScript/TypeScript

```typescript
// Using fetch API
async function getProvenance(commitHash: string) {
  const response = await fetch(`http://localhost:8000/provenance/${commitHash}`);
  const data = await response.json();
  return data;
}

// Get audit trail
async function getAuditTrail(filePath: string, maxCommits?: number) {
  const url = maxCommits
    ? `http://localhost:8000/audit-trail/${filePath}?max_commits=${maxCommits}`
    : `http://localhost:8000/audit-trail/${filePath}`;

  const response = await fetch(url);
  const data = await response.json();
  return data;
}

// Validate metadata
async function validateMetadata(metadata: any) {
  const response = await fetch('http://localhost:8000/validate', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ metadata })
  });
  const data = await response.json();
  return data;
}

// Usage
const metadata = await getProvenance('HEAD');
console.log('Dataset:', metadata.metadata.source.datasetName);

const audit = await getAuditTrail('data/dataset.csv', 10);
console.log('Commits:', audit.commit_count);

const validation = await validateMetadata({
  source: { datasetName: 'Test', providerName: 'Provider' },
  // ... rest of metadata
});
console.log('Valid:', validation.is_valid);
```

### curl Scripts

Create a shell script for common operations:

```bash
#!/bin/bash
# api-client.sh

API_URL="http://localhost:8000"

case "$1" in
  health)
    curl -s "$API_URL/health" | jq .
    ;;

  provenance)
    curl -s "$API_URL/provenance/${2:-HEAD}" | jq .
    ;;

  audit)
    curl -s "$API_URL/audit-trail/$2" | jq .
    ;;

  validate)
    curl -s -X POST "$API_URL/validate" \
      -H "Content-Type: application/json" \
      -d @"$2" | jq .
    ;;

  lineage)
    curl -s "$API_URL/lineage/$2" | jq .
    ;;

  *)
    echo "Usage: $0 {health|provenance|audit|validate|lineage} [args]"
    exit 1
    ;;
esac
```

Usage:
```bash
chmod +x api-client.sh

./api-client.sh health
./api-client.sh provenance HEAD
./api-client.sh audit data/dataset.csv
./api-client.sh validate metadata.json
./api-client.sh lineage data/dataset.csv
```

## Production Deployment

### Configuration

For production deployment, configure:

1. **Security**: Add authentication middleware
2. **CORS**: Restrict allowed origins
3. **Logging**: Configure structured logging
4. **Rate Limiting**: Add rate limiting middleware
5. **HTTPS**: Use TLS certificates

### Environment Variables

```bash
export API_HOST=0.0.0.0
export API_PORT=8000
export API_REPO_PATH=/data/repo
export API_LOG_LEVEL=info
```

### Systemd Service

Create a systemd service for production:

```ini
# /etc/systemd/system/dta-api.service
[Unit]
Description=DTA Provenance API Server
After=network.target

[Service]
Type=simple
User=dta
WorkingDirectory=/opt/dta-provenance
Environment="PATH=/opt/dta-provenance/venv/bin"
ExecStart=/opt/dta-provenance/venv/bin/dta-provenance serve --host 0.0.0.0 --port 8000 --repo /data/repo
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable dta-api
sudo systemctl start dta-api
sudo systemctl status dta-api
```

### Nginx Reverse Proxy

Configure Nginx as reverse proxy:

```nginx
server {
    listen 80;
    server_name api.example.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### Monitoring

Monitor API health:
```bash
# Health check script
#!/bin/bash
if ! curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "API health check failed"
    exit 1
fi
```

## Troubleshooting

### Common Issues

**Port already in use**:
```bash
# Find process using port 8000
lsof -i :8000

# Kill process or use different port
dta-provenance serve --port 8001
```

**Permission denied on repository**:
```bash
# Check repository permissions
ls -la /path/to/repo

# Run with proper user permissions
sudo -u git-user dta-provenance serve --repo /path/to/repo
```

**Module not found**:
```bash
# Install API dependencies
pip install 'dta-provenance[api]'

# Or from source
pip install -e '.[api]'
```

### Logging

Enable debug logging:
```bash
# Set log level to debug
dta-provenance serve --reload  # Auto-reload enables debug mode
```

View uvicorn logs:
```bash
# API logs are written to stdout
dta-provenance serve 2>&1 | tee api.log
```

## Next Steps

- Explore [Interactive Documentation](http://localhost:8000/docs)
- Learn about [DVC Integration](dvc-integration.md)
- Try [MLflow Integration](mlflow-integration.md)
- See [Basic Usage](basic-usage.md) for Git operations
