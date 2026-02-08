/**
 * MonthlyChart - TT-133
 * Grafico de barras mensal (jogos por mes)
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
} from 'recharts'
import { Card, CardContent } from '@/components/ui/card'
import { MonthlyData } from '@/services/statisticsService'

interface MonthlyChartProps {
  data: MonthlyData[]
}

const MonthlyChart = ({ data }: MonthlyChartProps) => {
  return (
    <Card className="bg-slate-800 border-slate-700">
      <CardContent className="p-4">
        <h3 className="text-base font-semibold text-slate-100 mb-4">Jogos por Mes</h3>
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
              />
              <Legend
                wrapperStyle={{ color: '#94a3b8', fontSize: 12 }}
              />
              <Bar
                dataKey="total"
                name="Total"
                fill="#3b82f6"
                radius={[4, 4, 0, 0]}
              />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </CardContent>
    </Card>
  )
}

export default MonthlyChart
