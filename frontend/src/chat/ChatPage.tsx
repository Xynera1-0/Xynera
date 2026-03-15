import { useAuth } from '@/auth/AuthContext'

export function ChatPage() {
  const { user, logout } = useAuth()

  return (
    <div className="flex h-screen bg-gray-950 text-gray-100">
      {/* Sidebar */}
      <aside className="w-64 flex flex-col bg-gray-900 border-r border-gray-800">
        <div className="px-4 py-5 border-b border-gray-800">
          <span className="text-lg font-bold text-white tracking-tight">Xynera</span>
        </div>

        <nav className="flex-1 px-2 py-4 overflow-y-auto">
          <button className="w-full text-left px-3 py-2 rounded-lg text-sm text-gray-400 hover:text-white hover:bg-white/5 transition-colors">
            + New query
          </button>
          {/* Session list will be populated once sessions API is wired */}
          <p className="mt-6 px-3 text-xs text-gray-600 uppercase tracking-wider">
            Recent queries
          </p>
          <p className="mt-2 px-3 text-xs text-gray-600 italic">No queries yet</p>
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
        {/* Message list — empty state */}
        <div className="flex-1 flex flex-col items-center justify-center gap-4 px-6">
          <div className="text-center max-w-lg">
            <h2 className="text-2xl font-semibold text-white">
              What do you want to know?
            </h2>
            <p className="mt-2 text-sm text-gray-400">
              Ask about competitors, pricing, positioning, win/loss signals, or market trends.
              Xynera runs a multi-agent analysis in real time.
            </p>
          </div>

          {/* Example prompts */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 w-full max-w-xl mt-2">
            {EXAMPLE_PROMPTS.map((prompt) => (
              <button
                key={prompt}
                className="text-left px-4 py-3 rounded-xl bg-gray-800 hover:bg-gray-700 border border-gray-700 text-sm text-gray-300 transition-colors"
              >
                {prompt}
              </button>
            ))}
          </div>
        </div>

        {/* Input bar */}
        <div className="border-t border-gray-800 px-4 py-4">
          <div className="max-w-3xl mx-auto flex items-end gap-3">
            <textarea
              rows={1}
              placeholder="Ask an intelligence question…"
              className="input-field resize-none flex-1 max-h-40 overflow-y-auto"
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault()
                  // Query submission will be wired in the next phase
                }
              }}
            />
            <button className="btn-primary shrink-0 h-9">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                viewBox="0 0 20 20"
                fill="currentColor"
                className="w-4 h-4"
              >
                <path d="M3.105 2.288a.75.75 0 0 0-.826.95l1.903 6.308H9.5a.75.75 0 0 1 0 1.5H4.182l-1.903 6.308a.75.75 0 0 0 .826.95 28.897 28.897 0 0 0 15.208-7.757.75.75 0 0 0 0-1.502A28.897 28.897 0 0 0 3.105 2.288Z" />
              </svg>
            </button>
          </div>
          <p className="text-center text-xs text-gray-600 mt-2">
            Analysis may take 20–40 seconds while agents gather live signals.
          </p>
        </div>
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
