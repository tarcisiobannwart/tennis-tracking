/**
 * WinLossLineChart - TT-133
 * Grafico de linhas sobrepostas de vitorias e derrotas (12+ meses)
 */

import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from 'recharts'
import { Card, CardContent } from '@/components/ui/card'
import { MonthlyData } from '@/services/statisticsService'

interface WinLossLineChartProps {
  data: MonthlyData[]
}

const WinLossLineChart = ({ data }: WinLossLineChartProps) => {
  return (
    <Card className="bg-slate-800 border-slate-700">
      <CardContent className="p-4">
        <h3 className="text-base font-semibold text-slate-100 mb-4">
          Vitorias vs Derrotas (12 meses)
        </h3>
        <div className="h-64">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={data} margin={{ top: 5, right: 10, left: -10, bottom: 5 }}>
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
              />
              <Legend
                wrapperStyle={{ color: '#94a3b8', fontSize: 12 }}
              />
              <Line
                type="monotone"
                dataKey="wins"
                name="Vitorias"
                stroke="#22c55e"
                strokeWidth={2}
                dot={{ r: 3, fill: '#22c55e' }}
                activeDot={{ r: 5 }}
              />
              <Line
                type="monotone"
                dataKey="losses"
                name="Derrotas"
                stroke="#ef4444"
                strokeWidth={2}
                dot={{ r: 3, fill: '#ef4444' }}
                activeDot={{ r: 5 }}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </CardContent>
    </Card>
  )
}

export default WinLossLineChart
