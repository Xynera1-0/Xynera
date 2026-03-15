"""Positioning & Messaging Gaps Agent"""

from typing import Dict, Any
from app.agents.base_agent import BaseAgent
from app.models.state import AgentOutput


class MessagingAgent(BaseAgent):
    """Identifies positioning and messaging gaps"""

    def __init__(self):
        super().__init__("messaging")

    def get_system_prompt(self, context: Dict[str, Any]) -> str:
        """Get the system prompt for messaging analysis"""
        return """You are a messaging and positioning expert specializing in how to talk about existing products.

Your task is to analyze messaging and positioning to identify:
1. Current messaging themes and positioning statements
2. Messaging clarity and consistency
3. Value proposition gaps
4. Buyer language vs company language misalignment
5. Positioning in buyer mind vs intended positioning
6. Messaging opportunities based on buyer concerns
7. Competitive messaging differentiation
8. Resonance gaps with target segments

Focus on:
- How to communicate existing features effectively
- Messaging gaps between intention and perception
- Value articulation opportunities
- Segment-specific messaging needs
- Positioning consensus and clarity"""

    def get_initial_query(self, user_query: str, context: Dict[str, Any]) -> str:
        """Transform user query for messaging analysis"""
        focus = context.get("focus", "")
        return f"""Analyze positioning and messaging gaps:

{user_query}

Focus on: {focus}

Provide:
1. Current messaging themes
2. Value proposition clarity
3. Buyer perception vs intended positioning
4. Messaging alignment issues
5. Language gaps (company vs buyer)
6. Differentiation messaging opportunities
7. Segment-specific messaging needs
8. Messaging recommendations
9. Confidence assessment"""

    async def messaging_agent(
        query: str,
        context: Dict[str, Any],
    ) -> AgentOutput:
        """Execute the messaging agent"""
        agent = MessagingAgent()
        return await agent.execute(query, context)


# Export the agent function for workflow integration
messaging_agent = MessagingAgent().messaging_agent
