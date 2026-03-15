"""Adjacent Market Collision Agent"""

from typing import Dict, Any
from app.agents.base_agent import BaseAgent
from app.models.state import AgentOutput


class AdjacentMarketAgent(BaseAgent):
    """Detects adjacent market opportunities and threats"""

    def __init__(self):
        super().__init__("adjacent_market")

    def get_system_prompt(self, context: Dict[str, Any]) -> str:
        """Get the system prompt for adjacent market analysis"""
        return """You are an adjacent market analyst specializing in identifying opportunities and threats from adjacent market spaces.

Your task is to analyze adjacent markets and identify:
1. Adjacent market categories and players
2. Emerging technologies entering the market
3. Convergence trends (companies/technologies coming together)
4. Disruption signals from adjacent spaces
5. Opportunities for cross-market adoption
6. Threats from adjacent market players expanding
7. Technology adjacencies and integrations
8. Regulatory or industry shifts affecting adjacency

Focus on:
- What's coming from outside the category
- Adjacent market threats
- Technology convergence opportunities
- Cross-market trend impacts
- Emerging competitive threats
- Strategic adjacency plays"""

    def get_initial_query(self, user_query: str, context: Dict[str, Any]) -> str:
        """Transform user query for adjacent market analysis"""
        focus = context.get("focus", "")
        return f"""Analyze adjacent market collisions and threats:

{user_query}

Focus on: {focus}

Provide:
1. Adjacent market categories and key players
2. Emerging technologies impacting the market
3. Convergence and integration opportunities
4. Disruption signals from adjacent spaces
5. Adjacent market threats
6. Cross-market adoption opportunities
7. Regulatory or industry shifts
8. Strategic recommendations
9. Confidence assessment"""

    async def adjacent_market_agent(
        query: str,
        context: Dict[str, Any],
    ) -> AgentOutput:
        """Execute the adjacent market agent"""
        agent = AdjacentMarketAgent()
        return await agent.execute(query, context)


# Export the agent function for workflow integration
adjacent_market_agent = AdjacentMarketAgent().adjacent_market_agent
