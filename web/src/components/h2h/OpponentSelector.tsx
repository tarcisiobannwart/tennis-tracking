/**
 * OpponentSelector - TT-134
 * Seletor de adversario para H2H
 */

import { useState, useMemo } from 'react'
import { Search, User, ChevronRight } from 'lucide-react'
import { Card, CardContent } from '@/components/ui/card'
import { OpponentSummary } from '@/services/h2hService'

interface OpponentSelectorProps {
  opponents: OpponentSummary[]
  selectedId?: string
  onSelect: (opponentId: string) => void
  isLoading?: boolean
}

const OpponentSelector = ({
  opponents,
  selectedId,
  onSelect,
  isLoading = false,
}: OpponentSelectorProps) => {
  const [searchTerm, setSearchTerm] = useState('')

  const filteredOpponents = useMemo(() => {
    if (!searchTerm.trim()) return opponents
    const term = searchTerm.toLowerCase()
    return opponents.filter((opp) => opp.name.toLowerCase().includes(term))
  }, [opponents, searchTerm])

  const formatDate = (dateStr?: string) => {
    if (!dateStr) return ''
    const date = new Date(dateStr)
    return date.toLocaleDateString('pt-BR', {
      day: '2-digit',
      month: 'short',
      year: 'numeric',
    })
  }

  return (
    <Card className="bg-slate-800 border-slate-700">
      <CardContent className="p-4">
        <h3 className="text-base font-semibold text-slate-100 mb-4">
          Selecionar Adversario
        </h3>

        {/* Search */}
        <div className="relative mb-4">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
          <input
            type="text"
            placeholder="Buscar adversario..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-10 pr-4 py-2.5 bg-slate-700 border border-slate-600 rounded-lg text-slate-100 placeholder:text-slate-500 text-sm focus:outline-none focus:ring-2 focus:ring-court-accent focus:border-transparent transition-all"
          />
        </div>

        {/* Lista de oponentes */}
        <div className="space-y-2 max-h-[400px] overflow-y-auto">
          {isLoading ? (
            <div className="space-y-2">
              {[...Array(5)].map((_, i) => (
                <div key={i} className="h-16 bg-slate-700 rounded-lg animate-pulse" />
              ))}
            </div>
          ) : filteredOpponents.length > 0 ? (
            filteredOpponents.map((opponent) => (
              <button
                key={opponent.id}
                onClick={() => onSelect(opponent.id)}
                className={`w-full flex items-center gap-3 p-3 rounded-lg transition-all text-left ${
                  selectedId === opponent.id
                    ? 'bg-court-accent/10 border border-court-accent/30'
                    : 'bg-slate-700/50 hover:bg-slate-700 border border-transparent'
                }`}
              >
                {/* Avatar */}
                <div className="w-10 h-10 rounded-full bg-slate-600 flex items-center justify-center flex-shrink-0 overflow-hidden">
                  {opponent.avatar_url ? (
                    <img
                      src={opponent.avatar_url}
                      alt={opponent.name}
                      className="w-full h-full object-cover"
                    />
                  ) : (
                    <User className="w-5 h-5 text-slate-400" />
                  )}
                </div>

                {/* Info */}
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-slate-200 truncate">
                    {opponent.name}
                  </p>
                  <div className="flex items-center gap-2 text-xs text-slate-400">
                    <span>
                      {opponent.total_matches} {opponent.total_matches === 1 ? 'jogo' : 'jogos'}
                    </span>
                    <span className="text-slate-600">|</span>
                    <span className="text-green-400">{opponent.player_wins}V</span>
                    <span className="text-slate-600">/</span>
                    <span className="text-red-400">{opponent.opponent_wins}D</span>
                  </div>
                  {opponent.last_match_date && (
                    <p className="text-xs text-slate-500 mt-0.5">
                      Ultimo: {formatDate(opponent.last_match_date)}
                    </p>
                  )}
                </div>

                {/* Arrow */}
                <ChevronRight className="w-4 h-4 text-slate-500 flex-shrink-0" />
              </button>
            ))
          ) : (
            <div className="text-center py-8 text-slate-500 text-sm">
              {searchTerm
                ? 'Nenhum adversario encontrado'
                : 'Voce ainda nao possui adversarios'}
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  )
}

export default OpponentSelector
