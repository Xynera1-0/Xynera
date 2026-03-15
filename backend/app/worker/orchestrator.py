"""
Orchestrator worker — two instances run concurrently, each doing:

    BLPOP ──► acquire_lock ──► set "processing"
          ──► build OrchestratorState
          ──► execute LangGraph workflow
          ──► store artifact in Redis
          ──► persist assistant message + insight in Postgres
          ──► release lock
"""

from __future__ import annotations

import asyncio
import logging
import uuid

import redis.asyncio as aioredis

from app.config import get_settings
from app.db.models import Insight, Message
from app.db.session import AsyncSessionLocal
from app.models.state import OrchestratorState
from app.queue.redis_queue import (
    acquire_lock,
    extend_lock,
    pop_job,
    release_lock,
    set_job_status,
    store_result,
)

settings = get_settings()
logger = logging.getLogger(__name__)

LOCK_TTL = 120            # seconds — generous for agent round-trips
LOCK_EXTEND_INTERVAL = 80 # extend well before expiry


async def _keep_lock_alive(
    redis: aioredis.Redis,
    job_id: str,
    worker_id: str,
    stop: asyncio.Event,
) -> None:
    """Background task that extends the lock while the workflow executes."""
    while not stop.is_set():
        await asyncio.sleep(LOCK_EXTEND_INTERVAL)
        if stop.is_set():
            break
        ok = await extend_lock(redis, job_id, worker_id, ttl=LOCK_TTL)
        if not ok:
            logger.warning("[%s] Lost lock ownership for job %s", worker_id, job_id)
            break


async def _run_workflow(job: dict) -> dict:
    """
    Build an OrchestratorState from the Redis job payload,
    then execute the LangGraph graph end-to-end.

    Returns the aggregated_insights dict as the artifact.
    """
    from app.workflows.orchestrator_workflow import execute_workflow

    state = OrchestratorState(
        user_id=job["user_id"],
        session_id=job["session_id"],
        request_id=job["job_id"],
        user_query=job["query"],
        user_metadata={},
    )

    result_state = await execute_workflow(state)

    artifact = {
        "type": "text_summary",
        "title": f"Analysis: {job['query'][:100]}",
        "data": result_state.aggregated_insights or {},
        "status": result_state.status.value,
        "confidence": result_state.final_confidence,
        "agents_completed": list(result_state.agent_outputs.keys()),
        "error": result_state.error_message,
    }
    return artifact


async def _persist_response(
    session_id: str,
    user_id: str,
    job_id: str,
    query: str,
    artifact: dict,
) -> None:
    """Save the assistant reply and an insight record to Postgres."""
    async with AsyncSessionLocal() as db:
        msg = Message(
            session_id=uuid.UUID(session_id),
            user_id=uuid.UUID(user_id),
            role="assistant",
            content=artifact.get("data", {}).get("summary", ""),
            artifact=artifact,
            job_id=job_id,
        )
        insight = Insight(
            user_id=uuid.UUID(user_id),
            query=query,
            artifact=artifact,
        )
        db.add_all([msg, insight])
        await db.commit()


async def run_worker(worker_id: str) -> None:
    """
    Main loop for one orchestrator worker.
    Two of these run side-by-side via asyncio.gather in run_workers.py.
    """
    logger.info("[%s] Orchestrator worker starting — listening on jobs:incoming", worker_id)
    redis = aioredis.from_url(settings.REDIS_URL, decode_responses=True)

    try:
        while True:
            # 1. BLPOP — blocks until a job lands in the queue
            job = await pop_job(redis, timeout=0)
            if job is None:
                continue

            job_id: str = job["job_id"]
            logger.info("[%s] Picked up job %s", worker_id, job_id)

            # 2. Acquire lock
            locked = await acquire_lock(redis, job_id, worker_id, ttl=LOCK_TTL)
            if not locked:
                logger.info("[%s] Lock not acquired for %s — another worker has it", worker_id, job_id)
                continue

            # 3. Start periodic lock extension
            stop = asyncio.Event()
            lock_task = asyncio.create_task(
                _keep_lock_alive(redis, job_id, worker_id, stop)
            )

            try:
                await set_job_status(redis, job_id, "processing")

                # 4. Execute the LangGraph workflow
                artifact = await _run_workflow(job)

                # 5. Store result in Redis
                await store_result(redis, job_id, artifact)

                # 6. Persist to Postgres
                await _persist_response(
                    job["session_id"],
                    job["user_id"],
                    job_id,
                    job["query"],
                    artifact,
                )

                logger.info("[%s] Completed job %s", worker_id, job_id)

            except Exception:
                logger.exception("[%s] Failed job %s", worker_id, job_id)
                await set_job_status(
                    redis, job_id, "failed", error="Internal processing error"
                )

            finally:
                stop.set()
                lock_task.cancel()
                await release_lock(redis, job_id, worker_id)

    finally:
        await redis.aclose()
