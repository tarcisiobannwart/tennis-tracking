/**
 * Statistics Dashboard Page - TT-133
 * Pagina de dashboard de estatisticas avancadas
 */

import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import {
  BarChart3,
  TrendingUp,
  Users,
  Activity,
  RefreshCw,
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { Tabs, TabsList, TabsTrigger, TabsContent } from '@/components/ui/tabs'
import { PageTransition, Skeleton } from '@/components/animations'
import StatsSummaryCard from '@/components/stats/StatsSummaryCard'
import MonthlyChart from '@/components/stats/MonthlyChart'
import WinLossLineChart from '@/components/stats/WinLossLineChart'
import SurfaceChart from '@/components/stats/SurfaceChart'
import OpponentDonutChart from '@/components/stats/OpponentDonutChart'
import ResultStreak from '@/components/stats/ResultStreak'
import {
  statisticsService,
  DashboardResponse,
  BreakdownItem,
} from '@/services/statisticsService'

const Statistics = () => {
  const [dashboard, setDashboard] = useState<DashboardResponse | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [activeTab, setActiveTab] = useState('overview')

  const fetchDashboard = async () => {
    setIsLoading(true)
    setError(null)

    try {
      const data = await statisticsService.getDashboard(12)
      setDashboard(data)
    } catch (err: any) {
      console.error('Erro ao buscar estatisticas:', err)
      setError(err.message || 'Erro ao carregar estatisticas')
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    fetchDashboard()
  }, [])

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="text-center">
          <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-red-500/10 flex items-center justify-center">
            <BarChart3 className="w-8 h-8 text-red-400" />
          </div>
          <h3 className="text-lg font-semibold text-slate-100 mb-2">Erro ao carregar estatisticas</h3>
          <p className="text-slate-400 text-sm mb-4">{error}</p>
          <Button onClick={fetchDashboard} variant="outline">
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
          <div>
            <h1 className="text-3xl font-bold tracking-tight text-slate-100">
              Estatisticas
            </h1>
            <p className="text-slate-400 mt-1">
              Dashboard completo do seu desempenho
            </p>
          </div>
          <Button
            variant="outline"
            size="sm"
            onClick={fetchDashboard}
            disabled={isLoading}
            className="bg-slate-800 border-slate-700 text-slate-300"
          >
            <RefreshCw className={`w-4 h-4 mr-2 ${isLoading ? 'animate-spin' : ''}`} />
            Atualizar
          </Button>
        </div>

        {isLoading ? (
          <div className="space-y-4">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              {[...Array(4)].map((_, i) => (
                <Skeleton key={i} className="h-24 rounded-xl" />
              ))}
            </div>
            <Skeleton className="h-80 rounded-xl" />
            <Skeleton className="h-80 rounded-xl" />
          </div>
        ) : dashboard ? (
          <>
            {/* Resumo Geral */}
            <StatsSummaryCard stats={dashboard.overall} />

            {/* Tabs */}
            <Tabs value={activeTab} onValueChange={setActiveTab}>
              <TabsList className="bg-slate-800 border border-slate-700 p-1 w-full sm:w-auto">
                <TabsTrigger value="overview" className="text-xs sm:text-sm">
                  <BarChart3 className="w-4 h-4 mr-1.5" />
                  Visao Geral
                </TabsTrigger>
                <TabsTrigger value="performance" className="text-xs sm:text-sm">
                  <TrendingUp className="w-4 h-4 mr-1.5" />
                  Performance
                </TabsTrigger>
                <TabsTrigger value="opponents" className="text-xs sm:text-sm">
                  <Users className="w-4 h-4 mr-1.5" />
                  Adversarios
                </TabsTrigger>
                <TabsTrigger value="streak" className="text-xs sm:text-sm">
                  <Activity className="w-4 h-4 mr-1.5" />
                  Sequencia
                </TabsTrigger>
              </TabsList>

              {/* Tab: Visao Geral */}
              <TabsContent value="overview" className="mt-6 space-y-6">
                {/* Breakdown por tipo */}
                <Card className="bg-slate-800 border-slate-700">
                  <CardContent className="p-4">
                    <h3 className="text-base font-semibold text-slate-100 mb-4">
                      Breakdown por Tipo de Jogo
                    </h3>
                    <div className="space-y-3">
                      {dashboard.by_type.map((item: BreakdownItem) => (
                        <BreakdownBar key={item.label} item={item} />
                      ))}
                    </div>
                  </CardContent>
                </Card>

                {/* Breakdown por tipo de resultado */}
                {dashboard.by_result_type.length > 0 && (
                  <Card className="bg-slate-800 border-slate-700">
                    <CardContent className="p-4">
                      <h3 className="text-base font-semibold text-slate-100 mb-4">
                        Por Tipo de Resultado
                      </h3>
                      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                        {dashboard.by_result_type.map((item) => (
                          <div
                            key={item.result_type}
                            className="p-3 rounded-lg bg-slate-700/50 text-center"
                          >
                            <p className="text-sm font-medium text-slate-300">{item.label}</p>
                            <p className="text-2xl font-bold text-slate-100 mt-1">{item.total}</p>
                            <p className="text-xs text-slate-400 mt-1">
                              {item.wins}V / {item.losses}D
                            </p>
                          </div>
                        ))}
                      </div>
                    </CardContent>
                  </Card>
                )}

                {/* Graficos mensais */}
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                  <MonthlyChart data={dashboard.monthly} />
                  <WinLossLineChart data={dashboard.monthly} />
                </div>
              </TabsContent>

              {/* Tab: Performance */}
              <TabsContent value="performance" className="mt-6 space-y-6">
                <SurfaceChart data={dashboard.by_surface} />

                {/* Faixa etaria do oponente */}
                {dashboard.opponent_profile.age_groups.length > 0 && (
                  <Card className="bg-slate-800 border-slate-700">
                    <CardContent className="p-4">
                      <h3 className="text-base font-semibold text-slate-100 mb-4">
                        Por Faixa Etaria do Oponente
                      </h3>
                      <div className="space-y-3">
                        {dashboard.opponent_profile.age_groups.map((item) => (
                          <BreakdownBar
                            key={item.age_group}
                            item={{
                              label: item.age_group,
                              total: item.total,
                              wins: item.wins,
                              losses: item.losses,
                              win_rate: item.win_rate,
                            }}
                          />
                        ))}
                      </div>
                    </CardContent>
                  </Card>
                )}
              </TabsContent>

              {/* Tab: Adversarios */}
              <TabsContent value="opponents" className="mt-6 space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <OpponentDonutChart
                    title="vs Destros / Canhotos"
                    data={dashboard.opponent_profile.handedness}
                  />
                  <OpponentDonutChart
                    title="vs Backhand 1 / 2 Maos"
                    data={dashboard.opponent_profile.backhand}
                  />
                </div>
              </TabsContent>

              {/* Tab: Sequencia */}
              <TabsContent value="streak" className="mt-6 space-y-6">
                <ResultStreak data={dashboard.streak} />
              </TabsContent>
            </Tabs>
          </>
        ) : null}
      </div>
    </PageTransition>
  )
}

