# FIXES.md — Bug Report

## Bug 1 — CRITICAL: .env committed with real credentials
- **File:** `api/.env`
- **Line:** entire file
- **Problem:** File containing `REDIS_PASSWORD=supersecretpassword123` was committed to the repo, exposing a real credential in git history.
- **Fix:** Removed file from git tracking (`git rm --cached api/.env`), added `.env` to `.gitignore`, created `.env.example` with placeholder values.

## Bug 2 — API Redis host hardcoded to localhost
- **File:** `api/main.py`
- **Line:** 8
- **Problem:** `redis.Redis(host="localhost")` fails inside Docker — containers cannot reach `localhost` on another container.
- **Fix:** Changed to `host=os.getenv("REDIS_HOST", "redis")` to read from environment variable.

## Bug 3 — API Redis password ignored
- **File:** `api/main.py`
- **Line:** 8
- **Problem:** Redis was configured with a password (in .env) but the Redis client was constructed without the `password` argument, causing authentication failures.
- **Fix:** Added `password=os.getenv("REDIS_PASSWORD")` to the Redis constructor.

## Bug 4 — API decode_responses not set, brittle .decode() call
- **File:** `api/main.py`
- **Line:** 20
- **Problem:** `status.decode()` called on line 20 assumes a bytes return from Redis. If `status` is `None` this raises `AttributeError`. With `decode_responses=True` the client returns strings directly.
- **Fix:** Added `decode_responses=True` to Redis constructor. Replaced `.decode()` with a proper None check returning 404.

## Bug 5 — API uvicorn binds to 127.0.0.1 by default
- **File:** Docker CMD (not yet written at time of discovery)
- **Problem:** Running uvicorn without `--host 0.0.0.0` makes the API unreachable from other containers or health check endpoints.
- **Fix:** Added `--host 0.0.0.0` to the Dockerfile CMD.

## Bug 6 — API requirements.txt missing version pins and uvicorn[standard]
- **File:** `api/requirements.txt`
- **Problem:** No version pins produce non-deterministic builds. `uvicorn` without `[standard]` misses production-grade async extras.
- **Fix:** Pinned all packages, changed to `uvicorn[standard]`.

## Bug 7 — Worker Redis host hardcoded to localhost
- **File:** `worker/worker.py`
- **Line:** 3
- **Problem:** Same container networking issue as Bug 2.
- **Fix:** Changed to `host=os.getenv("REDIS_HOST", "redis")`.

## Bug 8 — Worker Redis password ignored
- **File:** `worker/worker.py`
- **Line:** 3
- **Problem:** Same as Bug 3 — worker will fail to authenticate with Redis.
- **Fix:** Added `password=os.getenv("REDIS_PASSWORD")` to Redis constructor.

## Bug 9 — Worker has no graceful shutdown handling
- **File:** `worker/worker.py`
- **Problem:** Infinite `while True` loop with no SIGTERM/SIGINT handling. Docker sends SIGTERM on stop; without handling it the container is force-killed after the grace period, potentially mid-job.
- **Fix:** Added `signal.signal(SIGTERM)` and `signal.signal(SIGINT)` handlers with a `shutdown` flag that cleanly exits after the current job.

## Bug 10 — Worker requirements.txt missing version pin
- **File:** `worker/requirements.txt`
- **Problem:** `redis` with no version; non-deterministic builds.
- **Fix:** Pinned to `redis==5.0.4`.

## Bug 11 — Frontend API URL hardcoded to localhost:8000
- **File:** `frontend/app.js`
- **Line:** 5
- **Problem:** `const API_URL = "http://localhost:8000"` — same container networking issue. Frontend container cannot reach `localhost:8000` as that refers to itself.
- **Fix:** Changed to `const API_URL = process.env.API_URL || "http://api:8000"`.

## Bug 12 — Frontend package.json missing engines field and no lockfile
- **File:** `frontend/package.json`
- **Problem:** No `engines` field means unpredictable Node version in Docker. No `package-lock.json` means `npm install` picks latest compatible versions, breaking reproducibility.
- **Fix:** Added `"engines": { "node": ">=20" }`, ran `npm install` to generate `package-lock.json` and committed it.