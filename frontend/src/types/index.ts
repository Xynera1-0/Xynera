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

export interface Message {
  id: string
  session_id: string
  user_id: string
  role: 'user' | 'assistant'
  content: string | null
  artifact: Artifact | null
  job_id: string | null
  created_at: string
}

export interface ChatSession {
  id: string
  user_id: string
  title: string | null
  created_at: string
  updated_at: string
  messages?: Message[]
}

// ── Artifact types ────────────────────────────────────────────────────────────

export type ArtifactType =
  | 'trend_chart'
  | 'competitor_scorecard'
  | 'sentiment_heatmap'
  | 'pricing_table'
  | 'text_summary'

export interface Artifact {
  type: ArtifactType
  title: string
  data: unknown
  generated_at: string
}

// ── Job types ─────────────────────────────────────────────────────────────────

export type JobStatus = 'queued' | 'processing' | 'completed' | 'failed'

export interface JobStatusResponse {
  job_id: string
  status: JobStatus
  artifact?: Artifact
  error?: string
}
