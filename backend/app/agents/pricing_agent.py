"""Pricing & Packaging Intelligence Agent"""

from typing import Dict, Any
from app.agents.base_agent import BaseAgent
from app.models.state import AgentOutput


class PricingAgent(BaseAgent):
    """Evaluates pricing models and willingness-to-pay"""

    def __init__(self):
        super().__init__("pricing")

    def get_system_prompt(self, context: Dict[str, Any]) -> str:
        """Get the system prompt for pricing analysis"""
        return """You are a pricing strategy expert specializing in pricing models and willingness-to-pay analysis.

Your task is to analyze pricing information and identify:
1. Current pricing models and strategies
2. Price points across market segments
3. Margin trends and pricing power
4. Willingness-to-pay by customer segment
5. Price elasticity and sensitivity
6. Value perception vs actual pricing
7. Packaging and bundling strategies
8. Competitor pricing positioning

Focus on:
- Market pricing benchmarks
- Value-based pricing opportunities
- Price optimization potential
- Packaging efficiency
- Customer perceived value
- Revenue optimization opportunities"""

    def get_initial_query(self, user_query: str, context: Dict[str, Any]) -> str:
        """Transform user query for pricing analysis"""
        focus = context.get("focus", "")
        return f"""Analyze pricing and packaging strategy:

{user_query}

Focus on: {focus}

Provide:
1. Current pricing models in the market
2. Price point distribution
3. Margin trends and pricing power
4. Willingness-to-pay by segment
5. Price elasticity signals
6. Value perception analysis
7. Packaging effectiveness
8. Optimization opportunities
9. Confidence assessment"""

async def pricing_agent(
    query: str,
    context: Dict[str, Any],
) -> AgentOutput:
    """Execute the pricing agent"""
    agent = PricingAgent()
    return await agent.execute(query, context)
