"""MCP client using FIRECRAWL for scraping + PyTrends for trends"""

import logging
from typing import List, Dict, Any, Optional
from abc import ABC, abstractmethod
import httpx
import asyncio

logger = logging.getLogger(__name__)


class MCPClient(ABC):
    """Abstract MCP client interface"""

    @abstractmethod
    async def search_web(self, query: str, num_results: int = 5) -> List[Dict[str, Any]]:
        """Search and scrape web for information"""
        pass

    @abstractmethod
    async def search_news(self, query: str, num_results: int = 5) -> List[Dict[str, Any]]:
        """Search for news articles"""
        pass

    @abstractmethod
    async def search_trends(self, query: str, num_results: int = 5) -> List[Dict[str, Any]]:
        """Get Google Trends data"""
        pass

    @abstractmethod
    async def extract_page(self, url: str) -> Optional[str]:
        """Extract content from a page"""
        pass

    @abstractmethod
    async def reddit_analysis(self, query: str) -> List[Dict[str, Any]]:
        """Analyze Reddit discussions"""
        pass

    @abstractmethod
    async def advertisement_intelligence(self, query: str) -> List[Dict[str, Any]]:
        """Get advertising intelligence"""
        pass


# ✅ FIRECRAWL-ONLY CLIENT
class FirecrawlMCPClient(MCPClient):
    """Real MCP client using Firecrawl for scraping"""

    def __init__(self, firecrawl_key: str, tavily_key: str = None):
        self.firecrawl_key = firecrawl_key
        self.tavily_key = tavily_key
        self.logger = logging.getLogger("mcp.firecrawl")

    async def search_web(self, query: str, num_results: int = 5) -> List[Dict[str, Any]]:
        """Search web and scrape results using Firecrawl"""
        try:
            from firecrawl import FirecrawlApp

            app = FirecrawlApp(api_key=self.firecrawl_key)

            # Scrape Google search results
            search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}"

            try:
                result = app.scrape_url(
                    url=search_url,
                    params={"formats": ["markdown", "links"]}
                )

                links = result.get("links", [])
                results = []

                # Scrape top results
                for url in links[:num_results]:
                    try:
                        if url.startswith("http"):
                            scraped = app.scrape_url(
                                url=url,
                                params={"formats": ["markdown"]}
                            )

                            content = scraped.get("markdown", "")

                            results.append({
                                "title": url.split("/")[-1][:60],
                                "url": url,
                                "snippet": content[:200] if content else "",
                                "content": content,
                                "source": "firecrawl"
                            })
                    except Exception as e:
                        self.logger.warning(f"Failed to scrape {url}: {str(e)}")
                        continue

                self.logger.info(f"Firecrawl web search: scraped {len(results)} pages")
                return results

            except Exception as e:
                self.logger.error(f"Search scraping failed: {str(e)}")
                return []

        except Exception as e:
            self.logger.error(f"Web search failed: {str(e)}")
            return []

    async def search_news(self, query: str, num_results: int = 5) -> List[Dict[str, Any]]:
        """Search for news and scrape with Firecrawl"""
        try:
            from firecrawl import FirecrawlApp

            app = FirecrawlApp(api_key=self.firecrawl_key)

            # Search for news articles
            news_url = f"https://news.google.com/search?q={query.replace(' ', '+')}"

            try:
                result = app.scrape_url(
                    url=news_url,
                    params={"formats": ["markdown"]}
                )

                content = result.get("markdown", "")

                if content:
                    results = [{
                        "title": f"News: {query}",
                        "url": news_url,
                        "snippet": content[:200],
                        "content": content,
                        "source": "news_scrape",
                        "date": "2024-03-15"
                    }]
                else:
                    results = []

                self.logger.info(f"News search: scraped {len(results)} news pages")
                return results

            except Exception as e:
                self.logger.error(f"News scraping failed: {str(e)}")
                return []

        except Exception as e:
            self.logger.error(f"News search failed: {str(e)}")
            return []

    async def search_trends(self, query: str, num_results: int = 5) -> List[Dict[str, Any]]:
        """Get Google Trends data using PyTrends"""
        try:
            from pytrends.request import TrendReq

            pytrends = TrendReq(hl='en-US', tz=360)
            pytrends.build_payload([query], cat=0, timeframe='today 5-y')

            interest_df = pytrends.interest_over_time()
            related_queries = pytrends.related_queries()

            trends = []

            if not interest_df.empty:
                latest_value = interest_df[query].iloc[-1]
                trends.append({
                    "metric": "current_interest",
                    "value": int(latest_value),
                    "source": "google_trends",
                    "snippet": f"Current interest in '{query}': {latest_value}",
                })

            if related_queries.get('queries'):
                for rel_query in related_queries['queries'][:num_results]:
                    trends.append({
                        "metric": "related_query",
                        "value": rel_query['value'],
                        "query": rel_query['query'],
                        "source": "google_trends",
                        "snippet": f"Related search: {rel_query['query']}",
                    })

            self.logger.info(f"Google Trends: {len(trends)} data points")
            return trends if trends else []

        except Exception as e:
            self.logger.error(f"Trends search failed: {str(e)}")
            return []

    async def extract_page(self, url: str) -> Optional[str]:
        """Extract content from a page using Firecrawl"""
        try:
            from firecrawl import FirecrawlApp

            app = FirecrawlApp(api_key=self.firecrawl_key)
            result = app.scrape_url(
                url=url,
                params={"formats": ["markdown"]}
            )

            content = result.get("markdown", result.get("content", ""))
            self.logger.info(f"Extracted {len(content)} chars from {url}")
            return content

        except Exception as e:
            self.logger.error(f"Page extraction failed: {str(e)}")
            return None

    async def reddit_analysis(self, query: str) -> List[Dict[str, Any]]:
        """Analyze Reddit discussions by scraping Reddit"""
        try:
            from firecrawl import FirecrawlApp

            app = FirecrawlApp(api_key=self.firecrawl_key)

            # Scrape Reddit search results
            reddit_url = f"https://www.reddit.com/search/?q={query.replace(' ', '+')}"

            result = app.scrape_url(
                url=reddit_url,
                params={"formats": ["markdown"]}
            )

            content = result.get("markdown", "")

            discussions = []
            if content:
                discussions.append({
                    "subreddit": "r/search_results",
                    "title": f"Reddit discussions about {query}",
                    "url": reddit_url,
                    "snippet": content[:200],
                    "source": "reddit_scrape"
                })

            self.logger.info(f"Reddit analysis: found {len(discussions)} discussions")
            return discussions

        except Exception as e:
            self.logger.error(f"Reddit analysis failed: {str(e)}")
            return []

    async def advertisement_intelligence(self, query: str) -> List[Dict[str, Any]]:
        """Get advertising intelligence by scraping relevant sites"""
        try:
            from firecrawl import FirecrawlApp

            app = FirecrawlApp(api_key=self.firecrawl_key)

            # Search for ads-related content via Google
            ad_search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}+advertising"

            result = app.scrape_url(
                url=ad_search_url,
                params={"formats": ["markdown"]}
            )

            content = result.get("markdown", "")

            results = []
            if content:
                results.append({
                    "title": f"Ad Intelligence: {query}",
                    "url": ad_search_url,
                    "snippet": content[:200],
                    "source": "ads_scrape"
                })

            self.logger.info(f"Ad intelligence: {len(results)} results")
            return results

        except Exception as e:
            self.logger.error(f"Ad intelligence failed: {str(e)}")
            return []


