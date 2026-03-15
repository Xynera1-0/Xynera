# Xynera
A single conversational interface that gives any product team boardroom-quality competitive intelligence in minutes

The system is designed to process user intelligence queries through a real-time multi-agent pipeline.

Users interact through a conversational interface. Each user query becomes a job placed in a Redis queue. Two orchestrator agents continuously listen to this queue and pick up jobs as soon as they arrive.

Once a job is received, the orchestrator coordinates a LangGraph workflow that executes six specialist agents in parallel, each responsible for a different intelligence domain.

The system uses Redis only for job management, while user context and history are retrieved from a separate database accessed by the agent layer.

This separation ensures:

Redis remains lightweight and fast

persistent user context is stored in a durable database

agents can enrich analysis using historical context

Core Architecture

The architecture consists of the following major components:

User Interface
API Gateway
Redis Job Queue
Orchestrator Agents
LangGraph Execution Graph
Specialist Agent Pools
Tool Registry
External Data Sources
Synthesis and Rendering Agents
User Context Database

System flow:

User → React Chat Interface → FastAPI Gateway → Redis Job Queue → Orchestrator Agents → LangGraph Workflow → Specialist Agent Pools → Tool Registry → External Data Sources → Synthesis Agent → Renderer Agent → Response Artifact

Redis Job Queue

Redis is used only for handling incoming user jobs.

Jobs represent user intelligence queries that must be processed by the system.

Queue key:

jobs:incoming

Each job is a JSON object containing minimal metadata required for execution.

Job structure:

job_id
session_id
user_id
query
timestamp

Example job payload:

{
 "job_id": "uuid",
 "session_id": "session_8421",
 "user_id": "user_42",
 "query": "Why is Notion outperforming ClickUp?",
 "timestamp": 171222342
}

Redis is used because it supports fast push/pop operations and real-time worker consumption.

Real-Time Queue Listening

Two orchestrator workers run continuously and listen to the Redis queue.

They operate in a blocking mode, meaning they wait for jobs rather than polling repeatedly.

This is done using the Redis command:

BLPOP jobs:incoming

Blocking pop ensures:

instant job pickup

no CPU waste from polling loops

real-time responsiveness

Example behavior:

Worker A waits on queue
Worker B waits on queue
A user submits a job
Redis wakes one worker immediately
That worker starts processing the job

This design naturally distributes load between orchestrators.

Job Locking Mechanism

To prevent duplicate execution, a Redis lock is used for each job.

When a worker receives a job, it attempts to create a lock.

Lock key format:

lock:{job_id}

Lock creation uses the Redis NX flag so the key is only created if it does not already exist.

Example:

SET lock:{job_id} worker_id NX EX 60

If the lock succeeds, the worker processes the job.

If the lock fails, another worker has already claimed it.

Locks expire automatically after a short timeout to prevent deadlocks.

Separate User Context Database

User data and session history are not stored in Redis.

Instead, a separate database stores persistent context.

Possible database options include:

PostgreSQL
MongoDB
Supabase
PlanetScale

The database stores:

user profile
previous queries
product context
company context
saved insights

Example schema:

Users
Sessions
Conversations
Insights

Agents retrieve user context using the user_id or session_id contained in the job.

Context Retrieval Layer

When an orchestrator receives a job, the first step is to retrieve context from the database.

The context layer fetches:

user profile
recent conversation history
tracked products
previous intelligence queries

This information is injected into the LangGraph state before agents begin analysis.

Example context fields:

user_id
session_id
recent_queries
tracked_products
company_focus

The agents then incorporate this information into their reasoning.

LangGraph Workflow Initialization

After retrieving user context, the orchestrator initializes the LangGraph state.

The state contains both the user query and the retrieved context.

State structure includes:

query
user_id
session_id
user_context
market_signals
competitors
winloss
pricing
messaging
adjacent
synthesis
artifact

The orchestrator then starts the LangGraph execution.

Specialist Agent Execution

Six domain-specific agents analyze the query in parallel.

Each agent focuses on a specific intelligence domain.

Market Agent analyzes trends and category signals.

Competitive Agent examines competing products and features.

Win/Loss Agent analyzes customer feedback and switching behavior.

Pricing Agent examines pricing models and packaging structures.

Messaging Agent analyzes marketing language and positioning.

Adjacent Market Agent detects emerging threats from outside the category.

These agents operate simultaneously using LangGraph’s parallel node execution.

Agent Pools

Each agent type runs within a pool of workers.

Agent pools prevent slow data sources from blocking the entire system.

Example pool sizes:

Market Agents: 3
Competitive Agents: 3
Win/Loss Agents: 2
Pricing Agents: 2
Messaging Agents: 2
Adjacent Market Agents: 2

The orchestrator dispatches tasks to the available worker within the pool.

Tool Registry

Agents access external data through a centralized tool registry.

Tools provide a standardized interface for external data access.

Available tools include:

search engine queries
web scraping
Reddit search
Hacker News search
advertisement libraries

Agents request tools by name rather than calling APIs directly.

The registry routes the request to the correct implementation.

This design allows new data sources to be added easily.

External Data Signals

Agents gather live intelligence signals from several external sources.

Search APIs provide trending topics and news signals.

Web scraping tools extract structured content from product websites and documentation.

Reddit provides user sentiment and complaints.

Hacker News provides developer discussion signals.

Advertising libraries reveal messaging and positioning strategies.

All signals are converted into structured evidence objects containing:

claim
source_url
confidence
type

Synthesis Agent

After the six specialist agents complete their analysis, the synthesis agent aggregates their findings.

It identifies cross-domain insights such as:

market opportunities
competitive weaknesses
pricing patterns
emerging threats

The synthesis agent produces a structured summary of strategic intelligence.

Renderer Agent

The renderer agent converts the synthesis output into a visual artifact.

Artifact types may include:

trend_chart
competitor_scorecard
sentiment_heatmap
pricing_table
text_summary

Each artifact includes the data necessary for visualization.

Result Storage

After rendering, the final artifact is stored temporarily in Redis.

Key format:

result:{job_id}

The API layer retrieves this result when the frontend requests it.

This allows the frontend to display the response inside the chat interface.

Frontend Rendering

The frontend receives the artifact JSON and renders it inline.

A renderer component maps artifact types to UI components.

For example:

trend_chart renders a line chart
competitor_scorecard renders a comparison table
heatmap renders a sentiment grid

All visualizations appear directly inside the conversation thread.

Worker Runtime Model

Two orchestrator workers run continuously.

Each worker executes the following loop:

Wait for job from Redis queue
Acquire job lock
Retrieve user context from database
Initialize LangGraph state
Execute multi-agent workflow
Store artifact result
Release lock

This design allows the system to process multiple user queries simultaneously while maintaining consistent state management.

System Behavior Summary

User queries are submitted through the chat interface and pushed into a Redis queue.

Two orchestrator workers listen to this queue in real time.

When a job arrives, one worker claims it, retrieves user context from a database, and executes a LangGraph workflow.

Six specialist agents analyze the query in parallel using live external signals.

Their results are synthesized into a structured intelligence artifact, which is returned to the frontend and rendered directly inside the conversation.