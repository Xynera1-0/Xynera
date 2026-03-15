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
from services.technical_signals import get_patent_signals
from services.ad_intelligence import get_meta_ads_signals, get_linkedin_ad_library_signals
from services.playwright_crawler import crawl_with_tavily, smart_fallback_crawl

# Load environment variables
load_dotenv()

# Initialize FastMCP server with HTTP transport (not stdio)
mcp = FastMCP("Xynera Growth Intelligence Server")


@mcp.tool()
async def gather_user_voice(
    keywords: List[str],
    sources: Optional[List[str]] = None,
    subreddits: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Gather user voice intelligence from Reddit and Hacker News.
    
    Maps to: Market & Trend Sensing, Competitive Landscape, Win/Loss Intelligence
    
    Args:
        keywords: Search terms (e.g., ["pricing too high", "competitor X pricing"])
        sources: ["reddit", "hackernews"] (default: both)
        subreddits: Subreddits to search (default: ["SaaS", "startups", "Entrepreneur"])
    
    Returns:
        Dict with signals from each source and confidence scores
    """
    if sources is None:
        sources = ["reddit", "hackernews"]
    
    results = {
        "domain": "user_voice",
        "signals": {},
        "total_signals": 0,
    }
    
    try:
        # Reddit signals
        if "reddit" in sources:
            reddit_signals = await get_reddit_user_voice(
                keywords=keywords,
                subreddits=subreddits or ["SaaS", "startups", "Entrepreneur"],
                limit=10
            )
            results["signals"]["reddit"] = [s.model_dump() for s in reddit_signals]
            results["total_signals"] += len(reddit_signals)
        
        # HN signals
        if "hackernews" in sources:
            hn_signals = await get_hackernews_signals(keywords=keywords, limit=10)
            results["signals"]["hackernews"] = [s.model_dump() for s in hn_signals]
            results["total_signals"] += len(hn_signals)
        
        return results
    
    except Exception as e:
        return {"error": f"Error gathering user voice: {str(e)}"}


@mcp.tool()
async def gather_technical_signals(
    keywords: List[str],
) -> Dict[str, Any]:
    """
    Gather technical signals from USPTO patents and emerging tech.
    
    Maps to: Adjacent Market Collision, Market & Trend Sensing
    
    Useful for detecting pre-launch competitor activity and emerging tech.
    
    Args:
        keywords: Technology keywords to search
    
    Returns:
        Dict with patent signals and analysis
    """
    results = {
        "domain": "technical_signals",
        "source": "patents_uspto",
        "signals": [],
    }
    
    try:
        signals = await get_patent_signals(keywords=keywords, limit=15)
        results["signals"] = [s.model_dump() for s in signals]
        return results
    
    except Exception as e:
        return {"error": f"Error gathering technical signals: {str(e)}"}


@mcp.tool()
async def gather_meta_ads(
    company_names: List[str],
) -> Dict[str, Any]:
    """
    Gather Meta Ads intelligence from competitor campaigns.
    
    Maps to: Competitive Landscape, Positioning & Messaging Gaps
    
    Monitors competitor ad messaging, spend patterns, and creative strategies
    from Meta's Ads Library (Facebook, Instagram, Audience Network).
    
    Args:
        company_names: List of competitor companies to monitor
    
    Returns:
        Dict with Meta ad signals, messaging insights, and spend patterns
    """
    results = {
        "domain": "ad_intelligence",
        "source": "meta_ads",
        "companies_analyzed": company_names,
        "signals": [],
        "total_signals": 0,
    }
    
    try:
        meta_signals = await get_meta_ads_signals(company_names=company_names)
        results["signals"] = [s.model_dump() for s in meta_signals]
        results["total_signals"] = len(meta_signals)
        return results
    
    except Exception as e:
        return {"error": f"Error gathering Meta ad intelligence: {str(e)}"}


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
async def gather_ad_intelligence(
    company_names: List[str],
    sources: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Comprehensive ad intelligence from both Meta and LinkedIn.
    
    Maps to: Competitive Landscape, Positioning & Messaging Gaps
    
    Combines Meta Ads and LinkedIn Ad Library data for a complete
    competitive intelligence picture.
    
    Args:
        company_names: List of competitor companies
        sources: ["meta", "linkedin"] (default: both)
    
    Returns:
        Dict with ad signals from all sources
    """
    if sources is None:
        sources = ["meta", "linkedin"]
    
    results = {
        "domain": "ad_intelligence",
        "signals": {},
        "total_signals": 0,
    }
    
    try:
        # Meta ads
        if "meta" in sources:
            meta_signals = await get_meta_ads_signals(company_names=company_names)
            results["signals"]["meta_ads"] = [s.model_dump() for s in meta_signals]
            results["total_signals"] += len(meta_signals)
        
        # LinkedIn Ad Library
        if "linkedin" in sources:
            linkedin_signals = await get_linkedin_ad_library_signals(company_names=company_names)
            results["signals"]["linkedin_ad_library"] = [s.model_dump() for s in linkedin_signals]
            results["total_signals"] += len(linkedin_signals)
        
        return results
    
    except Exception as e:
        return {"error": f"Error gathering ad intelligence: {str(e)}"}


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
async def gather_all_intelligence(
    question: str,
    keywords: List[str],
    competitors: Optional[List[str]] = None,
    domains: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """
    Comprehensive intelligence gathering across all six domains.
    
    This is the main entry point for product growth teams.
    Gathers signals from Reddit, HN, Patents, and Ad sources simultaneously.
    
    Args:
        question: The strategic question being answered (e.g., "Should we lower pricing?")
        keywords: Search terms relevant to the question
        competitors: List of competitors to monitor
        domains: Specific intelligence domains to focus on (default: all 6)
    
    Returns:
        Aggregated intelligence with confidence scores and strategic insights
    """
    results = {
        "question": question,
        "domains_covered": domains or list(IntelligenceDomain),
        "signals_by_domain": {},
        "total_signals": 0,
        "top_insights": [],
    }
    
    try:
        # Gather from all sources in parallel
        tasks = []
        
        # User Voice (Market & Trend Sensing, Competitive Landscape, Win/Loss)
        if not domains or "market_trends" in domains or "competitive" in domains:
            tasks.append(gather_user_voice(keywords))
        
        # Technical Signals (Adjacent Market Collision)
        if not domains or "adjacent" in domains:
            tasks.append(gather_technical_signals(keywords))
        
        # Ad Intelligence (Competitive Landscape, Positioning)
        if (not domains or "competitive" in domains or "positioning" in domains) and competitors:
            tasks.append(gather_ad_intelligence(competitors))
        
        # Execute all in parallel
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        
        for response in responses:
            # Filter out exceptions and only process dict responses
            if isinstance(response, dict) and "error" not in response:
                domain = response.get("domain", "unknown")
                results["signals_by_domain"][domain] = response.get("signals", {})
                results["total_signals"] += response.get("total_signals", len(response.get("signals", {})))
        
        # Extract top insights (signals with confidence > 0.7)
        for domain, signals_dict in results["signals_by_domain"].items():
            if isinstance(signals_dict, dict):
                for source, signal_list in signals_dict.items():
                    if isinstance(signal_list, list):
                        for signal in signal_list:
                            if signal.get("confidence", {}).get("score", 0) > 0.7:
                                results["top_insights"].append({
                                    "domain": domain,
                                    "source": source,
                                    "title": signal.get("title"),
                                    "confidence": signal.get("confidence"),
                                })
        
        return results
    
    except Exception as e:
        return {"error": f"Error gathering intelligence: {str(e)}"}


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
