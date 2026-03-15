"""Competitive Landscape & Feature Bets Agent"""

from typing import Dict, Any
from app.agents.base_agent import BaseAgent
from app.models.state import AgentOutput


class CompetitiveLandscapeAgent(BaseAgent):
    """Analyzes competitive landscape and feature bets"""

    def __init__(self):
        super().__init__("competitive_landscape")

    def get_system_prompt(self, context: Dict[str, Any]) -> str:
        """Get the system prompt for competitive analysis"""
        return """You are a competitive intelligence expert specializing in landscape analysis and feature bet assessment.

Your task is to analyze competitive information and identify:
1. Major competitors and their market positioning
2. Key features and differentiators
3. Market share and competitive positioning
4. Feature roadmaps and recent launches
5. Gaps and opportunities in the market
6. Demand validation for specific feature bets
7. Whether specific bets are worth pursuing

Focus on:
- Competitive strengths and weaknesses
- Market gaps and white space
- Feature adoption and demand signals
- Competitive advantages and vulnerabilities
- Strategic positioning"""

    def get_initial_query(self, user_query: str, context: Dict[str, Any]) -> str:
        """Transform user query for competitive landscape analysis"""
        focus = context.get("focus", "")
        return f"""Analyze the competitive landscape and demand for feature bets:

{user_query}

Focus on: {focus}

Provide:
1. Major competitors and their positioning
2. Key differentiating features
3. Market share distribution
4. Competitive gaps and opportunities
5. Demand validation for specific bets
6. Strategic recommendations
7. Confidence assessment"""

async def competitive_landscape_agent(
    query: str,
    context: Dict[str, Any],
) -> AgentOutput:
    """Execute the competitive landscape agent"""
    agent = CompetitiveLandscapeAgent()
    return await agent.execute(query, context)
