"""
Xynera Growth Intelligence HTTP MCP Server

Six intelligence domains:
1. Market & Trend Sensing
2. Competitive Landscape & Feature Bets
3. Win/Loss Intelligence
4. Pricing & Packaging Intelligence
5. Positioning & Messaging Gaps
6. Adjacent Market Collision

Data sources:
- Reddit (User Voice)
- Hacker News (Market Trends)
- USPTO Patents (Technical Signals)
- Meta Ads (Competitive Intelligence)
- LinkedIn Ads (Organizational Signals)
- Playwright (Fallback for any source)
"""

import asyncio
from typing import List, Dict, Any, Optional
from fastmcp import FastMCP
from dotenv import load_dotenv

from services.utils.models import IntelligenceDomain, ConversationContext
from services.user_voice import get_reddit_user_voice, get_hackernews_signals
from services.ad_intelligence import get_meta_ads_signals, get_linkedin_ad_library_signals
from services.playwright_crawler import crawl_with_tavily, smart_fallback_crawl

# Load environment variables
load_dotenv()

# Initialize FastMCP server with HTTP transport (not stdio)
mcp = FastMCP("Xynera Growth Intelligence Server")


@mcp.tool()
async def gather_hackernews_signals(
    keywords: List[str],
    limit: int = 10,
) -> Dict[str, Any]:
    """
    Gather Hacker News signals from technical discussions.
    
    Maps to: Market & Trend Sensing, Adjacent Market Collision
    
    Extracts technical trends, emerging technologies, and developer
    sentiment from Hacker News discussions and front page stories.
    
    Args:
        keywords: Search terms (e.g., ["AI", "automation", "SaaS"])
        limit: Number of results per keyword (default: 10)
    
    Returns:
        Dict with Hacker News signal data and trend analysis
    """
    results = {
        "domain": "market_trends",
        "source": "hackernews",
        "signals": [],
        "total_signals": 0,
    }
    
    try:
        hn_signals = await get_hackernews_signals(keywords=keywords, limit=limit)
        results["signals"] = [s.model_dump() for s in hn_signals]
        results["total_signals"] = len(hn_signals)
        return results
    
    except Exception as e:
        return {"error": f"Error gathering Hacker News signals: {str(e)}"}


@mcp.tool()
async def gather_linkedin_ads(
    company_names: List[str],
) -> Dict[str, Any]:
    """
    Gather LinkedIn Ads intelligence from competitor campaigns.
    
    Maps to: Competitive Landscape, Positioning & Messaging Gaps
    
    Scrapes LinkedIn Ad Library to extract competitor ad campaigns,
    messaging strategy, and organizational signals (hiring patterns,
    product focus areas, target audience positioning).
    
    Args:
        company_names: List of competitor companies to monitor
    
    Returns:
        Dict with LinkedIn ad signals and messaging insights
    """
    results = {
        "domain": "ad_intelligence",
        "source": "linkedin_ad_library",
        "companies_analyzed": company_names,
        "signals": [],
        "total_signals": 0,
    }
    
    try:
        linkedin_signals = await get_linkedin_ad_library_signals(company_names=company_names)
        results["signals"] = [s.model_dump() for s in linkedin_signals]
        results["total_signals"] = len(linkedin_signals)
        return results
    
    except Exception as e:
        return {"error": f"Error gathering LinkedIn ad intelligence: {str(e)}"}


