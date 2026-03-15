import type { ArtifactData } from '@/types'

interface Props {
  data: ArtifactData
  summary?: string
}

export function TextSummary({ data, summary }: Props) {
  const facts = data.high_confidence_facts?.length ? data.high_confidence_facts : data.all_facts
  const sources = data.top_sources ?? []
  const summaries = data.agent_summaries ?? {}
  const meta = data.request_metadata
  const summaryText = summary || data.summary || ''

  return (
    <div className="space-y-4 text-sm">
      {/* Executive Summary */}
      {summaryText && (
        <section>
          <h4 className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">
            Executive Summary
          </h4>
          <div className="text-gray-200 leading-relaxed whitespace-pre-line">
            {summaryText}
          </div>
        </section>
      )}

      {/* Key findings */}
      {facts && facts.length > 0 && (
        <section>
          <h4 className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">
            Key findings
          </h4>
          <ul className="space-y-1.5">
            {facts.map((fact, i) => (
              <li key={i} className="flex gap-2 text-gray-200 leading-relaxed">
                <span className="text-brand-400 mt-0.5 shrink-0">&#9679;</span>
                <span>{fact}</span>
              </li>
            ))}
          </ul>
        </section>
      )}

      {/* Agent breakdown */}
      {Object.keys(summaries).length > 0 && (
        <section>
          <h4 className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">
            Agent breakdown
          </h4>
          <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
            {Object.entries(summaries).map(([agent, summary]) => (
              <div
                key={agent}
                className="rounded-lg bg-gray-800/60 border border-gray-700/50 px-3 py-2"
              >
                <p className="text-xs font-medium text-gray-300 capitalize">
                  {agent.replace(/_/g, ' ')}
                </p>
                <div className="flex items-baseline gap-2 mt-1">
                  <span className="text-lg font-semibold text-white">{summary.fact_count}</span>
                  <span className="text-[10px] text-gray-500">facts</span>
                  <ConfidenceBar value={summary.confidence} />
                </div>
              </div>
            ))}
          </div>
        </section>
      )}

      {/* Sources */}
      {sources.length > 0 && (
        <section>
          <h4 className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">
            Sources
          </h4>
          <div className="space-y-1.5">
            {sources.slice(0, 8).map((src, i) => (
              <div key={i} className="flex gap-2 text-xs">
                <span className="text-gray-600 shrink-0">[{i + 1}]</span>
                <div className="min-w-0">
                  <a
                    href={src.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-brand-400 hover:text-brand-300 truncate block"
                  >
                    {src.title || src.url}
                  </a>
                  {src.snippet && (
                    <p className="text-gray-500 truncate">{src.snippet}</p>
                  )}
                </div>
              </div>
            ))}
          </div>
        </section>
      )}

      {/* Metadata footer */}
      {meta && (
        <div className="flex flex-wrap gap-x-4 gap-y-1 text-[10px] text-gray-600 pt-2 border-t border-gray-800">
          <span>Processed in {Math.round(meta.processing_time_ms)}ms</span>
          <span>{meta.agents_used?.length ?? 0} agents</span>
          <span>{Math.round(meta.final_confidence * 100)}% overall confidence</span>
        </div>
      )}
    </div>
  )
}

function ConfidenceBar({ value }: { value: number }) {
  const pct = Math.round(value * 100)
  const color = pct >= 70 ? 'bg-emerald-500' : pct >= 40 ? 'bg-amber-500' : 'bg-red-500'
  return (
    <div className="flex-1 h-1 rounded-full bg-gray-700 overflow-hidden ml-1">
      <div className={`h-full rounded-full ${color}`} style={{ width: `${pct}%` }} />
    </div>
  )
}
