/**
 * ResultStreak - TT-133
 * Grid visual de sequencia de resultados (V/D)
 */

import { Card, CardContent } from '@/components/ui/card'
import { StreakItem } from '@/services/statisticsService'

interface ResultStreakProps {
  data: StreakItem[]
}

const ResultStreak = ({ data }: ResultStreakProps) => {
  if (data.length === 0) {
    return (
      <Card className="bg-slate-800 border-slate-700">
        <CardContent className="p-4">
          <h3 className="text-base font-semibold text-slate-100 mb-4">
            Sequencia de Resultados
          </h3>
          <div className="h-24 flex items-center justify-center text-slate-500 text-sm">
            Sem dados disponíveis
          </div>
        </CardContent>
      </Card>
    )
  }

  // Calcular sequencia atual
  let currentStreak = 0
  let streakType = data[0]?.result || 'V'
  for (const item of data) {
    if (item.result === streakType) {
      currentStreak++
    } else {
      break
    }
  }

  return (
    <Card className="bg-slate-800 border-slate-700">
      <CardContent className="p-4">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-base font-semibold text-slate-100">
            Sequencia de Resultados
          </h3>
          <div className="text-sm text-slate-400">
            Sequencia atual:{' '}
            <span
              className={`font-bold ${
                streakType === 'V' ? 'text-green-400' : 'text-red-400'
              }`}
            >
              {currentStreak} {streakType === 'V' ? 'vitorias' : 'derrotas'}
            </span>
          </div>
        </div>
        <div className="flex flex-wrap gap-1.5">
          {data.map((item, index) => (
            <div
              key={item.match_id}
              className="group relative"
            >
              <div
                className={`w-8 h-8 rounded flex items-center justify-center text-xs font-bold cursor-pointer transition-all hover:scale-110 ${
                  item.result === 'V'
                    ? 'bg-green-500/20 text-green-400 border border-green-500/30'
                    : 'bg-red-500/20 text-red-400 border border-red-500/30'
                }`}
              >
                {item.result}
              </div>
              {/* Tooltip */}
              <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 hidden group-hover:block z-10">
                <div className="bg-slate-900 border border-slate-700 rounded-lg p-2 text-xs whitespace-nowrap shadow-xl">
                  <p className="text-slate-300 font-medium">vs {item.opponent_name}</p>
                  <p className="text-slate-500">
                    {new Date(item.date).toLocaleDateString('pt-BR', {
                      day: '2-digit',
                      month: 'short',
                      year: 'numeric',
                    })}
                  </p>
                </div>
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  )
}

export default ResultStreak
