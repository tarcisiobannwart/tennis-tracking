import { useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import {
  ArrowLeft,
  Trophy,
  Users,
  Calendar,
  MapPin,
  TrendingUp,
  TrendingDown,
  Minus,
  ChevronLeft,
  ChevronRight,
  BarChart3,
  Settings,
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { PageTransition } from '@/components/animations'

// Mock data
const mockRanking = {
  id: '1',
  name: 'Ranking Clube Paulistano 2026',
  description: 'Ranking oficial do clube para o ano de 2026',
  ranking_type: 'round_robin',
  status: 'active',
  venue: 'Clube Paulistano',
  location: 'São Paulo, SP',
  current_round: 3,
  total_rounds: 8,
  total_participants: 16,
  start_date: '2026-01-15',
  end_date: '2026-06-30',
}

const mockStandings = [
  {
    position: 1,
    previous_position: 2,
    user_id: 'u1',
    user_name: 'Carlos Silva',
    points: 24.0,
    matches_played: 8,
    matches_won: 8,
    matches_lost: 0,
    sets_won: 16,
    sets_lost: 2,
    win_rate: 100.0,
    set_ratio: 8.0,
    position_history: [5, 3, 2, 1],
  },
  {
    position: 2,
    previous_position: 1,
    user_id: 'u2',
    user_name: 'Ana Martins',
    points: 21.5,
    matches_played: 8,
    matches_won: 7,
    matches_lost: 1,
    sets_won: 15,
    sets_lost: 4,
    win_rate: 87.5,
    set_ratio: 3.75,
    position_history: [2, 1, 1, 2],
  },
  {
    position: 3,
    previous_position: 4,
    user_id: 'u3',
    user_name: 'Pedro Santos',
    points: 18.0,
    matches_played: 8,
    matches_won: 6,
    matches_lost: 2,
    sets_won: 13,
    sets_lost: 6,
    win_rate: 75.0,
    set_ratio: 2.17,
    position_history: [6, 5, 4, 3],
  },
  {
    position: 4,
    previous_position: 3,
    user_id: 'u4',
    user_name: 'Maria Oliveira',
    points: 16.5,
    matches_played: 8,
    matches_won: 5,
    matches_lost: 3,
    sets_won: 12,
    sets_lost: 8,
    win_rate: 62.5,
    set_ratio: 1.5,
    position_history: [4, 3, 3, 4],
  },
  {
    position: 5,
    previous_position: 6,
    user_id: 'u5',
    user_name: 'João Costa',
    points: 15.5,
    matches_played: 6,
    matches_won: 4,
    matches_lost: 2,
    sets_won: 10,
    sets_lost: 6,
    win_rate: 66.7,
    set_ratio: 1.67,
    position_history: [8, 7, 6, 5],
  },
]

const mockRounds = [
  { round_number: 1, name: 'Rodada 1', total_matches: 8, completed_matches: 8, is_completed: true },
  { round_number: 2, name: 'Rodada 2', total_matches: 8, completed_matches: 8, is_completed: true },
  { round_number: 3, name: 'Rodada 3', total_matches: 8, completed_matches: 5, is_completed: false },
  { round_number: 4, name: 'Rodada 4', total_matches: 8, completed_matches: 0, is_completed: false },
]

const RankingDetail = () => {
  const { id } = useParams<{ id: string }>()
  const [selectedRound, setSelectedRound] = useState(mockRanking.current_round)

  const getPositionChange = (current: number, previous: number | null) => {
    if (!previous) return null
    const change = previous - current
    if (change > 0) return { direction: 'up', value: change }
    if (change < 0) return { direction: 'down', value: Math.abs(change) }
    return { direction: 'stable', value: 0 }
  }

  const handlePreviousRound = () => {
    if (selectedRound > 1) setSelectedRound(selectedRound - 1)
  }

  const handleNextRound = () => {
    if (selectedRound < mockRanking.current_round) setSelectedRound(selectedRound + 1)
  }

  return (
    <PageTransition>
      <div className="space-y-6 p-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Button variant="outline" size="sm" asChild>
              <Link to="/rankings">
                <ArrowLeft className="h-4 w-4 mr-2" />
                Voltar
              </Link>
            </Button>
            <div>
              <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
                {mockRanking.name}
              </h1>
              <div className="flex items-center gap-4 mt-2 text-sm text-gray-600 dark:text-gray-400">
                <div className="flex items-center gap-1">
                  <MapPin className="h-4 w-4" />
                  <span>{mockRanking.location}</span>
                </div>
                <div className="flex items-center gap-1">
                  <Users className="h-4 w-4" />
                  <span>{mockRanking.total_participants} participantes</span>
                </div>
                <div className="flex items-center gap-1">
                  <Calendar className="h-4 w-4" />
                  <span>Rodada {mockRanking.current_round}/{mockRanking.total_rounds}</span>
                </div>
              </div>
            </div>
          </div>
          <div className="flex gap-2">
            <Button variant="outline">
              <BarChart3 className="h-4 w-4 mr-2" />
              Estatísticas
            </Button>
            <Button variant="outline">
              <Settings className="h-4 w-4 mr-2" />
              Configurações
            </Button>
          </div>
        </div>

        {/* Round Navigator */}
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <Button
                variant="outline"
                size="sm"
                onClick={handlePreviousRound}
                disabled={selectedRound === 1}
              >
                <ChevronLeft className="h-4 w-4" />
              </Button>

              <div className="flex-1 mx-4">
                <div className="flex justify-between items-center mb-2">
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                    Rodada {selectedRound}
                  </h3>
                  <span className="text-sm text-gray-600 dark:text-gray-400">
                    {mockRounds[selectedRound - 1]?.completed_matches}/{mockRounds[selectedRound - 1]?.total_matches} jogos
                  </span>
                </div>
                <div className="h-2 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
                  <motion.div
                    className="h-full bg-gradient-to-r from-green-500 to-emerald-500"
                    initial={{ width: 0 }}
                    animate={{
                      width: `${(mockRounds[selectedRound - 1]?.completed_matches / mockRounds[selectedRound - 1]?.total_matches) * 100}%`
                    }}
                    transition={{ duration: 0.5 }}
                  />
                </div>
              </div>

              <Button
                variant="outline"
                size="sm"
                onClick={handleNextRound}
                disabled={selectedRound === mockRanking.current_round}
              >
                <ChevronRight className="h-4 w-4" />
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Standings Table */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Trophy className="h-5 w-5 text-yellow-500" />
              Tabela Classificatória
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-gray-200 dark:border-gray-700">
                    <th className="text-left py-3 px-4 text-sm font-semibold text-gray-900 dark:text-white">
                      Pos
                    </th>
                    <th className="text-left py-3 px-4 text-sm font-semibold text-gray-900 dark:text-white">
                      Jogador
                    </th>
                    <th className="text-center py-3 px-4 text-sm font-semibold text-gray-900 dark:text-white">
                      Pts
                    </th>
                    <th className="text-center py-3 px-4 text-sm font-semibold text-gray-900 dark:text-white">
                      J
                    </th>
                    <th className="text-center py-3 px-4 text-sm font-semibold text-gray-900 dark:text-white">
                      V
                    </th>
                    <th className="text-center py-3 px-4 text-sm font-semibold text-gray-900 dark:text-white">
                      D
                    </th>
                    <th className="text-center py-3 px-4 text-sm font-semibold text-gray-900 dark:text-white">
                      Sets
                    </th>
                    <th className="text-center py-3 px-4 text-sm font-semibold text-gray-900 dark:text-white">
                      % Vit
                    </th>
                    <th className="text-left py-3 px-4 text-sm font-semibold text-gray-900 dark:text-white">
                      Evolução
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {mockStandings.map((entry, idx) => {
                    const positionChange = getPositionChange(entry.position, entry.previous_position)

                    return (
                      <motion.tr
                        key={entry.user_id}
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: idx * 0.05 }}
                        className="border-b border-gray-100 dark:border-gray-800 hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors"
                      >
                        <td className="py-4 px-4">
                          <div className="flex items-center gap-2">
                            <span className="text-lg font-bold text-gray-900 dark:text-white">
                              {entry.position}
                            </span>
                            {positionChange && (
                              <div>
                                {positionChange.direction === 'up' && (
                                  <div className="flex items-center text-xs text-green-600 dark:text-green-400">
                                    <TrendingUp className="h-3 w-3" />
                                    <span>{positionChange.value}</span>
                                  </div>
                                )}
                                {positionChange.direction === 'down' && (
                                  <div className="flex items-center text-xs text-red-600 dark:text-red-400">
                                    <TrendingDown className="h-3 w-3" />
                                    <span>{positionChange.value}</span>
                                  </div>
                                )}
                                {positionChange.direction === 'stable' && (
                                  <Minus className="h-3 w-3 text-gray-400" />
                                )}
                              </div>
                            )}
                          </div>
                        </td>
                        <td className="py-4 px-4">
                          <div className="flex items-center gap-3">
                            <div className="w-8 h-8 bg-gradient-to-br from-green-400 to-emerald-600 rounded-full flex items-center justify-center text-white font-semibold text-sm">
                              {entry.user_name.charAt(0)}
                            </div>
                            <span className="font-medium text-gray-900 dark:text-white">
                              {entry.user_name}
                            </span>
                          </div>
                        </td>
                        <td className="py-4 px-4 text-center">
                          <span className="font-semibold text-gray-900 dark:text-white">
                            {entry.points}
                          </span>
                        </td>
                        <td className="py-4 px-4 text-center text-gray-600 dark:text-gray-400">
                          {entry.matches_played}
                        </td>
                        <td className="py-4 px-4 text-center">
                          <span className="text-green-600 dark:text-green-400 font-medium">
                            {entry.matches_won}
                          </span>
                        </td>
                        <td className="py-4 px-4 text-center">
                          <span className="text-red-600 dark:text-red-400 font-medium">
                            {entry.matches_lost}
                          </span>
                        </td>
                        <td className="py-4 px-4 text-center text-gray-600 dark:text-gray-400">
                          {entry.sets_won}/{entry.sets_lost}
                        </td>
                        <td className="py-4 px-4 text-center">
                          <span className="font-medium text-gray-900 dark:text-white">
                            {entry.win_rate.toFixed(1)}%
                          </span>
                        </td>
                        <td className="py-4 px-4">
                          {/* Mini sparkline */}
                          <div className="flex items-end gap-0.5 h-8">
                            {entry.position_history.map((pos, i) => (
                              <div
                                key={i}
                                className="flex-1 bg-green-500 dark:bg-green-400 rounded-t"
                                style={{
                                  height: `${100 - (pos / mockRanking.total_participants) * 100}%`,
                                  minHeight: '4px',
                                }}
                              />
                            ))}
                          </div>
                        </td>
                      </motion.tr>
                    )
                  })}
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>

        {/* Matches for selected round */}
        <Card>
          <CardHeader>
            <CardTitle>
              Jogos da Rodada {selectedRound}
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {[1, 2, 3, 4, 5].map((i) => (
                <div
                  key={i}
                  className="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-800/50 rounded-lg"
                >
                  <div className="flex items-center gap-4 flex-1">
                    <div className="text-sm text-gray-600 dark:text-gray-400">
                      {new Date().toLocaleDateString('pt-BR', { day: '2-digit', month: 'short' })}
                    </div>
                    <div className="flex-1 flex items-center justify-between">
                      <span className="font-medium text-gray-900 dark:text-white">
                        Jogador A
                      </span>
                      {i <= 3 ? (
                        <div className="flex items-center gap-2">
                          <span className="text-lg font-bold text-gray-900 dark:text-white">2</span>
                          <span className="text-gray-400">-</span>
                          <span className="text-lg font-bold text-gray-600 dark:text-gray-400">0</span>
                        </div>
                      ) : (
                        <span className="text-sm text-gray-500 dark:text-gray-500">
                          Agendado
                        </span>
                      )}
                      <span className="font-medium text-gray-900 dark:text-white">
                        Jogador B
                      </span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </PageTransition>
  )
}

export default RankingDetail
