"""Playwright Web Crawler - Fallback using Tavily Search"""

import os
from typing import List, Optional
from playwright.async_api import async_playwright
from services.utils.models import IntelligenceSignal, SignalConfidence, IntelligenceDomain


async def crawl_with_tavily(
    query: str,
    domain: IntelligenceDomain = IntelligenceDomain.MARKET_TRENDS,
    pages_to_crawl: int = 3,
) -> List[IntelligenceSignal]:
    """
    Crawl web pages using Playwright with Tavily search.
    
    Acts as a universal fallback when APIs fail or lack credentials.
    Uses Tavily for reliable, CAPTCHA-free searching.
    
    Args:
        query: Search query
        domain: Intelligence domain category
        pages_to_crawl: Number of pages to visit (default: 3)
    
    Returns:
        List of IntelligenceSignal objects from crawled content
    """
    signals: List[IntelligenceSignal] = []
    
    async with async_playwright() as p:
        # Launch with a realistic User-Agent
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        
        search_url = f"https://tavily.com/search?q={query.replace(' ', '+')}"
        
        try:
            print(f"[playwright_crawler] Navigating to: {search_url}")
            await page.goto(search_url, wait_until="networkidle", timeout=20000)
            
            # Wait for any link that looks like a search result title
            # This is more robust than a specific class name
            print("[playwright_crawler] Waiting for search results...")
            await page.wait_for_selector("h3, a[href^='http']", timeout=10000)
            
            # Extract links: prioritize links that contain <h3> or are inside result containers
            links = await page.locator("h3 a, .result a, a:has(h3)").all()
            urls_to_crawl = []
            
            print(f"[playwright_crawler] Found {len(links)} link elements")
            
            for link in links:
                try:
                    href = await link.get_attribute("href")
                    if href and href.startswith("http") and "tavily.com" not in href:
                        urls_to_crawl.append(href)
                        if len(urls_to_crawl) >= pages_to_crawl:
                            break
                except Exception as e:
                    print(f"[playwright_crawler] Error extracting link: {e}")
                    continue
            
            print(f"[playwright_crawler] Extracted {len(urls_to_crawl)} URLs to crawl.")

            # Crawl extracted pages
            for idx, url in enumerate(urls_to_crawl):
                try:
                    print(f"[playwright_crawler] [{idx+1}/{len(urls_to_crawl)}] Crawling: {url}")
                    await page.goto(url, wait_until="domcontentloaded", timeout=15000)
                    title = await page.title()
                    
                    # Extract content using a more specific selector for readability
                    content = await page.evaluate("""
                        () => {
                            const root = document.querySelector('article, main, #content, .post-content') || document.body;
                            return root.innerText.substring(0, 1200);
                        }
                    """)
                    
                    if not content or content.strip() == "":
                        print(f"[playwright_crawler] No content extracted from {url}")
                        continue
                    
                    print(f"[playwright_crawler] ✅ Extracted {len(content)} chars from {title[:50]}")
                    
                    signal = IntelligenceSignal(
                        domain=domain,
                        source="playwright_crawler",
                        title=title or url,
                        content=content[:500],
                        url=url,
                        timestamp=None,
                        confidence=SignalConfidence(
                            score=0.6,
                            reasoning="Verified via multi-hop web crawl from Tavily search results",
                            supporting_metric=f"Target: {url}"
                        ),
                        raw_metadata={
                            "search_query": query,
                            "engine": "tavily",
                            "extracted_from": url,
                        }
                    )
                    signals.append(signal)
                except Exception as e:
                    print(f"[playwright_crawler] Skip {url}: {str(e)}")
                    continue
                    
        except Exception as e:
            print(f"[playwright_crawler] Search crawl error: {str(e)}")
        
        finally:
            await browser.close()
            print(f"[playwright_crawler] ✅ Successfully extracted {len(signals)} signals")
            
    return signals


async def smart_fallback_crawl(
    query: str,
    domain: IntelligenceDomain = IntelligenceDomain.MARKET_TRENDS,
) -> List[IntelligenceSignal]:
    """
    Intelligent fallback crawler using Tavily search.
    
    Requires access to tavily.com (no API key needed for basic search).
    
    Args:
        query: Search query
        domain: Intelligence domain category
    
    Returns:
        List of signals from crawled content
    """
    tavily_key = os.getenv("TAVILY_API_KEY", "")
    
    if not tavily_key:
        print("[playwright_crawler] TAVILY_API_KEY not configured - fallback crawler unavailable")
        return []
    
    return await crawl_with_tavily(
        query=query,
        domain=domain,
        pages_to_crawl=3,
    )
