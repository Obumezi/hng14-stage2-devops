from fastapi import FastAPI
import redis
import uuid
import os
import threading
import time

app = FastAPI()

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))


# -----------------------------
# Redis safe connection
# -----------------------------
def get_redis():
    for i in range(10):
        try:
            client = redis.Redis(
                host=REDIS_HOST,
                port=REDIS_PORT,
                decode_responses=True
            )
            client.ping()
            print("✅ Connected to Redis")
            return client
        except Exception as e:
            print(f"⏳ Redis not ready, retrying... ({i+1}/10)")
            time.sleep(2)

    raise Exception("❌ Could not connect to Redis")


r = get_redis()


# -----------------------------
# Background job processor
# -----------------------------
def process_job(job_id: str):
    try:
        time.sleep(2)
        r.hset(f"job:{job_id}", "status", "completed")
    except Exception as e:
        r.hset(f"job:{job_id}", "status", "failed")


# -----------------------------
# Health check (Docker-safe)
# -----------------------------
@app.get("/health")
def health():
    return {"status": "ok"}


# -----------------------------
# Create job
# -----------------------------
@app.post("/jobs")
def create_job():
    job_id = str(uuid.uuid4())

    r.lpush("jobs", job_id)
    r.hset(f"job:{job_id}", "status", "queued")

    # safer thread handling
    thread = threading.Thread(target=process_job, args=(job_id,), daemon=True)
    thread.start()

    return {"job_id": job_id}


# -----------------------------
# Get job status
# -----------------------------
@app.get("/jobs/{job_id}")
def get_job(job_id: str):
    status = r.hget(f"job:{job_id}", "status")

    if not status:
        return {"error": "not found"}

    return {
        "job_id": job_id,
        "status": status
    }










""" from fastapi import FastAPI
import redis
import uuid
import os
import threading
import time

app = FastAPI()

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")

r = redis.Redis(host=REDIS_HOST, port=6379, decode_responses=True)


def process_job(job_id):
    time.sleep(2)
    r.hset(f"job:{job_id}", "status", "completed")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/jobs")
def create_job():
    job_id = str(uuid.uuid4())
    r.lpush("jobs", job_id)
    r.hset(f"job:{job_id}", "status", "queued")

    threading.Thread(target=process_job, args=(job_id,)).start()

    return {"job_id": job_id}


@app.get("/jobs/{job_id}")
def get_job(job_id: str):
    status = r.hget(f"job:{job_id}", "status")

    if not status:
        return {"error": "not found"}

    return {"job_id": job_id, "status": status}
 """


