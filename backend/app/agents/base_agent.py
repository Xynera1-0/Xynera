"""Base agent class with common functionality"""

import logging
import asyncio
from typing import Dict, Any, List
from abc import ABC, abstractmethod
from app.models.state import AgentOutput
from app.services.llm_client import query_llm
from app.services.mcp_client import get_mcp_client

logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """Abstract base class for all agents"""

    def __init__(self, agent_type: str):
        self.agent_type = agent_type
        self.logger = logging.getLogger(f"agents.{agent_type}")

    @abstractmethod
    def get_system_prompt(self, context: Dict[str, Any]) -> str:
        """
        Get the system prompt for this agent
        Each agent type overrides this with specialized instructions
        """
        pass

    @abstractmethod
    def get_initial_query(self, user_query: str, context: Dict[str, Any]) -> str:
        """
        Transform the user query into the specific query for this agent
        """
        pass

    async def get_external_data(self, query: str, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Fetch external data via MCP client
        Default implementation uses web search
        Can be overridden by specific agents
        """
        mcp_client = get_mcp_client()
        try:
            results = await mcp_client.search_web(query)
            return results
        except Exception as e:
            self.logger.error(f"Failed to fetch external data: {str(e)}")
            return []

    async def process_with_llm(
        self,
        query: str,
        system_prompt: str,
        external_data: List[Dict[str, Any]],
    ) -> tuple[List[str], List[Dict[str, str]], float, str]:
        """
        Process the query with external data using LLM
        Returns: (facts, sources, confidence_score, raw_analysis)
        """
        # Format external data for the LLM
        formatted_context = self._format_external_data(external_data)

        # Build the complete query with context
        complete_query = f"""{query}

Context from research:
{formatted_context}

IMPORTANT: Structure your response as follows:
## Key Findings
- List each key finding as a bullet point

## Analysis
Provide a detailed narrative analysis paragraph.

## Confidence
State your confidence level (high/medium/low) and why."""

        # Query the LLM
        try:
            response = await query_llm(complete_query, system_prompt)

            # Parse the response to extract facts, sources, and confidence
            facts, sources, confidence = self._parse_llm_response(
                response, external_data
            )

            return facts, sources, confidence, response

        except Exception as e:
            self.logger.error(f"LLM processing failed: {str(e)}")
            return [], [], 0.0, ""

    async def execute(
        self,
        user_query: str,
        context: Dict[str, Any],
    ) -> AgentOutput:
        """
        Main execution method for the agent
        1. Get system prompt
        2. Transform query
        3. Fetch external data
        4. Process with LLM
        5. Return structured output
        """
        from app.config import get_settings

        settings = get_settings()

        try:
            self.logger.info(f"Starting execution with query: {user_query[:100]}")

            # Step 1: Get system prompt
            system_prompt = self.get_system_prompt(context)

            # Step 2: Transform query for this agent
            agent_query = self.get_initial_query(user_query, context)

            # Step 3: Fetch external data
            external_data = await self.get_external_data(agent_query, context)
            self.logger.debug(f"Retrieved {len(external_data)} external sources")

            # Step 4: Process with LLM
            facts, sources, confidence, raw_analysis = await self.process_with_llm(
                agent_query,
                system_prompt,
                external_data,
            )

            # Step 5: Build output
            output = AgentOutput(
                agent_type=self.agent_type,
                facts=facts,
                sources=sources,
                confidence_score=max(0, min(1, confidence)),  # Clamp between 0 and 1
                raw_analysis=raw_analysis,
            )

            self.logger.info(
                f"Execution complete: {len(facts)} facts, "
                f"confidence={output.confidence_score:.2f}"
            )

            return output

        except Exception as e:
            self.logger.error(f"Execution failed: {str(e)}", exc_info=True)
            return AgentOutput(
                agent_type=self.agent_type,
                error=str(e),
                confidence_score=0.0,
            )

    def _format_external_data(self, external_data: List[Dict[str, Any]]) -> str:
        """Format external data for LLM input"""
        if not external_data:
            return "No external data sources found."

        formatted = "Sources:\n"
        for i, item in enumerate(external_data[:8]):
            title = item.get("title", "Unknown")
            # Use full content when available, fall back to snippet
            content = item.get("content", "") or item.get("snippet", "")
            content = content[:800]  # Allow up to 800 chars per source
            url = item.get("url", "")
            source_type = item.get("source", "web")
            formatted += f"\n{i+1}. [{source_type}] {title}\n   URL: {url}\n   Content: {content}\n"

        return formatted

    def _parse_llm_response(
        self,
        response: str,
        external_data: List[Dict[str, Any]],
    ) -> tuple[List[str], List[Dict[str, str]], float]:
        """
        Parse LLM response to extract facts, sources, and confidence.
        Handles markdown formatting with headers, bullets, numbered lists.
        """
        import re

        lines = response.strip().split("\n")

        facts = []
        in_confidence_section = False
        for line in lines:
            cleaned = line.strip()
            if not cleaned:
                in_confidence_section = False
                continue
            # Skip markdown headers but track confidence section
            if cleaned.startswith("#"):
                in_confidence_section = "confidence" in cleaned.lower()
                continue
            # Skip lines in confidence section
            if in_confidence_section:
                continue
            # Clean bullet points and numbered lists
            cleaned = re.sub(r'^[-*•]\s+', '', cleaned)
            cleaned = re.sub(r'^\d+[\.\)]\s+', '', cleaned)
            # Remove bold markers
            cleaned = cleaned.replace("**", "")
            if len(cleaned) > 15:  # Only keep substantive lines
                facts.append(cleaned)

        # Extract sources from external data
        sources = [
            {
                "title": item.get("title", "Unknown"),
                "url": item.get("url", ""),
                "snippet": item.get("snippet", item.get("content", ""))[:150],
            }
            for item in external_data[:8]
            if item.get("url")
        ]

        # Parse confidence from response text
        confidence = 0.5
        lower_resp = response.lower()
        if "high confidence" in lower_resp or "confidence: high" in lower_resp:
            confidence = 0.85
        elif "medium confidence" in lower_resp or "confidence: medium" in lower_resp or "moderate confidence" in lower_resp:
            confidence = 0.65
        elif "low confidence" in lower_resp or "confidence: low" in lower_resp:
            confidence = 0.35
        elif len(facts) >= 8:
            confidence = 0.8
        elif len(facts) >= 5:
            confidence = 0.75
        elif len(facts) >= 2:
            confidence = 0.6

        return facts, sources, confidence