/**
 * Componente auxiliar para barras de breakdown V/D
 */
const BreakdownBar = ({ item }: { item: BreakdownItem }) => {
  const total = item.wins + item.losses
  const winPercent = total > 0 ? (item.wins / total) * 100 : 0
  const lossPercent = total > 0 ? (item.losses / total) * 100 : 0

  return (
    <div className="space-y-1.5">
      <div className="flex items-center justify-between text-sm">
        <span className="text-slate-300 font-medium">{item.label}</span>
        <span className="text-slate-400">
          {item.wins}V / {item.losses}D ({item.win_rate}%)
        </span>
      </div>
      <div className="flex h-3 rounded-full overflow-hidden bg-slate-700">
        {winPercent > 0 && (
          <motion.div
            initial={{ width: 0 }}
            animate={{ width: `${winPercent}%` }}
            transition={{ duration: 0.6, ease: 'easeOut' }}
            className="bg-green-500 h-full"
          />
        )}
        {lossPercent > 0 && (
          <motion.div
            initial={{ width: 0 }}
            animate={{ width: `${lossPercent}%` }}
            transition={{ duration: 0.6, ease: 'easeOut', delay: 0.1 }}
            className="bg-red-500 h-full"
          />
        )}
      </div>
    </div>
  )
}

export default Statistics
