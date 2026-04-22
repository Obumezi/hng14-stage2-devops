# --------- BUILD STAGE ---------
FROM python:3.11-slim AS builder

WORKDIR /app

RUN apt-get update && apt-get install -y gcc

COPY worker/requirements.txt .

RUN pip install --no-cache-dir --user -r requirements.txt

# --------- FINAL STAGE ---------
FROM python:3.11-slim

RUN useradd -m appuser

# Install procps for health checks (contains pgrep)
RUN apt-get update && apt-get install -y procps && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY --from=builder --chown=appuser:appuser /root/.local /home/appuser/.local

COPY --chown=appuser:appuser worker/ .

ENV PATH=/home/appuser/.local/bin:$PATH

USER appuser

# Healthcheck (simple process check)
HEALTHCHECK --interval=10s --timeout=3s --retries=5 \
  CMD pgrep -f worker.py || exit 1

CMD ["python", "worker.py"]