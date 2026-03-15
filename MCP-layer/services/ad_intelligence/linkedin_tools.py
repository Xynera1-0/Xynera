"""LinkedIn Ad Library Intelligence (Playwright scraping)"""

from typing import List, Dict, Any
import asyncio
import re
from datetime import datetime
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError
from services.utils.models import IntelligenceSignal, SignalConfidence, IntelligenceDomain
from services.playwright_crawler import smart_fallback_crawl


async def scrape_linkedin_ad_library(company_name: str, max_ads: int = 10) -> List[Dict[str, Any]]:
    """
    Scrape LinkedIn Ad Library for competitor advertising campaigns.
    
    Extracts:
    - Ad creatives and copy
    - Target audiences
    - Campaign timing
    - Ad variations
    - Engagement metrics (if visible)
    
    Args:
        company_name: Company to research ads for
        max_ads: Maximum ads to extract
    
    Returns:
        List of ad data dictionaries
    """
    ads_data = []
    company_slug = company_name.replace(" ", "-").lower()
    
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            page.set_default_timeout(15000)
            
            # Set realistic user agent
            await page.set_extra_http_headers({
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            })
            
            try:
                # Navigate to LinkedIn Ads Library
                ad_library_url = f"https://www.linkedin.com/ads/library?company={company_slug}"
                await page.goto("https://www.linkedin.com/ads/library/politics", wait_until="domcontentloaded")
                
                # Wait for page to load
                await page.wait_for_timeout(3000)
                
                # Search for the company
                search_input = await page.query_selector("input[placeholder*='Search']")
                if search_input:
                    await search_input.fill(company_name)
                    await page.wait_for_timeout(2000)
                
                # Extract visible ad containers
                ad_containers = await page.query_selector_all("[data-test-id*='ad']")
                
                for i, container in enumerate(ad_containers[:max_ads]):
                    try:
                        ad_info = {
                            "company": company_name,
                            "ad_number": i + 1,
                            "title": "",
                            "description": "",
                            "creative_url": "",
                            "target_audience": "",
                            "impressions": None,
                            "engagement": None,
                        }
                        
                        # Extract ad text
                        try:
                            text_elem = await container.query_selector("div[data-test-id*='text']")
                            if text_elem:
                                ad_info["description"] = await text_elem.text_content()
                        except:
                            pass
                        
                        # Extract ad creative/image
                        try:
                            img_elem = await container.query_selector("img")
                            if img_elem:
                                ad_info["creative_url"] = await img_elem.get_attribute("src")
                        except:
                            pass
                        
                        # Extract targeting info if visible
                        try:
                            targeting_elem = await container.query_selector("[data-test-id*='targeting']")
                            if targeting_elem:
                                ad_info["target_audience"] = await targeting_elem.text_content()
                        except:
                            pass
                        
                        # Extract metrics
                        try:
                            metrics_text = await container.text_content()
                            # Look for impressions pattern
                            if metrics_text:
                                imp_match = re.search(r'([\d,]+)\s*impressions', metrics_text, re.IGNORECASE)
                                if imp_match:
                                    ad_info["impressions"] = int(imp_match.group(1).replace(",", ""))
                        except:
                            pass
                        
                        if ad_info["description"] or ad_info["creative_url"]:
                            ads_data.append(ad_info)
                    
                    except Exception as e:
                        print(f"[linkedin_ad_library] Error extracting ad #{i+1}: {str(e)}")
                        continue
                
                return ads_data
            
            finally:
                await browser.close()
    
    except Exception as e:
        print(f"[linkedin_ad_library] Scraping failed for {company_name}: {str(e)}")
        return []


async def get_linkedin_ad_library_signals(
    company_names: List[str],
    max_ads_per_company: int = 5,
) -> List[IntelligenceSignal]:
    """
    Extract competitive intelligence from LinkedIn Ad Library.
    
    Maps to: Competitive Landscape, Positioning & Messaging Gaps, Market & Trend Sensing
    
    Scrapes active advertising campaigns to understand:
    - Messaging strategy and positioning
    - Target audience focus
    - Campaign timing and cadence
    - Creative variations (A/B testing insights)
    - Product/feature emphasis
    
    Args:
        company_names: List of competitor companies
        max_ads_per_company: Number of recent ads to extract per company
    
    Returns:
        List of IntelligenceSignal objects from ad campaigns
    """
    signals: List[IntelligenceSignal] = []
    
    # Scrape LinkedIn Ad Library for each company
    tasks = [scrape_linkedin_ad_library(company, max_ads_per_company) for company in company_names]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    for idx, company_name in enumerate(company_names):
        result = results[idx]
        
        # Handle errors
        if isinstance(result, Exception):
            print(f"[linkedin_ad_library] Exception for {company_name}: {str(result)}")
            result = []
        
        if not result or not isinstance(result, list):
            # Fallback to web crawler if Ad Library scraping failed
            fallback_query = f"{company_name} LinkedIn ads campaigns messaging"
            try:
                fallback_signals = await smart_fallback_crawl(fallback_query, IntelligenceDomain.COMPETITIVE)
                signals.extend(fallback_signals[:3])
            except Exception as e:
                print(f"[linkedin_ad_library] Fallback also failed for {company_name}: {str(e)}")
            continue
        
        # Create signals from extracted ads
        for ad in result:
            # Build signal content from ad data
            ad_copy = ad.get("description", "")[:300]
            targeting = ad.get("target_audience", "")[:200]
            
            content = f"Ad Copy: {ad_copy}\n"
            if targeting:
                content += f"Target Audience: {targeting}"
            
            # Determine confidence based on data richness
            confidence_score = 0.75  # LinkedIn Ad Library is reliable source
            
            if ad.get("impressions"):
                confidence_score = 0.85
                metric_info = f"Impressions: {ad['impressions']:,}"
            else:
                metric_info = f"Ad #{ad['ad_number']}"
            
            signal = IntelligenceSignal(
                domain=IntelligenceDomain.POSITIONING,
                source="linkedin_ad_library",
                title=f"LinkedIn Ad Campaign - {company_name}",
                content=content,
                url=f"https://www.linkedin.com/ads/library?company={company_name.replace(' ', '-').lower()}",
                timestamp=datetime.now().isoformat(),
                confidence=SignalConfidence(
                    score=confidence_score,
                    reasoning="Public LinkedIn Ad Library - shows actual messaging and targeting strategy",
                    supporting_metric=metric_info
                ),
                raw_metadata={
                    "company": company_name,
                    "ad_number": ad.get("ad_number"),
                    "creative_url": ad.get("creative_url"),
                    "target_audience": targeting,
                    "impressions": ad.get("impressions"),
                    "source_type": "linkedin_ad_library"
                }
            )
            signals.append(signal)
    
    return signals
