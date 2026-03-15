"""Test MCP Server connection."""

import asyncio
import logging
import sys
from pathlib import Path

# Add backend to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from app.services.mcp_client import ServerMCPClient, get_mcp_client
from app.config import get_settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_mcp_server_connection():
    """Test connection to actual MCP server."""
    logger.info("=" * 60)
    logger.info("Testing MCP SERVER Connection")
    logger.info("=" * 60)

    settings = get_settings()
    mcp_server_url = getattr(settings, 'MCP_SERVER_URL', 'http://localhost:8000/mcp')
    mcp_mode = getattr(settings, 'MCP_MODE', 'mock')

    logger.info(f"\nMCP Server URL: {mcp_server_url}")
    logger.info(f"MCP Mode: {mcp_mode}")

    try:
        # Create server client
        client = ServerMCPClient(mcp_server_url=mcp_server_url)
        logger.info("✓ ServerMCPClient created")

        # Test a simple query
        logger.info("\nTesting web search...")
        results = await client.search_web("artificial intelligence", num_results=3)
        logger.info(f"✓ Web search returned {len(results)} results")
        if results:
            logger.info(f"  First result: {results[0].get('title', 'N/A')[:50]}")

        # Test news search
        logger.info("\nTesting news search...")
        news = await client.search_news("AI market trends", num_results=2)
        logger.info(f"✓ News search returned {len(news)} results")

        # Test trends
        logger.info("\nTesting trends...")
        trends = await client.search_trends("AI", num_results=3)
        logger.info(f"✓ Trends returned {len(trends)} data points")

        # Close client
        await client.close()
        logger.info("\n✅ MCP Server connection successful!")

    except Exception as e:
        logger.error(f"❌ MCP Server connection failed: {str(e)}")
        import traceback
        traceback.print_exc()


async def test_factory():
    """Test the MCP client factory with server mode."""
    logger.info("\n" + "=" * 60)
    logger.info("Testing MCP Client Factory (Server Mode)")
    logger.info("=" * 60)

    client = get_mcp_client()
    client_type = type(client).__name__

    logger.info(f"Factory returned: {client_type}")

    if client_type == "ServerMCPClient":
        logger.info("✓ Correctly using ServerMCPClient")
    else:
        logger.warning(f"⚠️  Expected ServerMCPClient but got {client_type}")


async def main():
    """Run all tests."""
    logger.info("\n" + "🚀 MCP SERVER INTEGRATION TEST 🚀".center(60))

    try:
        # Test factory
        await test_factory()

        # Test server connection
        await test_mcp_server_connection()

        logger.info("\n" + "=" * 60)
        logger.info("✅ MCP SERVER TESTS COMPLETED!")
        logger.info("=" * 60)

    except Exception as e:
        logger.error(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
