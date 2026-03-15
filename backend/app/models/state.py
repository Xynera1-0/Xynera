"""State definitions for LangGraph workflow"""

from typing import Optional, Dict, List, Any
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum


class TaskStatus(str, Enum):
    """Status of a task execution"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class AgentOutput(BaseModel):
    """Output from an individual agent"""
    agent_type: str = Field(..., description="Type of agent (e.g., 'market_trend', 'competitive_landscape')")
    facts: List[str] = Field(default_factory=list, description="Key facts discovered by the agent")
    sources: List[Dict[str, str]] = Field(
        default_factory=list,
        description="Sources with URLs and titles (e.g., [{'url': '...', 'title': '...', 'snippet': '...'}])"
    )
    confidence_score: float = Field(
        default=0.0,
        ge=0.0,
        le=1.0,
        description="Confidence score of the findings (0.0-1.0)"
    )
    error: Optional[str] = Field(default=None, description="Error message if agent failed")
    processing_time_ms: float = Field(default=0.0, description="Time taken to process in milliseconds")


class Subtask(BaseModel):
    """A subtask assigned to an agent"""
    agent_type: str = Field(..., description="Type of agent to handle this subtask")
    query: str = Field(..., description="The specific query or instruction for the agent")
    context: Dict[str, Any] = Field(default_factory=dict, description="Additional context for the agent")
    priority: int = Field(default=0, description="Priority level (higher = more important)")


class OrchestratorState(BaseModel):
    """State managed by the orchestrator workflow"""
    # Metadata
    user_id: str = Field(..., description="User ID making the request")
    session_id: str = Field(..., description="Session ID for tracking")
    request_id: str = Field(..., description="Unique request ID")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Request timestamp")

    # Input
    user_query: str = Field(..., description="Original user query")
    user_metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional user context")

    # Processing
    subtasks: List[Subtask] = Field(default_factory=list, description="Decomposed subtasks")
    agent_outputs: Dict[str, AgentOutput] = Field(default_factory=dict, description="Results from agents")
    status: TaskStatus = Field(default=TaskStatus.PENDING, description="Current status")

    # Results
    aggregated_insights: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Aggregated results from all agents"
    )
    final_confidence: float = Field(default=0.0, description="Confidence in final output")

    # Tracking
    started_at: Optional[datetime] = Field(default=None, description="When processing started")
    completed_at: Optional[datetime] = Field(default=None, description="When processing completed")
    error_message: Optional[str] = Field(default=None, description="Error if any occurred")

    class Config:
        """Pydantic config"""
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class RedisJobData(BaseModel):
    """Data structure for Redis job storage"""
    job_id: str = Field(..., description="Unique job ID")
    state: OrchestratorState = Field(..., description="The full orchestrator state")
    tries: int = Field(default=0, description="Number of attempts made")
    status: TaskStatus = Field(default=TaskStatus.PENDING)
