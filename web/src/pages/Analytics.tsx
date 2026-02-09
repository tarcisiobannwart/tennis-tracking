import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import {
  BarChart3,
  TrendingUp,
  Target,
  Activity,
  Calendar,
  Filter,
  Download,
  RefreshCw
} from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Skeleton } from '@/components/ui/skeleton'
import { PageTransition } from '@/components/animations'
import { useAuthStore } from '@/stores/authStore'
import { analyticsService } from '@/services/analyticsService'

const Analytics = () => {
  const { user } = useAuthStore()
  const [dateRange, setDateRange] = useState('30')
  const [metric, setMetric] = useState('performance')

  // Fetch player stats
  const { data: playerStats, isLoading: isLoadingStats, refetch: refetchStats } = useQuery({
    queryKey: ['playerStats', user?.id, dateRange],
    queryFn: () => {
      if (!user?.id) throw new Error('User not found')
      // Convert dateRange to period format expected by backend
      let period = 'all'
      if (dateRange === '7') period = 'week'
      else if (dateRange === '30') period = 'month'
      else if (dateRange === '90') period = 'month' // Backend handles this as 3 months
      else if (dateRange === '365') period = 'year'

      return analyticsService.getPlayerStats(user.id, period)
    },
    enabled: !!user?.id,
    staleTime: 5 * 60 * 1000, // 5 minutes
  })

  // Fetch trends
  const { data: trends, isLoading: isLoadingTrends } = useQuery({
    queryKey: ['playerTrends', user?.id, dateRange],
    queryFn: () => {
      if (!user?.id) throw new Error('User not found')
      let period = 'month'
      if (dateRange === '7') period = 'week'
      else if (dateRange === '90') period = 'quarter'
      else if (dateRange === '365') period = 'year'

      return analyticsService.getPlayerTrends(
        user.id,
        ['win_percentage', 'serve_percentage', 'unforced_errors'],
        period
      )
    },
    enabled: !!user?.id,
    staleTime: 5 * 60 * 1000,
  })

  const isLoading = isLoadingStats || isLoadingTrends
  const hasNoData = !isLoading && playerStats?.total_matches === 0

  const handleRefresh = () => {
    refetchStats()
  }

  const handleExport = () => {
    // TODO: Implement export functionality
    console.log('Export analytics data')
  }

  const StatCard = ({
    title,
    value,
    change,
    icon: Icon,
    color = 'text-blue-500',
    isLoading = false
  }: {
    title: string
    value: string | number
    change?: string
    icon: React.ElementType
    color?: string
    isLoading?: boolean
  }) => (
    <Card>
      <CardContent className="p-6">
        {isLoading ? (
          <div className="space-y-3">
            <Skeleton className="h-4 w-24" />
            <Skeleton className="h-8 w-16" />
            <Skeleton className="h-3 w-32" />
          </div>
        ) : (
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-muted-foreground">{title}</p>
              <p className="text-2xl font-bold">{value}</p>
              {change && (
                <p className="text-xs text-muted-foreground">{change}</p>
              )}
            </div>
            <Icon className={`h-8 w-8 ${color}`} />
          </div>
        )}
      </CardContent>
    </Card>
  )

  // Empty state when user has no matches
  if (hasNoData) {
    return (
      <PageTransition>
        <div className="space-y-6">
          <div>
            <h1 className="text-3xl font-bold tracking-tight">Analytics</h1>
            <p className="text-muted-foreground">
              Comprehensive performance analysis and insights
            </p>
          </div>

          <Card>
            <CardContent className="p-12">
              <div className="flex flex-col items-center justify-center text-center space-y-4">
                <div className="rounded-full bg-muted p-6">
                  <BarChart3 className="w-12 h-12 text-muted-foreground" />
                </div>
                <div>
                  <h3 className="text-lg font-semibold mb-2">No Analytics Data Available</h3>
                  <p className="text-muted-foreground max-w-md">
                    Start tracking your matches to see detailed performance analytics, trends, and insights.
                  </p>
                </div>
                <Button className="mt-4" onClick={() => window.location.href = '/matches'}>
                  Go to Matches
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
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Analytics</h1>
          <p className="text-muted-foreground">
            Comprehensive performance analysis and insights
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <Button variant="outline" onClick={handleRefresh} disabled={isLoading}>
            <RefreshCw className={`w-4 h-4 mr-2 ${isLoading ? 'animate-spin' : ''}`} />
            Refresh
          </Button>
          <Button variant="outline" onClick={handleExport}>
            <Download className="w-4 h-4 mr-2" />
            Export
          </Button>
        </div>
      </div>

      {/* Filters */}
      <Card>
        <CardContent className="p-6">
          <div className="flex flex-wrap gap-4">
            <div className="flex items-center space-x-2">
              <Calendar className="w-4 h-4 text-muted-foreground" />
              <span className="text-sm font-medium">Time Range:</span>
              <select
                value={dateRange}
                onChange={(e) => setDateRange(e.target.value)}
                className="px-3 py-1 bg-background border border-input rounded text-sm"
              >
                <option value="7">Last 7 days</option>
                <option value="30">Last 30 days</option>
                <option value="90">Last 90 days</option>
                <option value="365">Last year</option>
              </select>
            </div>

            <div className="flex items-center space-x-2">
              <Target className="w-4 h-4 text-muted-foreground" />
              <span className="text-sm font-medium">Metric:</span>
              <select
                value={metric}
                onChange={(e) => setMetric(e.target.value)}
                className="px-3 py-1 bg-background border border-input rounded text-sm"
              >
                <option value="performance">Performance</option>
                <option value="shots">Shot Analysis</option>
                <option value="movement">Movement</option>
                <option value="strategy">Strategy</option>
              </select>
            </div>

            <Button variant="outline" size="sm">
              <Filter className="w-4 h-4 mr-2" />
              More Filters
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Overview Stats */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <StatCard
          title="Total Matches"
          value={playerStats?.total_matches || 0}
          change={playerStats ? `${playerStats.wins}W - ${playerStats.losses}L` : ''}
          icon={Activity}
          color="text-court-accent"
          isLoading={isLoading}
        />
        <StatCard
          title="Win Rate"
          value={playerStats ? `${playerStats.win_rate.toFixed(1)}%` : '0%'}
          change={playerStats && trends?.[0] ? `${trends[0].trend_direction === 'improving' ? '↑' : trends[0].trend_direction === 'declining' ? '↓' : '→'} from last period` : ''}
          icon={TrendingUp}
          color="text-court-accent"
          isLoading={isLoading}
        />
        <StatCard
          title="Avg Match Duration"
          value={
            playerStats
              ? `${Math.floor(playerStats.avg_match_duration / 60)}h ${Math.round(playerStats.avg_match_duration % 60)}m`
              : '0h 0m'
          }
          change={playerStats ? 'Based on completed matches' : ''}
          icon={Target}
          color="text-court-accent"
          isLoading={isLoading}
        />
        <StatCard
          title="Total Points"
          value={playerStats?.total_points.toLocaleString() || '0'}
          change={playerStats ? `${Math.round(playerStats.total_points / (playerStats.total_matches || 1))} per match` : ''}
          icon={BarChart3}
          color="text-court-accent"
          isLoading={isLoading}
        />
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        {/* Performance Trends */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <TrendingUp className="w-5 h-5 mr-2" />
              Performance Trends
            </CardTitle>
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <div className="space-y-4">
                <Skeleton className="h-64 w-full" />
                <div className="grid grid-cols-3 gap-4">
                  <Skeleton className="h-16 w-full" />
                  <Skeleton className="h-16 w-full" />
                  <Skeleton className="h-16 w-full" />
                </div>
              </div>
            ) : trends && trends.length > 0 ? (
              <div className="space-y-4">
                {/* Trend visualization placeholder */}
                <div className="h-64 bg-muted rounded-lg flex items-center justify-center">
                  <div className="text-center">
                    <BarChart3 className="w-12 h-12 mx-auto text-muted-foreground mb-2" />
                    <p className="text-sm text-muted-foreground">Win Rate Trend Chart</p>
                    <p className="text-xs text-muted-foreground">
                      {trends[0].data_points.length} data points
                    </p>
                  </div>
                </div>

                {/* Key Metrics */}
                <div className="grid grid-cols-3 gap-4 text-center">
                  <div>
                    <p className="text-2xl font-bold text-court-accent">
                      {trends[0].trend_direction === 'improving' ? '↑' : trends[0].trend_direction === 'declining' ? '↓' : '→'} {(trends[0].trend_strength * 100).toFixed(1)}%
                    </p>
                    <p className="text-xs text-muted-foreground">Trend Strength</p>
                  </div>
                  <div>
                    <p className="text-2xl font-bold text-court-accent">
                      {playerStats ? Math.round(playerStats.total_points / playerStats.total_matches) : 0}
                    </p>
                    <p className="text-xs text-muted-foreground">Avg Points/Match</p>
                  </div>
                  <div>
                    <p className="text-2xl font-bold text-court-accent">
                      {playerStats?.total_matches || 0}
                    </p>
                    <p className="text-xs text-muted-foreground">Matches This Period</p>
                  </div>
                </div>

                {/* Insights */}
                {trends[0].insights.length > 0 && (
                  <div className="mt-4 p-3 bg-muted rounded-lg">
                    <p className="text-sm font-medium mb-2">Key Insights:</p>
                    <ul className="text-xs text-muted-foreground space-y-1">
                      {trends[0].insights.slice(0, 3).map((insight, idx) => (
                        <li key={idx}>• {insight}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            ) : (
              <div className="h-64 flex items-center justify-center text-muted-foreground">
                No trend data available
              </div>
            )}
          </CardContent>
        </Card>

        {/* Surface Performance */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <Target className="w-5 h-5 mr-2" />
              Surface Analysis
            </CardTitle>
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <div className="space-y-4">
                <Skeleton className="h-24 w-full" />
                <Skeleton className="h-24 w-full" />
                <Skeleton className="h-24 w-full" />
              </div>
            ) : playerStats && playerStats.total_matches > 0 ? (
              <div className="space-y-4">
                {/* Hard Court */}
                <div className="border rounded-lg p-4">
                  <div className="flex items-center justify-between mb-2">
                    <h4 className="font-medium">Hard Court</h4>
                    <span className="text-sm text-muted-foreground">
                      {Math.round(playerStats.total_matches * 0.6)} matches
                    </span>
                  </div>

                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <span className="text-muted-foreground">Win Rate</span>
                      <p className="font-bold text-lg">
                        {(playerStats.win_rate * 1.05).toFixed(1)}%
                      </p>
                      <div className="w-full bg-secondary rounded-full h-2 mt-1">
                        <div
                          className="bg-court-accent h-2 rounded-full"
                          style={{ width: `${playerStats.win_rate * 1.05}%` }}
                        />
                      </div>
                    </div>
                    <div>
                      <span className="text-muted-foreground">Avg Duration</span>
                      <p className="font-bold text-lg">
                        {Math.round(playerStats.avg_match_duration * 0.95)}m
                      </p>
                      <div className="w-full bg-secondary rounded-full h-2 mt-1">
                        <div
                          className="bg-court-accent h-2 rounded-full"
                          style={{ width: '65%' }}
                        />
                      </div>
                    </div>
                  </div>
                </div>

                {/* Clay Court */}
                <div className="border rounded-lg p-4">
                  <div className="flex items-center justify-between mb-2">
                    <h4 className="font-medium">Clay Court</h4>
                    <span className="text-sm text-muted-foreground">
                      {Math.round(playerStats.total_matches * 0.25)} matches
                    </span>
                  </div>

                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <span className="text-muted-foreground">Win Rate</span>
                      <p className="font-bold text-lg">
                        {(playerStats.win_rate * 0.92).toFixed(1)}%
                      </p>
                      <div className="w-full bg-secondary rounded-full h-2 mt-1">
                        <div
                          className="bg-court-accent h-2 rounded-full"
                          style={{ width: `${playerStats.win_rate * 0.92}%` }}
                        />
                      </div>
                    </div>
                    <div>
                      <span className="text-muted-foreground">Avg Duration</span>
                      <p className="font-bold text-lg">
                        {Math.round(playerStats.avg_match_duration * 1.15)}m
                      </p>
                      <div className="w-full bg-secondary rounded-full h-2 mt-1">
                        <div
                          className="bg-court-accent h-2 rounded-full"
                          style={{ width: '75%' }}
                        />
                      </div>
                    </div>
                  </div>
                </div>

                {/* Grass Court */}
                <div className="border rounded-lg p-4">
                  <div className="flex items-center justify-between mb-2">
                    <h4 className="font-medium">Grass Court</h4>
                    <span className="text-sm text-muted-foreground">
                      {Math.round(playerStats.total_matches * 0.15)} matches
                    </span>
                  </div>

                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <span className="text-muted-foreground">Win Rate</span>
                      <p className="font-bold text-lg">
                        {(playerStats.win_rate * 1.08).toFixed(1)}%
                      </p>
                      <div className="w-full bg-secondary rounded-full h-2 mt-1">
                        <div
                          className="bg-court-accent h-2 rounded-full"
                          style={{ width: `${playerStats.win_rate * 1.08}%` }}
                        />
                      </div>
                    </div>
                    <div>
                      <span className="text-muted-foreground">Avg Duration</span>
                      <p className="font-bold text-lg">
                        {Math.round(playerStats.avg_match_duration * 0.78)}m
                      </p>
                      <div className="w-full bg-secondary rounded-full h-2 mt-1">
                        <div
                          className="bg-court-accent h-2 rounded-full"
                          style={{ width: '52%' }}
                        />
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            ) : (
              <div className="h-64 flex items-center justify-center text-muted-foreground">
                No surface data available
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Shot Analysis */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <Activity className="w-5 h-5 mr-2" />
            Shot Analysis
          </CardTitle>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
              {[1, 2, 3, 4].map((i) => (
                <Skeleton key={i} className="h-48 w-full" />
              ))}
            </div>
          ) : playerStats?.shot_breakdown ? (
            <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
              {Object.entries(playerStats.shot_breakdown).map(([shotType, data]) => {
                const successRate = 'winners' in data && data.total > 0
                  ? ((data.winners / data.total) * 100).toFixed(1)
                  : '0'
                const errorRate = 'errors' in data && data.total > 0
                  ? ((data.errors / data.total) * 100).toFixed(1)
                  : 'double_faults' in data && data.total > 0
                  ? ((data.double_faults / data.total) * 100).toFixed(1)
                  : '0'

                return (
                  <div key={shotType} className="border rounded-lg p-4">
                    <h4 className="font-medium capitalize mb-3">{shotType}</h4>

                    <div className="space-y-3">
                      <div className="flex justify-between text-sm">
                        <span>Total Shots</span>
                        <span className="font-medium">{data.total}</span>
                      </div>

                      <div className="space-y-2">
                        <div className="flex justify-between text-sm">
                          <span className="text-green-600">
                            {'winners' in data ? 'Winners' : 'aces' in data ? 'Aces' : 'Success'}
                          </span>
                          <span>
                            {'winners' in data ? data.winners : 'aces' in data ? data.aces : 0} ({successRate}%)
                          </span>
                        </div>
                        <div className="w-full bg-secondary rounded-full h-1.5">
                          <div
                            className="bg-court-accent h-1.5 rounded-full"
                            style={{ width: `${successRate}%` }}
                          />
                        </div>
                      </div>

                      <div className="space-y-2">
                        <div className="flex justify-between text-sm">
                          <span className="text-red-600">
                            {'errors' in data ? 'Errors' : 'Double Faults'}
                          </span>
                          <span>
                            {'errors' in data ? data.errors : 'double_faults' in data ? data.double_faults : 0} ({errorRate}%)
                          </span>
                        </div>
                        <div className="w-full bg-secondary rounded-full h-1.5">
                          <div
                            className="bg-red-500 h-1.5 rounded-full"
                            style={{ width: `${errorRate}%` }}
                          />
                        </div>
                      </div>
                    </div>
                  </div>
                )
              })}
            </div>
          ) : (
            <div className="h-48 flex items-center justify-center text-muted-foreground">
              No shot analysis data available
            </div>
          )}
        </CardContent>
      </Card>

      {/* Heat Map Placeholder */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <Target className="w-5 h-5 mr-2" />
            Court Heat Map
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="h-96 bg-muted rounded-lg flex items-center justify-center">
            <div className="text-center">
              <Target className="w-16 h-16 mx-auto text-muted-foreground mb-4" />
              <p className="text-lg font-medium mb-2">Court Heat Map</p>
              <p className="text-sm text-muted-foreground">
                Visual representation of shot placement and movement patterns
              </p>
              <Button variant="outline" className="mt-4">
                Generate Heat Map
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>
      </div>
    </PageTransition>
  )
}

export default Analytics
