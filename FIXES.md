# 🛠️ Fixes Log

This document lists all bugs identified and resolved during development.

---

## 1. Hardcoded Redis Host

* **File:** `api/main.py`
* **Line:** ~6
* **Issue:** Redis host set to `"localhost"` which fails in Docker
* **Fix:**

```python
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
```

---

## 2. Missing Health Endpoint

* **File:** `api/main.py`
* **Line:** Added
* **Issue:** No `/health` endpoint causing deployment health checks to fail
* **Fix:**

```python
@app.get("/health")
def health():
    return {"status": "ok"}
```

---

## 3. Frontend Route Mismatch

* **File:** `frontend/app.js`
* **Line:** ~10
* **Issue:** Route `/submit` did not match pipeline expectation `/job`
* **Fix:** Renamed route to `/job`

---

## 4. Frontend Missing Health Endpoint

* **File:** `frontend/app.js`
* **Issue:** No health endpoint for deployment validation
* **Fix:**

```js
app.get('/health', (req, res) => {
  res.json({ status: 'ok' });
});
```

---

## 5. Worker Infinite Loop Without Graceful Shutdown

* **File:** `worker/worker.py`
* **Issue:** Worker could not stop cleanly
* **Fix:** Added signal handling for SIGTERM/SIGINT

---

## 6. Redis Connection Not Resilient

* **File:** `worker/worker.py`
* **Issue:** Worker crashed if Redis not ready
* **Fix:** Added retry loop using `r.ping()`

---

## 7. Missing Job Status Progression

* **File:** `worker/worker.py`
* **Issue:** Jobs moved from queued → completed without "processing"
* **Fix:** Added intermediate status

---

## 8. Dockerfile Running as Root

* **File:** `docker/*.Dockerfile`
* **Issue:** Containers ran as root user
* **Fix:** Added non-root user (`appuser`)

---

## 9. Missing .dockerignore at Root

* **Issue:** Build context included unnecessary files
* **Fix:** Moved `.dockerignore` to project root

---

## 10. Environment File Misplacement

* **Issue:** `.env` located inside `api/`
* **Fix:** Moved to project root

---

## 11. API URL Hardcoded in Frontend

* **File:** `frontend/app.js`
* **Issue:** Used `localhost` instead of environment variable
* **Fix:**

```js
const API_URL = process.env.API_URL;
```

---

## 12. Integration Test Failure Due to Endpoint Names

* **Issue:** Pipeline expected `/job` but API used different route
* **Fix:** Standardized routes across services

---
