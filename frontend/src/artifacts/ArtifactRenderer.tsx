import type { Artifact } from '@/types'
import { TextSummary } from './TextSummary'
import { TrendChart } from './TrendChart'
import { CompetitorScorecard } from './CompetitorScorecard'
import { SentimentHeatmap } from './SentimentHeatmap'
import { PricingTable } from './PricingTable'

interface Props {
  artifact: Artifact
}

export function ArtifactRenderer({ artifact }: Props) {
  const { data } = artifact

  const header = (
    <div className="flex items-center justify-between mb-3">
      <h3 className="text-sm font-semibold text-white">{artifact.title}</h3>
      <div className="flex items-center gap-2">
        {artifact.agents_completed?.length > 0 && (
          <span className="text-[10px] text-gray-500">
            {artifact.agents_completed.length} agents
          </span>
        )}
        <ConfidenceBadge value={artifact.confidence} />
      </div>
    </div>
  )

  let body: React.ReactNode

  switch (artifact.type) {
    case 'trend_chart':
      body = <TrendChart data={data} />
      break
    case 'competitor_scorecard':
      body = <CompetitorScorecard data={data} />
      break
    case 'sentiment_heatmap':
      body = <SentimentHeatmap data={data} />
      break
    case 'pricing_table':
      body = <PricingTable data={data} />
      break
    case 'text_summary':
    default:
      body = <TextSummary data={data} summary={artifact.summary} />
  }

  return (
    <div className="card ml-8">
      {header}
      {body}
    </div>
  )
}

function ConfidenceBadge({ value }: { value: number }) {
  const pct = Math.round(value * 100)
  const color =
    pct >= 70
      ? 'text-emerald-400 bg-emerald-400/10 border-emerald-400/20'
      : pct >= 40
        ? 'text-amber-400 bg-amber-400/10 border-amber-400/20'
        : 'text-red-400 bg-red-400/10 border-red-400/20'

  return (
    <span className={`text-[10px] font-mono px-1.5 py-0.5 rounded border ${color}`}>
      {pct}%
    </span>
  )
}
