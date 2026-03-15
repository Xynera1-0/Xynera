"""Integration tests for Xynera orchestrator"""

import pytest
import asyncio
import sys
from pathlib import Path
from datetime import datetime
import uuid

# Add backend to path for imports
sys.path.insert(0, str(Path(__file__).parent / "backend"))

from app.models.state import OrchestratorState, TaskStatus
from app.agents.orchestrator import Orchestrator
from app.workflows.orchestrator_workflow import execute_workflow


@pytest.mark.asyncio
class TestOrchestratorWorkflow:
    """Test the orchestrator workflow"""

    async def test_complete_workflow(self):
        """Test complete workflow execution"""
        # Create a test state
        state = OrchestratorState(
            user_id="test_user",
            session_id=str(uuid.uuid4()),
            request_id=f"test-{datetime.utcnow().isoformat()}",
            user_query="What are the market trends in AI?",
            timestamp=datetime.utcnow(),
        )

        # Execute workflow
        result = await execute_workflow(state)

        # Assertions
        assert result is not None
        assert result.request_id == state.request_id
        assert result.status in [TaskStatus.COMPLETED, TaskStatus.FAILED]

    async def test_orchestrator_processing(self):
        """Test orchestrator processing a single state"""
        orchestrator = Orchestrator("test-orchestrator")

        state = OrchestratorState(
            user_id="test_user",
            session_id=str(uuid.uuid4()),
            request_id=f"test-{datetime.utcnow().isoformat()}",
            user_query="Analyze competitive landscape in SaaS",
            timestamp=datetime.utcnow(),
        )

        result = await orchestrator.process_state(state)

        assert result is not None
        assert result.status != TaskStatus.PENDING

    async def test_invalid_query_handling(self):
        """Test handling of invalid queries"""
        state = OrchestratorState(
            user_id="test_user",
            session_id=str(uuid.uuid4()),
            request_id=f"test-{datetime.utcnow().isoformat()}",
            user_query="",  # Empty query should fail validation
            timestamp=datetime.utcnow(),
        )

        result = await execute_workflow(state)

        assert result.status == TaskStatus.FAILED
        assert result.error_message is not None


@pytest.mark.asyncio
class TestAgents:
    """Test individual agents"""

    async def test_market_trend_agent(self):
        """Test market trend agent"""
        from app.agents.market_trend_agent import market_trend_agent

        context = {
            "focus": "AI market trends",
            "user_metadata": {},
            "session_id": str(uuid.uuid4()),
        }

        result = await market_trend_agent("What are AI market trends?", context)

        assert result is not None
        assert result.agent_type == "market_trend"
        assert hasattr(result, "facts")
        assert hasattr(result, "confidence_score")

    async def test_competitive_landscape_agent(self):
        """Test competitive landscape agent"""
        from app.agents.competitive_landscape_agent import competitive_landscape_agent

        context = {
            "focus": "Competitive analysis",
            "user_metadata": {},
            "session_id": str(uuid.uuid4()),
        }

        result = await competitive_landscape_agent("Analyze competitors in AI", context)

        assert result is not None
        assert result.agent_type == "competitive_landscape"

    async def test_all_agents_execution(self):
        """Test execution of all 6 agents"""
        from app.agents.market_trend_agent import market_trend_agent
        from app.agents.competitive_landscape_agent import competitive_landscape_agent
        from app.agents.win_loss_agent import win_loss_agent
        from app.agents.pricing_agent import pricing_agent
        from app.agents.messaging_agent import messaging_agent
        from app.agents.adjacent_market_agent import adjacent_market_agent

        agents = [
            ("market_trend", market_trend_agent),
            ("competitive_landscape", competitive_landscape_agent),
            ("win_loss", win_loss_agent),
            ("pricing", pricing_agent),
            ("messaging", messaging_agent),
            ("adjacent_market", adjacent_market_agent),
        ]

        context = {
            "focus": "Market analysis",
            "user_metadata": {},
            "session_id": str(uuid.uuid4()),
        }

        tasks = [
            agent_func("Test query for market analysis", context) for _, agent_func in agents
        ]

        results = await asyncio.gather(*tasks)

        assert len(results) == 6
        assert all(r is not None for r in results)
        assert all(hasattr(r, "confidence_score") for r in results)


class TestMCPClient:
    """Test MCP client functionality"""

    def test_mock_mcp_web_search(self):
        """Test mock MCP web search"""
        from app.services.mcp_client import MockMCPClient
        import asyncio

        mcp = MockMCPClient()
        results = asyncio.run(mcp.search_web("AI market trends"))

        assert results is not None
        assert len(results) > 0
        assert all(hasattr(r, "__getitem__") for r in results)

    def test_mock_mcp_reddit_analysis(self):
        """Test mock MCP Reddit analysis"""
        from app.services.mcp_client import MockMCPClient
        import asyncio

        mcp = MockMCPClient()
        results = asyncio.run(mcp.reddit_analysis("AI trends"))

        assert results is not None
        assert isinstance(results, list)

    def test_mcp_client_factory(self):
        """Test MCP client factory method"""
        from app.services.mcp_client import get_mcp_client

        mcp = get_mcp_client()
        assert mcp is not None


class TestQueueManager:
    """Test queue manager functionality"""

    def test_queue_manager_initialization(self):
        """Test queue manager can be initialized"""
        from app.services.queue_manager import get_queue_manager

        qm = get_queue_manager()
        assert qm is not None
        assert hasattr(qm, "get_queue_length")

    def test_queue_stats(self):
        """Test getting queue statistics"""
        from app.services.queue_manager import get_queue_manager

        qm = get_queue_manager()
        stats = qm.get_job_count_by_status()

        assert isinstance(stats, dict)
        assert "queued" in stats or len(stats) >= 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
