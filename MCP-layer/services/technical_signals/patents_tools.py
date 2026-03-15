"""USPTO Patents Intelligence using PatentsView API (v1)"""

import os
import httpx
from typing import List
from services.utils.models import IntelligenceSignal, SignalConfidence, IntelligenceDomain
from services.playwright_crawler import smart_fallback_crawl


# New PatentsView v1 API endpoint
PATENTSVIEW_API = "https://search.patentsview.org/api/v1/patent/"


async def get_patent_signals(
    keywords: List[str],
    limit: int = 10,
) -> List[IntelligenceSignal]:
    """
    Extract technical signals from USPTO patent filings.
    
    Maps to: Adjacent Market Collision, Market & Trend Sensing
    
    Uses PatentsView v1 REST API (free, open data).
    Falls back to Playwright crawler if API is unavailable.
    Useful for detecting pre-launch technical signals and emerging tech.
    
    Args:
        keywords: Technology keywords to search
        limit: Number of patents per keyword
    
    Returns:
        List of IntelligenceSignal objects from patent data
    """
    signals: List[IntelligenceSignal] = []
    
    # Get API key from environment (optional for basic free tier)
    api_key = os.getenv("PATENTSVIEW_API_KEY", "")
    
    try:
        async with httpx.AsyncClient() as client:
            for keyword in keywords:
                try:
                    # Build headers with optional API key
                    headers = {}
                    if api_key:
                        headers["X-Api-Key"] = api_key
                    
                    # Updated query parameters for v1 API
                    params = {
                        "q": f'"{keyword}"',
                        "f": ["patent_id", "patent_title", "patent_date", "assignee_organization"],
                        "s": [{"patent_date": "desc"}],
                        "size": limit,  # Changed from per_page
                    }
                    
                    response = await client.get(
                        PATENTSVIEW_API,
                        params=params,
                        headers=headers,
                        timeout=10.0,
                    )
                    response.raise_for_status()
                    data = response.json()
                    
                    # Handle v1 API response structure
                    patents = data.get("data", {}).get("patents", [])
                    
                    for patent in patents[:limit]:
                        assignee = "Unknown"
                        if patent.get("assignees") and len(patent["assignees"]) > 0:
                            assignee = patent["assignees"][0].get("organization", "Unknown")
                        
                        signal = IntelligenceSignal(
                            domain=IntelligenceDomain.ADJACENT,
                            source="patents_uspto",
                            title=patent.get("title", ""),
                            content=f"Patent filed by {assignee} for {keyword}",
                            url=f"https://patents.google.com/patent/{patent.get('patent_id')}",
                            timestamp=patent.get("patent_date"),
                            confidence=SignalConfidence(
                                score=0.7,  # Patents are verified technical signals
                                reasoning="Official USPTO patent filing - verifiable technical innovation",
                                supporting_metric=f"Patent {patent.get('patent_id')}"
                            ),
                            raw_metadata={
                                "patent_id": patent.get("patent_id"),
                                "assignee": assignee,
                                "filing_date": patent.get("patent_date"),
                            }
                        )
                        signals.append(signal)
                
                except Exception as e:
                    print(f"Error fetching patents for '{keyword}': {str(e)}")
                    continue
    
    except Exception as e:
        # Fallback to Playwright crawler if PatentsView API fails
        print(f"[patents_tools] API error, falling back to web crawler: {str(e)}")
        
        # Use first keyword for crawler fallback
        fallback_query = ' '.join([f"{k} patent" for k in keywords[:2]]) if keywords else "patent filing"
        
        try:
            fallback_signals = await smart_fallback_crawl(fallback_query, IntelligenceDomain.ADJACENT)
            return fallback_signals if fallback_signals else []
        except Exception as fallback_error:
            print(f"[patents_tools] Fallback crawler also failed: {str(fallback_error)}")
            return []
    
    return signals
