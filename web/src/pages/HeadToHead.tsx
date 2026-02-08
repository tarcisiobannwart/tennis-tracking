/**
 * HeadToHead Page - TT-134
 * Pagina de comparativo H2H entre jogadores
 */

import { useState, useEffect } from 'react'
import { useParams } from 'react-router-dom'
import { motion } from 'framer-motion'
import {
  Users,
  BarChart3,
  RefreshCw,
  ArrowLeft,
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { PageTransition, Skeleton } from '@/components/animations'
import { useAuthStore } from '@/stores/authStore'
import H2HHeader from '@/components/h2h/H2HHeader'
import ComparisonTable from '@/components/h2h/ComparisonTable'
import H2HChart from '@/components/h2h/H2HChart'
import MatchHistory from '@/components/h2h/MatchHistory'
import OpponentSelector from '@/components/h2h/OpponentSelector'
import {
  h2hService,
  H2HResponse,
  OpponentSummary,
} from '@/services/h2hService'

const HeadToHead = () => {
  const { user } = useAuthStore()
  const [opponents, setOpponents] = useState<OpponentSummary[]>([])
  const [selectedOpponentId, setSelectedOpponentId] = useState<string | null>(null)
  const [h2hData, setH2HData] = useState<H2HResponse | null>(null)
  const [isLoadingOpponents, setIsLoadingOpponents] = useState(true)
  const [isLoadingH2H, setIsLoadingH2H] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const playerId = user?.id || user?._id || ''

  // Buscar lista de adversarios
  const fetchOpponents = async () => {
    if (!playerId) return
    setIsLoadingOpponents(true)
    setError(null)

    try {
      const data = await h2hService.getOpponents(playerId)
      setOpponents(data.opponents)
    } catch (err: any) {
      console.error('Erro ao buscar adversarios:', err)
      setError(err.message || 'Erro ao carregar adversarios')
    } finally {
      setIsLoadingOpponents(false)
    }
  }

  // Buscar dados H2H
  const fetchH2H = async (opponentId: string) => {
    if (!playerId) return
    setIsLoadingH2H(true)

    try {
      const data = await h2hService.getH2H(playerId, opponentId)
      setH2HData(data)
    } catch (err: any) {
      console.error('Erro ao buscar H2H:', err)
      setError(err.message || 'Erro ao carregar H2H')
    } finally {
      setIsLoadingH2H(false)
    }
  }

  useEffect(() => {
    fetchOpponents()
  }, [playerId])

  const handleSelectOpponent = (opponentId: string) => {
    setSelectedOpponentId(opponentId)
    fetchH2H(opponentId)
  }

  const handleBack = () => {
    setSelectedOpponentId(null)
    setH2HData(null)
  }

  if (error && !h2hData && opponents.length === 0) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="text-center">
          <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-red-500/10 flex items-center justify-center">
            <Users className="w-8 h-8 text-red-400" />
          </div>
          <h3 className="text-lg font-semibold text-slate-100 mb-2">Erro ao carregar H2H</h3>
          <p className="text-slate-400 text-sm mb-4">{error}</p>
          <Button onClick={fetchOpponents} variant="outline">
            Tentar Novamente
          </Button>
        </div>
      </div>
    )
  }

  return (
    <PageTransition>
      <div className="space-y-6 p-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            {selectedOpponentId && (
              <Button
                variant="outline"
                size="sm"
                onClick={handleBack}
                className="bg-slate-800 border-slate-700 text-slate-300"
              >
                <ArrowLeft className="w-4 h-4" />
              </Button>
            )}
            <div>
              <h1 className="text-3xl font-bold tracking-tight text-slate-100">
                Head to Head
              </h1>
              <p className="text-slate-400 mt-1">
                {selectedOpponentId
                  ? 'Comparativo detalhado'
                  : 'Selecione um adversario para comparar'}
              </p>
            </div>
          </div>
        </div>

        {/* Conteudo */}
        {!selectedOpponentId ? (
          /* Seletor de adversario */
          <OpponentSelector
            opponents={opponents}
            selectedId={selectedOpponentId || undefined}
            onSelect={handleSelectOpponent}
            isLoading={isLoadingOpponents}
          />
        ) : isLoadingH2H ? (
          /* Loading H2H */
          <div className="space-y-4">
            <Skeleton className="h-40 rounded-xl" />
            <Skeleton className="h-64 rounded-xl" />
            <Skeleton className="h-64 rounded-xl" />
          </div>
        ) : h2hData ? (
          /* Dados H2H */
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3 }}
            className="space-y-6"
          >
            {/* Header H2H */}
            <H2HHeader
              player={h2hData.player}
              opponent={h2hData.opponent}
              h2hScore={h2hData.h2h_score}
            />

            {/* Totais de sets e games */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <Card className="bg-slate-800 border-slate-700">
                <CardContent className="p-3 text-center">
                  <p className="text-xs text-slate-400">Sets (Voce)</p>
                  <p className="text-xl font-bold text-green-400">{h2hData.total_sets_player}</p>
                </CardContent>
              </Card>
              <Card className="bg-slate-800 border-slate-700">
                <CardContent className="p-3 text-center">
                  <p className="text-xs text-slate-400">Sets (Oponente)</p>
                  <p className="text-xl font-bold text-red-400">{h2hData.total_sets_opponent}</p>
                </CardContent>
              </Card>
              <Card className="bg-slate-800 border-slate-700">
                <CardContent className="p-3 text-center">
                  <p className="text-xs text-slate-400">Games (Voce)</p>
                  <p className="text-xl font-bold text-green-400">{h2hData.total_games_player}</p>
                </CardContent>
              </Card>
              <Card className="bg-slate-800 border-slate-700">
                <CardContent className="p-3 text-center">
                  <p className="text-xs text-slate-400">Games (Oponente)</p>
                  <p className="text-xl font-bold text-red-400">{h2hData.total_games_opponent}</p>
                </CardContent>
              </Card>
            </div>

            {/* Tabela comparativa */}
            <ComparisonTable
              comparison={h2hData.comparison}
              playerName={h2hData.player.name}
              opponentName={h2hData.opponent.name}
            />

            {/* Grafico de sets/games */}
            <H2HChart
              data={h2hData.sets_games_over_time}
              playerName={h2hData.player.name}
              opponentName={h2hData.opponent.name}
            />

            {/* Historico de confrontos */}
            <MatchHistory
              matches={h2hData.match_history}
              opponentName={h2hData.opponent.name}
            />
          </motion.div>
        ) : null}
      </div>
    </PageTransition>
  )
}

export default HeadToHead
