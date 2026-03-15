"""MCP (Model Context Protocol) client for external tools"""

import logging
from typing import List, Dict, Any, Optional
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)


class MCPClient(ABC):
    """Abstract MCP client interface"""

    @abstractmethod
    async def search_web(self, query: str, num_results: int = 5) -> List[Dict[str, Any]]:
        """Search the web for information"""
        pass

    @abstractmethod
    async def extract_page(self, url: str) -> Optional[str]:
        """Extract content from a web page"""
        pass

    @abstractmethod
    async def reddit_analysis(self, query: str) -> List[Dict[str, Any]]:
        """Analyze Reddit discussions related to a query"""
        pass

    @abstractmethod
    async def advertisement_intelligence(self, query: str) -> List[Dict[str, Any]]:
        """Get advertisement intelligence"""
        pass


class RealMCPClient(MCPClient):
    """Real MCP client that calls the actual MCP server"""

    def __init__(self, mcp_server_url: str):
        self.mcp_server_url = mcp_server_url
        self.logger = logging.getLogger("mcp.real")

    async def search_web(self, query: str, num_results: int = 5) -> List[Dict[str, Any]]:
        """Search the web via MCP server"""
        try:
            import httpx

            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.mcp_server_url}/search",
                    params={"q": query, "n": num_results},
                    timeout=10.0,
                )
                response.raise_for_status()
                return response.json().get("results", [])
        except Exception as e:
            self.logger.error(f"Web search failed: {str(e)}")
            return []

    async def extract_page(self, url: str) -> Optional[str]:
        """Extract content from a page via MCP server"""
        try:
            import httpx

            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.mcp_server_url}/extract",
                    params={"url": url},
                    timeout=10.0,
                )
                response.raise_for_status()
                return response.json().get("content", None)
        except Exception as e:
            self.logger.error(f"Page extraction failed: {str(e)}")
            return None

    async def reddit_analysis(self, query: str) -> List[Dict[str, Any]]:
        """Analyze Reddit discussions via MCP server"""
        try:
            import httpx

            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.mcp_server_url}/reddit",
                    params={"q": query},
                    timeout=10.0,
                )
                response.raise_for_status()
                return response.json().get("discussions", [])
        except Exception as e:
            self.logger.error(f"Reddit analysis failed: {str(e)}")
            return []

    async def advertisement_intelligence(self, query: str) -> List[Dict[str, Any]]:
        """Get advertisement intelligence via MCP server"""
        try:
            import httpx

            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.mcp_server_url}/ads",
                    params={"q": query},
                    timeout=10.0,
                )
                response.raise_for_status()
                return response.json().get("ads", [])
        except Exception as e:
            self.logger.error(f"Ad intelligence failed: {str(e)}")
            return []


class MockMCPClient(MCPClient):
    """Mock MCP client for testing without real MCP server"""

    def __init__(self):
        self.logger = logging.getLogger("mcp.mock")

    async def search_web(self, query: str, num_results: int = 5) -> List[Dict[str, Any]]:
        """Mock web search results"""
        self.logger.debug(f"Mock search for: {query}")

        # Mock results based on query keywords
        mock_results = [
            {
                "title": f"Result 1: {query} Overview",
                "url": f"https://example.com/1",
                "snippet": f"This article discusses key aspects of {query}. It covers market trends, competitive landscape, and strategic opportunities.",
            },
            {
                "title": f"Result 2: {query} Analysis",
                "url": f"https://example.com/2",
                "snippet": f"Detailed analysis of {query} including market size, growth rate, and key players.",
            },
            {
                "title": f"Result 3: {query} Trends",
                "url": f"https://example.com/3",
                "snippet": f"Latest trends in {query} including emerging technologies and consumer preferences.",
            },
            {
                "title": f"Result 4: {query} Competitors",
                "url": f"https://example.com/4",
                "snippet": f"Competitive landscape analysis of {query} market with major players and their strategies.",
            },
            {
                "title": f"Result 5: {query} Future",
                "url": f"https://example.com/5",
                "snippet": f"Future outlook for {query} industry with predictions for next 5 years.",
            },
        ]

        return mock_results[:num_results]

    async def extract_page(self, url: str) -> Optional[str]:
        """Mock page extraction"""
        self.logger.debug(f"Mock extract from: {url}")
        return f"Extracted content from {url}. Full article content including detailed analysis, statistics, and insights."

    async def reddit_analysis(self, query: str) -> List[Dict[str, Any]]:
        """Mock Reddit analysis"""
        self.logger.debug(f"Mock Reddit analysis for: {query}")

        return [
            {
                "subreddit": "r/business",
                "discussion_count": 156,
                "sentiment": "mixed",
                "key_points": [
                    f"Users discussing {query} and its market impact",
                    "Questions about pricing and value proposition",
                    "Competitive comparisons",
                ],
            },
            {
                "subreddit": "r/technology",
                "discussion_count": 89,
                "sentiment": "positive",
                "key_points": [
                    f"Technical aspects of {query}",
                    "Innovation opportunities",
                    "Integration with other tools",
                ],
            },
        ]

    async def advertisement_intelligence(self, query: str) -> List[Dict[str, Any]]:
        """Mock advertisement intelligence"""
        self.logger.debug(f"Mock ad intelligence for: {query}")

        return [
            {
                "brand": "CompetitorA",
                "ad_count": 245,
                "spend_estimate": "$50K-$100K/month",
                "messaging": f"Key benefits of {query}",
                "target_audience": "Business professionals aged 25-45",
            },
            {
                "brand": "CompetitorB",
                "ad_count": 182,
                "spend_estimate": "$30K-$70K/month",
                "messaging": f"{query} for enterprise",
                "target_audience": "C-level executives",
            },
        ]


# Global MCP client instance
_mcp_client: Optional[MCPClient] = None


def get_mcp_client() -> MCPClient:
    """
    Get or create the MCP client
    Switches between real and mock based on configuration
    """
    global _mcp_client

    if _mcp_client is None:
        from app.config import get_settings

        settings = get_settings()

        if settings.mcp_mode == "real":
            logger.info(f"Initializing real MCP client for {settings.mcp_server_url}")
            _mcp_client = RealMCPClient(settings.mcp_server_url)
        else:
            logger.info("Initializing mock MCP client")
            _mcp_client = MockMCPClient()

    return _mcp_client


def reset_mcp_client():
    """Reset the global MCP client (for testing)"""
    global _mcp_client
    _mcp_client = None
