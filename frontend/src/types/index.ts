export interface User {
  id: string
  email: string
  full_name: string | null
  is_active: boolean
  created_at: string
}

export interface TokenResponse {
  access_token: string
  refresh_token: string
  token_type: string
}

// ── Messages ──────────────────────────────────────────────────────────────────

export interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string | null
  artifact: Artifact | null
  job_id: string | null
  created_at: string
}

export interface ChatSession {
  id: string
  title: string | null
  created_at: string
}

// ── Artifacts ─────────────────────────────────────────────────────────────────

export type ArtifactType =
  | 'trend_chart'
  | 'competitor_scorecard'
  | 'sentiment_heatmap'
  | 'pricing_table'
  | 'text_summary'

export interface Artifact {
  type: ArtifactType
  title: string
  data: ArtifactData
  status: string
  confidence: number
  agents_completed: string[]
  error: string | null
}

export interface ArtifactData {
  all_facts: string[]
  top_sources: Source[]
  agent_summaries: Record<string, AgentSummary>
  confidence_by_agent: Record<string, number>
  high_confidence_facts: string[]
  request_metadata?: RequestMetadata
  trends?: TrendPoint[]
  competitors?: CompetitorEntry[]
  sentiment_segments?: SentimentSegment[]
  pricing_products?: PricingProduct[]
}

export interface Source {
  url: string
  title: string
  snippet: string
}

export interface AgentSummary {
  fact_count: number
  source_count: number
  confidence: number
}

export interface RequestMetadata {
  request_id: string
  user_id: string
  session_id: string
  original_query: string
  timestamp: string
  processing_time_ms: number
  final_confidence: number
  agents_used: string[]
}

export interface TrendPoint {
  label: string
  value: number
  date?: string
}

export interface CompetitorEntry {
  name: string
  scores: Record<string, number>
  strengths?: string[]
  weaknesses?: string[]
}

export interface SentimentSegment {
  label: string
  values: { category: string; score: number }[]
}

export interface PricingProduct {
  name: string
  plans: { tier: string; price: string; features: string[] }[]
}

// ── Jobs ──────────────────────────────────────────────────────────────────────

export type JobStatus = 'queued' | 'processing' | 'completed' | 'failed'

export interface JobStatusResponse {
  job_id: string
  status: JobStatus
  artifact?: Artifact
  error?: string
}

export interface JobCreatedResponse {
  job_id: string
  session_id: string
  status: string
}
