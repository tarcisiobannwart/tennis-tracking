/**
 * StatsSummaryCard - TT-133
 * Cards de resumo de vitorias e derrotas
 */

import { Trophy, XCircle, Target, TrendingUp } from 'lucide-react'
import { Card, CardContent } from '@/components/ui/card'
import { OverallStats } from '@/services/statisticsService'

interface StatsSummaryCardProps {
  stats: OverallStats
}

const StatsSummaryCard = ({ stats }: StatsSummaryCardProps) => {
  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
      {/* Total de Jogos */}
      <Card className="bg-slate-800 border-slate-700">
        <CardContent className="p-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-full bg-blue-500/10 flex items-center justify-center">
              <Target className="w-5 h-5 text-blue-400" />
            </div>
            <div>
              <p className="text-xs text-slate-400">Total de Jogos</p>
              <p className="text-2xl font-bold text-slate-100">{stats.total_matches}</p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Vitorias */}
      <Card className="bg-slate-800 border-slate-700">
        <CardContent className="p-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-full bg-green-500/10 flex items-center justify-center">
              <Trophy className="w-5 h-5 text-green-400" />
            </div>
            <div>
              <p className="text-xs text-slate-400">Vitorias</p>
              <p className="text-2xl font-bold text-green-400">{stats.wins}</p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Derrotas */}
      <Card className="bg-slate-800 border-slate-700">
        <CardContent className="p-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-full bg-red-500/10 flex items-center justify-center">
              <XCircle className="w-5 h-5 text-red-400" />
            </div>
            <div>
              <p className="text-xs text-slate-400">Derrotas</p>
              <p className="text-2xl font-bold text-red-400">{stats.losses}</p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Aproveitamento */}
      <Card className="bg-slate-800 border-slate-700">
        <CardContent className="p-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-full bg-court-accent/10 flex items-center justify-center">
              <TrendingUp className="w-5 h-5 text-court-accent" />
            </div>
            <div>
              <p className="text-xs text-slate-400">Aproveitamento</p>
              <p className="text-2xl font-bold text-court-accent">{stats.win_rate}%</p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

export default StatsSummaryCard
