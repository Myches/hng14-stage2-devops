# syntax=docker/dockerfile:1

FROM python:3.12-slim AS builder
WORKDIR /build

COPY requirements.txt .
RUN pip install --upgrade pip \
 && pip install --no-cache-dir --prefix=/install -r requirements.txt

FROM python:3.12-slim AS runtime
WORKDIR /app

RUN addgroup --system appgroup && adduser --system --ingroup appgroup appuser

COPY --from=builder /install /usr/local
COPY --chown=appuser:appgroup worker.py .

USER appuser

HEALTHCHECK --interval=15s --timeout=5s --start-period=20s --retries=3 \
    CMD python -c "import redis, os; r = redis.Redis(host=os.getenv('REDIS_HOST','redis'), password=os.getenv('REDIS_PASSWORD'), decode_responses=True); r.ping()"

CMD ["python", "-u", "worker.py"]