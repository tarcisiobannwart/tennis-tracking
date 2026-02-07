import { PlayerActivity } from '@/services/playerService'

interface ActivityChartProps {
  activity: PlayerActivity[]
}

export const ActivityChart = ({ activity }: ActivityChartProps) => {
  const maxMatches = Math.max(...activity.map(a => a.matches), 1)

  return (
    <div className="space-y-4">
      <h3 className="text-sm font-medium">Atividade (12 meses)</h3>
      <div className="flex items-end justify-between gap-1 h-32">
        {activity.map((item, index) => {
          const height = (item.matches / maxMatches) * 100
          const monthLabel = new Date(item.month + '-01').toLocaleDateString('pt-BR', {
            month: 'short'
          })

          return (
            <div key={index} className="flex flex-col items-center flex-1 gap-1">
              <div className="relative flex-1 w-full flex items-end">
                <div
                  className="w-full bg-court-accent rounded-t transition-all hover:opacity-80"
                  style={{ height: `${height}%` }}
                  title={`${item.matches} jogos em ${monthLabel}`}
                />
              </div>
              <span className="text-xs text-muted-foreground">
                {monthLabel}
              </span>
            </div>
          )
        })}
      </div>
    </div>
  )
}
