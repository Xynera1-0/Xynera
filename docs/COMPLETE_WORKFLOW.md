# Xynera Complete Workflow Documentation

## Overview

Xynera is a distributed multi-agent competitive intelligence platform that processes user queries through a sophisticated LangGraph-based workflow to deliver real-time market, competitive, pricing, and messaging insights.

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           USER INTERFACE                                │
│                      (React Chat Interface)                             │
│                     Conversational Intelligence                         │
└──────────────────────────────┬──────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                        API GATEWAY                                      │
│                    (FastAPI - backend/app/api/)                        │
│   • Authentication (JWT)                                               │
│   • Request Validation                                                 │
│   • Response Formatting                                                │
└──────────────────────────────┬──────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                      REDIS JOB QUEUE                                    │
│                  (RQ - Redis Queue)                                    │
│   • Job: {request_id, user_id, session_id, query, timestamp}         │
│   • Format: JSON serialized OrchestratorState                         │
│   • Purpose: Decouple API from processing                             │
└──────────────────────────────┬──────────────────────────────────────────┘
                    ┌──────────┴──────────┐
                    │                     │
                    ▼                     ▼
        ┌─────────────────────┐  ┌─────────────────────┐
        │  ORCHESTRATOR 1     │  │  ORCHESTRATOR 2     │
        │  (async worker)     │  │  (async worker)     │
        │  Listening to Queue │  │  Listening to Queue │
        └─────────────────────┘  └─────────────────────┘
                    │                     │
                    └──────────┬──────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    LANGGRAPH WORKFLOW ENGINE                            │
