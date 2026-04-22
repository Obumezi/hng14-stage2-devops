# HNG14 Stage 2 DevOps - Job Processing Stack

A production-grade, containerized job processing system with API, worker, and frontend services backed by Redis.

## Architecture Overview

```
┌─────────────┐
│   Frontend  │ (Node.js Express on port 3000)
└──────┬──────┘
       │ HTTP
       ▼
┌─────────────┐
│   Backend   │ (FastAPI Python on port 8000)
└──────┬──────┘
       │ Redis Queue
       ▼
┌──────────────┐    ┌─────────────┐
│   Worker    │◄──►│    Redis    │ (In-memory queue)
└──────────────┘    └─────────────┘
```

**Services:**
- **Frontend**: User-facing dashboard to submit and monitor jobs
- **Backend**: REST API to create jobs and query status
- **Worker**: Long-running process that pulls jobs from Redis queue and processes them
- **Redis**: Message broker and job state store

## Prerequisites

### For Local Development/Testing
- Docker (v20.10+)
- Docker Compose (v2.0+)
- Git

### For CI/CD Pipeline
- GitHub repository
- GitHub Actions enabled (free tier included)

## Quick Start

### 1. Clone and Setup

```bash
git clone <repository-url>
cd hng14-stage2-devops-main
cp .env.example .env
```

### 2. Configure Environment (Optional)

The `.env.example` file contains sensible defaults. For local development, the defaults work out of the box:

```env
REDIS_HOST=redis
REDIS_PORT=6379
BACKEND_PORT=8000
FRONTEND_PORT=3000
API_URL=http://backend:8000
```

For production deployments, customize resource limits:

```env
REDIS_CPU_LIMIT=1.0
REDIS_MEMORY_LIMIT=512m
BACKEND_CPU_LIMIT=1.0
BACKEND_MEMORY_LIMIT=512m
WORKER_CPU_LIMIT=1.0
WORKER_MEMORY_LIMIT=512m
FRONTEND_CPU_LIMIT=0.5
FRONTEND_MEMORY_LIMIT=256m
```

### 3. Bring Up the Stack

```bash
docker-compose up -d
```

This will:
1. Start Redis (port 6379, internal only)
2. Wait for Redis health check
3. Start Backend (port 8000)
4. Start Frontend (port 3000)
5. Start Worker (no exposed port, connects to Redis internally)

### 4. Verify Startup

Check that all services are healthy:

```bash
docker-compose ps
```

Expected output:
```
NAME              STATUS              PORTS
redis             Up (healthy)        (internal)
backend           Up (healthy)        0.0.0.0:8000
frontend          Up (healthy)        0.0.0.0:3000
worker            Up (healthy)        (no ports)
```

Verify each service:

```bash
# Backend health check
curl http://localhost:8000/health
# Expected: {"status":"ok"}

# Frontend health check
curl http://localhost:3000/health
# Expected: {"status":"ok"}
```

### 5. Use the Application

Open in browser: **http://localhost:3000**

- Click "Submit New Job" to create a job
- Jobs will appear in the dashboard as they progress through states:
  - `queued` → `processing` → `completed`

### 6. Shutdown

```bash
docker-compose down
```

To also remove Redis data:

```bash
docker-compose down -v
```

## API Reference

### Frontend

**Submit Job**
```
POST /jobs
```
Response:
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**Get Job Status**
```
GET /jobs/{job_id}
```
Response:
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "processing"
}
```

**Health Check**
```
GET /health
```

### Backend

All `/jobs` endpoints mirror the frontend (direct pass-through to backend).

**Submit Job**
```
POST /jobs
Response: {"job_id": "..."}
```

**Get Job Status**
```
GET /jobs/{job_id}
Response: {"job_id": "...", "status": "queued|processing|completed"}
```

**Health Check**
```
GET /health
Response: {"status": "ok"}
```

## Docker Images

All images are multi-stage builds with the following properties:

### ✅ Frontend (Node.js)
- **Base**: `node:20-alpine`
- **User**: `appuser` (non-root)
- **Size**: ~200MB
- **Health Check**: HTTP GET `/health`

### ✅ Backend (Python/FastAPI)
- **Base**: `python:3.11-slim`
- **User**: `appuser` (non-root)
- **Size**: ~400MB
- **Health Check**: HTTP GET `/health`
- **Dependencies**: No build tools in final image

### ✅ Worker (Python)
- **Base**: `python:3.11-slim`
- **User**: `appuser` (non-root)
- **Size**: ~350MB
- **Health Check**: Process check via `pgrep`

## CI/CD Pipeline

The GitHub Actions pipeline runs automatically on every push and pull request.

### Pipeline Stages (Sequential)

```
┌─────────────────────────────────────────────────────┐
│ 1. LINT (Python + JavaScript + Dockerfiles)        │
└──────────────┬──────────────────────────────────────┘
               │ (fail = stop)
┌──────────────▼──────────────────────────────────────┐
│ 2. TEST (pytest with coverage, mocked Redis)       │
└──────────────┬──────────────────────────────────────┘
               │ (fail = stop)
┌──────────────▼──────────────────────────────────────┐
│ 3. BUILD (Build + Tag + Push to local registry)    │
└──────────────┬──────────────────────────────────────┘
               │ (fail = stop)
┌──────────────▼──────────────────────────────────────┐
│ 4. SECURITY SCAN (Trivy - fail on CRITICAL)        │
└──────────────┬──────────────────────────────────────┘
               │ (fail = stop)
