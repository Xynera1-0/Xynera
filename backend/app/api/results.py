from fastapi import APIRouter, Depends, HTTPException, Request, status

from app.auth.dependencies import get_current_user
from app.db.models import User
from app.queue.redis_queue import get_job_status, get_result
from app.queue.schemas import JobStatusResponse

router = APIRouter(tags=["results"])


@router.get("/jobs/{job_id}/status", response_model=JobStatusResponse)
async def job_status(
    job_id: str,
    request: Request,
    _current_user: User = Depends(get_current_user),
):
    """Poll the current status of a submitted job."""
    redis = request.app.state.redis

    status_data = await get_job_status(redis, job_id)
    if not status_data:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Job not found")

    response = JobStatusResponse(
        job_id=job_id,
        status=status_data["status"],
        error=status_data.get("error"),
    )

    if status_data["status"] == "completed":
        response.artifact = await get_result(redis, job_id)

    return response
