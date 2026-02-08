/**
 * SurfaceChart - TT-133
 * Grafico por tipo de piso (saibro, hard, grama, carpete)
 */

import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
  Cell,
} from 'recharts'
import { Card, CardContent } from '@/components/ui/card'
import { SurfaceStats } from '@/services/statisticsService'

interface SurfaceChartProps {
  data: SurfaceStats[]
}

const SURFACE_COLORS: Record<string, string> = {
  clay: '#f97316',
  hard: '#3b82f6',
  grass: '#22c55e',
  carpet: '#a855f7',
}

const SurfaceChart = ({ data }: SurfaceChartProps) => {
  if (data.length === 0) {
    return (
      <Card className="bg-slate-800 border-slate-700">
        <CardContent className="p-4">
          <h3 className="text-base font-semibold text-slate-100 mb-4">Por Tipo de Piso</h3>
          <div className="h-48 flex items-center justify-center text-slate-500 text-sm">
            Sem dados de superficie disponíveis
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card className="bg-slate-800 border-slate-700">
      <CardContent className="p-4">
        <h3 className="text-base font-semibold text-slate-100 mb-4">Por Tipo de Piso</h3>
        <div className="h-64">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={data} margin={{ top: 5, right: 10, left: -10, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
              <XAxis
                dataKey="label"
                tick={{ fill: '#94a3b8', fontSize: 11 }}
                tickLine={{ stroke: '#475569' }}
                axisLine={{ stroke: '#475569' }}
              />
              <YAxis
                tick={{ fill: '#94a3b8', fontSize: 11 }}
                tickLine={{ stroke: '#475569' }}
                axisLine={{ stroke: '#475569' }}
                allowDecimals={false}
              />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#1e293b',
                  border: '1px solid #334155',
                  borderRadius: '8px',
                  color: '#f1f5f9',
                }}
                formatter={(value: number, name: string) => [value, name]}
              />
              <Legend wrapperStyle={{ color: '#94a3b8', fontSize: 12 }} />
              <Bar dataKey="wins" name="Vitorias" stackId="a" radius={[0, 0, 0, 0]}>
                {data.map((entry) => (
                  <Cell
                    key={entry.surface}
                    fill={SURFACE_COLORS[entry.surface] || '#64748b'}
                    fillOpacity={0.9}
                  />
                ))}
              </Bar>
              <Bar dataKey="losses" name="Derrotas" stackId="a" radius={[4, 4, 0, 0]}>
                {data.map((entry) => (
                  <Cell
                    key={entry.surface}
                    fill={SURFACE_COLORS[entry.surface] || '#64748b'}
                    fillOpacity={0.4}
                  />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
        {/* Stats abaixo do grafico */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-2 mt-4">
          {data.map((item) => (
            <div
              key={item.surface}
              className="flex items-center gap-2 p-2 rounded-lg bg-slate-700/50"
            >
              <div
                className="w-3 h-3 rounded-sm"
                style={{ backgroundColor: SURFACE_COLORS[item.surface] || '#64748b' }}
              />
              <div className="flex-1 min-w-0">
                <p className="text-xs text-slate-300 truncate">{item.label}</p>
                <p className="text-xs text-slate-400">
                  {item.wins}V/{item.losses}D ({item.win_rate}%)
                </p>
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  )
}

export default SurfaceChart
