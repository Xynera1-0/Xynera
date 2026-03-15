"""Hacker News intelligence using Algolia API (free, no key)"""

import httpx
from typing import List
from datetime import datetime
from services.utils.models import IntelligenceSignal, SignalConfidence, IntelligenceDomain
from services.playwright_crawler import smart_fallback_crawl


HACKERNEWS_ALGOLIA_API = "https://hn.algolia.com/api/v1/search"


async def get_hackernews_signals(
    keywords: List[str],
    limit: int = 10,
) -> List[IntelligenceSignal]:
    """
    Extract signals from Hacker News (technical/market signals).
    
    Maps to: Market & Trend Sensing, Adjacent Market Collision
    
    Uses Algolia's free HN search API (no authentication required).
    Falls back to Playwright crawler if API is unavailable.
    
    Args:
        keywords: Search terms
        limit: Number of results per keyword
    
    Returns:
        List of IntelligenceSignal objects
    """
    signals: List[IntelligenceSignal] = []
    
    try:
        async with httpx.AsyncClient() as client:
            for keyword in keywords:
                try:
                    # Query Algolia HN API
                    response = await client.get(
                        HACKERNEWS_ALGOLIA_API,
                        params={"query": keyword, "hitsPerPage": limit},
                        timeout=10.0,
                    )
                    response.raise_for_status()
                    data = response.json()
                    
                    for hit in data.get("hits", []):
                        if not hit.get("title"):
                            continue
                        
                        # Map to domain based on keywords
                        domain = IntelligenceDomain.MARKET_TRENDS
                        if any(w in keyword.lower() for w in ["ai", "ml", "tech", "framework"]):
                            domain = IntelligenceDomain.ADJACENT
                        
                        # Confidence: points + comments
                        score = (hit.get("points", 0) + hit.get("num_comments", 0)) / 100
                        confidence_score = min(score, 1.0)
                        
                        signal = IntelligenceSignal(
                            domain=domain,
                            source="hackernews",
                            title=hit.get("title", ""),
                            content=hit.get("story_text", hit.get("title", ""))[:500],
                            url=hit.get("url", f"https://news.ycombinator.com/item?id={hit.get('objectID')}"),
                            timestamp=hit.get("created_at"),
                            confidence=SignalConfidence(
                                score=confidence_score,
                                reasoning="Technical community signal from Hacker News",
                                supporting_metric=f"{hit.get('points', 0)} points, {hit.get('num_comments', 0)} comments"
                            ),
                            raw_metadata={
                                "author": hit.get("author", "unknown"),
                                "points": hit.get("points", 0),
                                "num_comments": hit.get("num_comments", 0),
                                "hn_id": hit.get("objectID"),
                            }
                        )
                        signals.append(signal)
                
                except Exception as e:
                    print(f"Error fetching HN signals for '{keyword}': {str(e)}")
                    continue
    
    except Exception as e:
        # Fallback to Playwright crawler if Algolia API fails
        print(f"[hackernews_tools] API error, falling back to web crawler: {str(e)}")
        
        # Use first keyword for crawler fallback
        fallback_query = ' '.join([f"{k} site:news.ycombinator.com" for k in keywords[:2]]) if keywords else "hacker news"
        
        try:
            fallback_signals = await smart_fallback_crawl(fallback_query, IntelligenceDomain.MARKET_TRENDS)
            return fallback_signals if fallback_signals else []
        except Exception as fallback_error:
            print(f"[hackernews_tools] Fallback crawler also failed: {str(fallback_error)}")
            return []
    
    return signals
