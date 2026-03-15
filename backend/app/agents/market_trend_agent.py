"""Market & Trend Sensing Agent"""

from typing import Dict, Any
from app.agents.base_agent import BaseAgent
from app.models.state import AgentOutput


class MarketTrendAgent(BaseAgent):
    """Identifies market trends and leading indicators"""

    def __init__(self):
        super().__init__("market_trend")

    def get_system_prompt(self, context: Dict[str, Any]) -> str:
        """Get the system prompt for market trend analysis"""
        return """You are an expert market analyst specializing in identifying trends and leading indicators.

Your task is to analyze market information and identify:
1. Current market direction and trajectory
2. Leading indicators that signal future trends
3. Key catalysts and inflection points
4. Market growth rates and size projections
5. Emerging market segments

Focus on data-driven insights with quantifiable metrics where possible.
Provide confidence levels for your assessments.
Highlight any contradicting signals or uncertainties."""

    def get_initial_query(self, user_query: str, context: Dict[str, Any]) -> str:
        """Transform user query for market trend analysis"""
        focus = context.get("focus", "")
        return f"""Based on the following query, identify market trends and leading indicators:

{user_query}

Focus on: {focus}

Provide:
1. Key market trends
2. Leading indicators
3. Market size and growth projections
4. Competitive dynamics
5. Confidence assessment"""

    async def market_trend_agent(
        query: str,
        context: Dict[str, Any],
    ) -> AgentOutput:
        """Execute the market trend agent"""
        agent = MarketTrendAgent()
        return await agent.execute(query, context)


# Export the agent function for workflow integration
market_trend_agent = MarketTrendAgent().market_trend_agent
