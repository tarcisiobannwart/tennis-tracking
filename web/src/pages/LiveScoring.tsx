/**
 * LiveScoring - TT-146
 * Página de scoring ao vivo com botões interativos para registrar pontos
 */

import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import {
  ArrowLeft,
  Trophy,
  Circle,
  AlertTriangle,
  Target,
  Zap,
  XCircle,
  Clock,
} from 'lucide-react'
import { Card, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { PageTransition } from '@/components/animations'
import { useUIStore } from '@/stores/uiStore'
import scoringService, { LiveBroadcastData, PointType } from '@/services/scoringService'
import matchService from '@/services/matchService'
import { Match } from '@/types'

type PointTypeOption = {
  value: PointType
  label: string
  icon: any
  color: string
}

const pointTypeOptions: PointTypeOption[] = [
  { value: 'ace', label: 'Ace', icon: Zap, color: 'bg-yellow-500' },
  { value: 'winner', label: 'Winner', icon: Target, color: 'bg-green-500' },
  { value: 'forced_error', label: 'Erro Forçado', icon: AlertTriangle, color: 'bg-orange-500' },
  { value: 'unforced_error', label: 'Erro Não-Forçado', icon: XCircle, color: 'bg-red-500' },
  { value: 'double_fault', label: 'Dupla Falta', icon: XCircle, color: 'bg-red-600' },
]

const LiveScoring = () => {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const { addNotification } = useUIStore()

  const [match, setMatch] = useState<Match | null>(null)
  const [liveData, setLiveData] = useState<LiveBroadcastData | null>(null)
  const [loading, setLoading] = useState(true)
  const [showPointTypeModal, setShowPointTypeModal] = useState(false)
  const [selectedWinnerId, setSelectedWinnerId] = useState<string | null>(null)
  const [processing, setProcessing] = useState(false)
  const [showMatchEndModal, setShowMatchEndModal] = useState(false)

  // Load match and live data
  useEffect(() => {
    loadMatchData()
    const interval = setInterval(loadLiveData, 3000) // Refresh every 3 seconds
    return () => clearInterval(interval)
  }, [id])

  const loadMatchData = async () => {
    if (!id) return
    try {
      const matchData = await matchService.getMatch(id)
      setMatch(matchData)
      await loadLiveData()
    } catch (error) {
      console.error('Failed to load match:', error)
      addNotification({
        type: 'error',
        title: 'Erro',
        message: 'Falha ao carregar dados da partida',
      })
    } finally {
      setLoading(false)
    }
  }

  const loadLiveData = async () => {
    if (!id || !match) return
    try {
      const data = await scoringService.getLiveBroadcastData(
        id,
        match.player1.name,
        match.player2.name,
        match.player1.ranking,
        match.player2.ranking,
        match.player1.country,
        match.player2.country,
        10 // Last 10 points
      )
      setLiveData(data)

      // Check if match is complete
      if (data.scoreboard.is_complete && !showMatchEndModal) {
        setShowMatchEndModal(true)
      }
    } catch (error) {
      console.error('Failed to load live data:', error)
    }
  }

  const handlePointButtonClick = (playerId: string) => {
    setSelectedWinnerId(playerId)
    setShowPointTypeModal(true)
  }

  const handleAddPoint = async (_pointType?: PointType) => {
    if (!selectedWinnerId || !id) return

    setProcessing(true)
    try {
      const response = await scoringService.addPoint(id, selectedWinnerId)

      // Show event notifications
      if (response.events.includes('match_won')) {
        setShowMatchEndModal(true)
      } else if (response.events.includes('set_won')) {
        addNotification({
          type: 'success',
          title: 'Set Vencido!',
          message: `Jogador ganhou o set`,
        })
      } else if (response.events.includes('game_won')) {
        addNotification({
          type: 'success',
          title: 'Game!',
          message: 'Game vencido',
        })
      }

      // Reload live data
      await loadLiveData()
    } catch (error) {
      console.error('Failed to add point:', error)
      addNotification({
        type: 'error',
        title: 'Erro',
        message: 'Falha ao registrar ponto',
      })
    } finally {
      setProcessing(false)
      setShowPointTypeModal(false)
      setSelectedWinnerId(null)
    }
  }

  const formatScore = (points: string) => {
    // Already formatted by backend
    return points
  }

  if (loading || !match || !liveData) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-court-accent"></div>
      </div>
    )
  }

  const { scoreboard, situation, last_points, key_stats } = liveData

  return (
    <PageTransition>
      <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 pb-24">
        {/* Header */}
        <div className="sticky top-0 z-10 bg-slate-900/95 backdrop-blur-sm border-b border-slate-800">
          <div className="max-w-7xl mx-auto px-4 py-4">
            <div className="flex items-center justify-between">
              <Button
                variant="ghost"
                size="sm"
                onClick={() => navigate(-1)}
                className="gap-2"
              >
                <ArrowLeft className="w-4 h-4" />
                Voltar
              </Button>
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 bg-red-500 rounded-full animate-pulse" />
                <span className="text-sm font-medium text-red-400">AO VIVO</span>
              </div>
            </div>
          </div>
        </div>

        <div className="max-w-7xl mx-auto px-4 py-6 space-y-6">
          {/* Scoreboard */}
          <Card className="bg-gradient-to-br from-slate-900 to-slate-800 border-slate-700">
            <CardContent className="p-6">
              {/* Match Info */}
              <div className="text-center mb-6">
                <h2 className="text-lg font-semibold text-slate-300">{match.tournament}</h2>
                <p className="text-sm text-slate-400">{match.round}</p>
              </div>

              {/* Player 1 Score */}
              <div className="mb-4">
                <div className="flex items-center justify-between p-4 bg-slate-800/50 rounded-lg">
                  <div className="flex items-center gap-3">
                    {scoreboard.player1.serving && (
                      <Circle className="w-3 h-3 fill-yellow-400 text-yellow-400" />
                    )}
                    <div>
                      <h3 className="text-xl font-bold text-white">
                        {scoreboard.player1.name}
                      </h3>
                      {scoreboard.player1.country && (
                        <p className="text-sm text-slate-400">
                          {scoreboard.player1.country}
                          {scoreboard.player1.ranking && ` • #${scoreboard.player1.ranking}`}
                        </p>
                      )}
                    </div>
                  </div>
                  <div className="flex items-center gap-4">
                    {/* Sets */}
                    {scoreboard.player1.games.map((games, idx) => (
                      <div
                        key={idx}
                        className={`w-12 h-12 rounded-lg flex items-center justify-center text-2xl font-bold ${
                          games > scoreboard.player2.games[idx]
                            ? 'bg-green-600'
                            : games < scoreboard.player2.games[idx]
                            ? 'bg-red-600/50'
                            : 'bg-slate-700'
                        }`}
                      >
                        {games}
                      </div>
                    ))}
                    {/* Current points */}
                    {!scoreboard.is_complete && (
                      <div className="w-16 h-12 rounded-lg bg-yellow-600 flex items-center justify-center text-xl font-bold">
                        {formatScore(scoreboard.player1.current_points)}
                      </div>
                    )}
                  </div>
                </div>
              </div>

              {/* Player 2 Score */}
              <div>
                <div className="flex items-center justify-between p-4 bg-slate-800/50 rounded-lg">
                  <div className="flex items-center gap-3">
                    {scoreboard.player2.serving && (
                      <Circle className="w-3 h-3 fill-yellow-400 text-yellow-400" />
                    )}
                    <div>
                      <h3 className="text-xl font-bold text-white">
                        {scoreboard.player2.name}
                      </h3>
                      {scoreboard.player2.country && (
                        <p className="text-sm text-slate-400">
                          {scoreboard.player2.country}
                          {scoreboard.player2.ranking && ` • #${scoreboard.player2.ranking}`}
                        </p>
                      )}
                    </div>
                  </div>
                  <div className="flex items-center gap-4">
                    {/* Sets */}
                    {scoreboard.player2.games.map((games, idx) => (
                      <div
                        key={idx}
                        className={`w-12 h-12 rounded-lg flex items-center justify-center text-2xl font-bold ${
                          games > scoreboard.player1.games[idx]
                            ? 'bg-green-600'
                            : games < scoreboard.player1.games[idx]
                            ? 'bg-red-600/50'
                            : 'bg-slate-700'
                        }`}
                      >
                        {games}
                      </div>
                    ))}
                    {/* Current points */}
                    {!scoreboard.is_complete && (
                      <div className="w-16 h-12 rounded-lg bg-yellow-600 flex items-center justify-center text-xl font-bold">
                        {formatScore(scoreboard.player2.current_points)}
                      </div>
                    )}
                  </div>
                </div>
              </div>

              {/* Game Situation */}
              {situation.situation_text && (
                <motion.div
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="mt-4 p-3 bg-court-accent/20 border border-court-accent/30 rounded-lg text-center"
                >
                  <p className="text-sm font-medium text-court-accent">
                    {situation.situation_text}
                  </p>
                </motion.div>
              )}
            </CardContent>
          </Card>

          {/* Point Buttons */}
          {!scoreboard.is_complete && (
            <div className="grid grid-cols-2 gap-4">
              <motion.div whileTap={{ scale: 0.95 }}>
                <Button
                  onClick={() => handlePointButtonClick(match.player1.id)}
                  disabled={processing}
                  className="w-full h-24 text-xl font-bold bg-blue-600 hover:bg-blue-700"
                  size="lg"
                >
                  <div className="flex flex-col items-center gap-2">
                    <Trophy className="w-6 h-6" />
                    <span>Ponto {match.player1.name.split(' ')[0]}</span>
                  </div>
                </Button>
              </motion.div>

              <motion.div whileTap={{ scale: 0.95 }}>
                <Button
                  onClick={() => handlePointButtonClick(match.player2.id)}
                  disabled={processing}
                  className="w-full h-24 text-xl font-bold bg-red-600 hover:bg-red-700"
                  size="lg"
                >
                  <div className="flex flex-col items-center gap-2">
                    <Trophy className="w-6 h-6" />
                    <span>Ponto {match.player2.name.split(' ')[0]}</span>
                  </div>
                </Button>
              </motion.div>
            </div>
          )}

          {/* Last Events */}
          {last_points.length > 0 && (
            <Card className="bg-slate-900 border-slate-800">
              <CardContent className="p-6">
                <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                  <Clock className="w-5 h-5" />
                  Últimos Pontos
                </h3>
                <div className="space-y-2">
                  {last_points.slice(0, 5).map((point, idx) => (
                    <div
                      key={idx}
                      className="flex items-center justify-between p-3 bg-slate-800/50 rounded-lg text-sm"
                    >
                      <div className="flex items-center gap-3">
                        <span className="text-slate-400">#{point.point_number}</span>
                        <span className="text-white">
                          Ponto para {point.winner_id === match.player1.id ? match.player1.name : match.player2.name}
                        </span>
                      </div>
                      <div className="flex items-center gap-2">
                        {point.events.includes('game_won') && (
                          <span className="px-2 py-1 bg-green-600/20 text-green-400 rounded text-xs">
                            GAME
                          </span>
                        )}
                        {point.events.includes('set_won') && (
                          <span className="px-2 py-1 bg-yellow-600/20 text-yellow-400 rounded text-xs">
                            SET
                          </span>
                        )}
                        <span className="text-slate-400 font-mono">{point.score_after}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}

          {/* Key Stats */}
          <Card className="bg-slate-900 border-slate-800">
            <CardContent className="p-6">
              <h3 className="text-lg font-semibold text-white mb-4">Estatísticas</h3>
              <div className="grid grid-cols-3 gap-4 text-center">
                <div>
                  <p className="text-2xl font-bold text-white">{key_stats.player1.aces}</p>
                  <p className="text-sm text-slate-400">Aces</p>
                  <p className="text-2xl font-bold text-white mt-1">{key_stats.player2.aces}</p>
                </div>
                <div>
                  <p className="text-2xl font-bold text-white">{key_stats.player1.winners}</p>
                  <p className="text-sm text-slate-400">Winners</p>
                  <p className="text-2xl font-bold text-white mt-1">{key_stats.player2.winners}</p>
                </div>
                <div>
                  <p className="text-2xl font-bold text-white">{key_stats.player1.unforced_errors}</p>
                  <p className="text-sm text-slate-400">Erros</p>
                  <p className="text-2xl font-bold text-white mt-1">{key_stats.player2.unforced_errors}</p>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Point Type Modal */}
        <AnimatePresence>
          {showPointTypeModal && (
            <>
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="fixed inset-0 bg-black/50 z-40"
                onClick={() => setShowPointTypeModal(false)}
              />
              <motion.div
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.9 }}
                className="fixed inset-x-4 top-1/2 -translate-y-1/2 z-50 max-w-md mx-auto"
              >
                <Card className="bg-slate-900 border-slate-700">
                  <CardContent className="p-6">
                    <h3 className="text-lg font-semibold text-white mb-4 text-center">
                      Tipo de Ponto
                    </h3>
                    <div className="space-y-2">
                      {pointTypeOptions.map((option) => {
                        const Icon = option.icon
                        return (
                          <Button
                            key={option.value}
                            onClick={() => handleAddPoint(option.value)}
                            className={`w-full justify-start gap-3 ${option.color} hover:opacity-90`}
                            disabled={processing}
                          >
                            <Icon className="w-5 h-5" />
                            {option.label}
                          </Button>
                        )
                      })}
                      <Button
                        onClick={() => handleAddPoint()}
                        variant="outline"
                        className="w-full"
                        disabled={processing}
                      >
                        Ponto Normal
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              </motion.div>
            </>
          )}
        </AnimatePresence>

        {/* Match End Modal */}
        <AnimatePresence>
          {showMatchEndModal && (
            <>
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="fixed inset-0 bg-black/70 z-40"
              />
              <motion.div
                initial={{ opacity: 0, scale: 0.9, y: 20 }}
                animate={{ opacity: 1, scale: 1, y: 0 }}
                exit={{ opacity: 0, scale: 0.9, y: 20 }}
                className="fixed inset-x-4 top-1/2 -translate-y-1/2 z-50 max-w-lg mx-auto"
              >
                <Card className="bg-gradient-to-br from-yellow-900/90 to-yellow-800/90 border-yellow-600">
                  <CardContent className="p-8 text-center">
                    <Trophy className="w-16 h-16 text-yellow-400 mx-auto mb-4" />
                    <h2 className="text-3xl font-bold text-white mb-2">Fim de Partida!</h2>
                    <p className="text-lg text-yellow-100 mb-6">
                      Vencedor: {scoreboard.player1.sets_won > scoreboard.player2.sets_won
                        ? match.player1.name
                        : match.player2.name}
                    </p>
                    <div className="space-y-3">
                      <Button
                        onClick={() => navigate(`/app/match/${id}`)}
                        className="w-full bg-yellow-600 hover:bg-yellow-700"
                        size="lg"
                      >
                        Ver Estatísticas Completas
                      </Button>
                      <Button
                        onClick={() => navigate('/app/matches')}
                        variant="outline"
                        className="w-full"
                      >
                        Voltar para Partidas
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              </motion.div>
            </>
          )}
        </AnimatePresence>
      </div>
    </PageTransition>
  )
}

export default LiveScoring
