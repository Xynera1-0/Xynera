"""LangGraph workflow orchestrator for competitive intelligence"""

import logging
from typing import Dict, Any, List
from datetime import datetime
from langgraph.graph import StateGraph, END
from app.models.state import OrchestratorState, Subtask, TaskStatus

logger = logging.getLogger(__name__)


# Define the workflow input/output schema
class WorkflowInput:
    """Input to the workflow"""
    def __init__(self, state: OrchestratorState):
        self.state = state


async def validate_input(state: OrchestratorState) -> OrchestratorState:
    """
    Node 1: Validate and enrich the incoming request
    - Check required fields
    - Add timestamps
    - Validate query format
    """
    logger.info(f"[Node 1] Validating input for request {state.request_id}")

    if not state.user_query or len(state.user_query.strip()) < 3:
        state.error_message = "Query too short or empty"
        state.status = TaskStatus.FAILED
        return state

    state.started_at = datetime.utcnow()
    state.status = TaskStatus.IN_PROGRESS
    logger.debug(f"Input validation successful for {state.request_id}")

    return state


async def decompose_task(state: OrchestratorState) -> OrchestratorState:
    """
    Node 2: Decompose the user query into subtasks
    - Analyze user query
    - Create subtasks for each agent type
    - Assign priorities and context
    """
    if state.status == TaskStatus.FAILED:
        return state

    logger.info(f"[Node 2] Decomposing task for request {state.request_id}")

    # Define the 6 agent types and their focus areas
    agent_configurations = {
        "market_trend": {
            "prompt": "Identify market trends and leading indicators",
            "priority": 1,
        },
        "competitive_landscape": {
            "prompt": "Analyze competitive landscape and feature bets",
            "priority": 1,
        },
        "win_loss": {
            "prompt": "Analyze deal losses and buyer perspective",
            "priority": 2,
        },
        "pricing": {
            "prompt": "Evaluate pricing models and willingness-to-pay",
            "priority": 2,
        },
        "messaging": {
            "prompt": "Identify positioning and messaging gaps",
            "priority": 2,
        },
        "adjacent_market": {
            "prompt": "Detect adjacent market opportunities and threats",
            "priority": 3,
        },
    }

    # Create subtasks for each agent
    state.subtasks = [
        Subtask(
            agent_type=agent_type,
            query=state.user_query,
            context={
                "focus": config["prompt"],
                "user_metadata": state.user_metadata,
                "session_id": state.session_id,
            },
            priority=config["priority"],
        )
        for agent_type, config in agent_configurations.items()
    ]

    logger.info(f"Created {len(state.subtasks)} subtasks for request {state.request_id}")

    return state


async def dispatch_to_agents(state: OrchestratorState) -> OrchestratorState:
    """
    Node 3: Dispatch subtasks to the agent pool
    - Route each subtask to appropriate agent
    - Execute agents in parallel
    - Collect results with timeout handling
    """
    if state.status == TaskStatus.FAILED or not state.subtasks:
        return state

    logger.info(f"[Node 3] Dispatching {len(state.subtasks)} subtasks for request {state.request_id}")

    # Import agent implementations (lazy import to avoid circular imports)
    from app.agents.market_trend_agent import market_trend_agent
    from app.agents.competitive_landscape_agent import competitive_landscape_agent
    from app.agents.win_loss_agent import win_loss_agent
    from app.agents.pricing_agent import pricing_agent
    from app.agents.messaging_agent import messaging_agent
    from app.agents.adjacent_market_agent import adjacent_market_agent

    # Map agent types to their implementations
    agent_map = {
        "market_trend": market_trend_agent,
        "competitive_landscape": competitive_landscape_agent,
        "win_loss": win_loss_agent,
        "pricing": pricing_agent,
        "messaging": messaging_agent,
        "adjacent_market": adjacent_market_agent,
    }

    # Execute agents in parallel
    import asyncio
    import time

    async def execute_agent(subtask: Subtask) -> tuple[str, Any]:
        """Execute a single agent with timeout"""
        from app.config import get_settings

        settings = get_settings()
        try:
            start_time = time.time()
            agent_func = agent_map.get(subtask.agent_type)
            if not agent_func:
                logger.error(f"Unknown agent type: {subtask.agent_type}")
                return subtask.agent_type, None

            # Execute agent with timeout
            result = await asyncio.wait_for(
                agent_func(subtask.query, subtask.context),
                timeout=settings.AGENT_TIMEOUT_SECONDS
            )
            elapsed_ms = (time.time() - start_time) * 1000
            result.processing_time_ms = elapsed_ms
            return subtask.agent_type, result
        except asyncio.TimeoutError:
            logger.error(f"Agent {subtask.agent_type} timed out for request {state.request_id}")
            return subtask.agent_type, None
        except Exception as e:
            logger.error(f"Agent {subtask.agent_type} failed: {str(e)}")
            return subtask.agent_type, None

    # Run all agents concurrently
    tasks = [execute_agent(subtask) for subtask in state.subtasks]
    results = await asyncio.gather(*tasks)

    # Collect results
    for agent_type, output in results:
        if output:
            state.agent_outputs[agent_type] = output
            logger.info(f"Agent {agent_type} completed with confidence {output.confidence_score}")
        else:
            logger.warning(f"Agent {agent_type} produced no output")

    logger.info(f"Agent dispatch complete: {len(state.agent_outputs)}/{len(state.subtasks)} agents succeeded")

    return state


