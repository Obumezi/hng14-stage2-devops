# 🚀 Full Stack Job Processing System

This project is a containerized microservices application consisting of:

* **Frontend (Express)** – handles user requests
* **Backend (FastAPI)** – manages job creation and status
* **Worker (Python)** – processes jobs asynchronously
* **Redis** – acts as a queue and datastore

---

##  Architecture

Frontend → Backend → Redis → Worker → Redis → Backend → Frontend

---

##  Prerequisites

Ensure the following are installed on your machine:

* Docker (v20+)
* Docker Compose (v2+)
* Git

Verify installation:

```bash
docker --version
docker compose version
git --version
```

---

## Setup Instructions (From Scratch)

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/YOUR_REPO.git
cd YOUR_REPO
```

---

### 2. Create environment file

```bash
cp .env.example .env
```

Edit `.env` if needed.

---

### 3. Build and start the full stack

```bash
docker compose up --build
```

---

## What a Successful Startup Looks Like

You should see:

* Redis starts successfully
* Backend connects to Redis
* Worker begins polling for jobs
* Frontend starts on port 3000

---
 Test the System

### Submit a job

```bash
curl -X POST http://localhost:3000/job
```

Response:

```json
{
  "job_id": "some-uuid"
}
```

---

### Check job status

```bash
curl http://localhost:3000/job/<job_id>
```

Expected flow:

```json
{ "status": "queued" }
→
{ "status": "processing" }
→
{ "status": "completed" }
```

---

 Health Checks

* Backend: http://localhost:8000/health
* Frontend: http://localhost:3000/health

---

## 🛑 Stop the Stack

```bash
docker compose down
```

---

 CI/CD Pipeline

The GitHub Actions pipeline includes:

* Lint (flake8, eslint, hadolint)
* Unit Tests (pytest + coverage)
* Build (Docker images)
* Security Scan (Trivy)
* Integration Test (full stack)
* Deploy (rolling update)

---
 Project Structure

```
api/
frontend/
worker/
docker/
docker-compose.yml
.env
.github/workflows/pipeline.yml
```

---



* Redis is internal and not exposed publicly
* All configuration is managed via environment variables
* Services communicate via a private Docker network

---
