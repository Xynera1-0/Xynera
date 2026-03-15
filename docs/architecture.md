"""
Xynera: Distributed Multi-Agent Competitive Intelligence Platform
=================================================================

A LangGraph-based multi-agent system for real-time competitive intelligence gathering.

## Architecture Overview

```
User Query
    ↓
Authentication Layer (handled by team)
    ↓
API Layer (handled by team)
    ↓
Redis Queue
    ↓
Orchestrator Agent 1 → LangGraph Workflow
Orchestrator Agent 2 ↗
    ├─ Input Validator
    ├─ Task Decomposer
    ├─ Agent Dispatcher (parallel execution)
    │   ├─ Market Trend Sensing Agent
    │   ├─ Competitive Landscape Agent
    │   ├─ Win/Loss Intelligence Agent
    │   ├─ Pricing & Packaging Agent
    │   ├─ Positioning & Messaging Agent
    │   └─ Adjacent Market Collision Agent
    ├─ Result Aggregator
    └─ Synthesis Trigger
        ↓
Data Layer & Synthesis (handled by team)
    ↓
Frontend Presentation
```

## Key Components

### 1. Orchestrator Agents (Two Parallel Instances)
- **Location**: `src/agents/orchestrator.py`, `src/agents/orchestrator_instances.py`
- **Purpose**: Listen to Redis queue, execute workflows
- **Scaling**: Horizontal scaling via additional workers
- **Tech**: Asyncio for concurrency

### 2. LangGraph Workflow
- **Location**: `src/workflows/orchestrator_workflow.py`
- **Nodes**:
  1. **validate_input**: Validates query and metadata
  2. **decompose_task**: Breaks query into 6 subtasks
  3. **dispatch_to_agents**: Routes to agent pool (parallel)
  4. **aggregate_results**: Combines insights
  5. **trigger_synthesis**: Prepares for downstream processing

### 3. Agent Pool (6 Specialized Agents)
- **Market Trend Agent**: Identifies market direction and indicators
- **Competitive Landscape Agent**: Analyzes competitors and feature bets
- **Win/Loss Agent**: Analyzes deal losses and buyer perspective
- **Pricing Agent**: Evaluates pricing models and willingness-to-pay
- **Messaging Agent**: Identifies positioning and messaging gaps
- **Adjacent Market Agent**: Detects external threats and opportunities

**All agents inherit from BaseAgent and execute in parallel.**

### 4. MCP Integration
- **Location**: `src/services/mcp_client.py`
- **Modes**:
  - **Real**: Calls actual MCP server
  - **Mock**: Predefined responses for development/testing
- **Tools**: Web search, page extraction, Reddit analysis, ad intelligence

### 5. LLM Integration
- **Provider**: Google Gemini
- **Location**: `src/services/llm_client.py`
- **Integration**: LangChain's ChatGoogleGenerativeAI

## Setup & Installation

### Prerequisites
- Python 3.10+
- Redis (for production)
- Google Gemini API key

### Installation Steps

1. **Create virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment**:
   ```bash
   cp .env.example .env
   # Edit .env and add:
   # - GOOGLE_API_KEY=your_key_here
   # - REDIS_HOST=localhost (or your Redis server)
   # - MCP_MODE=mock (or real if MCP server is ready)
   ```

4. **Verify setup**:
   ```bash
   python -m src.cli health-check
   ```

## Usage

### 1. Test a Query (Local Development)

```bash
python -m src.cli test-query --query "What are the AI market trends?" --user-id demo_user
```

**Output**:
- Agent execution results
- Confidence scores
- Total facts gathered
- Sources cited

### 2. Run Orchestrator Service

```bash
# Start with 2 orchestrators
python -m src.cli start-orchestrators --num 2

# Or use the main entry point
python -m src.orchestrator_main
```

### 3. Monitor Queue Status

```bash
python -m src.cli queue-stats
```

### 4. import and Use Programmatically

```python
import asyncio
from LangGraph_workflow.workflow import execute_competitive_intelligence
from src.models.state import OrchestratorState
from datetime import datetime
import uuid

async def main():
    state = OrchestratorState(
        user_id="user123",
        session_id=str(uuid.uuid4()),
        request_id="req-001",
        user_query="Analyze SaaS market trends",
        timestamp=datetime.utcnow(),
    )

    result = await execute_competitive_intelligence(state)

    print(f"Status: {result.status}")
    print(f"Confidence: {result.final_confidence}")
    print(f"Agents: {list(result.agent_outputs.keys())}")
    print(f"Insights: {result.aggregated_insights}")

asyncio.run(main())
```

## Configuration

### Environment Variables

```
# LLM Configuration
GOOGLE_API_KEY=your_key          # Required: Google Gemini API key

# Redis Configuration
REDIS_HOST=localhost             # Redis server host
REDIS_PORT=6379                  # Redis server port
REDIS_DB=0                        # Redis database number
REDIS_PASSWORD=                   # Optional: Redis password

# MCP Configuration
MCP_SERVER_URL=http://localhost:8000  # MCP server URL
MCP_MODE=mock                     # Options: "real" or "mock"

# Application Configuration
LOG_LEVEL=INFO                    # Logging level
DEBUG=False                       # Enable debug mode

# Orchestrator Configuration
NUM_ORCHESTRATORS=2               # Number of parallel orchestrators
ORCHESTRATOR_TIMEOUT=30           # Timeout in seconds
MAX_RETRIES=3                     # Max retries on failure

# Agent Configuration
AGENT_TEMPERATURE=0.7             # LLM temperature (0-1)
AGENT_TIMEOUT_SECONDS=30          # Timeout per agent
CONFIDENCE_THRESHOLD=0.6          # Minimum confidence score
```

### Settings Class

Configuration is managed by `src/config/settings.py` using Pydantic.

```python
from src.config.settings import get_settings

settings = get_settings()
print(settings.redis_url)
print(settings.mcp_mode)
```

## Testing

### Run All Tests

```bash
pytest tests/ -v
```

### Run Specific Test

```bash
pytest tests/test_orchestrator.py::TestOrchestratorWorkflow::test_complete_workflow -v
```

### Run Integration Tests

```bash
pytest tests/ -v -m integration
```

## Architecture Details

### State Flow

1. **Input State**: OrchestratorState with user_query, user_id, session_id
2. **Validation**: Check query format and length
3. **Decomposition**: Create 6 subtasks (one per agent type)
4. **Dispatch**: Route subtasks to agent pool
5. **Execution**: Agents run in parallel
   - Fetch external data via MCP
   - Process with Google Gemini LLM
   - Return structured output
6. **Aggregation**: Combine results from all agents
7. **Synthesis**: Prepare output for presentation layer

### Parallel Execution

```python
# In dispatch_to_agents node:
tasks = [agent_func(subtask) for subtask in subtasks]
results = await asyncio.gather(*tasks)  # All agents run concurrently
```

### Agent Output Structure

```python
AgentOutput(
    agent_type="market_trend",
    facts=["Fact 1", "Fact 2", ...],
    sources=[
        {"title": "...", "url": "...", "snippet": "..."},
        ...
    ],
    confidence_score=0.85,
)
```

### Aggregation Strategy

- Collects facts from all agents
- Extracts top sources by frequency
- Calculates overall confidence as average
- Highlights high-confidence findings (>0.7)

## Integration Points

### API Layer (Handled by Team)

Your API should:
1. Authenticate user (JWT token)
2. Create OrchestratorState with user_id, session_id
3. Submit to Redis queue
4. Poll for results or subscribe to result updates

**Example**:
```python
# In your API handler
from src.services.queue_manager import get_queue_manager

queue_manager = get_queue_manager()
job_id = queue_manager.enqueue_job(state)

# Later, retrieve results
result = queue_manager.get_job_result(job_id)
```

### Synthesis Layer (Handled by Team)

The workflow returns `aggregated_insights` dict containing:
- `all_facts`: Combined facts from all agents
- `agent_summaries`: Per-agent statistics
- `top_sources`: Most relevant sources
- `high_confidence_facts`: Facts with confidence > 0.7
- `confidence_by_agent`: Individual confidence scores

Use this for:
- Chart generation
- Report creation
- Artifact rendering
- Further processing

### Data Persistence (Handled by Team)

After completion, you should:
1. Store the result state
2. Index by request_id for retrieval
3. Archive for analytics
4. Link to user/session for history

## Scaling Strategies

### Horizontal Scaling

1. **More Orchestrators**:
   ```bash
   python -m src.cli start-orchestrators --num 10
   ```

2. **More Agents**:
   - Add instances of same agent type
   - Route via load balancer in MCP

3. **Redis Cluster**:
   - Use Redis Cluster for high availability
   - Update REDIS_URL in config

## Performance Considerations

- **Agent Timeout**: 30 seconds (configurable)
- **Parallel Execution**: All 6 agents run simultaneously
- **Total Workflow Time**: ~35-50 seconds (timeout + overhead)
- **Bottleneck**: MCP server response time
- **Caching**: Implement query caching in MCP layer

## Common Issues & Troubleshooting

### Issue: "GOOGLE_API_KEY environment variable is required"
**Solution**: Set GOOGLE_API_KEY in .env file

### Issue: "Redis connection refused"
**Solution**: Ensure Redis is running or use mock MCP mode

### Issue: Agents returning empty facts
**Solution**: Check MCP_MODE=mock for development

### Issue: Slow workflow execution
**Solution**:
- Check MCP server latency
- Monitor Redis queue depth
- Verify LLM API response times

## Monitoring & Logging

### Check Logs

```bash
# View orchestrator logs
python -m src.cli start-orchestrators 2>&1 | grep orchestrator

# View detailed logs
LOG_LEVEL=DEBUG python -m src.cli test-query --query "..."
```

### Queue Monitoring

```bash
# Watch queue in real-time
watch 'python -m src.cli queue-stats'
```

## Future Enhancements

- [ ] Streaming results via WebSocket
- [ ] Agent-specific caching
- [ ] Result versioning
- [ ] A/B testing for agent prompts
- [ ] Custom agent development
- [ ] Result analytics dashboard
- [ ] Webhook notifications

## Development

### Adding a New Agent

1. Create `src/agents/new_agent.py`:
   ```python
   class NewAgent(BaseAgent):
       def __init__(self):
           super().__init__("new_agent_type")

       def get_system_prompt(self, context):
           return "Your system prompt"

       def get_initial_query(self, query, context):
           return f"Transform query: {query}"
   ```

2. Register in workflow decomposer:
   ```python
   agent_configurations = {
       "new_agent_type": {"prompt": "...", "priority": 1},
       ...
   }
   ```

3. Update agent_map in dispatch_to_agents

### Modifying Agent Behavior

Each agent can override:
- `get_external_data()`: Change data fetching strategy
- `process_with_llm()`: Change LLM processing
- `_parse_llm_response()`: Change output parsing

## Support & Contact

For questions or issues:
- Check documentation in `docs/` directory
- Review test cases in `tests/`
- Check agent implementations for examples
"""
