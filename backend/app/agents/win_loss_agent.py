"""Win/Loss Intelligence Agent"""

from typing import Dict, Any
from app.agents.base_agent import BaseAgent
from app.models.state import AgentOutput


class WinLossAgent(BaseAgent):
    """Analyzes win/loss patterns and buyer perspective"""

    def __init__(self):
        super().__init__("win_loss")

    def get_system_prompt(self, context: Dict[str, Any]) -> str:
        """Get the system prompt for win/loss analysis"""
        return """You are a win/loss analyst specializing in understanding buyer behavior and competitive losses.

Your task is to analyze win/loss data and buyer insights to identify:
1. Reasons for deal losses
2. Key factors in deal wins
3. Buyer priorities and pain points
4. Competitive objections most commonly raised
5. Buyer perception gaps
6. Segments with highest/lowest win rates
7. Trends in deal outcomes

Focus on:
- Root causes of losses vs wins
- Buyer decision criteria
- Competitive comparison points
- Perception vs reality gaps
- Segment-specific patterns"""

    def get_initial_query(self, user_query: str, context: Dict[str, Any]) -> str:
        """Transform user query for win/loss analysis"""
        focus = context.get("focus", "")
        return f"""Analyze win/loss patterns and buyer perspective:

{user_query}

Focus on: {focus}

Provide:
1. Top reasons for deal losses
2. Key factors in deal wins
3. Buyer priorities and pain points
4. Competitive objections
5. Perception gaps
6. Segment-specific win/loss patterns
7. Actionable insights
8. Confidence assessment"""

    async def win_loss_agent(
        query: str,
        context: Dict[str, Any],
    ) -> AgentOutput:
        """Execute the win/loss agent"""
        agent = WinLossAgent()
        return await agent.execute(query, context)


# Export the agent function for workflow integration
win_loss_agent = WinLossAgent().win_loss_agent
