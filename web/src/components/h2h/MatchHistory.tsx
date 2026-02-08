/**
 * MatchHistory - TT-134
 * Lista de confrontos diretos H2H
 */

import { Calendar, MapPin, Clock, Trophy, CheckCircle2, XCircle } from 'lucide-react'
import { Card, CardContent } from '@/components/ui/card'
import { H2HMatchItem } from '@/services/h2hService'

interface MatchHistoryProps {
  matches: H2HMatchItem[]
  opponentName: string
}

const getSurfaceConfig = (surface?: string) => {
  switch (surface) {
    case 'hard':
      return { color: 'bg-blue-500', label: 'Hard Court' }
    case 'clay':
      return { color: 'bg-orange-500', label: 'Saibro' }
    case 'grass':
      return { color: 'bg-green-500', label: 'Grama' }
    case 'carpet':
      return { color: 'bg-purple-500', label: 'Carpete' }
    default:
      return { color: 'bg-slate-500', label: '' }
  }
}

const formatDate = (dateStr?: string) => {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return date.toLocaleDateString('pt-BR', {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
  })
}

const formatDuration = (minutes?: number) => {
  if (!minutes) return null
  const hours = Math.floor(minutes / 60)
  const mins = minutes % 60
  return `${hours}h${mins.toString().padStart(2, '0')}`
}

const MatchHistory = ({ matches, opponentName }: MatchHistoryProps) => {
  if (matches.length === 0) {
    return (
      <Card className="bg-slate-800 border-slate-700">
        <CardContent className="p-4">
          <h3 className="text-base font-semibold text-slate-100 mb-4">
            Historico de Confrontos
          </h3>
          <div className="h-24 flex items-center justify-center text-slate-500 text-sm">
            Nenhum confronto encontrado
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card className="bg-slate-800 border-slate-700">
      <CardContent className="p-4">
        <h3 className="text-base font-semibold text-slate-100 mb-4">
          Historico de Confrontos ({matches.length})
        </h3>
        <div className="space-y-3">
          {matches.map((match) => {
            const isWin = match.result === 'win'
            const surfaceConfig = getSurfaceConfig(match.surface)

            return (
              <div
                key={match.match_id}
                className="p-3 rounded-lg bg-slate-700/50 hover:bg-slate-700/80 transition-colors"
              >
                <div className="flex items-center justify-between gap-3">
                  {/* Resultado */}
                  <div
                    className={`w-9 h-9 rounded-full flex items-center justify-center flex-shrink-0 ${
                      isWin
                        ? 'bg-green-500/10 text-green-400'
                        : 'bg-red-500/10 text-red-400'
                    }`}
                  >
                    {isWin ? (
                      <CheckCircle2 className="w-5 h-5" />
                    ) : (
                      <XCircle className="w-5 h-5" />
                    )}
                  </div>

                  {/* Info */}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      <span
                        className={`text-sm font-bold ${
                          isWin ? 'text-green-400' : 'text-red-400'
                        }`}
                      >
                        {isWin ? 'Vitoria' : 'Derrota'}
                      </span>
                      <span className="text-lg font-bold text-court-accent">
                        {match.player_sets}-{match.opponent_sets}
                      </span>
                    </div>

                    {/* Sets detail */}
                    <div className="flex items-center gap-1.5 mb-1.5 flex-wrap">
                      {match.sets_detail.map((set) => (
                        <span
                          key={set.set_number}
                          className="px-1.5 py-0.5 rounded bg-slate-600 text-slate-300 text-xs font-mono"
                        >
                          {set.player_games}-{set.opponent_games}
                          {set.player_tiebreak !== undefined && (
                            <sup className="text-[9px]">{set.player_tiebreak}</sup>
                          )}
                        </span>
                      ))}
                    </div>

                    {/* Meta */}
                    <div className="flex items-center gap-3 text-xs text-slate-400 flex-wrap">
                      <div className="flex items-center gap-1">
                        <Calendar className="w-3 h-3" />
                        <span>{formatDate(match.date)}</span>
                      </div>
                      {match.tournament && (
                        <div className="flex items-center gap-1">
                          <Trophy className="w-3 h-3" />
                          <span className="truncate max-w-[150px]">{match.tournament}</span>
                        </div>
                      )}
                      {match.duration_minutes && (
                        <div className="flex items-center gap-1">
                          <Clock className="w-3 h-3" />
                          <span>{formatDuration(match.duration_minutes)}</span>
                        </div>
                      )}
                      {match.surface && (
                        <div className="flex items-center gap-1">
                          <div className={`w-2 h-2 rounded-sm ${surfaceConfig.color}`} />
                          <span>{surfaceConfig.label}</span>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            )
          })}
        </div>
      </CardContent>
    </Card>
  )
}

export default MatchHistory
