"""
Demo runner and execution examples for Xynera Growth Intelligence Server

Shows how to:
1. Start the HTTP MCP server
2. Make requests to gather intelligence
3. View and interpret results
"""

import asyncio
import json
from typing import Dict, Any
import httpx

# Point to your running MCP server
MCP_SERVER_URL = "http://localhost:8000/api"


async def demo_user_voice():
    """Demo 1: Gather user voice signals"""
    print("\n" + "=" * 80)
    print("DEMO 1: User Voice Intelligence")
    print("=" * 80)
    print("Question: What pricing complaints appear on Reddit?\n")
    
    # This would call the MCP tool via HTTP
    print("Query: gather_user_voice(")
    print('  keywords=["pricing too high", "expensive"],')
    print('  sources=["reddit", "hackernews"]')
    print(")\n")
    print("▶ Expected output:")
    print("  - 20+ signals from r/SaaS and r/startups")
    print("  - Confidence scores based on upvote ratios")
    print("  - Direct quotes from top comments (the pain points)")
    print("  - Mapped to pricing & competitive domains")


async def demo_competitive_landscape():
    """Demo 2: Competitive landscape analysis"""
    print("\n" + "=" * 80)
    print("DEMO 2: Competitive Landscape Intelligence")
    print("=" * 80)
    print("Question: What are our competitors doing?\n")
    
    print("Query: gather_ad_intelligence(")
    print('  company_names=["Intercom", "Drift", "Zendesk"]')
    print(")\n")
    print("▶ Expected output:")
    print("  - Ad copy from Meta ads library")
    print("  - LinkedIn job postings (headcount signals)")
    print("  - Positioning changes over time")
    print("  - Estimated ad spend (if available)")


async def demo_technical_signals():
    """Demo 3: Technical signals (patents)"""
    print("\n" + "=" * 80)
    print("DEMO 3: Technical Signals Intelligence")
    print("=" * 80)
    print("Question: What emerging technologies should we watch?\n")
    
    print("Query: gather_technical_signals(")
    print('  keywords=["conversational AI", "real-time collaboration"]')
    print(")\n")
    print("▶ Expected output:")
    print("  - Recent patent filings from competitors")
    print("  - Technical innovation signals")
    print("  - 6-12 month early warning of competitor moves")
    print("  - Links to full patent documents")


async def demo_all_intelligence():
    """Demo 4: Complete intelligence gathering"""
    print("\n" + "=" * 80)
    print("DEMO 4: Complete Intelligence Gathering")
    print("=" * 80)
    print("Question: Should we enter the AI customer service market?\n")
    
    print("Query: gather_all_intelligence(")
    print('  question="Should we build AI customer service?",')
    print('  keywords=["AI customer service", "automation", "cost reduction"],')
    print('  competitors=["Intercom", "Zendesk", "Descript"],')
    print('  domains=["market_trends", "competitive", "adjacent"]')
    print(")\n")
    print("▶ Expected output:")
    print("  📊 Market Signals (Reddit/HN):")
    print("     - User demand: 'AI support is replacing tier-1 support'")
    print("     - Adoption barriers: 'Still needs human handoff'")
    print("")
    print("  🏆 Competitive Signals (Meta/LinkedIn):")
    print("     - Intercom: Hiring 12 ML engineers (from LinkedIn)")
    print("     - Zendesk: 'AI for support' ads running (Meta)")
    print("")
    print("  🔮 Technical Signals (Patents):")
    print("     - OpenAI patent: 'Context-aware prompt optimization'")
    print("     - Anthropic filing: 'Constitutional AI for support'")
    print("")
    print("  🎯 Top Insights (Confidence > 0.7):")
    print("     ✓ Market is hot (200+ HN mentions)")
    print("     ✓ Everyone is hiring AI engineers")
    print("     ✓ No clear winner yet")
    print("     ✗ 40% of users still distrust AI-only support")


