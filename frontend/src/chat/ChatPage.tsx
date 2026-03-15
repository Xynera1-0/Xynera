import { useEffect } from 'react'
import { useAuth } from '@/auth/AuthContext'
import { useChatStore } from '@/store/chatStore'
import { MessageList } from './MessageList'
import { MessageInput } from './MessageInput'

export function ChatPage() {
  const { user, logout } = useAuth()
  const messages = useChatStore((s) => s.messages)
  const sessions = useChatStore((s) => s.sessions)
  const sessionId = useChatStore((s) => s.sessionId)
  const jobStatus = useChatStore((s) => s.jobStatus)
  const sendQuery = useChatStore((s) => s.sendQuery)
  const loadSessions = useChatStore((s) => s.loadSessions)
  const openSession = useChatStore((s) => s.openSession)
  const reset = useChatStore((s) => s.reset)

  const isBusy = jobStatus === 'queued' || jobStatus === 'processing'
  const hasMessages = messages.length > 0

  useEffect(() => {
    if (user) loadSessions()
  }, [user, loadSessions])

  function handleExampleClick(prompt: string) {
    sendQuery(prompt)
  }

  return (
    <div className="flex h-screen bg-gray-950 text-gray-100">
      {/* Sidebar */}
      <aside className="w-64 flex flex-col bg-gray-900 border-r border-gray-800">
        <div className="px-4 py-5 border-b border-gray-800">
          <span className="text-lg font-bold text-white tracking-tight">Xynera</span>
        </div>

        <nav className="flex-1 px-2 py-4 overflow-y-auto">
          <button
            onClick={reset}
            className="w-full text-left px-3 py-2 rounded-lg text-sm text-gray-400 hover:text-white hover:bg-white/5 transition-colors"
          >
            + New query
          </button>
          <p className="mt-6 px-3 text-xs text-gray-600 uppercase tracking-wider">
            Recent queries
          </p>

          {sessions.length === 0 ? (
            <p className="mt-2 px-3 text-xs text-gray-600 italic">No queries yet</p>
          ) : (
            <ul className="mt-2 space-y-0.5">
              {sessions.map((s) => (
                <li key={s.id}>
                  <button
                    onClick={() => openSession(s.id)}
                    className={`w-full text-left px-3 py-2 rounded-lg text-sm truncate transition-colors ${
                      sessionId === s.id
                        ? 'bg-white/10 text-white'
                        : 'text-gray-400 hover:text-white hover:bg-white/5'
                    }`}
                    title={s.title ?? 'Untitled'}
                  >
                    {s.title ?? 'Untitled'}
                  </button>
                </li>
              ))}
            </ul>
          )}
        </nav>

        {/* Footer: user info */}
        <div className="border-t border-gray-800 px-4 py-3 flex items-center gap-3">
          <div className="w-8 h-8 rounded-full bg-brand-700 flex items-center justify-center text-xs font-semibold text-white shrink-0">
            {(user?.full_name ?? user?.email ?? '?')[0].toUpperCase()}
          </div>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium text-white truncate">
              {user?.full_name ?? user?.email}
            </p>
            <p className="text-xs text-gray-500 truncate">{user?.email}</p>
          </div>
          <button
            onClick={logout}
            className="text-xs text-gray-500 hover:text-red-400 transition-colors"
            title="Sign out"
          >
            Sign out
          </button>
        </div>
      </aside>

      {/* Main area */}
      <main className="flex-1 flex flex-col overflow-hidden">
        {hasMessages ? (
          /* Conversation view */
          <MessageList />
        ) : (
          /* Empty state */
          <div className="flex-1 flex flex-col items-center justify-center gap-4 px-6">
            <div className="text-center max-w-lg">
              <h2 className="text-2xl font-semibold text-white">
                What do you want to know?
              </h2>
              <p className="mt-2 text-sm text-gray-400">
                Ask about competitors, pricing, positioning, win/loss signals, or market
                trends. Xynera runs a multi-agent analysis in real time.
              </p>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 w-full max-w-xl mt-2">
              {EXAMPLE_PROMPTS.map((prompt) => (
                <button
                  key={prompt}
                  onClick={() => handleExampleClick(prompt)}
                  disabled={isBusy}
                  className="text-left px-4 py-3 rounded-xl bg-gray-800 hover:bg-gray-700 border border-gray-700 text-sm text-gray-300 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {prompt}
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Input bar */}
        <MessageInput onSend={sendQuery} disabled={isBusy} />
      </main>
    </div>
  )
}

const EXAMPLE_PROMPTS = [
  'Why is Notion outperforming ClickUp?',
  'How is Linear positioning against Jira?',
  'What pricing signals is Figma sending?',
  'Where is Slack losing to Discord?',
]
