# --------- BUILD STAGE ---------
FROM python:3.11-slim AS builder

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends build-essential=12.10 && rm -rf /var/lib/apt/lists/*

COPY worker/requirements.txt .

RUN pip install --no-cache-dir --user -r requirements.txt

# --------- FINAL STAGE ---------
FROM python:3.11-slim

RUN useradd -m appuser

# Install procps for health checks (contains pgrep)
RUN apt-get update && apt-get install -y --no-install-recommends procps=2:4.0.2-3 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY --from=builder /root/.local /home/appuser/.local

COPY worker/ .

ENV PATH=/home/appuser/.local/bin:$PATH

USER appuser

# Healthcheck (simple process check)
HEALTHCHECK --interval=10s --timeout=3s --retries=5 \
  CMD pgrep -f worker.py || exit 1

CMD ["python", "worker.py"]