# --------- BUILD STAGE ---------
FROM python:3.11-slim AS builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y gcc

COPY backend/requirements.txt .

RUN pip install --no-cache-dir --user -r requirements.txt

# --------- FINAL STAGE ---------
FROM python:3.11-slim

# Create non-root user
RUN useradd -m appuser

# Install curl for health checks
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy only installed packages from builder
COPY --from=builder /root/.local /home/appuser/.local

# Copy app code
COPY backend/ .

# Set PATH for local installs
ENV PATH=/home/appuser/.local/bin:$PATH

# Switch user
USER appuser

EXPOSE 8000

# Healthcheck (REQUIRED)
HEALTHCHECK --interval=10s --timeout=3s --retries=5 \
  CMD curl -f http://localhost:8000/health || exit 1

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]