│              (backend/app/workflows/orchestrator_workflow.py)          │
│                                                                         │
│  NODE 1: INPUT VALIDATOR                                              │
│  ├─ Validate query format                                             │
│  ├─ Check required fields                                             │
│  └─ Add metadata/timestamps                                           │
│         │                                                              │
│         ▼                                                              │
│  NODE 2: TASK DECOMPOSER                                              │
│  ├─ Break user query into 6 subtasks                                  │
│  ├─ Assign priorities                                                 │
│  └─ Add context for each agent                                        │
│         │                                                              │
│         ▼                                                              │
│  NODE 3: AGENT DISPATCHER                                             │
│  ├─ Route subtasks to agent pool                                      │
│  ├─ Execute all 6 agents in PARALLEL                                  │
│  └─ Apply 30-second timeout per agent                                 │
│         │                                                              │
│         ▼                                                              │
│  NODE 4: RESULT AGGREGATOR                                            │
│  ├─ Collect outputs from all agents                                   │
│  ├─ Combine facts and sources                                         │
│  ├─ Calculate overall confidence                                      │
│  └─ Identify key insights                                             │
│         │                                                              │
│         ▼                                                              │
│  NODE 5: SYNTHESIS TRIGGER                                            │
│  ├─ Format aggregated insights                                        │
│  ├─ Prepare for downstream processing                                 │
│  └─ Mark as ready for presentation                                    │
└─────────────────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                        AGENT POOL EXECUTION                             │
│                 (Parallel - All 6 Agents Simultaneously)               │
│                                                                         │
│  ┌──────────────────────────────────────────────────────────────┐     │
│  │ MARKET & TREND SENSING AGENT                                │     │
│  │ ├─ Identifies category direction                            │     │
│  │ ├─ Analyzes leading indicators                              │     │
│  │ ├─ Market size & growth projections                         │     │
│  │ └─ Returns: facts, sources, confidence_score               │     │
│  └──────────────────────────────────────────────────────────────┘     │
│                                                                         │
│  ┌──────────────────────────────────────────────────────────────┐     │
│  │ COMPETITIVE LANDSCAPE AGENT                                 │     │
│  │ ├─ Analyzes competitor actions                              │     │
│  │ ├─ Validates market demand                                  │     │
│  │ ├─ Assesses feature bets                                    │     │
│  │ └─ Returns: facts, sources, confidence_score               │     │
│  └──────────────────────────────────────────────────────────────┘     │
│                                                                         │
│  ┌──────────────────────────────────────────────────────────────┐     │
│  │ WIN/LOSS INTELLIGENCE AGENT                                 │     │
│  │ ├─ Analyzes deal losses                                     │     │
│  │ ├─ Buyer perspective insights                               │     │
│  │ ├─ Competitive objections                                   │     │
│  │ └─ Returns: facts, sources, confidence_score               │     │
│  └──────────────────────────────────────────────────────────────┘     │
│                                                                         │
│  ┌──────────────────────────────────────────────────────────────┐     │
│  │ PRICING & PACKAGING AGENT                                   │     │
│  │ ├─ Evaluates pricing models                                 │     │
│  │ ├─ Analyzes willingness-to-pay                              │     │
│  │ ├─ Margin trends & optimization                             │     │
│  │ └─ Returns: facts, sources, confidence_score               │     │
│  └──────────────────────────────────────────────────────────────┘     │
│                                                                         │
│  ┌──────────────────────────────────────────────────────────────┐     │
│  │ POSITIONING & MESSAGING AGENT                               │     │
│  │ ├─ Identifies messaging gaps                                │     │
│  │ ├─ Analyzes positioning clarity                             │     │
│  │ ├─ Value proposition gaps                                   │     │
│  │ └─ Returns: facts, sources, confidence_score               │     │
│  └──────────────────────────────────────────────────────────────┘     │
│                                                                         │
│  ┌──────────────────────────────────────────────────────────────┐     │
│  │ ADJACENT MARKET COLLISION AGENT                             │     │
│  │ ├─ Detects external market threats                          │     │
│  │ ├─ Identifies convergence opportunities                     │     │
│  │ ├─ Emerging technology signals                              │     │
│  │ └─ Returns: facts, sources, confidence_score               │     │
│  └──────────────────────────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                      EXTERNAL DATA SOURCES                              │
│ (Accessed via MCP - Mock or Real)                                      │
│                                                                         │
│  • Web Search → Trending topics, news signals                          │
│  • Page Extraction → Product websites, documentation                   │
│  • Reddit Analysis → User sentiment, complaints                        │
│  • Advertisement Intelligence → Messaging, positioning                 │
└─────────────────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                       LLM PROCESSING LAYER                              │
│              (Google Gemini via LangChain)                             │
│                                                                         │
│  Each agent:                                                           │
│  1. Fetches external data via MCP                                      │
│  2. Passes to Gemini with specialized system prompt                    │
│  3. Analyzes with user query + external data                           │
│  4. Returns structured output (facts, sources, confidence)             │
└─────────────────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                  RESULTS AGGREGATION & STORAGE                          │
│                                                                         │
│  Aggregated Insights Include:                                          │
│  • all_facts: Combined facts from all 6 agents                         │
│  • agent_summaries: Per-agent statistics                               │
│  • top_sources: Most relevant URLs and content                         │
│  • high_confidence_facts: Facts with confidence > 0.7                  │
│  • confidence_by_agent: Individual confidence scores                   │
│  • final_confidence: Average of all agents                             │
└─────────────────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────────┐
│              DATABASE & SYNTHESIS LAYER (Team Implementation)           │
│                                                                         │
│  • Persist results to database                                         │
│  • Generate synthesis intelligence                                     │
│  • Create dynamic artifacts                                            │
│  • Render visualizations                                               │
└─────────────────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         FRONTEND RENDERING                              │
│                                                                         │
│  Artifacts Include:                                                    │
│  • Trend Charts                                                        │
│  • Competitor Comparisons                                              │
│  • Insight Summaries                                                   │
│  • Confidence Scores                                                   │
└─────────────────────────────────────────────────────────────────────────┘
```

## Workflow Execution Flow

### Step 1: Request Submission
```
User Query
    ↓
FastAPI Endpoint receives request
    ↓
JWT Authentication validates user
    ↓
Create OrchestratorState:
{
    user_id: str
    session_id: str
    request_id: str (unique UUID)
    user_query: str
    user_metadata: dict
    timestamp: datetime
}
```

### Step 2: Queue Processing
```
OrchestratorState
    ↓
Enqueue to Redis via queue_manager
    ↓
Job stored in Redis:
{
    job_id: request_id
    status: "pending"
    state: serialized_state
}
    ↓
Orchestrator 1 or 2 picks up (BLPOP)
    ↓
Acquire lock to prevent duplicate execution
```

### Step 3: LangGraph Workflow Execution

#### Node 1: Input Validator
```
Receives: OrchestratorState with user_query

Actions:
├─ Validate query length (min 3 chars)
├─ Check required fields
├─ Add started_at timestamp
└─ Set status to IN_PROGRESS

