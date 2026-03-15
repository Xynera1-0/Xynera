const AGENT_LABELS: Record<string, string> = {
  market_trend: 'Market Trends',
  competitive_landscape: 'Competitive Intel',
  win_loss: 'Win / Loss',
  pricing: 'Pricing',
  messaging: 'Messaging',
  adjacent_market: 'Adjacent Markets',
}

const ALL_AGENTS = Object.keys(AGENT_LABELS)

export function ProcessingIndicator() {
  return (
    <div className="flex justify-start">
      <div className="max-w-2xl w-full pl-8 space-y-3">
        <p className="text-sm text-gray-400 flex items-center gap-2">
          <span className="relative flex h-2.5 w-2.5">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-brand-400 opacity-75" />
            <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-brand-500" />
          </span>
          Agents analyzing your query...
        </p>

        <div className="flex flex-wrap gap-2">
          {ALL_AGENTS.map((agent, i) => (
            <span
              key={agent}
              className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium bg-gray-800 border border-gray-700 text-gray-400"
              style={{ animationDelay: `${i * 150}ms` }}
            >
              <span className="w-1.5 h-1.5 rounded-full bg-amber-400 animate-pulse" />
              {AGENT_LABELS[agent]}
            </span>
          ))}
        </div>
      </div>
    </div>
  )
}
