import json

from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect
from jose import JWTError

from app.auth.service import decode_token
from app.queue.redis_queue import CHANNEL_PREFIX, get_job_status, get_result

router = APIRouter()


@router.websocket("/ws/jobs/{job_id}")
async def ws_job_updates(
    websocket: WebSocket,
    job_id: str,
    token: str = Query(...),
):
    """
    Real-time job status via WebSocket.

    Connect:  ws://host/ws/jobs/{job_id}?token=<access_token>

    The server pushes JSON frames:
        {"job_id": "...", "status": "processing"}
        {"job_id": "...", "status": "completed", "artifact": {...}}
        {"job_id": "...", "status": "failed", "error": "..."}

    Connection closes automatically on terminal status.
    """
    # Auth via query param (WS can't use Authorization header)
    try:
        payload = decode_token(token)
        if payload.get("type") != "access":
            await websocket.close(code=4001, reason="Invalid token type")
            return
    except JWTError:
        await websocket.close(code=4001, reason="Invalid or expired token")
        return

    await websocket.accept()
    redis = websocket.app.state.redis

    # If job already finished before WS connected, send immediately
    existing = await get_job_status(redis, job_id)
    if existing and existing["status"] in ("completed", "failed"):
        if existing["status"] == "completed":
            existing["artifact"] = await get_result(redis, job_id)
        await websocket.send_text(json.dumps(existing))
        await websocket.close()
        return

    # Subscribe to live updates
    pubsub = redis.pubsub()
    await pubsub.subscribe(f"{CHANNEL_PREFIX}{job_id}")

    try:
        async for message in pubsub.listen():
            if message["type"] != "message":
                continue

            data = json.loads(message["data"])

            if data.get("status") == "completed":
                data["artifact"] = await get_result(redis, job_id)

            await websocket.send_text(json.dumps(data))

            if data.get("status") in ("completed", "failed"):
                break
    except WebSocketDisconnect:
        pass
    finally:
        await pubsub.unsubscribe(f"{CHANNEL_PREFIX}{job_id}")
        await pubsub.aclose()
