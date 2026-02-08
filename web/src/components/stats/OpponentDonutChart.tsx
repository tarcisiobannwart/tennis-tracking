/**
 * OpponentDonutChart - TT-133
 * Donut charts para lateralidade (destro/canhoto) e backhand (1/2 maos)
 */

import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend } from 'recharts'
import { Card, CardContent } from '@/components/ui/card'

interface DonutData {
  label: string
  total: number
  wins: number
  losses: number
  win_rate: number
}

interface OpponentDonutChartProps {
  title: string
  data: DonutData[]
}

const COLORS = ['#22c55e', '#ef4444', '#3b82f6', '#f97316', '#a855f7', '#eab308']

const OpponentDonutChart = ({ title, data }: OpponentDonutChartProps) => {
  if (data.length === 0) {
    return (
      <Card className="bg-slate-800 border-slate-700">
        <CardContent className="p-4">
          <h3 className="text-base font-semibold text-slate-100 mb-4">{title}</h3>
          <div className="h-48 flex items-center justify-center text-slate-500 text-sm">
            Sem dados disponíveis
          </div>
        </CardContent>
      </Card>
    )
  }

  const chartData = data.map((item) => ({
    name: item.label,
    value: item.total,
    wins: item.wins,
    losses: item.losses,
    win_rate: item.win_rate,
  }))

  const totalMatches = chartData.reduce((acc, item) => acc + item.value, 0)

  return (
    <Card className="bg-slate-800 border-slate-700">
      <CardContent className="p-4">
        <h3 className="text-base font-semibold text-slate-100 mb-4">{title}</h3>
        <div className="h-52">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={chartData}
                cx="50%"
                cy="50%"
                innerRadius={50}
                outerRadius={75}
                paddingAngle={3}
                dataKey="value"
                label={({ name, percent }) =>
                  `${name} ${(percent * 100).toFixed(0)}%`
                }
                labelLine={false}
              >
                {chartData.map((_, index) => (
                  <Cell
                    key={`cell-${index}`}
                    fill={COLORS[index % COLORS.length]}
                    stroke="transparent"
                  />
                ))}
              </Pie>
              <Tooltip
                contentStyle={{
                  backgroundColor: '#1e293b',
                  border: '1px solid #334155',
                  borderRadius: '8px',
                  color: '#f1f5f9',
                }}
                formatter={(value: number, name: string, props: any) => [
                  `${value} jogos (${props.payload.wins}V/${props.payload.losses}D - ${props.payload.win_rate}%)`,
                  name,
                ]}
              />
            </PieChart>
          </ResponsiveContainer>
        </div>
        {/* Legenda com detalhes */}
        <div className="space-y-2 mt-2">
          {data.map((item, index) => (
            <div key={item.label} className="flex items-center justify-between text-sm">
              <div className="flex items-center gap-2">
                <div
                  className="w-3 h-3 rounded-full"
                  style={{ backgroundColor: COLORS[index % COLORS.length] }}
                />
                <span className="text-slate-300">{item.label}</span>
              </div>
              <div className="text-slate-400">
                {item.wins}V/{item.losses}D ({item.win_rate}%)
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  )
}

export default OpponentDonutChart
