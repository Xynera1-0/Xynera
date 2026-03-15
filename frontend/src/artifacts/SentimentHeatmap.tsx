import type { ArtifactData } from '@/types'

interface Props {
  data: ArtifactData
}

export function SentimentHeatmap({ data }: Props) {
  const segments = data.sentiment_segments ?? []

  if (segments.length === 0) {
    return <p className="text-xs text-gray-500 italic">No sentiment data available.</p>
  }

  // Collect all unique categories across segments
  const categories = Array.from(
    new Set(segments.flatMap((seg) => seg.values.map((v) => v.category))),
  )

  return (
    <div className="overflow-x-auto">
      <table className="w-full text-xs">
        <thead>
          <tr className="border-b border-gray-700">
            <th className="text-left py-2 pr-3 text-gray-400 font-medium">Segment</th>
            {categories.map((cat) => (
              <th key={cat} className="text-center py-2 px-1.5 text-gray-400 font-medium capitalize">
                {cat.replace(/_/g, ' ')}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {segments.map((seg) => {
            const valueMap = Object.fromEntries(seg.values.map((v) => [v.category, v.score]))
            return (
              <tr key={seg.label} className="border-b border-gray-800/50">
                <td className="py-2 pr-3 text-white font-medium whitespace-nowrap">
                  {seg.label}
                </td>
                {categories.map((cat) => {
                  const score = valueMap[cat] ?? 0
                  return (
                    <td key={cat} className="text-center py-2 px-1.5">
                      <HeatCell value={score} />
                    </td>
                  )
                })}
              </tr>
            )
          })}
        </tbody>
      </table>

      {/* Legend */}
      <div className="flex items-center gap-3 mt-3 text-[10px] text-gray-500">
        <span>Sentiment:</span>
        <div className="flex items-center gap-1">
          <span className="w-3 h-3 rounded-sm bg-red-500/80" /> Negative
        </div>
        <div className="flex items-center gap-1">
          <span className="w-3 h-3 rounded-sm bg-amber-500/80" /> Neutral
        </div>
        <div className="flex items-center gap-1">
          <span className="w-3 h-3 rounded-sm bg-emerald-500/80" /> Positive
        </div>
      </div>
    </div>
  )
}

/**
 * Renders a color-coded cell based on score [-1, 1] mapped to [red, amber, green].
 * If score is [0, 1], treat 0 as negative, 0.5 as neutral, 1 as positive.
 */
function HeatCell({ value }: { value: number }) {
  // Normalize to 0–1 range
  const norm = value < 0 ? (value + 1) / 2 : value

  let bg: string
  let text: string
  if (norm >= 0.65) {
    bg = 'bg-emerald-500/20'
    text = 'text-emerald-400'
  } else if (norm >= 0.35) {
    bg = 'bg-amber-500/20'
    text = 'text-amber-400'
  } else {
    bg = 'bg-red-500/20'
    text = 'text-red-400'
  }

  const display = value < 0
    ? value.toFixed(2)
    : (value * 100).toFixed(0)

  return (
    <span className={`inline-block w-10 py-1 rounded font-mono text-[11px] ${bg} ${text}`}>
      {display}
    </span>
  )
}
