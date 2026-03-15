import { apiClient, tokenStore } from './client'
import type { JobCreatedResponse, JobStatusResponse, ChatSession, Message } from '@/types'

export async function submitQuery(
  query: string,
  sessionId?: string,
): Promise<JobCreatedResponse> {
  const { data } = await apiClient.post<JobCreatedResponse>('/api/v1/queries', {
    query,
    session_id: sessionId ?? null,
  })
  return data
}

export async function getJobStatus(jobId: string): Promise<JobStatusResponse> {
  const { data } = await apiClient.get<JobStatusResponse>(`/api/v1/jobs/${jobId}/status`)
  return data
}

export async function listSessions(): Promise<ChatSession[]> {
  const { data } = await apiClient.get<ChatSession[]>('/api/v1/sessions')
  return data
}

export async function getSessionMessages(sessionId: string): Promise<Message[]> {
  const { data } = await apiClient.get<Message[]>(`/api/v1/sessions/${sessionId}/messages`)
  return data
}

/**
 * Open a WebSocket that streams real-time status updates for a job.
 * Returns a cleanup function that closes the socket.
 */
export function subscribeToJob(
  jobId: string,
  onMessage: (data: JobStatusResponse) => void,
  onError?: (err: Event) => void,
): () => void {
  const token = tokenStore.getAccessToken()
  const protocol = window.location.protocol === 'https:' ? 'wss' : 'ws'
  const host = window.location.host
  const url = `${protocol}://${host}/ws/jobs/${jobId}?token=${token}`

  const ws = new WebSocket(url)

  ws.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data) as JobStatusResponse
      onMessage(data)
    } catch { /* ignore parse errors */ }
  }

  ws.onerror = (event) => {
    onError?.(event)
  }

  return () => {
    if (ws.readyState === WebSocket.OPEN || ws.readyState === WebSocket.CONNECTING) {
      ws.close()
    }
  }
}