async def aggregate_results(state: OrchestratorState) -> OrchestratorState:
    """
    Node 4: Aggregate results from all agents
    - Combine findings from all agents
    - Calculate overall confidence
    - Identify key insights and contradictions
    """
    if state.status == TaskStatus.FAILED:
        return state

    logger.info(f"[Node 4] Aggregating results for request {state.request_id}")

    if not state.agent_outputs:
        state.error_message = "No agent outputs to aggregate"
        state.status = TaskStatus.FAILED
        return state

    # Aggregate insights
    aggregated = {
        "all_facts": [],
        "top_sources": [],
        "agent_summaries": {},
        "confidence_by_agent": {},
        "high_confidence_facts": [],
        "agent_analyses": {},
    }

    # Collect facts and sources
    for agent_type, output in state.agent_outputs.items():
        aggregated["agent_summaries"][agent_type] = {
            "fact_count": len(output.facts),
            "source_count": len(output.sources),
            "confidence": output.confidence_score,
        }
        aggregated["confidence_by_agent"][agent_type] = output.confidence_score

        aggregated["all_facts"].extend(output.facts)

        # Store each agent's full analysis text
        if output.raw_analysis:
            aggregated["agent_analyses"][agent_type] = output.raw_analysis

        # Add high confidence facts
        if output.confidence_score >= 0.6:
            aggregated["high_confidence_facts"].extend(
                [f"{fact} (Agent: {agent_type}, Conf: {output.confidence_score:.0%})" for fact in output.facts]
            )

        # Collect top sources (skip empty URLs)
        for src in output.sources[:5]:
            if src.get("url"):
                aggregated["top_sources"].append(src)

    # Deduplicate sources by URL
    seen_urls = set()
    unique_sources = []
    for src in aggregated["top_sources"]:
        url = src.get("url", "")
        if url and url not in seen_urls:
            seen_urls.add(url)
            unique_sources.append(src)
    aggregated["top_sources"] = unique_sources[:10]

    # Calculate overall confidence
    confidences = [o.confidence_score for o in state.agent_outputs.values() if o.confidence_score > 0]
    if confidences:
        state.final_confidence = sum(confidences) / len(confidences)
    else:
        state.final_confidence = 0.0

    state.aggregated_insights = aggregated
    state.status = TaskStatus.COMPLETED

    logger.info(f"Aggregation complete: {len(aggregated['all_facts'])} total facts, "
                f"confidence: {state.final_confidence:.2f}")

    return state


