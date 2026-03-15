"""Main entry point for running Xynera orchestrator"""

import logging
import sys
import asyncio
from app.config import get_settings
from app.agents.orchestrator_instances import OrchestratorPool

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def main():
    """Main entry point"""
    logger.info("Starting Xynera Orchestrator")

    try:
        # Load settings
        settings = get_settings()
        logger.info(f"Configuration loaded:")
        logger.info(f"  Redis: {settings.redis_host}:{settings.redis_port}")
        logger.info(f"  MCP Mode: {settings.mcp_mode}")
        logger.info(f"  Orchestrators: {settings.num_orchestrators}")

        # Start orchestrator pool
        pool = OrchestratorPool(settings.num_orchestrators)
        logger.info(f"Orchestrator pool created with {settings.num_orchestrators} instances")

        # Run orchestrators
        asyncio.run(pool.start_all())

    except KeyboardInterrupt:
        logger.info("Orchestrator interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Orchestrator failed: {str(e)}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
