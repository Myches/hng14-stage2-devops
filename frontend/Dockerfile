# syntax=docker/dockerfile:1

FROM node:20-slim AS builder
WORKDIR /build

COPY package*.json ./
RUN npm ci --only=production

FROM node:20-slim AS runtime
WORKDIR /app

RUN groupadd --system appgroup && useradd --system --gid appgroup appuser

COPY --from=builder /build/node_modules ./node_modules
COPY --chown=appuser:appgroup app.js .
COPY --chown=appuser:appgroup views/ ./views/

USER appuser

EXPOSE 3000

HEALTHCHECK --interval=10s --timeout=5s --start-period=15s --retries=3 \
    CMD node -e "require('http').get('http://localhost:3000/health', r => process.exit(r.statusCode === 200 ? 0 : 1)).on('error', () => process.exit(1))"

CMD ["node", "app.js"]