@mcp.tool()
async def analyze_linkedin_ads(
    company_names: List[str],
    max_ads_per_company: int = 5,
) -> Dict[str, Any]:
    """
    Deep-dive into competitor LinkedIn Ad campaigns.
    
    Maps to: Competitive Landscape, Positioning & Messaging Gaps
    
    Scrapes LinkedIn Ad Library to understand:
    - Messaging strategy and positioning claims
    - Target audience focus (what personas they're going after)
    - Campaign timing and cadence
    - Product/feature emphasis in ads
    - A/B testing insights from ad variations
    
    Use this when you need to understand how competitors are positioning
    themselves and what messaging resonates with their target buyers.
    
    Args:
        company_names: List of competitor companies to analyze
        max_ads_per_company: Number of recent ads to extract (default: 5)
    
    Returns:
        Dict with extracted ad campaigns and strategic insights
    """
    results = {
        "domain": "ad_intelligence",
        "source": "linkedin_ad_library",
        "companies_analyzed": company_names,
        "signals": [],
        "messaging_insights": [],
    }
    
    try:
        signals = await get_linkedin_ad_library_signals(
            company_names=company_names,
            max_ads_per_company=max_ads_per_company,
        )
        
        results["signals"] = [s.model_dump() for s in signals]
        results["total_signals"] = len(signals)
        
        # Extract messaging patterns
        for signal in signals:
            if signal.content:
                results["messaging_insights"].append({
                    "company": signal.raw_metadata.get("company"),
                    "message": signal.content[:200],
                    "confidence": signal.confidence.score,
                    "metric": signal.confidence.supporting_metric,
                })
        
        return results
    
    except Exception as e:
        return {"error": f"Error analyzing LinkedIn ads: {str(e)}"}


@mcp.tool()
def list_intelligence_domains() -> Dict[str, str]:
    """List the six intelligence domains available"""
    return {
        "market_trends": "Market & Trend Sensing - Where is the category heading and what are the leading indicators?",
        "competitive": "Competitive Landscape & Feature Bets - Who's doing what? Is the demand genuine? Is a bet worth making?",
        "win_loss": "Win/Loss Intelligence - Why are deals being lost? What does the market look like from the buyer's side?",
        "pricing": "Pricing & Packaging Intelligence - Is the pricing model right? Where is willingness-to-pay shifting?",
        "positioning": "Positioning & Messaging Gaps - Not what to build - how to talk about what already exists.",
        "adjacent": "Adjacent Market Collision - What's coming from outside your category that you're not watching?",
    }


@mcp.tool()
async def force_crawl(
    query: str,
    domain: Optional[str] = None,
) -> Dict[str, Any]:
    """
    The "Force" Tool - Playwright-based web crawler with Tavily search.
    
    Use this when:
    - APIs are down or returning errors
    - You need manual web crawling for specific research
    - You want to crawl competitor websites, news pages, or forums
    - You're investigating a term not covered by Reddit/HN/Patents
    
    Maps to: ALL intelligence domains
    
    Requires: TAVILY_API_KEY in .env
    
    Args:
        query: Search term or URL to crawl
        domain: Intelligence domain (default: market_trends)
        search_engine: "google" or "tavily" (default: google)
    
    Returns:
        Crawled signals from web pages
    """
    domain_enum = IntelligenceDomain.MARKET_TRENDS
    if domain:
        try:
            domain_enum = IntelligenceDomain[domain.upper()]
        except KeyError:
            domain_enum = IntelligenceDomain.MARKET_TRENDS
    
    try:
        signals = await crawl_with_tavily(
            query=query,
            domain=domain_enum,
            pages_to_crawl=3,
        )
        
        return {
            "domain": str(domain_enum),
            "source": "playwright_crawler_tavily",
            "query": query,
            "signals": [s.model_dump() for s in signals],
            "total_signals": len(signals),
        }
    
    except Exception as e:
        return {"error": f"Crawling failed: {str(e)}", "query": query}


if __name__ == "__main__":
    print("=" * 80)
    print("🚀 Xynera Growth Intelligence Server")
    print("=" * 80)
    print("\nStarting HTTP MCP server...")
    print("Core intelligence domains: 6")
    print("Data sources: Reddit, HN, Patents, Meta Ads, LinkedIn, Playwright")
    print("\nServer will be available at: http://localhost:8000")
    print("API documentation: http://localhost:8000/docs")
    print("=" * 80 + "\n")
    
    # Run FastMCP with HTTP transport (not stdio)
    mcp.run(transport="http", host="127.0.0.1", port=8000)
