"""Command-line interface for Xynera"""

import logging
import typer
import asyncio
from typing import Optional
import sys
from rich.console import Console
from rich.table import Table
from datetime import datetime
import uuid
from app.config import get_settings
from app.models.state import OrchestratorState
from app.agents.orchestrator_instances import OrchestratorPool
from app.services.queue_manager import get_queue_manager

app = typer.Typer()
console = Console()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@app.command()
def test_query(
    query: str = typer.Option(
        ...,
        "--query",
        "-q",
        help="The query to test",
    ),
    user_id: str = typer.Option(
        "test_user",
        "--user-id",
        "-u",
        help="User ID",
    ),
    session_id: Optional[str] = typer.Option(
        None,
        "--session-id",
        "-s",
        help="Session ID (auto-generated if not provided)",
    ),
):
    """Test a query through the orchestrator workflow"""
    console.print(f"[bold blue]Testing Query:[/bold blue] {query}", style="bold")

    try:
        settings = get_settings()
        console.print(f"[green]✓[/green] Settings loaded")

        # Create an orchestrator state
        state = OrchestratorState(
            user_id=user_id,
            session_id=session_id or str(uuid.uuid4()),
            request_id=f"test-{datetime.utcnow().isoformat()}",
            user_query=query,
            timestamp=datetime.utcnow(),
        )

        console.print(f"[green]✓[/green] State created (request_id: {state.request_id})")

        # Execute workflow
        from app.agents.orchestrator import Orchestrator

        orchestrator = Orchestrator("test-orchestrator")
        console.print("[cyan]Executing workflow...[/cyan]")

        result_state = asyncio.run(orchestrator.process_state(state))

        # Display results
        console.print("\n[bold green]Execution Results:[/bold green]")

        result_table = Table(title="Agent Results")
        result_table.add_column("Agent Type", style="cyan")
        result_table.add_column("Facts", style="green")
        result_table.add_column("Confidence", style="yellow")
        result_table.add_column("Status", style="magenta")

        for agent_type, output in result_state.agent_outputs.items():
            status = "✓ Done" if output.confidence_score > 0 else "✗ Failed"
            result_table.add_row(
                agent_type,
                str(len(output.facts)),
                f"{output.confidence_score:.2f}",
                status,
            )

        console.print(result_table)

        # Display summary
        console.print(f"\n[bold cyan]Summary:[/bold cyan]")
        console.print(f"  Status: {result_state.status}")
        console.print(f"  Overall Confidence: {result_state.final_confidence:.2f}")
        console.print(f"  Agents Executed: {len(result_state.agent_outputs)}")
        console.print(f"  Total Facts Gathered: {sum(len(o.facts) for o in result_state.agent_outputs.values())}")

        if result_state.aggregated_insights:
            console.print(f"  Top Sources: {len(result_state.aggregated_insights.get('top_sources', []))}")

    except Exception as e:
        console.print(f"[red]✗ Error:[/red] {str(e)}", style="bold red")
        logger.error(f"Test query failed: {str(e)}", exc_info=True)
        sys.exit(1)


@app.command()
def start_orchestrators(
    num_orchestrators: int = typer.Option(
        2,
        "--num",
        "-n",
        help="Number of orchestrator instances to start",
    ),
):
    """Start the orchestrator pool"""
    console.print(
        f"[bold blue]Starting Orchestrator Pool[/bold blue] ({num_orchestrators} instances)",
        style="bold",
    )

    try:
        settings = get_settings()
        console.print(f"[green]✓[/green] Settings loaded")
        console.print(f"  Redis: {settings.redis_host}:{settings.redis_port}")
        console.print(f"  MCP Mode: {settings.mcp_mode}")

        pool = OrchestratorPool(num_orchestrators)
        console.print(f"[green]✓[/green] Orchestrator pool created")

        console.print("[cyan]Starting all orchestrators...[/cyan]")
        console.print("[yellow]Press Ctrl+C to stop[/yellow]")

        asyncio.run(pool.start_all())

    except KeyboardInterrupt:
        console.print("\n[yellow]Orchestrator pool stopped[/yellow]")
    except Exception as e:
        console.print(f"[red]✗ Error:[/red] {str(e)}", style="bold red")
        logger.error(f"Failed to start orchestrators: {str(e)}", exc_info=True)
        sys.exit(1)


@app.command()
def queue_stats():
    """Display queue statistics"""
    console.print("[bold blue]Queue Statistics[/bold blue]", style="bold")

    try:
        queue_manager = get_queue_manager()
        stats = queue_manager.get_job_count_by_status()

        table = Table(title="Queue Status")
        table.add_column("Status", style="cyan")
        table.add_column("Count", style="green")

        total = 0
        for status, count in stats.items():
            table.add_row(status.capitalize(), str(count))
            total += count

        table.add_row("[bold]Total[/bold]", f"[bold]{total}[/bold]")
        console.print(table)

    except Exception as e:
        console.print(f"[red]✗ Error:[/red] {str(e)}", style="bold red")
        sys.exit(1)


@app.command()
def health_check():
    """Check system health"""
    console.print("[bold blue]Health Check[/bold blue]", style="bold")

    checks = []

    # Check settings
    try:
        settings = get_settings()
        checks.append(("Settings", True, "Loaded successfully"))
    except Exception as e:
        checks.append(("Settings", False, str(e)))

    # Check Redis
    try:
        queue_manager = get_queue_manager()
        stats = queue_manager.get_job_count_by_status()
        checks.append(("Redis Connection", True, "Connected"))
    except Exception as e:
        checks.append(("Redis Connection", False, str(e)))

    # Check MCP
    try:
        from app.services.mcp_client import get_mcp_client

        mcp = get_mcp_client()
        mode = "Mock" if mcp.__class__.__name__ == "MockMCPClient" else "Real"
        checks.append(("MCP Client", True, f"Ready ({mode})"))
    except Exception as e:
        checks.append(("MCP Client", False, str(e)))

    # Display results
    console.print()
    for check_name, passed, message in checks:
        status = "[green]✓[/green]" if passed else "[red]✗[/red]"
        console.print(f"{status} {check_name}: {message}")

    # Overall status
    all_passed = all(check[1] for check in checks)
    console.print()
    if all_passed:
        console.print("[green bold]✓ All systems operational[/green bold]")
    else:
        console.print("[red bold]✗ Some systems have issues[/red bold]")
        sys.exit(1)


@app.command()
def show_config():
    """Show current configuration"""
    console.print("[bold blue]Configuration[/bold blue]", style="bold")

    try:
        settings = get_settings()

        config_table = Table()
        config_table.add_column("Setting", style="cyan")
        config_table.add_column("Value", style="green")

        config_table.add_row("Redis Host", settings.redis_host)
        config_table.add_row("Redis Port", str(settings.redis_port))
        config_table.add_row("MCP Mode", settings.mcp_mode)
        config_table.add_row("MCP Server URL", settings.mcp_server_url)
        config_table.add_row("Orchestrators", str(settings.num_orchestrators))
        config_table.add_row("Agent Timeout", f"{settings.agent_timeout_seconds}s")
        config_table.add_row("Log Level", settings.log_level)
        config_table.add_row("Debug", str(settings.debug))

        console.print(config_table)

    except Exception as e:
        console.print(f"[red]✗ Error:[/red] {str(e)}", style="bold red")
        sys.exit(1)


if __name__ == "__main__":
    app()
