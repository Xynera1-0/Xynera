"""Playwright Web Crawler - Hybrid Approach Using Tavily API + Playwright"""

import os
import httpx
from typing import List
from playwright.async_api import async_playwright
from services.utils.models import IntelligenceSignal, SignalConfidence, IntelligenceDomain


async def smart_fallback_crawl(
    query: str,
    domain: IntelligenceDomain = IntelligenceDomain.MARKET_TRENDS,
) -> List[IntelligenceSignal]:
    """
    Intelligent Hybrid Crawler.
    1. Uses Tavily API to get clean, ranked URLs (reliable).
    2. Uses Playwright to crawl the full text of those URLs (deep).
    
    Args:
        query: Search query
        domain: Intelligence domain category
    
    Returns:
        List of IntelligenceSignal objects from crawled content
    """
    tavily_key = os.getenv("TAVILY_API_KEY", "")
    if not tavily_key:
        print("[playwright_crawler] ⚠️ TAVILY_API_KEY missing.")
        return []

    signals: List[IntelligenceSignal] = []
    urls_to_crawl = []

    # STEP 1: Get URLs via Tavily API (Avoids the '0 link elements' error)
    try:
        async with httpx.AsyncClient() as client:
            print(f"[playwright_crawler] 🎯 Searching Tavily API for: {query}")
            resp = await client.post(
                "https://api.tavily.com/search",
                json={
                    "api_key": tavily_key,
                    "query": query,
                    "search_depth": "advanced",
                    "max_results": 3
                },
                timeout=10.0
            )
            search_data = resp.json()
            urls_to_crawl = [r['url'] for r in search_data.get('results', [])]
            print(f"[playwright_crawler] ✅ API found {len(urls_to_crawl)} URLs.")
    except Exception as e:
        print(f"[playwright_crawler] ❌ API search failed: {e}")
        return []

    # STEP 2: Deep Crawl with Playwright
    if not urls_to_crawl:
        print("[playwright_crawler] No URLs to crawl")
        return []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        # Use a high-quality User-Agent to avoid bot-blocks on target sites
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        )
        page = await context.new_page()

        for idx, url in enumerate(urls_to_crawl):
            try:
                print(f"[playwright_crawler] 🕷️ [{idx+1}/{len(urls_to_crawl)}] Deep crawling: {url}")
                await page.goto(url, wait_until="domcontentloaded", timeout=15000)
                title = await page.title()
                
                # Intelligent content extraction (skips headers/footers)
                content = await page.evaluate("""
                    () => {
                        const root = document.querySelector('article, main, #content, .post-content') || document.body;
                        return root.innerText.substring(0, 1500);
                    }
                """)

                if not content or content.strip() == "":
                    print(f"[playwright_crawler] ⚠️ No content from {url}")
                    continue

                signal = IntelligenceSignal(
                    domain=domain,
                    source="hybrid_crawler",
                    title=title or url,
                    content=content[:500],
                    url=url,
                    timestamp=None,
                    confidence=SignalConfidence(
                        score=0.7,
                        reasoning="Direct deep-crawl of API-verified search result",
                        supporting_metric=f"Source: {url}"
                    ),
                    raw_metadata={
                        "query": query,
                        "engine": "tavily_api",
                        "extracted_from": url,
                    }
                )
                signals.append(signal)
                print(f"[playwright_crawler] ✅ Extracted {len(content)} chars")
            except Exception as e:
                print(f"[playwright_crawler] ❌ Failed to crawl {url}: {e}")
                continue

        await browser.close()
    
    print(f"[playwright_crawler] ✅ Successfully extracted {len(signals)} signals")
    return signals


async def crawl_with_tavily(
    query: str,
    domain: IntelligenceDomain = IntelligenceDomain.MARKET_TRENDS,
    pages_to_crawl: int = 3,
) -> List[IntelligenceSignal]:
    """
    Wrapper for backward compatibility - calls smart_fallback_crawl.
    
    Args:
        query: Search query
        domain: Intelligence domain category
        pages_to_crawl: Ignored (uses Tavily API max_results)
    
    Returns:
        List of IntelligenceSignal objects
    """
    return await smart_fallback_crawl(query, domain)
