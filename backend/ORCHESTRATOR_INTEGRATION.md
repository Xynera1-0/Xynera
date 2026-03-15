# Orchestrator & Agent Integration Guide

This document describes how the LangGraph orchestrator, orchestrator agents, and agent pool have been integrated into the Xynera backend.

## Project Structure

```
backend/
├── app/
│   ├── config.py              # ← UPDATED: Now includes orchestrator settings
│   ├── main.py                # ← FastAPI app entry point
│   ├── orchestrator_main.py   # ← Orchestrator service entry point
│   ├── cli.py                 # ← CLI for testing and management
│   │
│   ├── workflows/
│   │   ├── __init__.py
│   │   └── orchestrator_workflow.py  # ← LangGraph workflow (5 nodes)
│   │
│   ├── agents/
│   │   ├── base_agent.py      # ← Base class for all agents
│   │   ├── orchestrator.py    # ← Orchestrator class
│   │   ├── orchestrator_instances.py # ← Two parallel instances
│   │   ├── market_trend_agent.py
│   │   ├── competitive_landscape_agent.py
│   │   ├── win_loss_agent.py
│   │   ├── pricing_agent.py
│   │   ├── messaging_agent.py
│   │   └── adjacent_market_agent.py
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   └── state.py           # ← OrchestratorState, AgentOutput
│   │
│   ├── services/
│   │   ├── llm_client.py      # ← Google Gemini integration
│   │   ├── mcp_client.py      # ← MCP server (real & mock modes)
│   │   └── queue_manager.py   # ← Redis queue management
│   │
│   ├── api/                    # ← Your API routes
│   ├── auth/                   # ← Authentication layer
│   └── db/                     # ← Database layer
│
├── Dockerfile
└── requirements.txt
```

## Key Changes to Existing Files

### 1. Updated `config.py`
Added orchestrator and agent configuration to existing settings:

```python
# MCP Configuration
MCP_SERVER_URL: str = "http://localhost:8000"
MCP_MODE: str = "mock"  # Options: "real" or "mock"

# Orchestrator Configuration
NUM_ORCHESTRATORS: int = 2
ORCHESTRATOR_TIMEOUT: int = 30
MAX_RETRIES: int = 3

# Agent Configuration
AGENT_TEMPERATURE: float = 0.7
AGENT_TIMEOUT_SECONDS: int = 30
CONFIDENCE_THRESHOLD: float = 0.6

# LLM Providers
GOOGLE_API_KEY: str = ""
```

Update your `.env` file to include these variables.

## How It Works

### 1. Orchestrator Service (Separate Process)

Run the orchestrator service in a separate process/container:

```bash
# Option 1: Direct Python
python -m app.orchestrator_main

# Option 2: Using CLI
python -m app.cli start-orchestrators --num 2

# Option 3: Docker
docker run -e GOOGLE_API_KEY=xxx -e REDIS_URL=redis://... xynera orchestrator
```

This starts 2 parallel orchestrator workers listening to the Redis queue.

### 2. API Integration

In your FastAPI routes, create an orchestrator state and enqueue it:

```python
from datetime import datetime
import uuid
from app.models.state import OrchestratorState
from app.services.queue_manager import get_queue_manager

@app.post("/api/intelligence")
async def analyze_market(query: str, user_id: str):
    # Create state
    state = OrchestratorState(
        user_id=user_id,
        session_id=request.headers.get("x-session-id", str(uuid.uuid4())),
        request_id=f"req-{uuid.uuid4()}",
        user_query=query,
        timestamp=datetime.utcnow(),
        user_metadata={"source": "api", "endpoint": "/intelligence"},
    )

    # Enqueue to Redis
    queue_mgr = get_queue_manager()
    job_id = queue_mgr.enqueue_job(state)

    return {"job_id": job_id, "status": "queued"}

@app.get("/api/intelligence/{job_id}")
async def get_result(job_id: str):
    queue_mgr = get_queue_manager()

    # Check job status
    status = queue_mgr.get_job_status(job_id)
    if status == "finished":
        result = queue_mgr.get_job_result(job_id)
        return {
            "status": "completed",
            "result": result.aggregated_insights,
            "confidence": result.final_confidence,
        }
    elif status == "failed":
        return {"status": "failed"}
    else:
        return {"status": status}
```

### 3. Workflow Data Flow

```
API Request
    ↓
Create OrchestratorState (input: user_query, user_id, session_id)
    ↓
Enqueue to Redis
    ↓
Orchestrator picks up job
    ↓
Execute LangGraph Workflow:
    1. Validate input
    2. Decompose to 6 subtasks
    3. Dispatch to agent pool (parallel)
       • Market Trend Agent
       • Competitive Landscape Agent
       • Win/Loss Agent
       • Pricing Agent
       • Messaging Agent
       • Adjacent Market Agent
    4. Aggregate results from all agents
    5. Prepare output for synthesis
    ↓
Return OrchestratorState (output: agent_outputs, aggregated_insights, final_confidence)
    ↓
Store result in Redis/Database
    ↓
API retrieves result
    ↓
Frontend renders artifact
```

