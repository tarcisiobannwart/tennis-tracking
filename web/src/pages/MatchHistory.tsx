/**
 * Match History Page - TT-135
 * Pagina de historico de jogos com placares detalhados
 * Ref: LetzPlay /u/matches/history
 */

import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import {
  Search,
  Filter,
  Calendar,
  MapPin,
  Clock,
  Trophy,
  ChevronRight,
  Users,
  X,
  Inbox,
  CheckCircle2,
  XCircle,
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { Chip } from '@/components/ui/chip'
import { PageTransition, StaggerContainer, StaggerItem, Skeleton } from '@/components/animations'
import {
  matchHistoryService,
  MatchHistoryFilters,
  MatchHistoryItem,
  MatchHistoryResponse,
} from '@/services/matchHistoryService'

const MatchHistory = () => {
  const [matches, setMatches] = useState<MatchHistoryItem[]>([])
  const [total, setTotal] = useState(0)
  const [currentPage, setCurrentPage] = useState(1)
  const [totalPages, setTotalPages] = useState(0)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  // Filtros
  const [activeTypeFilter, setActiveTypeFilter] = useState<
    'all' | 'ranking' | 'amistoso' | 'torneio'
  >('all')
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedSurface, setSelectedSurface] = useState<string | null>(null)
  const [showFiltersPanel, setShowFiltersPanel] = useState(false)
  const [startDate, setStartDate] = useState<string>('')
  const [endDate, setEndDate] = useState<string>('')

  const limit = 20

  // Buscar partidas
  const fetchMatches = async () => {
    setIsLoading(true)
    setError(null)

    try {
      const filters: MatchHistoryFilters = {
        skip: (currentPage - 1) * limit,
        limit,
      }

      if (activeTypeFilter !== 'all') {
        filters.match_type = activeTypeFilter
      }

      if (searchTerm.trim()) {
        filters.opponent_name = searchTerm.trim()
      }

      if (selectedSurface) {
        filters.surface = selectedSurface as any
      }

      if (startDate) {
        filters.start_date = startDate
      }

      if (endDate) {
        filters.end_date = endDate
      }

      const response: MatchHistoryResponse = await matchHistoryService.getMatchHistory(filters)

      setMatches(response.matches)
      setTotal(response.total)
      setTotalPages(response.total_pages)
    } catch (err: any) {
      console.error('Erro ao buscar historico de partidas:', err)
      setError(err.message || 'Erro ao carregar historico de partidas')
    } finally {
      setIsLoading(false)
    }
  }

  // Efeito para buscar quando filtros mudarem
  useEffect(() => {
    fetchMatches()
  }, [currentPage, activeTypeFilter, selectedSurface, startDate, endDate])

  // Debounce search
  useEffect(() => {
    const timer = setTimeout(() => {
      if (currentPage === 1) {
        fetchMatches()
      } else {
        setCurrentPage(1)
      }
    }, 500)

    return () => clearTimeout(timer)
  }, [searchTerm])

  // Surface config
  const getSurfaceConfig = (surface?: string) => {
    switch (surface) {
      case 'hard':
        return { color: 'bg-blue-500', label: 'Hard Court', accent: '#3b82f6' }
      case 'clay':
        return { color: 'bg-orange-500', label: 'Saibro', accent: '#f97316' }
      case 'grass':
        return { color: 'bg-green-500', label: 'Grama', accent: '#22c55e' }
      case 'carpet':
        return { color: 'bg-purple-500', label: 'Carpete', accent: '#a855f7' }
      default:
        return { color: 'bg-slate-500', label: 'Desconhecido', accent: '#64748b' }
    }
  }

  // Match type badge
  const getMatchTypeBadge = (type: string) => {
    switch (type) {
      case 'ranking':
        return {
          label: 'Ranking',
          className: 'bg-yellow-500/10 text-yellow-400 border-yellow-500/20',
        }
      case 'torneio':
        return {
          label: 'Torneio',
          className: 'bg-purple-500/10 text-purple-400 border-purple-500/20',
        }
      case 'amistoso':
        return {
          label: 'Amistoso',
          className: 'bg-blue-500/10 text-blue-400 border-blue-500/20',
        }
      default:
        return {
          label: type,
          className: 'bg-slate-500/10 text-slate-400 border-slate-500/20',
        }
    }
  }

  // Format date
  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr)
    return date.toLocaleDateString('pt-BR', {
      day: '2-digit',
      month: 'short',
      year: 'numeric',
    })
  }

  // Format duration
  const formatDuration = (minutes?: number) => {
    if (!minutes) return null
    const hours = Math.floor(minutes / 60)
    const mins = minutes % 60
    return `${hours}h${mins.toString().padStart(2, '0')}`
  }

  // Limpar filtros
  const clearFilters = () => {
    setActiveTypeFilter('all')
    setSearchTerm('')
    setSelectedSurface(null)
    setStartDate('')
    setEndDate('')
    setCurrentPage(1)
  }

  // Contagem de filtros ativos
  const activeFiltersCount =
    (activeTypeFilter !== 'all' ? 1 : 0) +
    (searchTerm ? 1 : 0) +
    (selectedSurface ? 1 : 0) +
    (startDate ? 1 : 0) +
    (endDate ? 1 : 0)

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="text-center">
          <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-red-500/10 flex items-center justify-center">
            <XCircle className="w-8 h-8 text-red-400" />
          </div>
          <h3 className="text-lg font-semibold text-slate-100 mb-2">Erro ao carregar historico</h3>
          <p className="text-slate-400 text-sm mb-4">{error}</p>
          <Button onClick={fetchMatches} variant="outline">
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
              Historico de Jogos
            </h1>
            <p className="text-slate-400 mt-1">
              {total} {total === 1 ? 'partida encontrada' : 'partidas encontradas'}
            </p>
          </div>
        </div>

        {/* Filtros: Tipo de Partida */}
        <div className="flex items-center gap-3 flex-wrap">
          <Chip
            variant={activeTypeFilter === 'all' ? 'active' : 'default'}
            clickable
            onClick={() => setActiveTypeFilter('all')}
          >
            Todas
          </Chip>
          <Chip
            variant={activeTypeFilter === 'ranking' ? 'active' : 'default'}
            clickable
            onClick={() => setActiveTypeFilter('ranking')}
          >
            <Trophy className="w-3 h-3" />
            Ranking
          </Chip>
          <Chip
            variant={activeTypeFilter === 'torneio' ? 'active' : 'default'}
            clickable
            onClick={() => setActiveTypeFilter('torneio')}
          >
            <Trophy className="w-3 h-3" />
            Torneio
          </Chip>
          <Chip
            variant={activeTypeFilter === 'amistoso' ? 'active' : 'default'}
            clickable
            onClick={() => setActiveTypeFilter('amistoso')}
          >
            <Users className="w-3 h-3" />
            Amistoso
          </Chip>
        </div>

        {/* Barra de busca e filtros */}
        <div className="flex flex-col sm:flex-row gap-3">
          {/* Search */}
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
            <input
              type="text"
              placeholder="Buscar por oponente..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-2.5 bg-slate-800 border border-slate-700 rounded-lg text-slate-100 placeholder:text-slate-500 text-sm focus:outline-none focus:ring-2 focus:ring-court-accent focus:border-transparent transition-all"
            />
          </div>

          {/* Filters Button */}
          <Button
            variant="outline"
            onClick={() => setShowFiltersPanel(!showFiltersPanel)}
            className="bg-slate-800 border-slate-700 text-slate-300 hover:border-court-accent hover:text-court-accent relative"
          >
            <Filter className="w-4 h-4 mr-2" />
            Filtros Avancados
            {activeFiltersCount > 0 && (
              <span className="absolute -top-1 -right-1 w-5 h-5 rounded-full bg-court-accent text-white text-xs flex items-center justify-center">
                {activeFiltersCount}
              </span>
            )}
          </Button>

          {/* Clear Filters */}
          {activeFiltersCount > 0 && (
            <Button
              variant="outline"
              onClick={clearFilters}
              className="bg-slate-800 border-slate-700 text-slate-300 hover:border-red-500 hover:text-red-400"
            >
              <X className="w-4 h-4" />
            </Button>
          )}
        </div>

        {/* Painel de Filtros Avancados */}
        <AnimatePresence>
          {showFiltersPanel && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              transition={{ duration: 0.2 }}
              className="overflow-hidden"
            >
              <Card className="bg-slate-800 border-slate-700">
                <CardContent className="p-4 space-y-4">
                  {/* Superficie */}
                  <div>
                    <label className="block text-sm font-medium text-slate-300 mb-2">
                      Superficie
                    </label>
                    <div className="flex gap-2 flex-wrap">
                      {['hard', 'clay', 'grass', 'carpet'].map((surface) => {
                        const config = getSurfaceConfig(surface)
                        return (
                          <button
                            key={surface}
                            onClick={() =>
                              setSelectedSurface(selectedSurface === surface ? null : surface)
                            }
                            className={`px-3 py-2 rounded-lg text-sm font-medium transition-all ${
                              selectedSurface === surface
                                ? `${config.color} text-white`
                                : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
                            }`}
                          >
                            {config.label}
                          </button>
                        )
                      })}
                    </div>
                  </div>

                  {/* Periodo */}
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                    <div>
                      <label className="block text-sm font-medium text-slate-300 mb-2">
                        Data Inicial
                      </label>
                      <input
                        type="date"
                        value={startDate}
                        onChange={(e) => setStartDate(e.target.value)}
                        className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-slate-100 text-sm focus:outline-none focus:ring-2 focus:ring-court-accent focus:border-transparent"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-slate-300 mb-2">
                        Data Final
                      </label>
                      <input
                        type="date"
                        value={endDate}
                        onChange={(e) => setEndDate(e.target.value)}
                        className="w-full px-3 py-2 bg-slate-700 border border-slate-600 rounded-lg text-slate-100 text-sm focus:outline-none focus:ring-2 focus:ring-court-accent focus:border-transparent"
                      />
                    </div>
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Lista de Partidas */}
        {isLoading ? (
          <div className="space-y-3">
            {[...Array(5)].map((_, i) => (
              <Skeleton key={i} className="h-32 rounded-xl" />
            ))}
          </div>
        ) : matches.length > 0 ? (
          <StaggerContainer className="space-y-3">
            <AnimatePresence mode="popLayout">
              {matches.map((match) => {
                const typeBadge = getMatchTypeBadge(match.match_type)
                const surfaceConfig = getSurfaceConfig(match.surface)
                const isVictory = match.result === 'vitoria'

                return (
                  <StaggerItem key={match.id}>
                    <Link to={`/match-history/${match.id}`}>
                      <Card className="bg-slate-800 border-slate-700 hover:border-court-accent transition-all duration-300 overflow-hidden group hover:shadow-lg hover:shadow-court-accent/10">
                        <CardContent className="p-4">
                          <div className="flex items-center justify-between gap-4">
                            {/* Left: Resultado Icon */}
                            <div
                              className={`w-12 h-12 rounded-full flex items-center justify-center flex-shrink-0 ${
                                isVictory
                                  ? 'bg-green-500/10 text-green-400'
                                  : 'bg-red-500/10 text-red-400'
                              }`}
                            >
                              {isVictory ? (
                                <CheckCircle2 className="w-6 h-6" />
                              ) : (
                                <XCircle className="w-6 h-6" />
                              )}
                            </div>

                            {/* Center: Info */}
                            <div className="flex-1 min-w-0">
                              {/* Oponente e Placar */}
                              <div className="flex items-center gap-3 mb-2">
                                <h3 className="text-base font-semibold text-slate-100 truncate">
                                  vs {match.opponent.name}
                                </h3>
                                <div className="flex items-center gap-2 text-lg font-bold text-court-accent">
                                  {match.score.sets}
                                </div>
                              </div>

                              {/* Sets Detail */}
                              <div className="flex items-center gap-2 mb-2 flex-wrap">
                                {match.score.sets_detail.map((set) => (
                                  <span
                                    key={set.set_number}
                                    className="px-2 py-1 rounded bg-slate-700 text-slate-300 text-xs font-mono"
                                  >
                                    {set.user_games}-{set.opponent_games}
                                    {set.user_tiebreak !== undefined && (
                                      <sup className="text-[10px]">
                                        {set.user_tiebreak}
                                      </sup>
                                    )}
                                  </span>
                                ))}
                              </div>

                              {/* Meta Info */}
                              <div className="flex items-center gap-4 text-xs text-slate-400 flex-wrap">
                                {/* Data */}
                                <div className="flex items-center gap-1">
                                  <Calendar className="w-3 h-3" />
                                  <span>{formatDate(match.date)}</span>
                                </div>

                                {/* Torneio */}
                                {match.tournament && (
                                  <div className="flex items-center gap-1">
                                    <MapPin className="w-3 h-3" />
                                    <span className="truncate max-w-[200px]">
                                      {match.tournament}
                                    </span>
                                  </div>
                                )}

                                {/* Duracao */}
                                {match.duration_minutes && (
                                  <div className="flex items-center gap-1">
                                    <Clock className="w-3 h-3" />
                                    <span>{formatDuration(match.duration_minutes)}</span>
                                  </div>
                                )}
                              </div>
                            </div>

                            {/* Right: Badges e Arrow */}
                            <div className="flex flex-col items-end gap-2 flex-shrink-0">
                              {/* Type Badge */}
                              <div
                                className={`px-2 py-1 rounded text-xs font-medium border ${typeBadge.className}`}
                              >
                                {typeBadge.label}
                              </div>

                              {/* Surface */}
                              {match.surface && (
                                <div className="flex items-center gap-1">
                                  <div className={`w-2 h-2 rounded-sm ${surfaceConfig.color}`} />
                                  <span className="text-xs text-slate-400">
                                    {surfaceConfig.label}
                                  </span>
                                </div>
                              )}

                              {/* Arrow */}
                              <ChevronRight className="w-5 h-5 text-slate-500 group-hover:text-court-accent transition-colors" />
                            </div>
                          </div>
                        </CardContent>
                      </Card>
                    </Link>
                  </StaggerItem>
                )
              })}
            </AnimatePresence>
          </StaggerContainer>
        ) : (
          /* Empty State */
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="flex flex-col items-center justify-center min-h-[50vh] text-center"
          >
            <div className="w-20 h-20 mb-6 rounded-full bg-slate-800 border-2 border-dashed border-slate-700 flex items-center justify-center">
              <Inbox className="w-10 h-10 text-slate-600" />
            </div>
            <h3 className="text-xl font-semibold text-slate-300 mb-2">
              Nenhuma partida encontrada
            </h3>
            <p className="text-slate-500 text-sm max-w-sm mb-6">
              {activeFiltersCount > 0
                ? 'Tente ajustar seus filtros ou buscar por outros termos.'
                : 'Voce ainda nao possui historico de partidas.'}
            </p>
            {activeFiltersCount > 0 && (
              <Button variant="outline" onClick={clearFilters}>
                Limpar Filtros
              </Button>
            )}
          </motion.div>
        )}

        {/* Paginacao */}
        {totalPages > 1 && (
          <div className="flex items-center justify-center gap-2 mt-6">
            <Button
              variant="outline"
              size="sm"
              onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
              disabled={currentPage === 1}
              className="bg-slate-800 border-slate-700 text-slate-300 disabled:opacity-50"
            >
              Anterior
            </Button>

            <div className="flex items-center gap-1">
              {[...Array(Math.min(5, totalPages))].map((_, i) => {
                let pageNum: number
                if (totalPages <= 5) {
                  pageNum = i + 1
                } else if (currentPage <= 3) {
                  pageNum = i + 1
                } else if (currentPage >= totalPages - 2) {
                  pageNum = totalPages - 4 + i
                } else {
                  pageNum = currentPage - 2 + i
                }

                return (
                  <button
                    key={i}
                    onClick={() => setCurrentPage(pageNum)}
                    className={`w-8 h-8 rounded text-sm font-medium transition-all ${
                      currentPage === pageNum
                        ? 'bg-court-accent text-white'
                        : 'bg-slate-800 text-slate-400 hover:bg-slate-700'
                    }`}
                  >
                    {pageNum}
                  </button>
                )
              })}
            </div>

            <Button
              variant="outline"
              size="sm"
              onClick={() => setCurrentPage((p) => Math.min(totalPages, p + 1))}
              disabled={currentPage === totalPages}
              className="bg-slate-800 border-slate-700 text-slate-300 disabled:opacity-50"
            >
              Proximo
            </Button>
          </div>
        )}
      </div>
    </PageTransition>
  )
}

export default MatchHistory
