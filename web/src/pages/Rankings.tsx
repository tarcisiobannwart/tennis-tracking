import { useState, useMemo } from 'react'
import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import {
  Search,
  Filter,
  Trophy,
  Users,
  Calendar,
  MapPin,
  TrendingUp,
  TrendingDown,
  Minus,
  Plus,
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { Chip } from '@/components/ui/chip'
import { PageTransition, StaggerContainer, StaggerItem } from '@/components/animations'

// Mock data para desenvolvimento
const mockRankings = [
  {
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
    my_position: 5,
    my_stats: {
      points: 15.5,
      matches_played: 6,
      matches_won: 4,
      matches_lost: 2,
      win_rate: 66.7,
      position_history: [8, 7, 6, 5],
    },
    start_date: '2026-01-15',
    end_date: '2026-06-30',
  },
  {
    id: '2',
    name: 'Torneio Desafio Verão',
    description: 'Sistema de desafio para todos os níveis',
    ranking_type: 'challenge',
    status: 'active',
    venue: 'Centro Esportivo',
    location: 'Rio de Janeiro, RJ',
    current_round: 1,
    total_rounds: null,
    total_participants: 24,
    my_position: 12,
    my_stats: {
      points: 8.0,
      matches_played: 3,
      matches_won: 2,
      matches_lost: 1,
      win_rate: 66.7,
      position_history: [15, 13, 12],
    },
    start_date: '2026-02-01',
    end_date: '2026-03-31',
  },
  {
    id: '3',
    name: 'Ranking Iniciantes 2026',
    description: 'Ranking exclusivo para iniciantes',
    ranking_type: 'round_robin',
    status: 'completed',
    venue: 'Academia Tennis Pro',
    location: 'Campinas, SP',
    current_round: 4,
    total_rounds: 4,
    total_participants: 12,
    my_position: 3,
    my_stats: {
      points: 22.0,
      matches_played: 8,
      matches_won: 7,
      matches_lost: 1,
      win_rate: 87.5,
      position_history: [6, 5, 4, 3],
    },
    start_date: '2026-01-10',
    end_date: '2026-02-05',
  },
]

type StatusFilter = 'all' | 'active' | 'inactive' | 'completed'
type TypeFilter = 'all' | 'round_robin' | 'challenge'

const Rankings = () => {
  const [searchTerm, setSearchTerm] = useState('')
  const [statusFilter, setStatusFilter] = useState<StatusFilter>('all')
  const [typeFilter, setTypeFilter] = useState<TypeFilter>('all')
  const [showFilters, setShowFilters] = useState(false)

  // Filter rankings
  const filteredRankings = useMemo(() => {
    return mockRankings.filter(ranking => {
      const matchesSearch =
        ranking.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        ranking.location.toLowerCase().includes(searchTerm.toLowerCase())

      const matchesStatus = statusFilter === 'all' || ranking.status === statusFilter
      const matchesType = typeFilter === 'all' || ranking.ranking_type === typeFilter

      return matchesSearch && matchesStatus && matchesType
    })
  }, [searchTerm, statusFilter, typeFilter])

  const getStatusConfig = (status: string) => {
    switch (status) {
      case 'active':
        return { color: 'bg-green-500', label: 'Ativo' }
      case 'inactive':
        return { color: 'bg-gray-500', label: 'Inativo' }
      case 'completed':
        return { color: 'bg-blue-500', label: 'Concluído' }
      default:
        return { color: 'bg-gray-500', label: 'Desconhecido' }
    }
  }

  const getTypeConfig = (type: string) => {
    switch (type) {
      case 'round_robin':
        return { label: 'Todos contra Todos', icon: Users }
      case 'challenge':
        return { label: 'Desafio', icon: Trophy }
      default:
        return { label: 'Desconhecido', icon: Users }
    }
  }

  const getPositionTrend = (positionHistory: number[]) => {
    if (!positionHistory || positionHistory.length < 2) return null

    const current = positionHistory[positionHistory.length - 1]
    const previous = positionHistory[positionHistory.length - 2]

    if (current < previous) return { direction: 'up', change: previous - current }
    if (current > previous) return { direction: 'down', change: current - previous }
    return { direction: 'stable', change: 0 }
  }

  return (
    <PageTransition>
      <div className="space-y-6 p-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
              Meus Rankings
            </h1>
            <p className="text-gray-600 dark:text-gray-400 mt-1">
              Acompanhe sua posição e evolução nos rankings
            </p>
          </div>
          <Button asChild>
            <Link to="/rankings/new">
              <Plus className="h-4 w-4 mr-2" />
              Criar Ranking
            </Link>
          </Button>
        </div>

        {/* Search and Filters */}
        <Card>
          <CardContent className="p-4">
            <div className="flex flex-col md:flex-row gap-4">
              <div className="flex-1 relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
                <input
                  type="text"
                  placeholder="Buscar por nome ou localização..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-green-500 dark:bg-gray-800 dark:text-white"
                />
              </div>
              <Button
                variant="outline"
                onClick={() => setShowFilters(!showFilters)}
              >
                <Filter className="h-4 w-4 mr-2" />
                Filtros
              </Button>
            </div>

            {showFilters && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                exit={{ opacity: 0, height: 0 }}
                className="mt-4 pt-4 border-t border-gray-200 dark:border-gray-700"
              >
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Status
                    </label>
                    <div className="flex flex-wrap gap-2">
                      {(['all', 'active', 'inactive', 'completed'] as StatusFilter[]).map((status) => (
                        <Chip
                          key={status}
                          active={statusFilter === status}
                          onClick={() => setStatusFilter(status)}
                        >
                          {status === 'all' ? 'Todos' : getStatusConfig(status).label}
                        </Chip>
                      ))}
                    </div>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      Tipo
                    </label>
                    <div className="flex flex-wrap gap-2">
                      {(['all', 'round_robin', 'challenge'] as TypeFilter[]).map((type) => (
                        <Chip
                          key={type}
                          active={typeFilter === type}
                          onClick={() => setTypeFilter(type)}
                        >
                          {type === 'all' ? 'Todos' : getTypeConfig(type).label}
                        </Chip>
                      ))}
                    </div>
                  </div>
                </div>
              </motion.div>
            )}
          </CardContent>
        </Card>

        {/* Rankings List */}
        <StaggerContainer>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {filteredRankings.map((ranking) => {
              const statusConfig = getStatusConfig(ranking.status)
              const typeConfig = getTypeConfig(ranking.ranking_type)
              const positionTrend = getPositionTrend(ranking.my_stats?.position_history || [])
              const TypeIcon = typeConfig.icon

              return (
                <StaggerItem key={ranking.id}>
                  <Link to={`/rankings/${ranking.id}`}>
                    <Card className="hover:shadow-lg transition-shadow cursor-pointer">
                      <CardContent className="p-6">
                        <div className="flex items-start justify-between mb-4">
                          <div className="flex-1">
                            <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-1">
                              {ranking.name}
                            </h3>
                            <p className="text-sm text-gray-600 dark:text-gray-400">
                              {ranking.description}
                            </p>
                          </div>
                          <div className={`w-2 h-2 rounded-full ${statusConfig.color} ml-4 mt-2`} />
                        </div>

                        <div className="flex items-center gap-4 text-sm text-gray-600 dark:text-gray-400 mb-4">
                          <div className="flex items-center gap-1">
                            <TypeIcon className="h-4 w-4" />
                            <span>{typeConfig.label}</span>
                          </div>
                          <div className="flex items-center gap-1">
                            <MapPin className="h-4 w-4" />
                            <span>{ranking.location}</span>
                          </div>
                        </div>

                        {/* My Position Card */}
                        {ranking.my_position && (
                          <div className="bg-gradient-to-r from-green-50 to-emerald-50 dark:from-green-900/20 dark:to-emerald-900/20 rounded-lg p-4 mb-4">
                            <div className="flex items-center justify-between">
                              <div>
                                <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">
                                  Minha Posição
                                </p>
                                <div className="flex items-center gap-2">
                                  <span className="text-3xl font-bold text-green-600 dark:text-green-400">
                                    #{ranking.my_position}
                                  </span>
                                  {positionTrend && positionTrend.direction !== 'stable' && (
                                    <div className={`flex items-center gap-1 text-sm ${
                                      positionTrend.direction === 'up'
                                        ? 'text-green-600 dark:text-green-400'
                                        : 'text-red-600 dark:text-red-400'
                                    }`}>
                                      {positionTrend.direction === 'up' ? (
                                        <TrendingUp className="h-4 w-4" />
                                      ) : (
                                        <TrendingDown className="h-4 w-4" />
                                      )}
                                      <span>{positionTrend.change}</span>
                                    </div>
                                  )}
                                  {positionTrend && positionTrend.direction === 'stable' && (
                                    <Minus className="h-4 w-4 text-gray-400" />
                                  )}
                                </div>
                              </div>
                              <div className="text-right">
                                <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">
                                  V/D
                                </p>
                                <div className="text-lg font-semibold">
                                  <span className="text-green-600 dark:text-green-400">
                                    {ranking.my_stats?.matches_won}
                                  </span>
                                  <span className="text-gray-400 mx-1">/</span>
                                  <span className="text-red-600 dark:text-red-400">
                                    {ranking.my_stats?.matches_lost}
                                  </span>
                                </div>
                              </div>
                            </div>

                            {/* Mini sparkline */}
                            {ranking.my_stats?.position_history && ranking.my_stats.position_history.length > 1 && (
                              <div className="mt-3 h-8">
                                <div className="flex items-end justify-between h-full">
                                  {ranking.my_stats.position_history.map((pos, idx) => (
                                    <div
                                      key={idx}
                                      className="flex-1 mx-0.5"
                                    >
                                      <div
                                        className="bg-green-500 dark:bg-green-400 rounded-t"
                                        style={{
                                          height: `${100 - (pos / ranking.total_participants) * 100}%`,
                                          minHeight: '4px',
                                        }}
                                      />
                                    </div>
                                  ))}
                                </div>
                              </div>
                            )}
                          </div>
                        )}

                        {/* Stats */}
                        <div className="grid grid-cols-3 gap-4 text-center">
                          <div>
                            <p className="text-2xl font-bold text-gray-900 dark:text-white">
                              {ranking.total_participants}
                            </p>
                            <p className="text-xs text-gray-600 dark:text-gray-400">
                              Participantes
                            </p>
                          </div>
                          <div>
                            <p className="text-2xl font-bold text-gray-900 dark:text-white">
                              {ranking.my_stats?.points || 0}
                            </p>
                            <p className="text-xs text-gray-600 dark:text-gray-400">
                              Pontos
                            </p>
                          </div>
                          <div>
                            <p className="text-2xl font-bold text-gray-900 dark:text-white">
                              {ranking.my_stats?.win_rate.toFixed(0)}%
                            </p>
                            <p className="text-xs text-gray-600 dark:text-gray-400">
                              Vitórias
                            </p>
                          </div>
                        </div>

                        {/* Progress */}
                        {ranking.total_rounds && (
                          <div className="mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
                            <div className="flex items-center justify-between text-sm text-gray-600 dark:text-gray-400 mb-2">
                              <span>Rodada {ranking.current_round} de {ranking.total_rounds}</span>
                              <span>{Math.round((ranking.current_round / ranking.total_rounds) * 100)}%</span>
                            </div>
                            <div className="h-2 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
                              <div
                                className="h-full bg-gradient-to-r from-green-500 to-emerald-500 transition-all"
                                style={{ width: `${(ranking.current_round / ranking.total_rounds) * 100}%` }}
                              />
                            </div>
                          </div>
                        )}
                      </CardContent>
                    </Card>
                  </Link>
                </StaggerItem>
              )
            })}
          </div>
        </StaggerContainer>

        {/* Empty State */}
        {filteredRankings.length === 0 && (
          <Card>
            <CardContent className="p-12 text-center">
              <Trophy className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
                Nenhum ranking encontrado
              </h3>
              <p className="text-gray-600 dark:text-gray-400 mb-4">
                Tente ajustar os filtros ou criar um novo ranking
              </p>
              <Button asChild>
                <Link to="/rankings/new">
                  Criar Ranking
                </Link>
              </Button>
            </CardContent>
          </Card>
        )}
      </div>
    </PageTransition>
  )
}

export default Rankings
