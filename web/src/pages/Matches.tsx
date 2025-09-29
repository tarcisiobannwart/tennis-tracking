import { useState } from 'react'
import { Link } from 'react-router-dom'
import {
  Search,
  Filter,
  Plus,
  Calendar,
  Trophy,
  Clock,
  Play,
  Eye,
  MoreHorizontal
} from 'lucide-react'
import { useMatches } from '@/hooks/useMatchData'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { MatchFilters } from '@/services/matchService'
import { Match } from '@/types'

const Matches = () => {
  const [filters, setFilters] = useState<MatchFilters>({
    page: 1,
    limit: 20
  })
  const [searchTerm, setSearchTerm] = useState('')

  const { data: matchesData, isLoading, error } = useMatches(filters)

  // Verificação defensiva dos dados
  const matches = Array.isArray(matchesData?.data) ? matchesData.data : []

  const handleFilterChange = (newFilters: Partial<MatchFilters>) => {
    setFilters(prev => ({ ...prev, ...newFilters, page: 1 }))
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'live':
        return 'text-green-600 bg-green-100 dark:bg-green-900'
      case 'completed':
        return 'text-blue-600 bg-blue-100 dark:bg-blue-900'
      case 'scheduled':
        return 'text-yellow-600 bg-yellow-100 dark:bg-yellow-900'
      case 'cancelled':
        return 'text-red-600 bg-red-100 dark:bg-red-900'
      default:
        return 'text-gray-600 bg-gray-100 dark:bg-gray-900'
    }
  }

  const getSurfaceIcon = (surface: string) => {
    const iconClass = "w-4 h-4"
    switch (surface) {
      case 'hard':
        return <div className={`${iconClass} bg-blue-500 rounded-sm`} />
      case 'clay':
        return <div className={`${iconClass} bg-orange-500 rounded-sm`} />
      case 'grass':
        return <div className={`${iconClass} bg-green-500 rounded-sm`} />
      default:
        return <div className={`${iconClass} bg-gray-500 rounded-sm`} />
    }
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center">
          <Trophy className="w-16 h-16 mx-auto text-muted-foreground mb-4" />
          <h3 className="text-lg font-medium mb-2">Error loading matches</h3>
          <p className="text-muted-foreground">Please try again later</p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Matches</h1>
          <p className="text-muted-foreground">
            Manage and analyze tennis matches
          </p>
        </div>
        <Button>
          <Plus className="w-4 h-4 mr-2" />
          New Match
        </Button>
      </div>

      {/* Filters and Search */}
      <Card>
        <CardContent className="p-6">
          <div className="flex flex-col md:flex-row gap-4">
            {/* Search */}
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-muted-foreground" />
              <input
                type="text"
                placeholder="Search matches, players, tournaments..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10 pr-4 py-2 w-full bg-background border border-input rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-ring"
              />
            </div>

            {/* Status Filter */}
            <select
              value={filters.status || ''}
              onChange={(e) => handleFilterChange({ status: e.target.value || undefined })}
              className="px-3 py-2 bg-background border border-input rounded-md text-sm"
            >
              <option value="">All Status</option>
              <option value="live">Live</option>
              <option value="completed">Completed</option>
              <option value="scheduled">Scheduled</option>
              <option value="cancelled">Cancelled</option>
            </select>

            {/* Surface Filter */}
            <select
              value={filters.surface || ''}
              onChange={(e) => handleFilterChange({ surface: e.target.value || undefined })}
              className="px-3 py-2 bg-background border border-input rounded-md text-sm"
            >
              <option value="">All Surfaces</option>
              <option value="hard">Hard Court</option>
              <option value="clay">Clay</option>
              <option value="grass">Grass</option>
              <option value="carpet">Carpet</option>
            </select>

            <Button variant="outline">
              <Filter className="w-4 h-4 mr-2" />
              More Filters
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Matches Grid */}
      {isLoading ? (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {[...Array(6)].map((_, i) => (
            <Card key={i} className="animate-pulse">
              <CardContent className="p-6">
                <div className="space-y-3">
                  <div className="h-4 bg-muted rounded w-3/4"></div>
                  <div className="h-4 bg-muted rounded w-1/2"></div>
                  <div className="h-8 bg-muted rounded"></div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      ) : (
        <div className="space-y-4">
          {matches && matches.length > 0 ? matches.map((match: Match) => (
            <Card key={match.id} className="hover:shadow-md transition-shadow">
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  {/* Match Info */}
                  <div className="flex items-center space-x-6">
                    {/* Players */}
                    <div className="flex-1">
                      <div className="flex items-center space-x-4 mb-2">
                        <div className="text-lg font-medium">
                          {match.player1.name}
                        </div>
                        <span className="text-muted-foreground">vs</span>
                        <div className="text-lg font-medium">
                          {match.player2.name}
                        </div>
                      </div>

                      {/* Score */}
                      {match.score && match.score.sets && (
                        <div className="flex items-center space-x-2 text-sm font-mono">
                          <span className="font-medium">
                            {match.score.sets.map((set: any, index: number) => (
                              <span key={index}>
                                {set.player1Games}-{set.player2Games}
                                {index < match.score.sets.length - 1 ? ' ' : ''}
                              </span>
                            ))}
                          </span>
                        </div>
                      )}
                    </div>

                    {/* Tournament Info */}
                    <div className="text-right">
                      <div className="flex items-center space-x-2 text-sm text-muted-foreground mb-1">
                        <Trophy className="w-4 h-4" />
                        <span>{match.tournament}</span>
                      </div>
                      <div className="flex items-center space-x-2 text-sm text-muted-foreground mb-1">
                        <Calendar className="w-4 h-4" />
                        <span>{new Date(match.date).toLocaleDateString()}</span>
                      </div>
                      <div className="flex items-center space-x-2 text-sm text-muted-foreground">
                        {getSurfaceIcon(match.surface)}
                        <span className="capitalize">{match.surface}</span>
                      </div>
                    </div>

                    {/* Status */}
                    <div className="flex flex-col items-end space-y-2">
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(match.status)}`}>
                        {match.status === 'live' && <Play className="w-3 h-3 inline mr-1" />}
                        {match.status.charAt(0).toUpperCase() + match.status.slice(1)}
                      </span>

                      {match.duration && (
                        <div className="flex items-center space-x-1 text-xs text-muted-foreground">
                          <Clock className="w-3 h-3" />
                          <span>{Math.floor(match.duration / 60)}h {match.duration % 60}m</span>
                        </div>
                      )}
                    </div>
                  </div>

                  {/* Actions */}
                  <div className="flex items-center space-x-2">
                    <Link to={`/match/${match.id}`}>
                      <Button variant="outline" size="sm">
                        <Eye className="w-4 h-4 mr-1" />
                        View
                      </Button>
                    </Link>

                    {match.status === 'live' && (
                      <Link to={`/live?match=${match.id}`}>
                        <Button size="sm">
                          <Play className="w-4 h-4 mr-1" />
                          Live
                        </Button>
                      </Link>
                    )}

                    <Button variant="ghost" size="sm">
                      <MoreHorizontal className="w-4 h-4" />
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          )) : (
            <div className="text-center py-12">
              <p className="text-muted-foreground">Nenhuma partida encontrada</p>
            </div>
          )}

          {/* Pagination */}
          {matchesData && matchesData.total > matchesData.limit && (
            <Card>
              <CardContent className="p-4">
                <div className="flex items-center justify-between">
                  <div className="text-sm text-muted-foreground">
                    Showing {((matchesData.page - 1) * matchesData.limit) + 1} to{' '}
                    {Math.min(matchesData.page * matchesData.limit, matchesData.total)} of{' '}
                    {matchesData.total} matches
                  </div>
                  <div className="flex space-x-2">
                    <Button
                      variant="outline"
                      size="sm"
                      disabled={!matchesData.hasPrev}
                      onClick={() => handleFilterChange({ page: matchesData.page - 1 })}
                    >
                      Previous
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      disabled={!matchesData.hasNext}
                      onClick={() => handleFilterChange({ page: matchesData.page + 1 })}
                    >
                      Next
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}
        </div>
      )}
    </div>
  )
}

export default Matches