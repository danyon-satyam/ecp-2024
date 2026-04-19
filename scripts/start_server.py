"""
Production server startup script.

Windows note: Uvicorn multi-process workers use the 'spawn' method on
Windows (not 'fork' like Linux). With heavy dependencies like CatBoost,
each spawned worker reloads the model — causing memory pressure and
timeouts under load. On Windows, we use a single process with multiple
threads via the thread_count parameter for concurrency instead.

On Linux/GCP: multi-worker mode works correctly and should be used.

Usage:
  python scripts/start_server.py              # Auto-detects OS
  python scripts/start_server.py --workers 4  # Override (Linux only)
  python scripts/start_server.py --port 8080
"""
import sys
import argparse
import uvicorn

sys.path.insert(0, ".")
from app.core.config import settings


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Start the Student Sentiment API server."
    )
    parser.add_argument("--workers", type=int, default=None)
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--host", type=str, default="0.0.0.0")
    args = parser.parse_args()

    is_windows = sys.platform == "win32"

    if is_windows:
        # Windows: single process, use asyncio (uvloop not available)
        # Concurrency comes from async endpoints + thread pool for DB
        print(f"\n{'='*55}")
        print(f"  {settings.app_name}")
        print(f"  Windows mode: single process + async concurrency")
        print(f"  Port: {args.port}")
        print(f"{'='*55}\n")

        uvicorn.run(
            "app.main:app",
            host=args.host,
            port=args.port,
            workers=1,           # Single process on Windows
            loop="asyncio",      # uvloop not available on Windows
            log_level="warning", # Reduce log noise under load
            access_log=False,    # Disable access log under load
            reload=False,
        )
    else:
        # Linux/GCP: true multi-process workers
        worker_count = args.workers or settings.workers
        print(f"\n{'='*55}")
        print(f"  {settings.app_name}")
        print(f"  Linux mode: {worker_count} workers")
        print(f"  Port: {args.port}")
        print(f"{'='*55}\n")

        uvicorn.run(
            "app.main:app",
            host=args.host,
            port=args.port,
            workers=worker_count,
            loop="uvloop",
            log_level="warning",
            access_log=False,
            reload=False,
        )


if __name__ == "__main__":
    main()