async def trigger_synthesis(state: OrchestratorState) -> OrchestratorState:
    """
    Node 5: Synthesize a narrative summary from all agent findings
    - Use LLM to create a cohesive analysis
    - Add metadata for the presentation layer
    """
    if state.status == TaskStatus.FAILED:
        return state

    logger.info(f"[Node 5] Synthesizing results for request {state.request_id}")

    state.completed_at = datetime.utcnow()

    if state.aggregated_insights:
        # Build context from agent analyses for the synthesis LLM call
        agent_analyses = state.aggregated_insights.get("agent_analyses", {})
        all_facts = state.aggregated_insights.get("all_facts", [])

        synthesis_context = ""
        for agent_type, analysis in agent_analyses.items():
            synthesis_context += f"\n### {agent_type.replace('_', ' ').title()} Agent:\n{analysis[:800]}\n"

        if not synthesis_context and all_facts:
            synthesis_context = "\nKey findings:\n" + "\n".join(f"- {f}" for f in all_facts[:20])

        # Generate narrative summary via LLM
        summary = ""
        if synthesis_context:
            try:
                from app.services.llm_client import query_llm

                summary_prompt = f"""Based on the following competitive intelligence research about "{state.user_query}", write a clear, actionable executive summary.

{synthesis_context}

Write 2-4 paragraphs that:
1. Highlight the most important findings across all analysis areas
2. Identify key patterns, opportunities, and risks
3. Provide actionable recommendations

Be concise and data-driven. Do NOT use markdown headers — just write flowing paragraphs."""

                summary = await query_llm(
                    summary_prompt,
                    system_prompt="You are a senior competitive intelligence analyst writing an executive briefing.",
                    temperature=0.4,
                )
                logger.info(f"Generated synthesis summary ({len(summary)} chars)")
            except Exception as e:
                logger.error(f"Synthesis LLM call failed: {e}")
                # Fallback: use top facts as summary
                if all_facts:
                    summary = "Key findings from analysis:\n\n" + "\n".join(f"• {f}" for f in all_facts[:10])

        state.aggregated_insights["summary"] = summary

        # Remove raw agent analyses from the final output to reduce payload size
        state.aggregated_insights.pop("agent_analyses", None)

        # Add metadata
        state.aggregated_insights["request_metadata"] = {
            "request_id": state.request_id,
            "user_id": state.user_id,
            "session_id": state.session_id,
            "original_query": state.user_query,
            "timestamp": state.timestamp.isoformat(),
            "processing_time_ms": (
                (state.completed_at - state.started_at).total_seconds() * 1000
                if state.started_at
                else 0
            ),
            "final_confidence": state.final_confidence,
            "agents_used": list(state.agent_outputs.keys()),
        }

    logger.info(f"Synthesis complete for request {state.request_id}")

    return state


def build_workflow():
    """Build and compile the LangGraph workflow"""
    logger.info("Building orchestrator workflow graph")

    # Create state graph
    workflow = StateGraph(OrchestratorState)

    # Add nodes
    workflow.add_node("validate_input", validate_input)
    workflow.add_node("decompose_task", decompose_task)
    workflow.add_node("dispatch_to_agents", dispatch_to_agents)
    workflow.add_node("aggregate_results", aggregate_results)
    workflow.add_node("trigger_synthesis", trigger_synthesis)

    # Add edges (linear flow for now, can add conditional edges later)
    workflow.set_entry_point("validate_input")
    workflow.add_edge("validate_input", "decompose_task")
    workflow.add_edge("decompose_task", "dispatch_to_agents")
    workflow.add_edge("dispatch_to_agents", "aggregate_results")
    workflow.add_edge("aggregate_results", "trigger_synthesis")
    workflow.add_edge("trigger_synthesis", END)

    # Compile workflow
    compiled_workflow = workflow.compile()

    logger.info("Workflow graph compiled successfully")

    return compiled_workflow


# Global workflow instance
_workflow = None


def get_workflow():
    """Get or create the compiled workflow"""
    global _workflow
    if _workflow is None:
        _workflow = build_workflow()
    return _workflow


async def execute_workflow(state: OrchestratorState) -> OrchestratorState:
    """Execute the workflow on the given state"""
    workflow = get_workflow()

    logger.info(f"Executing workflow for request {state.request_id}")

    # LangGraph 0.2+ expects a dict matching the state schema fields
    result = await workflow.ainvoke(state.model_dump())

    logger.info(f"Workflow execution complete for request {state.request_id}")

    # Result is a dict of state fields — reconstruct the Pydantic model
    if isinstance(result, dict):
        return OrchestratorState(**result)
    return result
