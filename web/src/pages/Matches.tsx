import { useState, useMemo } from 'react'
import { Link } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import {
  Search,
  Filter,
  ArrowUpDown,
  Play,
  Eye,
  Bookmark,
  Clock,
  Calendar,
  MapPin,
  TrendingUp,
  Inbox
} from 'lucide-react'
import { useMatches } from '@/hooks/useMatchData'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { Chip } from '@/components/ui/chip'
import { MatchFilters } from '@/services/matchService'
import { Match } from '@/types'

type StatusFilter = 'all' | 'live' | 'completed' | 'scheduled'

const Matches = () => {
  const [activeStatusFilter, setActiveStatusFilter] = useState<StatusFilter>('all')
  const [searchTerm, setSearchTerm] = useState('')
  const [debouncedSearch, setDebouncedSearch] = useState('')
  const [showFiltersPanel, setShowFiltersPanel] = useState(false)
  const [sortBy, setSortBy] = useState<'date' | 'tournament' | 'surface'>('date')
  const [bookmarkedMatches, setBookmarkedMatches] = useState<Set<string>>(new Set())

  // Construir filtros para API
  const apiFilters: MatchFilters = useMemo(() => {
    const filters: MatchFilters = {
      page: 1,
      limit: 20
    }

    if (activeStatusFilter !== 'all') {
      filters.status = activeStatusFilter
    }

    return filters
  }, [activeStatusFilter])

  const { data: matchesData, isLoading, error } = useMatches(apiFilters)

  // Verificação defensiva dos dados
  const matches = Array.isArray(matchesData?.data) ? matchesData.data : []

  // Debounce search
  useState(() => {
    const timer = setTimeout(() => {
      setDebouncedSearch(searchTerm)
    }, 300)
    return () => clearTimeout(timer)
  })

  // Filtrar e ordenar matches
  const filteredMatches = useMemo(() => {
    let filtered = [...matches]

    // Filtro de busca
    if (debouncedSearch) {
      const search = debouncedSearch.toLowerCase()
      filtered = filtered.filter(match =>
        match.player1.name.toLowerCase().includes(search) ||
        match.player2.name.toLowerCase().includes(search) ||
        match.tournament.toLowerCase().includes(search)
      )
    }

    // Ordenação
    filtered.sort((a, b) => {
      switch (sortBy) {
        case 'date':
          return new Date(b.date).getTime() - new Date(a.date).getTime()
        case 'tournament':
          return a.tournament.localeCompare(b.tournament)
        case 'surface':
          return a.surface.localeCompare(b.surface)
        default:
          return 0
      }
    })

    return filtered
  }, [matches, debouncedSearch, sortBy])

  // Surface color mapping
  const getSurfaceConfig = (surface: string) => {
    switch (surface) {
      case 'hard':
        return { color: 'bg-blue-500', label: 'Hard Court', accent: '#3b82f6' }
      case 'clay':
        return { color: 'bg-orange-500', label: 'Clay', accent: '#f97316' }
      case 'grass':
        return { color: 'bg-green-500', label: 'Grass', accent: '#22c55e' }
      case 'carpet':
        return { color: 'bg-purple-500', label: 'Carpet', accent: '#a855f7' }
      default:
        return { color: 'bg-slate-500', label: 'Unknown', accent: '#64748b' }
    }
  }

  // Status badge config
  const getStatusConfig = (status: string) => {
    switch (status) {
      case 'live':
        return {
          label: 'Live',
          className: 'bg-red-500/10 text-red-400 border-red-500/20',
          icon: <Play className="w-3 h-3" fill="currentColor" />
        }
      case 'completed':
        return {
          label: 'Completed',
          className: 'bg-blue-500/10 text-blue-400 border-blue-500/20',
          icon: null
        }
      case 'scheduled':
        return {
          label: 'Scheduled',
          className: 'bg-yellow-500/10 text-yellow-400 border-yellow-500/20',
          icon: <Clock className="w-3 h-3" />
        }
      case 'cancelled':
        return {
          label: 'Cancelled',
          className: 'bg-slate-500/10 text-slate-400 border-slate-500/20',
          icon: null
        }
      default:
        return {
          label: status,
          className: 'bg-slate-500/10 text-slate-400 border-slate-500/20',
          icon: null
        }
    }
  }

  // Toggle bookmark
  const toggleBookmark = (matchId: string) => {
    setBookmarkedMatches(prev => {
      const newSet = new Set(prev)
      if (newSet.has(matchId)) {
        newSet.delete(matchId)
      } else {
        newSet.add(matchId)
      }
      return newSet
    })
  }

  // Format duration
  const formatDuration = (duration?: number) => {
    if (!duration) return null
    const hours = Math.floor(duration / 60)
    const minutes = duration % 60
    return `${hours}h ${minutes}m`
  }

  // Format score
  const formatScore = (match: Match) => {
    if (!match.score?.sets || match.score.sets.length === 0) {
      return null
    }

    return match.score.sets.map((set, index) => (
      <span key={index} className="font-mono">
        {set.player1Games}-{set.player2Games}
        {set.player1Tiebreak !== undefined && (
          <sup className="text-xs">{set.player1Tiebreak}</sup>
        )}
        {index < match.score.sets.length - 1 && ' '}
      </span>
    ))
  }

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-[60vh]">
        <div className="text-center">
          <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-red-500/10 flex items-center justify-center">
            <TrendingUp className="w-8 h-8 text-red-400" />
          </div>
          <h3 className="text-lg font-semibold text-slate-100 mb-2">
            Erro ao carregar partidas
          </h3>
          <p className="text-slate-400 text-sm">
            Tente novamente mais tarde ou verifique sua conexão.
          </p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6 p-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-slate-100">
            Partidas
          </h1>
          <p className="text-slate-400 mt-1">
            Explore e analise partidas de tênis
          </p>
        </div>
      </div>

      {/* Filters Row 1: Status Chips */}
      <div className="flex items-center gap-3 flex-wrap">
        <Chip
          variant={activeStatusFilter === 'all' ? 'active' : 'default'}
          clickable
          onClick={() => setActiveStatusFilter('all')}
        >
          Todas
        </Chip>
        <Chip
          variant={activeStatusFilter === 'live' ? 'active' : 'default'}
          clickable
          onClick={() => setActiveStatusFilter('live')}
        >
          <Play className="w-3 h-3" fill="currentColor" />
          Live
        </Chip>
        <Chip
          variant={activeStatusFilter === 'completed' ? 'active' : 'default'}
          clickable
          onClick={() => setActiveStatusFilter('completed')}
        >
          Finalizadas
        </Chip>
        <Chip
          variant={activeStatusFilter === 'scheduled' ? 'active' : 'default'}
          clickable
          onClick={() => setActiveStatusFilter('scheduled')}
        >
          <Clock className="w-3 h-3" />
          Agendadas
        </Chip>
      </div>

      {/* Filters Row 2: Search, Filters, Sorting */}
      <div className="flex flex-col sm:flex-row gap-3">
        {/* Search */}
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
          <input
            type="text"
            placeholder="Buscar jogadores, torneios..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-10 pr-4 py-2.5 bg-slate-800 border border-slate-700 rounded-lg text-slate-100 placeholder:text-slate-500 text-sm focus:outline-none focus:ring-2 focus:ring-court-accent focus:border-transparent transition-all"
          />
        </div>

        {/* Filters Button */}
        <Button
          variant="outline"
          onClick={() => setShowFiltersPanel(!showFiltersPanel)}
          className="bg-slate-800 border-slate-700 text-slate-300 hover:border-court-accent hover:text-court-accent"
        >
          <Filter className="w-4 h-4 mr-2" />
          Filtros
        </Button>

        {/* Sort Button */}
        <Button
          variant="outline"
          onClick={() => {
            const sortOrder: Array<'date' | 'tournament' | 'surface'> = ['date', 'tournament', 'surface']
            const currentIndex = sortOrder.indexOf(sortBy)
            setSortBy(sortOrder[(currentIndex + 1) % sortOrder.length])
          }}
          className="bg-slate-800 border-slate-700 text-slate-300 hover:border-court-accent hover:text-court-accent"
        >
          <ArrowUpDown className="w-4 h-4 mr-2" />
          {sortBy === 'date' && 'Data'}
          {sortBy === 'tournament' && 'Torneio'}
          {sortBy === 'surface' && 'Superfície'}
        </Button>
      </div>

      {/* Filters Panel (expandable) */}
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
              <CardContent className="p-4">
                <div className="text-sm text-slate-400">
                  Filtros adicionais em desenvolvimento...
                </div>
              </CardContent>
            </Card>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Matches Grid */}
      {isLoading ? (
        <div className="grid gap-4 sm:grid-cols-1 md:grid-cols-2 lg:grid-cols-3">
          {[...Array(6)].map((_, i) => (
            <Card key={i} className="bg-slate-800 border-slate-700 animate-pulse">
              <CardContent className="p-0">
                <div className="h-40 bg-slate-700/50 rounded-t-lg" />
                <div className="p-4 space-y-3">
                  <div className="h-4 bg-slate-700 rounded w-3/4" />
                  <div className="h-3 bg-slate-700 rounded w-1/2" />
                  <div className="h-6 bg-slate-700 rounded" />
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      ) : filteredMatches.length > 0 ? (
        <motion.div
          className="grid gap-4 sm:grid-cols-1 md:grid-cols-2 lg:grid-cols-3"
          layout
        >
          <AnimatePresence mode="popLayout">
            {filteredMatches.map((match: Match) => {
              const surfaceConfig = getSurfaceConfig(match.surface)
              const statusConfig = getStatusConfig(match.status)
              const isBookmarked = bookmarkedMatches.has(match.id)

              return (
                <motion.div
                  key={match.id}
                  layout
                  initial={{ opacity: 0, scale: 0.9 }}
                  animate={{ opacity: 1, scale: 1 }}
                  exit={{ opacity: 0, scale: 0.9 }}
                  transition={{ duration: 0.2 }}
                >
                  <Card
                    className="bg-slate-800 border-slate-700 hover:border-court-accent transition-all duration-300 overflow-hidden group hover:shadow-lg hover:shadow-court-accent/10"
                    style={{ '--court-accent': surfaceConfig.accent } as React.CSSProperties}
                  >
                    <CardContent className="p-0">
                      {/* Thumbnail/Header Section */}
                      <div className={`relative h-24 ${surfaceConfig.color} bg-opacity-20 border-b border-slate-700 flex items-center justify-center`}>
                        {/* Surface Icon */}
                        <div className={`w-12 h-12 rounded-lg ${surfaceConfig.color} opacity-30`} />

                        {/* Status Badge - Top Right */}
                        <div className="absolute top-3 right-3">
                          <div className={`flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium border ${statusConfig.className}`}>
                            {statusConfig.icon}
                            {statusConfig.label}
                          </div>
                        </div>

                        {/* Bookmark Button - Top Left */}
                        <button
                          onClick={() => toggleBookmark(match.id)}
                          className="absolute top-3 left-3 w-8 h-8 rounded-full bg-slate-900/50 backdrop-blur-sm border border-slate-700 flex items-center justify-center hover:bg-slate-900/80 transition-colors"
                        >
                          <Bookmark
                            className={`w-4 h-4 transition-colors ${isBookmarked ? 'fill-yellow-400 text-yellow-400' : 'text-slate-400'}`}
                          />
                        </button>
                      </div>

                      {/* Content Section */}
                      <div className="p-4 space-y-3">
                        {/* Players */}
                        <div>
                          <h3 className="text-base font-semibold text-slate-100 truncate">
                            {match.player1.name}
                          </h3>
                          <div className="flex items-center gap-2 text-sm text-slate-400">
                            <span className="text-xs">vs</span>
                            <span className="truncate">{match.player2.name}</span>
                          </div>
                        </div>

                        {/* Score */}
                        {formatScore(match) && (
                          <div className="flex items-center gap-2 text-lg font-bold text-court-accent">
                            {formatScore(match)}
                          </div>
                        )}

                        {/* Meta Info */}
                        <div className="space-y-1.5">
                          {/* Tournament */}
                          <div className="flex items-center gap-2 text-xs text-slate-400">
                            <MapPin className="w-3 h-3" />
                            <span className="truncate">{match.tournament}</span>
                          </div>

                          {/* Date */}
                          <div className="flex items-center gap-2 text-xs text-slate-400">
                            <Calendar className="w-3 h-3" />
                            <span>{new Date(match.date).toLocaleDateString('pt-BR')}</span>
                          </div>

                          {/* Duration */}
                          {match.duration && (
                            <div className="flex items-center gap-2 text-xs text-slate-400">
                              <Clock className="w-3 h-3" />
                              <span>{formatDuration(match.duration)}</span>
                            </div>
                          )}
                        </div>

                        {/* Surface Tag */}
                        <div className="flex items-center gap-2">
                          <div className={`w-3 h-3 rounded-sm ${surfaceConfig.color}`} />
                          <span className="text-xs text-slate-400 capitalize">
                            {surfaceConfig.label}
                          </span>
                        </div>

                        {/* Actions */}
                        <div className="flex gap-2 pt-2">
                          <Link to={`/match/${match.id}`} className="flex-1">
                            <Button
                              variant="outline"
                              size="sm"
                              className="w-full bg-transparent border-slate-700 text-slate-300 hover:border-court-accent hover:text-court-accent"
                            >
                              <Eye className="w-3 h-3 mr-1.5" />
                              Ver Detalhes
                            </Button>
                          </Link>

                          {match.status === 'live' && (
                            <Link to={`/live?match=${match.id}`}>
                              <Button
                                size="sm"
                                className="bg-court-accent text-white hover:bg-court-accent-hover border-0"
                              >
                                <Play className="w-3 h-3" fill="currentColor" />
                              </Button>
                            </Link>
                          )}
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                </motion.div>
              )
            })}
          </AnimatePresence>
        </motion.div>
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
            {debouncedSearch
              ? 'Tente ajustar seus filtros ou buscar por outros termos.'
              : 'Não há partidas disponíveis no momento.'}
          </p>
          {(debouncedSearch || activeStatusFilter !== 'all') && (
            <Button
              variant="outline"
              onClick={() => {
                setSearchTerm('')
                setDebouncedSearch('')
                setActiveStatusFilter('all')
              }}
              className="bg-slate-800 border-slate-700 text-slate-300 hover:border-court-accent hover:text-court-accent"
            >
              Limpar Filtros
            </Button>
          )}
        </motion.div>
      )}
    </div>
  )
}

export default Matches
