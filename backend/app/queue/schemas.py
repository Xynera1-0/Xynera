import uuid
from datetime import datetime, timezone
from typing import Optional

from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    """Body sent by the frontend when the user submits a question."""
    query: str
    session_id: Optional[str] = None


class JobCreatedResponse(BaseModel):
    job_id: str
    session_id: str
    status: str = "queued"


class JobPayload(BaseModel):
    """Internal representation pushed onto the Redis queue."""
    job_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str
    user_id: str
    query: str
    timestamp: int = Field(
        default_factory=lambda: int(datetime.now(timezone.utc).timestamp())
    )


class JobStatusResponse(BaseModel):
    job_id: str
    status: str  # queued | processing | completed | failed
    artifact: Optional[dict] = None
    error: Optional[str] = None