Outputs: Modified OrchestratorState
```

#### Node 2: Task Decomposer
```
Receives: OrchestratorState with validated query

Actions:
├─ Analyze user query
├─ Create 6 subtasks (one per agent type):
│  ├─ market_trend: "Identify market trends"
│  ├─ competitive_landscape: "Analyze competitors"
│  ├─ win_loss: "Analyze deal losses"
│  ├─ pricing: "Evaluate pricing"
│  ├─ messaging: "Identify messaging gaps"
│  └─ adjacent_market: "Detect external threats"
├─ Set priorities (1-3, 1 highest)
└─ Add context (query, metadata)

Outputs: List[Subtask] with full context
```

#### Node 3: Agent Dispatcher (🔑 PARALLEL EXECUTION 🔑)
```
Receives: List[Subtask]

Actions:
├─ FOR EACH Subtask:
│  └─ Launch async task to execute agent
│
├─ Execute ALL 6 agents SIMULTANEOUSLY:
│  ├─ Market Trend Agent (async)
│  ├─ Competitive Landscape Agent (async)
│  ├─ Win/Loss Agent (async)
│  ├─ Pricing Agent (async)
│  ├─ Messaging Agent (async)
│  └─ Adjacent Market Agent (async)
│
├─ Wait for ALL to complete (asyncio.gather)
├─ Apply 30-second timeout per agent
└─ Collect results with errors handled gracefully

Agent Execution (per agent):
┌─────────────────────────────────────┐
│ 1. Get system prompt               │
├─────────────────────────────────────┤
│ 2. Transform query for agent type   │
├─────────────────────────────────────┤
│ 3. Fetch external data via MCP:    │
│    • Web search                     │
│    • Page extraction                │
│    • Reddit/Ads intelligence        │
├─────────────────────────────────────┤
│ 4. Process with Google Gemini:     │
│    system_prompt + query + context │
├─────────────────────────────────────┤
│ 5. Parse LLM response:             │
│    • Extract facts                  │
│    • Extract sources               │
│    • Calculate confidence          │
├─────────────────────────────────────┤
│ 6. Return AgentOutput:            │
│    {                               │
│      agent_type: str               │
│      facts: List[str]              │
│      sources: List[Dict]           │
│      confidence_score: float       │
│      error: Optional[str]          │
│    }                               │
└─────────────────────────────────────┘

Outputs: Dict[agent_type, AgentOutput]
```

#### Node 4: Result Aggregator
```
Receives: Dict[agent_type, AgentOutput] from all 6 agents

Actions:
├─ Collect facts from all agents
├─ Combine sources (remove duplicates)
├─ Build agent summaries:
│  {
│    agent_type: {
│      fact_count: int,
│      source_count: int,
│      confidence: float
│    }
│  }
├─ Calculate overall confidence = avg(all confidence scores)
├─ Identify high_confidence_facts (confidence > 0.7)
└─ Create aggregated_insights dictionary

Outputs:
{
    all_facts: List[str],
    agent_summaries: Dict,
    top_sources: List[Dict],
    high_confidence_facts: List[str],
    confidence_by_agent: Dict,
    final_confidence: float
}
```

#### Node 5: Synthesis Trigger
```
Receives: OrchestratorState with aggregated_insights

Actions:
├─ Add completed_at timestamp
├─ Format for downstream processing
├─ Include request_metadata:
│  {
│    request_id: str,
│    user_id: str,
│    session_id: str,
│    original_query: str,
│    timestamp: str,
│    processing_time_ms: float,
│    final_confidence: float,
│    agents_used: List[str]
│  }
└─ Mark state as COMPLETED

Outputs: Final OrchestratorState with all results
```

### Step 4: Result Persistence
```
Final OrchestratorState
    ↓
Team Implementation (Not in Scope):
├─ Store in database
├─ Index by request_id
├─ Link to user/session
└─ Archive for analytics
    ↓
Return to API
    ↓
Store in Redis (temporary)
    ↓
Frontend polls for result
```

### Step 5: Frontend Rendering
```
Aggregated Insights
    ↓
Synthesis Agent (Team Implementation):
├─ Combine agent insights
├─ Identify strategic patterns
└─ Generate artifacts
    ↓
Rendering Agent (Team Implementation):
├─ Convert to visualizations
└─ Format for chat display
    ↓
