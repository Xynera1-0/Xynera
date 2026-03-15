"""
LangGraph Workflow Entry Point for Xynera

This module provides the main entry point for the orchestrator workflow.
It can be imported directly or run as a standalone service.

Usage:
    from app.workflows.entrypoint import execute_competitive_intelligence
    result = await execute_competitive_intelligence(state)
"""

import logging
from orchestrator_workflow import execute_workflow, get_workflow
from app.models.state import OrchestratorState

logger = logging.getLogger(__name__)


async def execute_competitive_intelligence(state: OrchestratorState) -> OrchestratorState:
    """
    Execute the competitive intelligence workflow

    Args:
        state: OrchestratorState with user query and metadata

    Returns:
        OrchestratorState with results from all agents and aggregated insights
    """
    logger.info(f"Executing competitive intelligence workflow for {state.request_id}")
    return await execute_workflow(state)


def get_compiled_workflow():
    """Get the compiled LangGraph workflow graph"""
    return get_workflow()


if __name__ == "__main__":
    # Example usage
    import asyncio
    from datetime import datetime
    import uuid

    async def main():
        # Create a test state
        state = OrchestratorState(
            user_id="demo_user",
            session_id=str(uuid.uuid4()),
            request_id=f"demo-{datetime.utcnow().isoformat()}",
            user_query="What are the latest trends in AI and machine learning?",
            timestamp=datetime.utcnow(),
        )

        # Execute workflow
        result = await execute_competitive_intelligence(state)

        # Print results
        print(f"\nExecution completed!")
        print(f"Status: {result.status}")
        print(f"Confidence: {result.final_confidence:.2f}")
        print(f"Agents executed: {list(result.agent_outputs.keys())}")

    asyncio.run(main())
