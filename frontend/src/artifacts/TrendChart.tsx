import {
  ResponsiveContainer,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
} from 'recharts'
import type { ArtifactData } from '@/types'

interface Props {
  data: ArtifactData
}

export function TrendChart({ data }: Props) {
  const points = data.trends ?? []

  if (points.length === 0) {
    return <p className="text-xs text-gray-500 italic">No trend data available.</p>
  }

  return (
    <div className="h-64 w-full">
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart data={points} margin={{ top: 8, right: 8, bottom: 0, left: -12 }}>
          <defs>
            <linearGradient id="trendFill" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#6366f1" stopOpacity={0.3} />
              <stop offset="95%" stopColor="#6366f1" stopOpacity={0} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" />
          <XAxis
            dataKey="label"
            tick={{ fontSize: 10, fill: '#6b7280' }}
            axisLine={{ stroke: '#374151' }}
            tickLine={false}
          />
          <YAxis
            tick={{ fontSize: 10, fill: '#6b7280' }}
            axisLine={{ stroke: '#374151' }}
            tickLine={false}
          />
          <Tooltip
            contentStyle={{
              backgroundColor: '#111827',
              border: '1px solid #374151',
              borderRadius: 8,
              fontSize: 12,
            }}
            labelStyle={{ color: '#9ca3af' }}
            itemStyle={{ color: '#a5b4fc' }}
          />
          <Area
            type="monotone"
            dataKey="value"
            stroke="#6366f1"
            strokeWidth={2}
            fill="url(#trendFill)"
            dot={{ r: 3, fill: '#6366f1', stroke: '#111827', strokeWidth: 2 }}
            activeDot={{ r: 5 }}
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  )
}
