# FastAPI Logging Issues & Solutions

## Problem Summary

### Issue: Request timing logs not appearing anywhere

**Symptoms:**
- `app.log` was empty (0 bytes)
- No logs visible in uvicorn terminal after making requests
- Middleware was confirmed executing (via `middleware_debug.log`)

---

## Root Cause

**Uvicorn hijacks Python's logging system on startup.**

When uvicorn starts, it reconfigures the root logger and all handlers. Any `logging.basicConfig()` or custom logger setup done at module level gets overridden or ignored after uvicorn initializes.

Specifically:
- `logging.basicConfig()` with `force=True` still didn't work because uvicorn re-runs its own logging config after the app module loads
- Named loggers (`logging.getLogger("fastapi_todo")`) had their handlers cleared on reload
- `logger.info()` calls in middleware were silently dropped

---

## What Was Tried (and Failed)

1. `logging.basicConfig(force=True)` — overridden by uvicorn
2. Custom named logger `"fastapi_todo"` with file handler — handlers cleared on reload
3. `logging.StreamHandler(sys.stdout)` — output captured by uvicorn, not written to file
4. `timing_file_logger` as module-level logger — same issue, cleared on reload

---

## Solution

**Write directly to the log file inside the middleware** using Python's built-in `open()`, bypassing the logging system entirely.

```python
@app.middleware("http")
async def request_timing_middleware(request: Request, call_next):
    import time
    from datetime import datetime
    import os

    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time

    log_line = f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} INFO timing_middleware Request timing | {request.method} {request.url.path} | Duration: {duration:.4f}s | Status: {response.status_code}\n"
    log_path = os.path.join(os.path.dirname(__file__), "app.log")
    with open(log_path, "a") as f:
        f.write(log_line)
    print(log_line.strip())

    return response
```

**Why this works:** `open()` is not affected by uvicorn's logging configuration. It writes directly to the filesystem regardless of how Python's `logging` module is configured.

---

## Viewing Logs

```bash
# Watch live
tail -f /Users/Mac/code/project/FastAPI/app.log

# Filter timing logs only
grep "Request timing" /Users/Mac/code/project/FastAPI/app.log
```

**Sample output:**
```
2026-02-20 23:43:07 INFO timing_middleware Request timing | GET /health | Duration: 0.0059s | Status: 200
2026-02-20 23:43:16 INFO timing_middleware Request timing | POST /auth/login | Duration: 0.3682s | Status: 200
2026-02-20 23:43:16 INFO timing_middleware Request timing | GET /todos | Duration: 0.0175s | Status: 200
```
