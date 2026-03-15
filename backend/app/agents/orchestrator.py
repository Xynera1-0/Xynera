"""Orchestrator agents that coordinate workflow execution"""

import logging
import asyncio
import uuid
from typing import Optional
from datetime import datetime
from app.models.state import OrchestratorState
from app.workflows.orchestrator_workflow import execute_workflow
from app.services.queue_manager import get_queue_manager

logger = logging.getLogger(__name__)


class Orchestrator:
    """
    Single orchestrator instance that:
    1. Listens to a Redis queue
    2. Picks up jobs
    3. Executes the LangGraph workflow
    4. Stores results
    """

    def __init__(self, orchestrator_id: str):
        """
        Initialize orchestrator
        Args:
            orchestrator_id: Unique identifier for this orchestrator instance
        """
        self.orchestrator_id = orchestrator_id
        self.logger = logging.getLogger(f"orchestrator.{orchestrator_id}")
        self.is_running = False
        self.queue_manager = get_queue_manager()

    async def start(self):
        """Start the orchestrator - runs infinite loop listening to queue"""
        self.is_running = True
        self.logger.info(f"Orchestrator {self.orchestrator_id} started")

        try:
            while self.is_running:
                await self._process_next_job()
                # Small delay to prevent CPU spinning
                await asyncio.sleep(0.1)

        except KeyboardInterrupt:
            self.logger.info(f"Orchestrator {self.orchestrator_id} interrupted")
            self.is_running = False
        except Exception as e:
            self.logger.error(f"Orchestrator error: {str(e)}", exc_info=True)
            self.is_running = False

    async def stop(self):
        """Stop the orchestrator gracefully"""
        self.logger.info(f"Stopping orchestrator {self.orchestrator_id}")
        self.is_running = False

    async def _process_next_job(self):
        """
        Process the next job in the queue
        Implements the main orchestrator loop:
        1. Get job from queue
        2. Create workflow state
        3. Execute workflow
        4. Store results
        5. Handle errors
        """
        try:
            # Try to get a job from the queue
            # In RQ, this would be handled by Workers, but here we're simulating
            # a direct orchestrator that pulls and processes jobs

            queue_stats = self.queue_manager.get_job_count_by_status()
            if queue_stats.get("queued", 0) == 0:
                # No jobs to process
                await asyncio.sleep(1)  # Wait longer if queue is empty
                return

            self.logger.debug(
                f"Queue stats: {queue_stats}"
            )

        except Exception as e:
            self.logger.error(f"Error processing job: {str(e)}", exc_info=True)

    async def process_state(self, state: OrchestratorState) -> Optional[OrchestratorState]:
        """
        Process a single state through the workflow
        Called directly or via queue

        Returns the completed state or None if failed
        """
        try:
            state_id = state.request_id
            self.logger.info(f"Processing state {state_id} (query: {state.user_query[:50]}...)")

            # Execute the workflow
            result_state = await execute_workflow(state)

            self.logger.info(
                f"State {state_id} processing complete. "
                f"Status: {result_state.status}, Confidence: {result_state.final_confidence:.2f}"
            )

            # Store result (will be persisted by other team members)
            await self._store_result(result_state)

            return result_state

        except Exception as e:
            self.logger.error(f"Failed to process state: {str(e)}", exc_info=True)
            state.error_message = f"Orchestrator error: {str(e)}"
            return state

    async def _store_result(self, state: OrchestratorState):
        """
        Store the processing result
        In production, this would save to database
        For now, just log it
        """
        try:
            self.logger.info(
                f"Storing result for {state.request_id}: "
                f"Agents: {list(state.agent_outputs.keys())}, "
                f"Status: {state.status}"
            )

            # In production, this would store to database/Redis
            # For now, we'll let other team members handle persistence

        except Exception as e:
            self.logger.error(f"Failed to store result: {str(e)}")

    def get_stats(self) -> dict:
        """Get orchestrator statistics"""
        return {
            "orchestrator_id": self.orchestrator_id,
            "is_running": self.is_running,
            "queue_stats": self.queue_manager.get_job_count_by_status(),
        }
