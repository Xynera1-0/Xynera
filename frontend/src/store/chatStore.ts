import { create } from 'zustand'
import { submitQuery, subscribeToJob, listSessions, getSessionMessages } from '@/api/chat'
import type { Artifact, JobStatus, ChatSession } from '@/types'

interface ChatMessage {
  id: string
  role: 'user' | 'assistant'
  content: string | null
  artifact: Artifact | null
  timestamp: number
}

interface ChatState {
  sessionId: string | null
  sessions: ChatSession[]
  messages: ChatMessage[]
  jobId: string | null
  jobStatus: JobStatus | null
  agentsWorking: string[]
  error: string | null

  sendQuery: (query: string) => Promise<void>
  loadSessions: () => Promise<void>
  openSession: (sessionId: string) => Promise<void>
  reset: () => void
}

let cleanupWs: (() => void) | null = null

export const useChatStore = create<ChatState>((set, get) => ({
  sessionId: null,
  sessions: [],
  messages: [],
  jobId: null,
  jobStatus: null,
  agentsWorking: [],
  error: null,

  loadSessions: async () => {
    try {
      const sessions = await listSessions()
      set({ sessions })
    } catch (err) {
      console.error('[loadSessions] failed:', err)
    }
  },

  openSession: async (sessionId: string) => {
    // Cleanup any active WS
    if (cleanupWs) {
      cleanupWs()
      cleanupWs = null
    }

    try {
      const msgs = await getSessionMessages(sessionId)
      const chatMessages: ChatMessage[] = msgs.map((m) => ({
        id: m.id,
        role: m.role as 'user' | 'assistant',
        content: m.content,
        artifact: m.artifact,
        timestamp: new Date(m.created_at).getTime(),
      }))
      set({
        sessionId,
        messages: chatMessages,
        jobId: null,
        jobStatus: null,
        agentsWorking: [],
        error: null,
      })
    } catch {
      set({ error: 'Failed to load session' })
    }
  },

  sendQuery: async (query: string) => {
    // Prevent double-send
    if (get().jobStatus === 'processing' || get().jobStatus === 'queued') return

    // Add user message immediately
    const userMsg: ChatMessage = {
      id: `local-${Date.now()}`,
      role: 'user',
      content: query,
      artifact: null,
      timestamp: Date.now(),
    }

    set((s) => ({
      messages: [...s.messages, userMsg],
      error: null,
      jobStatus: 'queued',
      agentsWorking: [],
    }))

    try {
      const prevSessionId = get().sessionId
      const { job_id, session_id } = await submitQuery(query, prevSessionId ?? undefined)
      set({ jobId: job_id, sessionId: session_id })

      // Optimistically add session to sidebar if it's new
      if (!prevSessionId) {
        const newSession: ChatSession = {
          id: session_id,
          title: query.length > 120 ? query.slice(0, 120) + '...' : query,
          created_at: new Date().toISOString(),
        }
        set((s) => ({
          sessions: [newSession, ...s.sessions],
        }))
      }

      // Also refresh from server to stay in sync
      get().loadSessions()

      // Subscribe to real-time updates via WebSocket
      if (cleanupWs) cleanupWs()

      cleanupWs = subscribeToJob(
        job_id,
        (data) => {
          set({ jobStatus: data.status as JobStatus })

          if (data.status === 'completed' && data.artifact) {
            const assistantMsg: ChatMessage = {
              id: `job-${job_id}`,
              role: 'assistant',
              content: null,
              artifact: data.artifact as Artifact,
              timestamp: Date.now(),
            }
            set((s) => ({
              messages: [...s.messages, assistantMsg],
              jobStatus: 'completed',
              jobId: null,
              agentsWorking: [],
            }))
            cleanupWs?.()
            cleanupWs = null
          }

          if (data.status === 'failed') {
            set({
              error: data.error ?? 'Processing failed',
              jobStatus: 'failed',
              jobId: null,
              agentsWorking: [],
            })
            cleanupWs?.()
            cleanupWs = null
          }
        },
        () => {
          // WebSocket error — fall back to polling
          set({ error: 'Connection lost. Please try again.' })
        },
      )
    } catch {
      set({ error: 'Failed to submit query', jobStatus: null })
    }
  },

  reset: () => {
    if (cleanupWs) {
      cleanupWs()
      cleanupWs = null
    }
    set({
      sessionId: null,
      messages: [],
      jobId: null,
      jobStatus: null,
      agentsWorking: [],
      error: null,
    })
  },
}))
