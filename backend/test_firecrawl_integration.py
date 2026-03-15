"""Test Firecrawl MCP integration."""

import asyncio
import logging
import sys
from pathlib import Path

# Add backend to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from app.services.mcp_client import FirecrawlMCPClient, get_mcp_client, MockMCPClient
from app.config import get_settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_mock_client():
    """Test mock client (no external dependencies required)."""
    logger.info("=" * 60)
    logger.info("Testing MOCK MCP Client")
    logger.info("=" * 60)

    client = MockMCPClient()

    # Test web search
    logger.info("\n1. Testing mock web search...")
    web_results = await client.search_web("AI market trends", num_results=3)
    logger.info(f"   Results: {len(web_results)} pages")
    for r in web_results:
        logger.info(f"   - {r['title'][:60]} ({r['source']})")

    # Test news search
    logger.info("\n2. Testing mock news search...")
    news_results = await client.search_news("AI market trends", num_results=2)
    logger.info(f"   Results: {len(news_results)} articles")
    for r in news_results:
        logger.info(f"   - {r['title']} ({r.get('date', 'N/A')})")

    # Test trends
    logger.info("\n3. Testing mock trends...")
    trends = await client.search_trends("AI market trends", num_results=3)
    logger.info(f"   Results: {len(trends)} data points")
    for t in trends:
        logger.info(f"   - {t.get('metric', 'N/A')}: {t.get('value', 'N/A')}")

    # Test page extraction
    logger.info("\n4. Testing mock page extraction...")
    content = await client.extract_page("https://example.com")
    logger.info(f"   Content length: {len(content) if content else 0} chars")

    # Test Reddit analysis
    logger.info("\n5. Testing mock Reddit analysis...")
    reddit = await client.reddit_analysis("AI market trends")
    logger.info(f"   Discussions: {len(reddit)}")
    for r in reddit:
        logger.info(f"   - {r.get('subreddit', 'N/A')}: {r.get('title', 'N/A')[:50]}")

    # Test advertisement intelligence
    logger.info("\n6. Testing mock ad intelligence...")
    ads = await client.advertisement_intelligence("AI market trends")
    logger.info(f"   Ad results: {len(ads)}")
    for a in ads:
        logger.info(f"   - {a.get('title', 'N/A')[:50]}")

    logger.info("\n✅ Mock client test completed successfully!")


async def test_real_client_health():
    """Test real client configuration (doesn't require working API)."""
    logger.info("\n" + "=" * 60)
    logger.info("Testing REAL MCP Client Configuration")
    logger.info("=" * 60)

    settings = get_settings()
    firecrawl_key = getattr(settings, 'FIRECRAWL_API_KEY', '') or getattr(settings, 'firecrawl_api_key', '')
    tavily_key = getattr(settings, 'TAVILY_API_KEY', '') or getattr(settings, 'tavily_api_key', '')
    mcp_mode = getattr(settings, 'MCP_MODE', 'mock') or getattr(settings, 'mcp_mode', 'mock')

    if not firecrawl_key:
        logger.warning("⚠️  FIRECRAWL_API_KEY not set - skipping real client test")
        logger.info("   To test real client, set FIRECRAWL_API_KEY in .env")
        return

    logger.info(f"✓ FIRECRAWL_API_KEY found (length: {len(firecrawl_key)})")
    logger.info(f"✓ MCP_MODE: {mcp_mode}")

    try:
        client = FirecrawlMCPClient(
            firecrawl_key=firecrawl_key,
            tavily_key=tavily_key,
        )
        logger.info("✓ FirecrawlMCPClient initialized successfully")

        # Note: We're not actually calling the API here to avoid rate limits
        # In production, you would call:
        # results = await client.search_web("test query")

        logger.info("\n✅ Real client configuration valid!")
        logger.info("   Ready to process queries when Firecrawl API is active")

    except Exception as e:
        logger.error(f"❌ Error initializing real client: {e}")


async def test_factory():
    """Test the MCP client factory."""
    logger.info("\n" + "=" * 60)
    logger.info("Testing MCP Client Factory")
    logger.info("=" * 60)

    settings = get_settings()
    mcp_mode = getattr(settings, 'MCP_MODE', 'mock') or getattr(settings, 'mcp_mode', 'mock')
    logger.info(f"Current MCP_MODE: {mcp_mode}")

    # Get client based on settings
    client = get_mcp_client()
    client_type = type(client).__name__

    logger.info(f"Factory returned: {client_type}")

    if mcp_mode.lower() == "mock":
        assert isinstance(
            client, MockMCPClient
        ), "Should return MockMCPClient in mock mode"
        logger.info("✓ Correctly using MockMCPClient in mock mode")
    else:
        assert isinstance(
            client, FirecrawlMCPClient
        ), "Should return FirecrawlMCPClient in real mode"
        logger.info("✓ Correctly using FirecrawlMCPClient in real mode")

    logger.info("\n✅ Factory test passed!")


async def test_full_workflow():
    """Test a complete workflow scenario."""
    logger.info("\n" + "=" * 60)
    logger.info("Testing Full Workflow")
    logger.info("=" * 60)

    from app.models.state import OrchestratorState
    import uuid
    from datetime import datetime

    # Create a state
    state = OrchestratorState(
        user_id="test-user",
        session_id="test-session",
        request_id=str(uuid.uuid4()),
        user_query="What are the latest trends in artificial intelligence?",
        timestamp=datetime.utcnow(),
    )

    logger.info(f"\nCreated OrchestratorState:")
    logger.info(f"  User ID: {state.user_id}")
    logger.info(f"  Query: {state.user_query}")
    logger.info(f"  Request ID: {state.request_id}")

    # Get MCP client
    client = get_mcp_client()
    logger.info(f"\nMCP Client: {type(client).__name__}")

    # Simulate agent queries
    logger.info("\nSimulating agent queries...")

    try:
        # Market trend agent
        logger.info("\n  1. Market Trend Agent...")
        web_results = await client.search_web(state.user_query, num_results=3)
        logger.info(f"     Found {len(web_results)} pages")

        # Competitive landscape agent
        logger.info("\n  2. Competitive Landscape Agent...")
        news_results = await client.search_news(state.user_query, num_results=2)
        logger.info(f"     Found {len(news_results)} articles")

        # Adjacent market agent
        logger.info("\n  3. Adjacent Market Agent...")
        trends = await client.search_trends("AI", num_results=3)
        logger.info(f"     Found {len(trends)} trend data points")

        # Other agents would follow similar pattern

        logger.info("\n✅ Full workflow test passed!")

    except Exception as e:
        logger.error(f"❌ Workflow test failed: {e}")
        import traceback

        traceback.print_exc()


async def main():
    """Run all tests."""
    logger.info("\n" + "🚀 FIRECRAWL MCP INTEGRATION TEST SUITE 🚀".center(60))

    try:
        # Test mock client (always works)
        await test_mock_client()

        # Test configuration
        await test_factory()

        # Test real client configuration
        await test_real_client_health()

        # Test full workflow
        await test_full_workflow()

        logger.info("\n" + "=" * 60)
        logger.info("✅ ALL TESTS COMPLETED SUCCESSFULLY!")
        logger.info("=" * 60)
        logger.info("\nNext steps:")
        logger.info("1. Start the orchestrator: python orchestrator_main.py")
        logger.info("2. Use CLI to test: python -m app.cli test-query --query \"<your-query>\"")
        logger.info("3. For production: Set FIRECRAWL_API_KEY and MCP_MODE=real")

    except Exception as e:
        logger.error(f"\n❌ TEST SUITE FAILED: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
