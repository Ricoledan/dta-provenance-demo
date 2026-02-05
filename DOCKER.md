# Docker Setup Guide

This guide shows how to run the DTA Provenance Demo using Docker containers.

## Quick Start

### Option 1: Docker Compose (Recommended)

Start all services with one command:

```bash
docker-compose up -d
```

This starts:
- **Git-native**: Provenance tracking CLI
- **Blockchain**: Hardhat local blockchain node
- **Jupyter**: Interactive notebook server

Access services:
- Jupyter Notebook: http://localhost:8888
- Blockchain RPC: http://localhost:8545

Stop all services:
```bash
docker-compose down
```

### Option 2: Individual Containers

#### Git-Native Container

Build:
```bash
docker build -f Dockerfile.git-native -t dta-provenance:git-native .
```

Run:
```bash
# Help
docker run dta-provenance:git-native

# Validate a file
docker run -v $(pwd)/standards/examples:/data \
  dta-provenance:git-native \
  dta-provenance validate /data/healthcare-imaging.json

# Interactive shell
docker run -it --entrypoint /bin/bash dta-provenance:git-native
```

#### Blockchain Container

Build:
```bash
docker build -f Dockerfile.blockchain -t dta-provenance:blockchain .
```

Run:
```bash
# Start local blockchain node
docker run -p 8545:8545 dta-provenance:blockchain

# Run tests
docker run dta-provenance:blockchain npx hardhat test

# Interactive shell
docker run -it --entrypoint /bin/bash dta-provenance:blockchain
```

## Common Tasks

### Run Tests

```bash
# Git-native tests
docker-compose exec git-native pytest -v

# Blockchain tests
docker-compose exec blockchain npx hardhat test

# Run all tests
docker-compose exec git-native pytest && \
docker-compose exec blockchain npx hardhat test
```

### Validate DTA Examples

```bash
# Validate all examples
for file in standards/examples/*.json; do
  docker-compose exec git-native dta-provenance validate "$file"
done
```

### Use CLI Tools

```bash
# Git-native CLI
docker-compose exec git-native dta-provenance --help
docker-compose exec git-native dta-provenance validate /app/standards/examples/healthcare-imaging.json

# Blockchain deployment
docker-compose exec blockchain npx hardhat run scripts/deploy.js --network localhost
```

### Interactive Development

```bash
# Git-native shell
docker-compose exec git-native /bin/bash

# Blockchain shell
docker-compose exec blockchain /bin/bash

# Python REPL with provenance modules
docker-compose exec git-native python
>>> from src.provenance import ProvenanceMetadata
>>> # ... your code here
```

### Jupyter Notebook

Access the interactive demo:

1. Start Jupyter:
   ```bash
   docker-compose up jupyter
   ```

2. Open http://localhost:8888 in your browser

3. Open `DTA_Provenance_Demo.ipynb`

## Volume Persistence

Docker volumes preserve data across container restarts:

- `git-data`: Git repositories and data
- `blockchain-data`: Blockchain cache and artifacts
- `jupyter-data`: Jupyter configuration

View volumes:
```bash
docker volume ls | grep dta
```

Clean up volumes:
```bash
docker-compose down -v
```

## Troubleshooting

### Port Already in Use

If ports 8545 or 8888 are already in use, modify `docker-compose.yml`:

```yaml
ports:
  - "9545:8545"  # Use port 9545 instead
  - "9888:8888"  # Use port 9888 instead
```

### Permission Issues

If you encounter permission issues with volumes:

```bash
# Fix ownership
docker-compose exec git-native chown -R $(id -u):$(id -g) /data
```

### Rebuild Containers

Force rebuild after code changes:

```bash
docker-compose build --no-cache
docker-compose up -d
```

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f git-native
docker-compose logs -f blockchain
docker-compose logs -f jupyter
```

## Production Deployment

For production use, consider:

1. **Security**:
   - Use proper authentication for Jupyter
   - Secure blockchain RPC endpoints
   - Run containers as non-root user

2. **Networking**:
   - Use reverse proxy (nginx, Traefik)
   - Enable TLS/SSL
   - Restrict network access

3. **Resource Limits**:
   ```yaml
   services:
     git-native:
       deploy:
         resources:
           limits:
             cpus: '1.0'
             memory: 1G
   ```

4. **Environment Variables**:
   - Use `.env` file for sensitive data
   - Never commit secrets to Git

5. **Monitoring**:
   - Add health checks
   - Use logging aggregation
   - Monitor resource usage

## Multi-Architecture Support

Build for multiple architectures (ARM64, AMD64):

```bash
# Enable Docker buildx
docker buildx create --use

# Build multi-arch images
docker buildx build --platform linux/amd64,linux/arm64 \
  -f Dockerfile.git-native \
  -t dta-provenance:git-native \
  --push .
```

## CI/CD Integration

Example GitHub Actions workflow:

```yaml
- name: Build and test Docker images
  run: |
    docker-compose build
    docker-compose up -d
    docker-compose exec -T git-native pytest
    docker-compose exec -T blockchain npx hardhat test
    docker-compose down
```

## Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Dockerfile Best Practices](https://docs.docker.com/develop/develop-images/dockerfile_best-practices/)

---

**Need help?** Open an issue on GitHub or check the main [README.md](README.md)
