/**
 * Match Result Card - Card de resultado de partida para feed social.
 *
 * Implementado para TT-130: Exibe placar de sets, avatares dos jogadores,
 * ranking de origem, e badge do tipo de partida.
 */

import React from 'react'
import { Trophy, Clock, MapPin } from 'lucide-react'
import { Card, CardContent } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'

interface Player {
  id: string
  name: string
  avatar?: string
  ranking?: number
}

interface MatchResult {
  match_id: string
  player1: Player
  player2: Player
  score: string // Ex: "6-4, 7-5"
  winner_id: string
  match_type?: string // singles, doubles
  tournament?: string
  court?: string
  duration?: string
  date: string
}

interface MatchResultCardProps {
  matchResult: MatchResult
}

export const MatchResultCard: React.FC<MatchResultCardProps> = ({ matchResult }) => {
  const {
    player1,
    player2,
    score,
    winner_id,
    match_type = 'singles',
    tournament,
    court,
    duration,
    date,
  } = matchResult

  const isPlayer1Winner = winner_id === player1.id
  const isPlayer2Winner = winner_id === player2.id

  // Parse score to get sets
  const sets = score.split(',').map((s) => s.trim())

  return (
    <Card className="overflow-hidden">
      <CardContent className="p-0">
        {/* Header com tipo de partida e torneio */}
        <div className="bg-gradient-to-r from-court-accent/20 to-court-accent/10 px-4 py-3 border-b border-slate-700">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Trophy className="w-4 h-4 text-court-accent" />
              <span className="text-sm font-medium text-slate-200">
                {tournament || 'Partida'}
              </span>
            </div>
            <Badge variant="outline" className="text-xs">
              {match_type === 'singles' ? 'Simples' : 'Duplas'}
            </Badge>
          </div>
        </div>

        {/* Players e Placar */}
        <div className="p-6">
          {/* Player 1 */}
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-3 flex-1">
              <div className="relative">
                {player1.avatar ? (
                  <img
                    src={player1.avatar}
                    alt={player1.name}
                    className="w-12 h-12 rounded-full object-cover border-2 border-slate-700"
                  />
                ) : (
                  <div className="w-12 h-12 rounded-full bg-slate-700 flex items-center justify-center text-lg font-semibold text-slate-300">
                    {player1.name.charAt(0)}
                  </div>
                )}
                {isPlayer1Winner && (
                  <div className="absolute -top-1 -right-1 w-5 h-5 bg-yellow-500 rounded-full flex items-center justify-center">
                    <Trophy className="w-3 h-3 text-yellow-900" />
                  </div>
                )}
              </div>
              <div>
                <div className="font-semibold text-slate-100">{player1.name}</div>
                {player1.ranking && (
                  <div className="text-xs text-slate-400">Ranking: #{player1.ranking}</div>
                )}
              </div>
            </div>

            {/* Sets Player 1 */}
            <div className="flex gap-2">
              {sets.map((set, idx) => {
                const [p1Score, p2Score] = set.split('-').map((s) => s.trim())
                const wonSet = parseInt(p1Score) > parseInt(p2Score)
                return (
                  <div
                    key={idx}
                    className={`w-10 h-10 rounded flex items-center justify-center text-sm font-bold ${
                      wonSet
                        ? 'bg-court-accent text-white'
                        : 'bg-slate-700 text-slate-300'
                    }`}
                  >
                    {p1Score}
                  </div>
                )
              })}
            </div>
          </div>

          {/* Player 2 */}
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3 flex-1">
              <div className="relative">
                {player2.avatar ? (
                  <img
                    src={player2.avatar}
                    alt={player2.name}
                    className="w-12 h-12 rounded-full object-cover border-2 border-slate-700"
                  />
                ) : (
                  <div className="w-12 h-12 rounded-full bg-slate-700 flex items-center justify-center text-lg font-semibold text-slate-300">
                    {player2.name.charAt(0)}
                  </div>
                )}
                {isPlayer2Winner && (
                  <div className="absolute -top-1 -right-1 w-5 h-5 bg-yellow-500 rounded-full flex items-center justify-center">
                    <Trophy className="w-3 h-3 text-yellow-900" />
                  </div>
                )}
              </div>
              <div>
                <div className="font-semibold text-slate-100">{player2.name}</div>
                {player2.ranking && (
                  <div className="text-xs text-slate-400">Ranking: #{player2.ranking}</div>
                )}
              </div>
            </div>

            {/* Sets Player 2 */}
            <div className="flex gap-2">
              {sets.map((set, idx) => {
                const [p1Score, p2Score] = set.split('-').map((s) => s.trim())
                const wonSet = parseInt(p2Score) > parseInt(p1Score)
                return (
                  <div
                    key={idx}
                    className={`w-10 h-10 rounded flex items-center justify-center text-sm font-bold ${
                      wonSet
                        ? 'bg-court-accent text-white'
                        : 'bg-slate-700 text-slate-300'
                    }`}
                  >
                    {p2Score}
                  </div>
                )
              })}
            </div>
          </div>
        </div>

        {/* Footer com info adicional */}
        <div className="px-6 pb-4 flex items-center gap-4 text-xs text-slate-400">
          {court && (
            <div className="flex items-center gap-1">
              <MapPin className="w-3 h-3" />
              <span>{court}</span>
            </div>
          )}
          {duration && (
            <div className="flex items-center gap-1">
              <Clock className="w-3 h-3" />
              <span>{duration}</span>
            </div>
          )}
          <div className="ml-auto">
            {new Date(date).toLocaleDateString('pt-BR', {
              day: '2-digit',
              month: 'short',
              year: 'numeric',
            })}
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