## Configuration

### Environment Variables

Add these to your `.env`:

```bash
# Google Gemini API
GOOGLE_API_KEY=your_api_key_here

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=

# MCP Server
MCP_SERVER_URL=http://localhost:8000
MCP_MODE=mock  # Use "mock" for development, "real" for production

# Orchestrator
NUM_ORCHESTRATORS=2
ORCHESTRATOR_TIMEOUT=30
MAX_RETRIES=3

# Agent Configuration
AGENT_TEMPERATURE=0.7
AGENT_TIMEOUT_SECONDS=30
CONFIDENCE_THRESHOLD=0.6
```

### Using Mock MCP Server (Development)

By default, MCP_MODE is set to "mock". This means:
- No external MCP server needed
- Agents use predefined mock data
- Perfect for local testing and development

### Using Real MCP Server (Production)

When ready to connect to a real MCP server:
1. Ensure your MCP server is running
2. Update `.env`: `MCP_MODE=real`
3. Update `.env`: `MCP_SERVER_URL=http://your-mcp-server:port`

## CLI Tool

The CLI tool provides convenient commands for testing and management:

```bash
# Test a query locally
python -m app.cli test-query --query "What are AI market trends?" --user-id demo_user

# Start orchestrators
python -m app.cli start-orchestrators --num 2

# Monitor queue
python -m app.cli queue-stats

# Health check
python -m app.cli health-check

# Show configuration
python -m app.cli show-config
```

## Testing

Run tests with the same path setup:

```bash
pytest tests/ -v
```

Tests import from `app.*` automatically (path is configured in test_orchestrator.py).

## Deployment Architecture

### Single Server
```
Frontend
    ↓
FastAPI (API Layer)
    ↓
Redis Queue
    ↓
Orchestrator (2 workers)
    ↓
Agent Pool (6 types × N workers)
    ↓
MCP Server (External data)
```

### Multi-Container (Docker)
```
Container 1: FastAPI + CLI
Container 2: Orchestrator Worker 1
Container 3: Orchestrator Worker 2
Container 4: Redis
Container 5: MCP Server (optional)
```

Example docker-compose.yml integration:

```yaml
services:
  api:
    image: xynera:latest
    command: uvicorn app.main:app --host 0.0.0.0
    ports:
      - "8000:8000"
    environment:
      - GOOGLE_API_KEY=${GOOGLE_API_KEY}
      - REDIS_URL=redis://redis:6379

  orchestrator1:
    image: xynera:latest
    command: python -m app.orchestrator_main
    environment:
      - GOOGLE_API_KEY=${GOOGLE_API_KEY}
      - REDIS_URL=redis://redis:6379
      - NUM_ORCHESTRATORS=1

  orchestrator2:
    image: xynera:latest
    command: python -m app.orchestrator_main
    environment:
      - GOOGLE_API_KEY=${GOOGLE_API_KEY}
      - REDIS_URL=redis://redis:6379
      - NUM_ORCHESTRATORS=1

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
```

## Integration Checklist

- [ ] Update `.env` with GOOGLE_API_KEY and other orchestrator settings
- [ ] Test orchestrator locally: `python -m app.cli health-check`
- [ ] Test a query: `python -m app.cli test-query --query "test query"`
- [ ] Integrate API layer with queue manager
- [ ] Deploy orchestrator as separate service/container
- [ ] Connect frontend to API results endpoint
- [ ] Monitor logs and queue statistics
- [ ] Test end-to-end workflow

## Troubleshooting

### "GOOGLE_API_KEY environment variable is required"
- Ensure `GOOGLE_API_KEY` is set in `.env`
- Restart orchestrator service

### "Redis connection refused"
- Check Redis is running: `redis-cli ping`
- Verify `REDIS_URL` in `.env`

### Agents returning empty results
- Check `MCP_MODE` in `.env` (should be "mock" for testing)
- Verify LLM API key is valid
- Check orchestrator logs

### Tests failing with import errors
- Ensure `PYTHONPATH` includes backend: `export PYTHONPATH=$PYTHONPATH:./backend`
- Or run from project root: `pytest tests/`

## Next Steps

1. **Integrate with your API**: Connect orchestrator state creation to your API routes
2. **Implement result persistence**: Store results in your database
3. **Build synthesis layer**: Aggregate results into final intelligence artifacts
4. **Deploy orchestrator**: Run as separate container/process
5. **Monitor and optimize**: Track performance and adjust settings

## Support

- Check `/backend/app/cli.py` for available commands
- Review agent implementations in `/backend/app/agents/` for customization
- See `/docs/architecture.md` for detailed system documentation
