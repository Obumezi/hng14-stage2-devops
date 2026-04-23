import redis
import time
import os
import signal


REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
QUEUE_NAME = "jobs"

r = redis.Redis(
    host=os.getenv("REDIS_HOST", "localhost"),
    port=int(os.getenv("REDIS_PORT", 6379))
)

running = True


def shutdown_handler(signum, frame):
    global running
    running = False


signal.signal(signal.SIGTERM, shutdown_handler)
signal.signal(signal.SIGINT, shutdown_handler)


def wait_for_redis():
    while True:
        try:
            r.ping()
            print("Connected to Redis")
            break
        except redis.ConnectionError:
            print("Waiting for Redis...")
            time.sleep(2)


def process_job(job_id):
    try:
        print(f"Processing job {job_id}")
        r.hset(f"job:{job_id}", "status", "processing")

        time.sleep(2)

        r.hset(f"job:{job_id}", "status", "completed")
        print(f"Done: {job_id}")
    except Exception as e:
        print(f"Error processing job {job_id}: {e}")


wait_for_redis()

while running:
    job = r.brpop(QUEUE_NAME, timeout=5)

    if job:
        _, job_id = job
        process_job(job_id)

print("Worker shutting down gracefully...")
