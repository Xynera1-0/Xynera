"""
Redis-backed job queue with atomic locking, status tracking, and pub/sub.

Keys:
    jobs:incoming             – LIST   (LPUSH producer / BLPOP consumer)
    lock:{job_id}             – STRING (SET NX EX — one worker per job)
    job:status:{job_id}       – STRING (JSON status envelope, TTL 1 h)
    result:{job_id}           – STRING (JSON artifact, TTL 1 h)
    job:updates:{job_id}      – PUB/SUB channel for WebSocket push
"""

from __future__ import annotations

import json
import uuid
from typing import Any

import redis.asyncio as aioredis

# ── Key prefixes ──────────────────────────────────────────────────────────────
QUEUE_KEY = "jobs:incoming"
LOCK_PREFIX = "lock:"
STATUS_PREFIX = "job:status:"
RESULT_PREFIX = "result:"
CHANNEL_PREFIX = "job:updates:"

# ── Lua: release lock only if caller still owns it ────────────────────────────
_RELEASE_IF_OWNER_LUA = """
if redis.call("GET", KEYS[1]) == ARGV[1] then
    return redis.call("DEL", KEYS[1])
else
    return 0
end
"""


# ── Queue ─────────────────────────────────────────────────────────────────────

async def push_job(redis: aioredis.Redis, job: dict) -> str:
    """Push a job onto the incoming queue.  Returns the job_id."""
    job_id = job.get("job_id") or str(uuid.uuid4())
    job["job_id"] = job_id
    await redis.lpush(QUEUE_KEY, json.dumps(job))
    return job_id


async def pop_job(redis: aioredis.Redis, timeout: int = 0) -> dict | None:
    """Blocking pop (BLPOP).  Blocks until a job arrives or timeout expires."""
    result = await redis.blpop(QUEUE_KEY, timeout=timeout)
    if result is None:
        return None
    _, raw = result
    return json.loads(raw)


# ── Locking ───────────────────────────────────────────────────────────────────

async def acquire_lock(
    redis: aioredis.Redis,
    job_id: str,
    worker_id: str,
    ttl: int = 60,
) -> bool:
    """SET lock:{job_id} worker_id NX EX ttl — returns True if acquired."""
    key = f"{LOCK_PREFIX}{job_id}"
    return bool(await redis.set(key, worker_id, nx=True, ex=ttl))


async def release_lock(
    redis: aioredis.Redis,
    job_id: str,
    worker_id: str,
) -> bool:
    """Atomically release the lock only if this worker still owns it."""
    key = f"{LOCK_PREFIX}{job_id}"
    result = await redis.eval(_RELEASE_IF_OWNER_LUA, 1, key, worker_id)
    return result == 1


async def extend_lock(
    redis: aioredis.Redis,
    job_id: str,
    worker_id: str,
    ttl: int = 60,
) -> bool:
    """Extend lock TTL if this worker still owns it."""
    key = f"{LOCK_PREFIX}{job_id}"
    current = await redis.get(key)
    if current != worker_id:
        return False
    return bool(await redis.expire(key, ttl))


# ── Job status ────────────────────────────────────────────────────────────────

async def set_job_status(
    redis: aioredis.Redis,
    job_id: str,
    status: str,
    *,
    error: str | None = None,
    ttl: int = 3600,
) -> None:
    """Write status and publish update on the job's pub/sub channel."""
    payload: dict[str, Any] = {"job_id": job_id, "status": status}
    if error:
        payload["error"] = error
    raw = json.dumps(payload)
    await redis.set(f"{STATUS_PREFIX}{job_id}", raw, ex=ttl)
    await redis.publish(f"{CHANNEL_PREFIX}{job_id}", raw)


async def get_job_status(redis: aioredis.Redis, job_id: str) -> dict | None:
    raw = await redis.get(f"{STATUS_PREFIX}{job_id}")
    return json.loads(raw) if raw else None


# ── Result storage ────────────────────────────────────────────────────────────

async def store_result(
    redis: aioredis.Redis,
    job_id: str,
    artifact: dict,
    ttl: int = 3600,
) -> None:
    """Store the final artifact and mark the job completed."""
    await redis.set(f"{RESULT_PREFIX}{job_id}", json.dumps(artifact), ex=ttl)
    await set_job_status(redis, job_id, "completed", ttl=ttl)


async def get_result(redis: aioredis.Redis, job_id: str) -> dict | None:
    raw = await redis.get(f"{RESULT_PREFIX}{job_id}")
    return json.loads(raw) if raw else None
