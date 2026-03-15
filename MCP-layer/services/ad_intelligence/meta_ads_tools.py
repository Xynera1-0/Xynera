"""Meta Ads Intelligence (Facebook/Instagram - Ads Archive API)"""

from typing import List
import httpx
import os
import json
from services.utils.models import IntelligenceSignal, SignalConfidence, IntelligenceDomain


async def get_meta_ads_signals(
    company_names: List[str],
) -> List[IntelligenceSignal]:
    """
    Extract Meta ads intelligence from Meta Ads Archive API.
    
    Maps to: Competitive Landscape, Positioning & Messaging Gaps
    
    Uses Meta's official Ads Archive API to gather:
    - Ad creatives and copy
    - Page/account running ads
    - Ad spend data
    - Ad snapshots
    
    Requires META_ACCESS_TOKEN in .env (get from Meta Business Suite)
    
    Args:
        company_names: List of competitor companies to monitor
    
    Returns:
        List of IntelligenceSignal objects from Meta ads
    """
    signals: List[IntelligenceSignal] = []
    token = os.getenv("META_ACCESS_TOKEN", "")
    
    if not token:
        print("[meta_ads] META_ACCESS_TOKEN not configured in .env")
        return signals
    
    async with httpx.AsyncClient() as client:
        for company in company_names:
            # Meta API expects ad_reached_countries as JSON array
            params = {
                "access_token": token,
                "ad_reached_countries": json.dumps(["US"]),  # JSON string: ["US"]
                "ad_type": "ALL",
                "search_terms": company,  # Plain string
                "fields": "id,ad_creative_bodies,page_name,ad_snapshot_url,spend"
            }
            
            try:
                print(f"[meta_ads] Searching Meta Ads for: {company}")
                response = await client.get(
                    "https://graph.facebook.com/v19.0/ads_archive",
                    params=params,
                    timeout=10.0
                )
                response.raise_for_status()
                data = response.json().get("data", [])
                print(f"[meta_ads] Found {len(data)} ads for {company}")
                
                for ad in data:
                    ad_copy = ad.get("ad_creative_bodies", [""])[0][:300]
                    
                    signal = IntelligenceSignal(
                        domain=IntelligenceDomain.COMPETITIVE,
                        source="meta_ads",
                        title=f"Meta Ad - {ad.get('page_name', 'Unknown')}",
                        content=ad_copy,
                        url=ad.get("ad_snapshot_url", "https://www.facebook.com/ads/library/"),
                        timestamp=None,
                        confidence=SignalConfidence(
                            score=0.9,
                            reasoning="Direct signal from Meta's official transparency archive",
                            supporting_metric=f"Spend: {ad.get('spend', 'N/A')}"
                        ),
                        raw_metadata={
                            "company": company,
                            "page_name": ad.get("page_name"),
                            "ad_id": ad.get("id"),
                            "spend": ad.get("spend"),
                            "source_type": "meta_ads_archive"
                        }
                    )
                    signals.append(signal)
            
            except Exception as e:
                print(f"[meta_ads] API error for {company}: {str(e)}")
                # Try to get more error details
                try:
                    if 'response' in locals():
                        error_data = response.json()
                        print(f"[meta_ads] Response: {error_data}")
                except:
                    pass
                continue
    
    return signals
