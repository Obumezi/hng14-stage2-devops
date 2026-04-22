# --------- BUILD STAGE ---------
FROM node:20-alpine AS builder

WORKDIR /app

COPY frontend/package*.json ./

RUN npm ci --only=production

# --------- FINAL STAGE ---------
FROM node:20-alpine

# Create non-root user
RUN addgroup -S appgroup && adduser -S appuser -G appgroup

WORKDIR /app

# Copy node_modules from builder
COPY --from=builder --chown=appuser:appuser /app/node_modules ./node_modules

# Copy app code
COPY --chown=appuser:appuser frontend/ .

USER appuser

EXPOSE 3000

# Healthcheck
HEALTHCHECK --interval=10s --timeout=3s --retries=5 \
  CMD wget --spider http://localhost:3000/health || exit 1

CMD ["node", "server.js"]