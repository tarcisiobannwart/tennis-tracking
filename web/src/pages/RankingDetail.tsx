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
  Loader2,
  AlertCircle,
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { PageTransition } from '@/components/animations'
import { useRanking, useStandings, useRounds } from '@/hooks/useRankingData'

const RankingDetail = () => {
  const { id } = useParams<{ id: string }>()

  // Fetch data from API
  const {
    data: ranking,
    isLoading: isLoadingRanking,
    isError: isErrorRanking,
    error: errorRanking,
    refetch: refetchRanking
  } = useRanking(id || '')

  const {
    data: standingsData,
    isLoading: isLoadingStandings,
    isError: isErrorStandings,
    refetch: refetchStandings
  } = useStandings(id || '')

  const {
    data: rounds,
    isLoading: isLoadingRounds,
    isError: isErrorRounds,
    refetch: refetchRounds
  } = useRounds(id || '')

  const [selectedRound, setSelectedRound] = useState(1)

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
    if (ranking && selectedRound < ranking.current_round) setSelectedRound(selectedRound + 1)
  }

  // Loading state for ranking
  if (isLoadingRanking) {
    return (
      <PageTransition>
        <div className="space-y-6 p-6">
          <Card>
            <CardContent className="p-12 text-center">
              <Loader2 className="h-12 w-12 text-gray-400 mx-auto mb-4 animate-spin" />
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
                Carregando ranking...
              </h3>
              <p className="text-gray-600 dark:text-gray-400">
                Por favor, aguarde
              </p>
            </CardContent>
          </Card>
        </div>
      </PageTransition>
    )
  }

  // Error state for ranking
  if (isErrorRanking || !ranking) {
    return (
      <PageTransition>
        <div className="space-y-6 p-6">
          <Card>
            <CardContent className="p-12 text-center">
              <AlertCircle className="h-12 w-12 text-red-500 mx-auto mb-4" />
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
                Erro ao carregar ranking
              </h3>
              <p className="text-gray-600 dark:text-gray-400 mb-4">
                {errorRanking instanceof Error ? errorRanking.message : 'Ranking não encontrado'}
              </p>
              <div className="flex gap-2 justify-center">
                <Button onClick={() => refetchRanking()}>
                  Tentar Novamente
                </Button>
                <Button variant="outline" asChild>
                  <Link to="/rankings">
                    Voltar para Rankings
                  </Link>
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      </PageTransition>
    )
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
                {ranking.name}
              </h1>
              <div className="flex items-center gap-4 mt-2 text-sm text-gray-600 dark:text-gray-400">
                <div className="flex items-center gap-1">
                  <MapPin className="h-4 w-4" />
                  <span>{ranking.location}</span>
                </div>
                <div className="flex items-center gap-1">
                  <Users className="h-4 w-4" />
                  <span>{ranking.total_participants} participantes</span>
                </div>
                <div className="flex items-center gap-1">
                  <Calendar className="h-4 w-4" />
                  <span>Rodada {ranking.current_round}/{ranking.total_rounds}</span>
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
            {isLoadingRounds ? (
              <div className="flex items-center justify-center p-4">
                <Loader2 className="h-6 w-6 text-gray-400 animate-spin mr-2" />
                <span className="text-sm text-gray-600 dark:text-gray-400">
                  Carregando rodadas...
                </span>
              </div>
            ) : isErrorRounds ? (
              <div className="text-center p-4">
                <AlertCircle className="h-8 w-8 text-red-500 mx-auto mb-2" />
                <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">
                  Erro ao carregar rodadas
                </p>
                <Button size="sm" variant="outline" onClick={() => refetchRounds()}>
                  Tentar Novamente
                </Button>
              </div>
            ) : (
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
                    {rounds && rounds[selectedRound - 1] && (
                      <span className="text-sm text-gray-600 dark:text-gray-400">
                        {rounds[selectedRound - 1].completed_matches}/{rounds[selectedRound - 1].total_matches} jogos
                      </span>
                    )}
                  </div>
                  <div className="h-2 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
                    <motion.div
                      className="h-full bg-gradient-to-r from-green-500 to-emerald-500"
                      initial={{ width: 0 }}
                      animate={{
                        width: rounds && rounds[selectedRound - 1]
                          ? `${(rounds[selectedRound - 1].completed_matches / rounds[selectedRound - 1].total_matches) * 100}%`
                          : '0%'
                      }}
                      transition={{ duration: 0.5 }}
                    />
                  </div>
                </div>

                <Button
                  variant="outline"
                  size="sm"
                  onClick={handleNextRound}
                  disabled={selectedRound === ranking.current_round}
                >
                  <ChevronRight className="h-4 w-4" />
                </Button>
              </div>
            )}
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
            {isLoadingStandings ? (
              <div className="flex items-center justify-center p-8">
                <Loader2 className="h-8 w-8 text-gray-400 animate-spin mr-2" />
                <span className="text-gray-600 dark:text-gray-400">
                  Carregando classificação...
                </span>
              </div>
            ) : isErrorStandings ? (
              <div className="text-center p-8">
                <AlertCircle className="h-10 w-10 text-red-500 mx-auto mb-3" />
                <p className="text-gray-600 dark:text-gray-400 mb-3">
                  Erro ao carregar classificação
                </p>
                <Button size="sm" onClick={() => refetchStandings()}>
                  Tentar Novamente
                </Button>
              </div>
            ) : !standingsData?.standings || standingsData.standings.length === 0 ? (
              <div className="text-center p-8">
                <Trophy className="h-10 w-10 text-gray-400 mx-auto mb-3" />
                <p className="text-gray-600 dark:text-gray-400">
                  Nenhuma classificação disponível ainda
                </p>
              </div>
            ) : (
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
                    {standingsData.standings.map((entry, idx) => {
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
                                    height: `${100 - (pos / ranking.total_participants) * 100}%`,
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
            )}
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
