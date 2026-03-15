"""
Start two orchestrator workers that listen on the Redis job queue.

Usage:
    cd backend
    python run_workers.py
"""

import asyncio
import logging
import sys

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)-5s %(name)s — %(message)s",
    stream=sys.stdout,
)

from app.worker.orchestrator import run_worker  # noqa: E402


async def main() -> None:
    await asyncio.gather(
        run_worker("orchestrator-1"),
        run_worker("orchestrator-2"),
    )


if __name__ == "__main__":
    asyncio.run(main())