class ServerMCPClient(MCPClient):
    """MCP client that connects to actual MCP server"""

    def __init__(self, mcp_server_url: str = "http://localhost:8000/mcp"):
        self.mcp_server_url = mcp_server_url.rstrip('/')
        self.logger = logging.getLogger("mcp.server")
        self.client = httpx.AsyncClient(base_url=self.mcp_server_url, timeout=30.0)

    async def _call_mcp_tool(self, tool_name: str, **params) -> Dict[str, Any]:
        """Generic method to call MCP tools"""
        try:
            response = await self.client.post(
                "/call",
                json={"tool": tool_name, "params": params}
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            self.logger.error(f"MCP tool call failed ({tool_name}): {str(e)}")
            return {"error": str(e), "results": []}

    async def search_web(self, query: str, num_results: int = 5) -> List[Dict[str, Any]]:
        """Search web via MCP server"""
        result = await self._call_mcp_tool("search_web", query=query, num_results=num_results)
        return result.get("results", [])

    async def search_news(self, query: str, num_results: int = 5) -> List[Dict[str, Any]]:
        """Search news via MCP server"""
        result = await self._call_mcp_tool("search_news", query=query, num_results=num_results)
        return result.get("results", [])

    async def search_trends(self, query: str, num_results: int = 5) -> List[Dict[str, Any]]:
        """Get trends via MCP server"""
        result = await self._call_mcp_tool("search_trends", query=query, num_results=num_results)
        return result.get("results", [])

    async def extract_page(self, url: str) -> Optional[str]:
        """Extract page via MCP server"""
        result = await self._call_mcp_tool("extract_page", url=url)
        return result.get("content")

    async def reddit_analysis(self, query: str) -> List[Dict[str, Any]]:
        """Analyze Reddit via MCP server"""
        result = await self._call_mcp_tool("reddit_analysis", query=query)
        return result.get("results", [])

    async def advertisement_intelligence(self, query: str) -> List[Dict[str, Any]]:
        """Get ad intelligence via MCP server"""
        result = await self._call_mcp_tool("advertisement_intelligence", query=query)
        return result.get("results", [])

    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()


class TavilyMCPClient(MCPClient):
    """MCP client using Tavily API for web search"""

    def __init__(self, tavily_key: str):
        self.tavily_key = tavily_key
        self.logger = logging.getLogger("mcp.tavily")

    async def _tavily_search(
        self, query: str, num_results: int = 5, search_depth: str = "basic", topic: str = "general"
    ) -> Dict[str, Any]:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(
                "https://api.tavily.com/search",
                json={
                    "api_key": self.tavily_key,
                    "query": query,
                    "search_depth": search_depth,
                    "max_results": num_results,
                    "include_answer": True,
                    "include_raw_content": False,
                    "topic": topic,
                },
            )
            resp.raise_for_status()
            return resp.json()

    async def search_web(self, query: str, num_results: int = 5) -> List[Dict[str, Any]]:
        try:
            data = await self._tavily_search(query, num_results, search_depth="advanced")
            results = []
            if data.get("answer"):
                results.append({
                    "title": "AI Summary",
                    "url": "",
                    "snippet": data["answer"],
                    "content": data["answer"],
                    "source": "tavily_answer",
                })
            for item in data.get("results", []):
                results.append({
                    "title": item.get("title", ""),
                    "url": item.get("url", ""),
                    "snippet": item.get("content", "")[:300],
                    "content": item.get("content", ""),
                    "source": "tavily",
                })
            self.logger.info(f"Tavily web search: {len(results)} results for '{query[:50]}'")
            return results
        except Exception as e:
            self.logger.error(f"Tavily web search failed: {e}")
            return []

    async def search_news(self, query: str, num_results: int = 5) -> List[Dict[str, Any]]:
        try:
            data = await self._tavily_search(query, num_results, topic="news")
            results = []
            for item in data.get("results", []):
                results.append({
                    "title": item.get("title", ""),
                    "url": item.get("url", ""),
                    "snippet": item.get("content", "")[:300],
                    "content": item.get("content", ""),
                    "source": "tavily_news",
                    "date": item.get("published_date", ""),
                })
            self.logger.info(f"Tavily news search: {len(results)} results")
            return results
        except Exception as e:
            self.logger.error(f"Tavily news search failed: {e}")
            return []

    async def search_trends(self, query: str, num_results: int = 5) -> List[Dict[str, Any]]:
        try:
            data = await self._tavily_search(f"{query} market trends 2024 2025", num_results)
            results = []
            if data.get("answer"):
                results.append({
                    "metric": "trend_summary",
                    "value": data["answer"],
                    "source": "tavily_trends",
                    "snippet": data["answer"][:200],
                })
            for item in data.get("results", []):
                results.append({
                    "metric": "trend_data",
                    "value": item.get("content", "")[:200],
                    "source": "tavily_trends",
                    "snippet": item.get("content", "")[:200],
                    "url": item.get("url", ""),
                    "title": item.get("title", ""),
                })
            return results
        except Exception as e:
            self.logger.error(f"Tavily trends search failed: {e}")
            return []

    async def extract_page(self, url: str) -> Optional[str]:
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                resp = await client.post(
                    "https://api.tavily.com/extract",
                    json={"api_key": self.tavily_key, "urls": [url]},
                )
                resp.raise_for_status()
                data = resp.json()
                results = data.get("results", [])
                if results:
                    return results[0].get("raw_content", "")
            return None
        except Exception as e:
            self.logger.error(f"Tavily extract failed: {e}")
            return None

    async def reddit_analysis(self, query: str) -> List[Dict[str, Any]]:
        try:
            data = await self._tavily_search(
                f"site:reddit.com {query}", num_results=5, search_depth="advanced"
            )
            results = []
            for item in data.get("results", []):
                results.append({
                    "subreddit": "reddit",
                    "title": item.get("title", ""),
                    "url": item.get("url", ""),
                    "snippet": item.get("content", "")[:300],
                    "source": "tavily_reddit",
                })
            return results
        except Exception as e:
            self.logger.error(f"Tavily reddit search failed: {e}")
            return []

    async def advertisement_intelligence(self, query: str) -> List[Dict[str, Any]]:
        try:
            data = await self._tavily_search(f"{query} advertising strategy", num_results=5)
            results = []
            for item in data.get("results", []):
                results.append({
                    "title": item.get("title", ""),
                    "url": item.get("url", ""),
                    "snippet": item.get("content", "")[:300],
                    "source": "tavily_ads",
                })
            return results
        except Exception as e:
            self.logger.error(f"Tavily ad intelligence failed: {e}")
            return []


class MockMCPClient(MCPClient):
    """Mock MCP client for testing"""

    def __init__(self):
        self.logger = logging.getLogger("mcp.mock")

    async def search_web(self, query: str, num_results: int = 5) -> List[Dict[str, Any]]:
        return [{"title": f"Mock: {query}", "url": "https://example.com", "snippet": "Mock result", "source": "mock"}]

    async def search_news(self, query: str, num_results: int = 5) -> List[Dict[str, Any]]:
        return [{"title": f"News: {query}", "url": "https://example.com", "snippet": "Mock news", "source": "mock_news", "date": "2024-03-15"}]

    async def search_trends(self, query: str, num_results: int = 5) -> List[Dict[str, Any]]:
        return [{"metric": "interest", "value": 75, "query": query, "source": "mock_trends"}]

    async def extract_page(self, url: str) -> Optional[str]:
        return f"Mock content from {url}"

    async def reddit_analysis(self, query: str) -> List[Dict[str, Any]]:
        return [{"subreddit": "r/test", "title": "Mock discussion", "snippet": "Mock"}]

    async def advertisement_intelligence(self, query: str) -> List[Dict[str, Any]]:
        return [{"title": "Mock ad", "source": "mock_ads"}]


# Global instance
_mcp_client: Optional[MCPClient] = None


def get_mcp_client() -> MCPClient:
    global _mcp_client
    if _mcp_client is None:
        from app.config import get_settings

        settings = get_settings()

        # Handle case-insensitive attribute access
        mcp_mode = getattr(settings, 'MCP_MODE', 'mock') or getattr(settings, 'mcp_mode', 'mock')
        mcp_server_url = getattr(settings, 'MCP_SERVER_URL', 'http://localhost:8000/mcp') or getattr(settings, 'mcp_server_url', 'http://localhost:8000/mcp')
        firecrawl_key = getattr(settings, 'FIRECRAWL_API_KEY', '') or getattr(settings, 'firecrawl_api_key', '')
        tavily_key = getattr(settings, 'TAVILY_API_KEY', '') or getattr(settings, 'tavily_api_key', '')

        if mcp_mode.lower() == "server":
            logger.info(f"Initializing SERVER MCP client (connecting to {mcp_server_url})")
            _mcp_client = ServerMCPClient(mcp_server_url=mcp_server_url)
        elif mcp_mode.lower() == "tavily" or (mcp_mode.lower() == "mock" and tavily_key):
            # Auto-upgrade from mock to tavily when a key is available
            logger.info("Initializing TAVILY MCP client")
            _mcp_client = TavilyMCPClient(tavily_key=tavily_key)
        elif mcp_mode.lower() == "real":
            logger.info("Initializing REAL MCP client (Firecrawl + PyTrends)")
            _mcp_client = FirecrawlMCPClient(
                firecrawl_key=firecrawl_key,
                tavily_key=tavily_key,
            )
        else:
            logger.info("Initializing MOCK MCP client")
            _mcp_client = MockMCPClient()

    return _mcp_client


def reset_mcp_client():
    global _mcp_client
    _mcp_client = None