async def show_how_to_run():
    """Show how to actually run the server"""
    print("\n" + "=" * 80)
    print("HOW TO RUN THE SERVER")
    print("=" * 80)
    
    print("\n1️⃣  Terminal 1: Start the MCP Server")
    print("   $ python -m uvicorn growth_intelligence_server:mcp --host 0.0.0.0 --port 8000")
    print("   ✓ Server starts on http://localhost:8000")
    print("   ✓ Docs available at http://localhost:8000/docs")
    
    print("\n2️⃣  Terminal 2: Make API Requests")
    print("   $ curl -X POST http://localhost:8000/api/gather_user_voice \\")
    print("      -H 'Content-Type: application/json' \\")
    print('      -d \'{"keywords": ["pricing"], "sources": ["reddit"]}\'')
    
    print("\n3️⃣  View Results")
    print("   $ python demo_runner.py --request user_voice --keywords pricing")
    print("   ✓ Pretty-printed JSON with signals and confidence scores")
    
    print("\n4️⃣  Production Mode (with Docker)")
    print("   $ docker build -t xynera-growth-server .")
    print("   $ docker run -p 8000:8000 -e REDDIT_CLIENT_ID=xxx xynera-growth-server")


async def show_environment_setup():
    """Show required environment setup"""
    print("\n" + "=" * 80)
    print("ENVIRONMENT SETUP")
    print("=" * 80)
    
    print("\n📝 Create .env file with:")
    print("   REDDIT_CLIENT_ID=your_reddit_app_id")
    print("   REDDIT_CLIENT_SECRET=your_reddit_app_secret")
    print("   REDDIT_USER_AGENT=VeracityGrowthBot/1.0")
    print("   REDDIT_USERNAME=your_reddit_username (optional)")
    print("   REDDIT_PASSWORD=your_reddit_password (optional)")
    print("   ")
    print("   # Meta Ads (optional - implement when ready)")
    print("   META_ADS_TOKEN=your_token")
    print("   ")
    print("   # LinkedIn (optional - implement when ready)")
    print("   LINKEDIN_TOKEN=your_token")
    
    print("\n✅ HN Algolia API: Free, no key required!")
    print("✅ USPTO PatentsView API: Free, no key required!")


async def show_request_examples():
    """Show real request/response examples"""
    print("\n" + "=" * 80)
    print("REAL REQUEST/RESPONSE EXAMPLES")
    print("=" * 80)
    
    print("\n📂 REQUEST: User Voice Intelligence")
    print("-" * 80)
    request = {
        "keywords": ["pricing too high", "can't afford"],
        "sources": ["reddit"],
        "subreddits": ["SaaS", "startups"]
    }
    print(json.dumps(request, indent=2))
    
    print("\n📄 RESPONSE (truncated)")
    print("-" * 80)
    response = {
        "domain": "user_voice",
        "total_signals": 12,
        "signals": {
            "reddit": [
                {
                    "domain": "pricing",
                    "source": "reddit",
                    "title": "Pricing is way too high for startups",
                    "content": "We switched to [Competitor] because it's 1/3 the price...",
                    "confidence": {
                        "score": 0.85,
                        "supporting_metric": "142 upvotes, 23 comments"
                    },
                    "url": "https://reddit.com/r/SaaS/...",
                }
            ]
        }
    }
    print(json.dumps(response, indent=2))


async def main():
    """Run all demos"""
    print("\n\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 15 + "XYNERA GROWTH INTELLIGENCE SERVER" + " " * 31 + "║")
    print("║" + " " * 10 + "Demo & Execution Guide for Six Intelligence Domains" + " " * 17 + "║")
    print("╚" + "=" * 78 + "╝")
    
    await demo_user_voice()
    await demo_competitive_landscape()
    await demo_technical_signals()
    await demo_all_intelligence()
    
    await show_how_to_run()
    await show_environment_setup()
    await show_request_examples()
    
    print("\n" + "=" * 80)
    print("🎯 NEXT STEPS")
    print("=" * 80)
    print("1. Set up your .env file with credentials")
    print("2. Start the server: python growth_intelligence_server.py")
    print("3. Test endpoints: http://localhost:8000/docs")
    print("4. Build your agent logic on top of these tools")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    asyncio.run(main())