┌──────────────▼──────────────────────────────────────┐
│ 5. INTEGRATION TEST (Full stack up, job flow)      │
└──────────────┬──────────────────────────────────────┘
               │ (fail = stop)
┌──────────────▼──────────────────────────────────────┐
│ 6. DEPLOY (Rolling update on main only)            │
└─────────────────────────────────────────────────────┘
```

#### Stage Details

**1. LINT**
- Python code: `flake8 backend/`
- JavaScript code: `eslint frontend/`
- Dockerfiles: `hadolint docker/*.Dockerfile`

**2. TEST**
- Runs 4 pytest tests with Redis mocked
- Generates coverage report (artifact)
- Min coverage: 100% for critical paths

**3. BUILD**
- Builds 3 Docker images
- Tags with commit SHA and `latest`
- Pushes to local Docker registry (service container)

**4. SECURITY SCAN**
- Trivy scans all 3 images
- Fails on any CRITICAL vulnerabilities
- Uploads SARIF reports (artifact)

**5. INTEGRATION TEST**
- Brings full stack up in runner
- Submits job via frontend
- Polls until completion (60s timeout)
- Verifies final status is `completed`
- Tears down cleanly

**6. DEPLOY** (main branch only)
- Pulls latest images from registry
- Performs rolling update with health checks
- 60-second timeout per service
- Rolls back if health check fails

### Viewing Pipeline Results

1. Go to **Actions** tab in GitHub
2. Click on a workflow run
3. View logs for each stage
4. Download artifacts (coverage report, SARIF scan results)

### Pipeline Artifacts

- **coverage-report**: pytest coverage as XML (can be viewed in IDE)
- **trivy-report**: Vulnerability scan results in SARIF format

## Troubleshooting

### Container won't start

```bash
# Check logs
docker-compose logs <service-name>

# Example:
docker-compose logs backend
```

### Health check failing

```bash
# Manually test health endpoints
curl -v http://localhost:8000/health
curl -v http://localhost:3000/health

# Check network connectivity between services
docker-compose exec backend curl http://redis:6379/health
```

### Jobs not processing

```bash
# Verify Redis has jobs in queue
docker-compose exec redis redis-cli
> LLEN jobs
> HGETALL job:<job-id>
```

### Redis connection refused

```bash
# Ensure Redis is running and healthy
docker-compose ps redis

# Check Redis is listening
docker-compose exec redis redis-cli ping
# Expected: PONG
```

## Development Workflow

### Running Tests Locally

```bash
# Install dependencies
pip install -r backend/requirements.txt
pip install pytest pytest-cov

# Run tests
pytest backend --cov=backend --cov-report=term

# Generate HTML report
pytest backend --cov=backend --cov-report=html
open htmlcov/index.html
```

### Linting

```bash
# Python
pip install flake8
flake8 backend/

# JavaScript
npm install -g eslint
echo '{"extends": "eslint:recommended"}' > .eslintrc.json
eslint frontend/

# Dockerfiles
sudo apt-get install hadolint
hadolint docker/*.Dockerfile
```

### Building Images Manually

```bash
docker build -t backend:dev -f docker/backend.Dockerfile .
docker build -t frontend:dev -f docker/frontend.Dockerfile .
docker build -t worker:dev -f docker/worker.Dockerfile .
```

## Production Deployment Notes

For production deployments beyond the GitHub Actions pipeline:

1. **Push to Registry**: Replace local registry with Docker Hub/ECR/etc
   ```bash
   docker tag backend:latest myregistry.azurecr.io/backend:v1.0.0
   docker push myregistry.azurecr.io/backend:v1.0.0
   ```

2. **Orchestration**: Use Docker Swarm or Kubernetes for:
   - Scaling workers
   - Auto-recovery
   - Distributed deployments
   - Secret management

3. **Secrets Management**: Never hardcode credentials
   - Use environment files (not in Git)
   - Use container secret managers
   - Rotate regularly

4. **Monitoring**: Set up monitoring for:
   - Container health
   - Redis queue depth
   - Job processing metrics
   - Error rates

5. **Backup**: Persist Redis data
   ```bash
   docker run -v redis-data:/data redis:7-alpine redis-server --appendonly yes
   ```

## File Structure

```
hng14-stage2-devops-main/
├── backend/
│   ├── main.py              # FastAPI application
│   ├── requirements.txt      # Python dependencies
│   └── test_api.py          # Unit tests
├── frontend/
│   ├── server.js            # Express application
│   ├── package.json         # Node dependencies
│   └── views/
│       └── index.html       # Dashboard UI
├── worker/
│   ├── worker.py            # Job processor
│   └── requirements.txt      # Python dependencies
├── docker/
│   ├── backend.Dockerfile
│   ├── frontend.Dockerfile
│   └── worker.Dockerfile
├── github/
│   └── workflows/
│       └── pipeline.yml     # CI/CD configuration
├── docker-compose.yml       # Local stack configuration
├── .env.example             # Environment variables template
├── README.md                # This file
└── FIXES.md                 # Bug fixes documentation
```

## License

[Add your license here]

## Support

For issues or questions, please:
1. Check the [Troubleshooting](#troubleshooting) section
2. Review logs: `docker-compose logs -f`
3. Open an issue on GitHub
4. Review FIXES.md for known issues and solutions

