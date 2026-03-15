# Xynera Setup Complete ✅

## Virtual Environment & Dependencies Installed

### Setup Done:
- ✅ Created Python virtual environment (.venv)
- ✅ Installed all 40+ dependencies from requirements.txt
- ✅ Installed Firecrawl and PyTrends packages
- ✅ Fixed case-sensitivity issues in MCP client
- ✅ All integration tests passing

### Current Environment:
```bash
Location: e:/CodeGen/Xynera/.venv
Python Version: 3.13
Packages: 40+ (see requirements.txt)
```

## Quick Start Commands

### 1. Activate Virtual Environment
```bash
# Windows (Git Bash)
source .venv/Scripts/activate

# Or Windows PowerShell
.venv\Scripts\Activate.ps1
```

### 2. Run Integration Tests
```bash
cd backend
python test_firecrawl_integration.py
```

**Expected Output:**
- ✅ Mock MCP client tests
- ✅ Factory pattern tests
- ✅ Real client configuration validation
- ✅ Full workflow simulation
- All tests should pass

### 3. Start Orchestrator Server
```bash
cd backend
python orchestrator_main.py
```

This will:
- Load configuration from .env
- Initialize 2 parallel orchestrator instances
- Listen on Redis queue for incoming jobs
- Process competitive intelligence requests

### 4. Test with CLI
```bash
cd backend
python -m app.cli test-query --query "What are the latest AI trends?"
```

Available CLI commands:
- `test-query` - Submit a test intelligence query
- `start-orchestrators` - Launch orchestrator pool
- `queue-stats` - Show Redis queue statistics
- `health-check` - Verify system health
- `show-config` - Display active configuration

## Configuration

### .env File Settings
```env
# MCP Configuration
MCP_MODE=mock                    # Use "mock" for testing, "real" for production
FIRECRAWL_API_KEY=your_key_here # Get from https://www.firecrawl.dev/
TAVILY_API_KEY=optional_backup   # Optional backup (not required)

# LLM Configuration
GOOGLE_API_KEY=your_gemini_key   # For Google Gemini
ANTHROPIC_API_KEY=optional       # Optional

# Database
DATABASE_URL=sqlite:///xynera.db # Or postgresql://...

# Redis
REDIS_URL=redis://localhost:6379
```

### Key Attributes:
- **MCP_MODE**: Controls which client to use
  - `mock`: Uses MockMCPClient (no API keys needed, for testing)
  - `real`: Uses FirecrawlMCPClient (requires FIRECRAWL_API_KEY)

## System Architecture

### Components:
1. **MCP Client Layer** (`app/services/mcp_client.py`)
   - FirecrawlMCPClient: Real web scraping via Firecrawl
   - MockMCPClient: Mock responses for testing
   - Factory pattern for dynamic selection

2. **Workflow Engine** (`app/workflows/orchestrator_workflow.py`)
   - 5-node LangGraph workflow
   - Input validation → Task decomposition → Agent dispatch → Result aggregation → Synthesis

3. **Agent Pool** (`app/agents/`)
   - 6 specialized agents (Market Trend, Competitive Landscape, Win/Loss, Pricing, Messaging, Adjacent Market)
   - Each runs an async task in parallel
   - All results aggregated with confidence scoring

4. **Orchestrator** (`app/agents/orchestrator.py`)
   - 2 parallel orchestrator instances
   - Listen to Redis queue
   - Process and coordinate workflow execution

5. **API/Queue** (`app/services/queue_manager.py`)
   - Redis + RQ for async job management
   - Distributed job queuing

## Testing Results

### Mock Client Tests:
- ✅ Web search: 1 page found
- ✅ News search: 1 article found
- ✅ Trends: 1 data point found
- ✅ Page extraction: 37 chars extracted
- ✅ Reddit analysis: 1 discussion found
- ✅ Ad intelligence: 1 result found

### Factory Tests:
- ✅ Factory correctly returns MockMCPClient in mock mode
- ✅ Configuration properly loaded

### Real Client Config:
- ✅ FIRECRAWL_API_KEY detected (length: 35)
- ✅ FirecrawlMCPClient initializes successfully
- ✅ Ready for production when API is active

### Full Workflow:
- ✅ OrchestratorState created
- ✅ Mock queries executed
- ✅ All agent simulations passed
- ✅ Results aggregated successfully

## Next Steps

### For Development:
1. Keep MCP_MODE=mock for development (no API costs)
2. Run tests to validate changes
3. Update agents as needed

### For Production:
1. Set `MCP_MODE=real` in .env
2. Add FIRECRAWL_API_KEY from https://www.firecrawl.dev/
3. Configure GOOGLE_API_KEY for Gemini LLM
4. Set up PostgreSQL database
5. Configure Redis for production
6. Run full orchestrator: `python orchestrator_main.py`

### Data Sources Available:
- **Web Scraping**: Firecrawl (primary)
- **Trends**: PyTrends (free Google Trends)
- **News**: Firecrawl + Google News
- **Reddit**: Firecrawl + Reddit scraping
- **Ads Intelligence**: Firecrawl + Google Ads search

## Troubleshooting

### Virtual Environment Issues:
```bash
# If venv doesn't work, recreate it:
rm -rf .venv
python -m venv .venv
source .venv/Scripts/activate
pip install -r backend/requirements.txt
```

### Import Errors:
```bash
# Make sure you're in the right directory and venv is activated
cd backend
source ../.venv/Scripts/activate
python test_firecrawl_integration.py
```

### MCP Client Issues:
- Check that MCP_MODE is set correctly in .env
- For mock mode: No API keys needed
- For real mode: FIRECRAWL_API_KEY is required

### Redis Errors:
- Ensure Redis is running locally: `redis-cli ping` should return PONG
- Or use a cloud Redis URL in REDIS_URL

## Files Overview

```
backend/
├── app/
│   ├── config.py                 # Pydantic settings
│   ├── models/
│   │   └── state.py              # OrchestratorState, AgentOutput
│   ├── services/
│   │   ├── mcp_client.py         # Firecrawl + Mock clients
│   │   ├── queue_manager.py      # Redis + RQ integration
│   │   └── llm_client.py         # Google Gemini client
│   ├── workflows/
│   │   └── orchestrator_workflow.py  # 5-node LangGraph
│   ├── agents/
│   │   ├── base_agent.py         # Abstract base class
│   │   ├── *_agent.py            # 6 specialized agents
│   │   ├── orchestrator.py       # Single orchestrator worker
│   │   └── orchestrator_instances.py  # Multi-instance pool
│   └── cli.py                    # CLI interface
├── orchestrator_main.py          # Entry point
├── requirements.txt              # All dependencies
├── test_firecrawl_integration.py # Integration tests
└── .env.example                  # Configuration template
```

## Performance Notes

- **Parallel Execution**: All 6 agents run simultaneously via asyncio.gather()
- **Timeout**: 30 seconds per agent, configurable in settings
- **Retry Logic**: 3 retries for failed requests
- **Confidence Scoring**: Aggregated from all agents
- **Mock Mode**: Instant responses for development
- **Real Mode**: Limited by Firecrawl API rate limits

## Support

For issues or questions:
1. Check the logs in orchestrator output
2. Verify .env configuration
3. Run integration tests: `python test_firecrawl_integration.py`
4. Check Redis connection: `redis-cli ping`
5. Review agent logs for specific failures

---

**Setup Date**: 2026-03-15
**Status**: ✅ Ready for Development & Testing
