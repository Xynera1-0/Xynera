"""Redis queue management using RQ (Redis Queue)"""

import logging
import json
from typing import Optional, Callable, Any
from redis import Redis
from rq import Queue, Worker
from rq.job import Job, JobStatus
from app.models.state import OrchestratorState, RedisJobData, TaskStatus

logger = logging.getLogger(__name__)


class QueueManager:
    """Manages job queuing and worker coordination via Redis"""

    def __init__(self, redis_url: str):
        self.redis_url = redis_url
        self.redis_conn = Redis.from_url(redis_url)
        self.queue = Queue(connection=self.redis_conn)
        self.logger = logging.getLogger("queue")

    def enqueue_job(self, state: OrchestratorState) -> str:
        """
        Enqueue a new job to the queue
        Returns the job ID
        """
        try:
            # Serialize state to job data
            job_data = {
                "request_id": state.request_id,
                "user_id": state.user_id,
                "session_id": state.session_id,
                "user_query": state.user_query,
                "user_metadata": state.user_metadata,
            }

            # Enqueue job (will be picked up by orchestrator workers)
            job = self.queue.enqueue(
                "src.workflows.orchestrator_workflow:execute_workflow",
                state,
                job_id=state.request_id,
            )

            self.logger.info(f"Job enqueued: {job.id}")
            return job.id

        except Exception as e:
            self.logger.error(f"Failed to enqueue job: {str(e)}")
            raise

    def get_job_status(self, job_id: str) -> Optional[str]:
        """Get the status of a job"""
        try:
            job = Job.fetch(job_id, connection=self.redis_conn)
            return job.get_status()
        except Exception as e:
            self.logger.error(f"Failed to get job status: {str(e)}")
            return None

    def get_job_result(self, job_id: str) -> Optional[OrchestratorState]:
        """Get the result of a completed job"""
        try:
            job = Job.fetch(job_id, connection=self.redis_conn)
            if job.is_finished:
                result = job.result
                if isinstance(result, OrchestratorState):
                    return result
                return None
            elif job.is_failed:
                self.logger.error(f"Job {job_id} failed: {job.exc_info}")
                return None
            else:
                self.logger.debug(f"Job {job_id} status: {job.get_status()}")
                return None
        except Exception as e:
            self.logger.error(f"Failed to get job result: {str(e)}")
            return None

    def remove_job(self, job_id: str) -> bool:
        """Remove a job from the queue/registry"""
        try:
            job = Job.fetch(job_id, connection=self.redis_conn)
            job.delete()
            self.logger.info(f"Job {job_id} removed")
            return True
        except Exception as e:
            self.logger.error(f"Failed to remove job: {str(e)}")
            return False

    def get_queue_length(self) -> int:
        """Get the number of jobs in the queue"""
        return len(self.queue)

    def get_job_count_by_status(self) -> dict:
        """Get count of jobs by status"""
        try:
            from rq import get_current_job

            stats = {
                "queued": len(self.queue),
                "started": len(self.queue.started_job_registry),
                "finished": len(self.queue.finished_job_registry),
                "failed": len(self.queue.failed_job_registry),
            }
            return stats
        except Exception as e:
            self.logger.error(f"Failed to get job stats: {str(e)}")
            return {}

    def start_worker(self, num_workers: int = 1):
        """Start worker(s) to process jobs from the queue"""
        self.logger.info(f"Starting {num_workers} worker(s)")

        try:
            workers = []
            for i in range(num_workers):
                worker = Worker([self.queue], connection=self.redis_conn)
                worker.work()
                workers.append(worker)

            return workers
        except Exception as e:
            self.logger.error(f"Failed to start workers: {str(e)}")
            raise


# Global queue manager instance
_queue_manager: Optional[QueueManager] = None


def get_queue_manager() -> QueueManager:
    """Get or create the queue manager"""
    global _queue_manager

    if _queue_manager is None:
        from app.config.settings import get_settings

        settings = get_settings()
        _queue_manager = QueueManager(settings.redis_url)

    return _queue_manager