Frontend displays:
├─ Trend charts
├─ Competitor comparisons
├─ Insight summaries
└─ Confidence scores
```

## Agent Implementation Details

### Base Agent Class (backend/app/agents/base_agent.py)
```python
class BaseAgent(ABC):
    async def execute(query, context) -> AgentOutput:
        1. Get system prompt (specialized per agent type)
        2. Transform query for this agent
        3. Fetch external data (via MCP)
        4. Process with Gemini LLM
        5. Parse response (facts, sources, confidence)
        6. Return structured AgentOutput
```

### Six Agent Types

**1. Market Trend Agent** (`backend/app/agents/market_trend_agent.py`)
- Analyzes market direction and trends
- Identifies leading indicators
- Provides market size/growth projections
- System prompt: Focus on market trends and catalysts

**2. Competitive Landscape Agent** (`backend/app/agents/competitive_landscape_agent.py`)
- Analyzes competitors and their actions
- Validates market demand
- Assesses feature bets
- System prompt: Focus on competitive positioning

**3. Win/Loss Agent** (`backend/app/agents/win_loss_agent.py`)
- Analyzes why deals are lost
- Understands buyer perspective
- Identifies deal patterns
- System prompt: Focus on buyer feedback and patterns

**4. Pricing Agent** (`backend/app/agents/pricing_agent.py`)
- Evaluates pricing models
- Analyzes willingness-to-pay
- Examines margin trends
- System prompt: Focus on pricing and value

**5. Messaging Agent** (`backend/app/agents/messaging_agent.py`)
- Identifies messaging gaps
- Analyzes positioning
- Evaluates value articulation
- System prompt: Focus on how to talk about existing features

**6. Adjacent Market Agent** (`backend/app/agents/adjacent_market_agent.py`)
- Detects external threats
- Identifies convergence opportunities
- Tracks emerging technologies
- System prompt: Focus on adjacent market signals

## Data Flow

### Request State Object
```python
OrchestratorState(
    # Metadata
    user_id: str                          # User making request
    session_id: str                       # Session ID
    request_id: str                       # Unique request ID
    timestamp: datetime                   # Request timestamp

    # Input
    user_query: str                       # User's query
    user_metadata: Dict[str, Any]        # Additional context

    # Processing
    subtasks: List[Subtask]              # Decomposed tasks
    agent_outputs: Dict[str, AgentOutput] # Agent results
    status: TaskStatus                    # Current status

    # Results
    aggregated_insights: Dict[str, Any]   # Combined results
    final_confidence: float                # Overall confidence

    # Tracking
    started_at: datetime                  # Start time
    completed_at: datetime                # End time
    error_message: Optional[str]          # Error if any
)
```

### Agent Output Structure
```python
AgentOutput(
    agent_type: str                       # "market_trend", etc.
    facts: List[str]                      # Key findings
    sources: List[Dict]                   # [{title, url, snippet}, ...]
    confidence_score: float               # 0.0-1.0
    error: Optional[str]                  # Error message
    processing_time_ms: float             # Execution time
)
```

## Configuration

### Environment Variables
```
# LLM
GOOGLE_API_KEY=sk-xxx...

# Redis Queue
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_URL=redis://localhost:6379/0

# MCP Configuration
MCP_SERVER_URL=http://localhost:8000
MCP_MODE=mock                 # "mock" or "real"

# Orchestrator
NUM_ORCHESTRATORS=2           # Number of workers
ORCHESTRATOR_TIMEOUT=30       # Timeout in seconds
MAX_RETRIES=3                 # Retry attempts

# Agents
AGENT_TEMPERATURE=0.7         # LLM temperature
AGENT_TIMEOUT_SECONDS=30      # Per-agent timeout
CONFIDENCE_THRESHOLD=0.6      # Minimum confidence
```

### Settings Class
```python
from app.config import get_settings

settings = get_settings()
# Access: settings.google_api_key, settings.mcp_mode, etc.
```

## Performance Characteristics

### Timeline
- **Input Validation**: < 100ms
- **Task Decomposition**: < 100ms
- **MCP Data Fetching**: 5-10 seconds per agent
- **LLM Processing**: 10-15 seconds per agent
- **Total Per-Agent Time**: 15-25 seconds
- **All 6 Agents (Parallel)**: ~20-30 seconds total
- **Result Aggregation**: < 500ms
- **Total Workflow**: 35-50 seconds

### Resource Usage
- **Memory**: ~500MB base + 100-200MB per concurrent query
- **CPU**: Multi-core (asyncio parallelization)
- **Network**: Depends on MCP server latency
- **Redis**: Minimal (job metadata only)

### Scaling
```
Add more orchestrators:
  NUM_ORCHESTRATORS=4          → 4 parallel workers

