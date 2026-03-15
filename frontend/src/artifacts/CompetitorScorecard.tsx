import type { ArtifactData } from '@/types'

interface Props {
  data: ArtifactData
}

export function CompetitorScorecard({ data }: Props) {
  const competitors = data.competitors ?? []

  if (competitors.length === 0) {
    return <p className="text-xs text-gray-500 italic">No competitor data available.</p>
  }

  // Collect all unique score dimensions across competitors
  const dimensions = Array.from(
    new Set(competitors.flatMap((c) => Object.keys(c.scores))),
  )

  return (
    <div className="space-y-3">
      {/* Score comparison table */}
      <div className="overflow-x-auto">
        <table className="w-full text-xs">
          <thead>
            <tr className="border-b border-gray-700">
              <th className="text-left py-2 pr-3 text-gray-400 font-medium">Competitor</th>
              {dimensions.map((dim) => (
                <th key={dim} className="text-center py-2 px-2 text-gray-400 font-medium capitalize">
                  {dim.replace(/_/g, ' ')}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {competitors.map((comp) => (
              <tr key={comp.name} className="border-b border-gray-800/50">
                <td className="py-2.5 pr-3 font-medium text-white">{comp.name}</td>
                {dimensions.map((dim) => {
                  const val = comp.scores[dim] ?? 0
                  return (
                    <td key={dim} className="text-center py-2.5 px-2">
                      <ScorePill value={val} />
                    </td>
                  )
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Strengths / Weaknesses detail cards */}
      {competitors.some((c) => c.strengths?.length || c.weaknesses?.length) && (
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 pt-1">
          {competitors.map((comp) => (
            <div
              key={comp.name}
              className="rounded-lg bg-gray-800/50 border border-gray-700/50 px-3 py-2"
            >
              <p className="text-xs font-semibold text-white mb-1.5">{comp.name}</p>

              {comp.strengths && comp.strengths.length > 0 && (
                <div className="mb-1">
                  <span className="text-[10px] text-emerald-400 uppercase tracking-wider">Strengths</span>
                  <ul className="mt-0.5 space-y-0.5">
                    {comp.strengths.map((s, i) => (
                      <li key={i} className="text-[11px] text-gray-300 leading-snug flex gap-1.5">
                        <span className="text-emerald-500 shrink-0">+</span>
                        {s}
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {comp.weaknesses && comp.weaknesses.length > 0 && (
                <div>
                  <span className="text-[10px] text-red-400 uppercase tracking-wider">Weaknesses</span>
                  <ul className="mt-0.5 space-y-0.5">
                    {comp.weaknesses.map((w, i) => (
                      <li key={i} className="text-[11px] text-gray-300 leading-snug flex gap-1.5">
                        <span className="text-red-500 shrink-0">-</span>
                        {w}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

function ScorePill({ value }: { value: number }) {
  const pct = Math.round(value * 100)
  const color =
    pct >= 70
      ? 'text-emerald-400 bg-emerald-400/10'
      : pct >= 40
        ? 'text-amber-400 bg-amber-400/10'
        : 'text-red-400 bg-red-400/10'

  return (
    <span className={`inline-block px-1.5 py-0.5 rounded font-mono text-[11px] ${color}`}>
      {pct}
    </span>
  )
}
