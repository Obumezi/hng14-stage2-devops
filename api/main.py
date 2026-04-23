from fastapi import FastAPI
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
    try:
        job_id = str(uuid.uuid4())

        r.lpush("jobs", job_id)
        r.hset(f"job:{job_id}", "status", "queued")

        threading.Thread(target=process_job, args=(job_id,), daemon=True).start()

        return {"job_id": job_id}

    except Exception as e:
        return {"error": str(e)}


@app.get("/jobs/{job_id}")
def get_job(job_id: str):
    status = r.hget(f"job:{job_id}", "status")

    if not status:
        return {"error": "not found"}

    return {"job_id": job_id, "status": status}