Each orchestrator can handle:
  • ~1-2 queries per minute (depends on MCP latency)
  • ~3 concurrent queries with 16GB RAM

Queue capacity:
  • Redis: Millions of jobs
  • Limited mainly by database storage
```

## Integration Points

### 1. API Layer (Your Implementation)
```python
@app.post("/api/intelligence")
async def get_intelligence(query: str, user_id: str, session_id: str):
    # Create state
    state = OrchestratorState(
        user_id=user_id,
        session_id=session_id,
        request_id=str(uuid.uuid4()),
        user_query=query,
        timestamp=datetime.utcnow(),
    )

    # Option A: Direct execution
    orchestrator = Orchestrator("api-worker")
    result = await orchestrator.process_state(state)

    # Option B: Queue-based
    queue_manager = get_queue_manager()
    queue_manager.enqueue_job(state)

    return {"request_id": state.request_id}
```

### 2. Orchestrator Service
```bash
cd backend
python orchestrator_main.py
```
Runs continuously, listening to Redis queue

### 3. Database Persistence (Your Implementation)
```python
# Store result
result = await orchestrator.process_state(state)

db.save(
    request_id=result.request_id,
    user_id=result.user_id,
    insights=result.aggregated_insights,
    confidence=result.final_confidence,
    processing_time=result.completed_at - result.started_at,
)
```

### 4. Synthesis & Rendering (Your Implementation)
```python
# Process aggregated insights
insights = result.aggregated_insights

# Build synthesis intelligence
synthesis_output = synthesize_insights(insights)

# Create dynamic artifacts
artifacts = render_artifacts(synthesis_output)

# Return to frontend
return {
    "artifacts": artifacts,
    "confidence": result.final_confidence,
    "sources": insights["top_sources"],
}
```

## Testing & Monitoring

### CLI Commands
```bash
# Test a query
python -m app.cli test-query --query "AI market trends"

# Start orchestrators
python -m app.cli start-orchestrators --num 2

# Check queue status
python -m app.cli queue-stats

# Verify system health
python -m app.cli health-check

# Show configuration
python -m app.cli show-config
```

### Tests
```bash
pytest backend/app/tests/ -v
```

### Monitoring
```python
# Get orchestrator stats
orchestrator = Orchestrator("worker-1")
stats = orchestrator.get_stats()
# Returns: {
#     orchestrator_id: str,
#     is_running: bool,
#     queue_stats: Dict
# }

# Get queue stats
queue_mgr = get_queue_manager()
queue_mgr.get_job_count_by_status()
# Returns: {
#     "queued": int,
#     "started": int,
#     "finished": int,
#     "failed": int
# }
```

## Error Handling

### Graceful Degradation
- If MCP fails → Return empty sources, lower confidence
- If LLM times out → Return partial results, confidence < 0.5
- If agent crashes → Skip agent, continue with others
- If all agents fail → Return error state, confidence = 0

### Retry Logic
- Automatic exponential backoff: 1s → 2s → 4s
- Max 3 retries per operation
- Timeout after 30 seconds per agent

### Logging
```python
# Full execution trace
LOG_LEVEL=DEBUG python -m app.cli test-query --query "..."

# Check orchestrator logs
orchestrator_process.stdout
```

## Summary

The Xynera workflow is a sophisticated multi-agent intelligence gathering system that:

1. **Accepts** user queries through a chat interface
2. **Queues** jobs in Redis for distributed processing
3. **Dispatches** two parallel orchestrator workers
4. **Executes** a 5-node LangGraph workflow
5. **Processes** 6 specialized agents in parallel
6. **Aggregates** results into comprehensive insights
7. **Returns** confidence-scored findings with sources
8. **Persists** to database for synthesis and rendering

The architecture supports horizontal scaling, handles failures gracefully, and provides confidence scores for result quality assessment. Total processing time is 35-50 seconds per query with real-time queue-based distribution.
