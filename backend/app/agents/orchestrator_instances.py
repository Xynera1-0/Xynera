"""Two parallel orchestrator instances"""

import logging
import asyncio
import signal
from typing import List
from app.agents.orchestrator import Orchestrator

logger = logging.getLogger(__name__)


class OrchestratorPool:
    """
    Manages multiple orchestrator instances running in parallel
    Each orchestrator listens to the same Redis queue
    """

    def __init__(self, num_orchestrators: int = 2):
        """
        Initialize orchestrator pool
        Args:
            num_orchestrators: Number of parallel orchestrators to run
        """
        self.num_orchestrators = num_orchestrators
        self.orchestrators: List[Orchestrator] = [
            Orchestrator(f"orchestrator-{i}") for i in range(num_orchestrators)
        ]
        self.logger = logging.getLogger("orchestrator.pool")
        self._shutdown = False

    async def start_all(self):
        """Start all orchestrators in parallel"""
        self.logger.info(f"Starting orchestrator pool with {self.num_orchestrators} instances")

        # Set up signal handlers for graceful shutdown
        loop = asyncio.get_event_loop()
        for sig in (signal.SIGTERM, signal.SIGINT):
            loop.add_signal_handler(sig, self._handle_shutdown)

        try:
            # Run all orchestrators concurrently
            tasks = [orch.start() for orch in self.orchestrators]
            await asyncio.gather(*tasks)

        except Exception as e:
            self.logger.error(f"Orchestrator pool error: {str(e)}", exc_info=True)
        finally:
            await self.stop_all()

    async def stop_all(self):
        """Stop all orchestrators gracefully"""
        self.logger.info("Stopping all orchestrators")
        self._shutdown = True

        tasks = [orch.stop() for orch in self.orchestrators]
        await asyncio.gather(*tasks, return_exceptions=True)

        self.logger.info("All orchestrators stopped")

    def _handle_shutdown(self):
        """Handle shutdown signal"""
        self.logger.info("Shutdown signal received")
        # Schedule stop_all to run in the event loop
        asyncio.create_task(self.stop_all())

    def get_stats(self) -> dict:
        """Get statistics for all orchestrators"""
        return {
            "total_orchestrators": self.num_orchestrators,
            "orchestrators": [orch.get_stats() for orch in self.orchestrators],
        }


async def create_and_start_orchestrators(num_orchestrators: int = 2):
    """
    Convenience function to create and start orchestrator pool
    Usage: asyncio.run(create_and_start_orchestrators(2))
    """
    pool = OrchestratorPool(num_orchestrators)
    await pool.start_all()


# Convenience references to the two default orchestrators
def get_orchestrator_instances() -> tuple[Orchestrator, Orchestrator]:
    """Get the two default orchestrator instances"""
    orchestrator_1 = Orchestrator("orchestrator-1")
    orchestrator_2 = Orchestrator("orchestrator-2")
    return orchestrator_1, orchestrator_2


if __name__ == "__main__":
    # Example: Run two orchestrators
    import sys

    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    logger.info("Starting Xynera orchestrator pool")

    try:
        # Create pool with 2 orchestrators
        num_orchestrators = int(sys.argv[1]) if len(sys.argv) > 1 else 2
        asyncio.run(create_and_start_orchestrators(num_orchestrators))
    except KeyboardInterrupt:
        logger.info("Orchestrator pool interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Failed to start orchestrator pool: {str(e)}")
        sys.exit(1)
