import uuid

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_user
from app.db.models import ChatSession, Message, User
from app.db.session import get_db
from app.queue.redis_queue import push_job, set_job_status
from app.queue.schemas import JobCreatedResponse, JobPayload, QueryRequest

router = APIRouter(tags=["queries"])


@router.post(
    "/queries",
    response_model=JobCreatedResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
async def submit_query(
    body: QueryRequest,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Accept a user intelligence query and push it onto the Redis job queue."""
    redis = request.app.state.redis

    # Resolve or create a chat session
    if body.session_id:
        result = await db.execute(
            select(ChatSession).where(
                ChatSession.id == uuid.UUID(body.session_id),
                ChatSession.user_id == current_user.id,
            )
        )
        session = result.scalar_one_or_none()
        if not session:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Session not found")
        session_id = str(session.id)
    else:
        session = ChatSession(user_id=current_user.id, title=body.query[:120])
        db.add(session)
        await db.flush()
        session_id = str(session.id)

    # Persist the user message
    job_id = str(uuid.uuid4())
    user_msg = Message(
        session_id=session.id,
        user_id=current_user.id,
        role="user",
        content=body.query,
        job_id=job_id,
    )
    db.add(user_msg)
    await db.commit()

    # Push to Redis queue
    job = JobPayload(
        job_id=job_id,
        session_id=session_id,
        user_id=str(current_user.id),
        query=body.query,
    )
    await push_job(redis, job.model_dump())
    await set_job_status(redis, job_id, "queued")

    return JobCreatedResponse(job_id=job_id, session_id=session_id)
