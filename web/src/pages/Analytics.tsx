import { useState } from 'react'
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

const Analytics = () => {
  const [dateRange, setDateRange] = useState('30d')
  const [metric, setMetric] = useState('performance')

  // Mock data - in real app this would come from API
  const analyticsData = {
    overview: {
      totalMatches: 156,
      winRate: 73.2,
      avgMatchDuration: 127, // minutes
      totalPoints: 12847
    },
    trends: {
      matchesPlayed: [12, 15, 18, 22, 19, 25, 28],
      winRate: [68, 71, 69, 75, 72, 74, 73],
      avgDuration: [125, 130, 122, 135, 128, 124, 127]
    },
    surfacePerformance: [
      { surface: 'Hard', matches: 89, winRate: 75.3, avgDuration: 125 },
      { surface: 'Clay', matches: 45, winRate: 68.9, avgDuration: 142 },
      { surface: 'Grass', matches: 22, winRate: 77.3, avgDuration: 98 }
    ],
    shotAnalysis: {
      forehand: { total: 3842, winners: 186, errors: 124 },
      backhand: { total: 2973, winners: 142, errors: 98 },
      serve: { total: 1584, aces: 89, doubleFaults: 34 },
      volley: { total: 245, winners: 67, errors: 23 }
    }
  }

  const StatCard = ({
    title,
    value,
    change,
    icon: Icon,
    color = 'text-blue-500'
  }: {
    title: string
    value: string | number
    change?: string
    icon: React.ElementType
    color?: string
  }) => (
    <Card>
      <CardContent className="p-6">
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
      </CardContent>
    </Card>
  )

  return (
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
          <Button variant="outline">
            <RefreshCw className="w-4 h-4 mr-2" />
            Refresh
          </Button>
          <Button variant="outline">
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
                <option value="7d">Last 7 days</option>
                <option value="30d">Last 30 days</option>
                <option value="90d">Last 3 months</option>
                <option value="1y">Last year</option>
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
          value={analyticsData.overview.totalMatches}
          change="+12% from last period"
          icon={Activity}
          color="text-blue-500"
        />
        <StatCard
          title="Win Rate"
          value={`${analyticsData.overview.winRate}%`}
          change="+2.3% from last period"
          icon={TrendingUp}
          color="text-green-500"
        />
        <StatCard
          title="Avg Match Duration"
          value={`${Math.floor(analyticsData.overview.avgMatchDuration / 60)}h ${analyticsData.overview.avgMatchDuration % 60}m`}
          change="-5 min from last period"
          icon={Target}
          color="text-orange-500"
        />
        <StatCard
          title="Total Points"
          value={analyticsData.overview.totalPoints.toLocaleString()}
          change="+1,247 from last period"
          icon={BarChart3}
          color="text-purple-500"
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
            <div className="space-y-4">
              {/* Win Rate Chart Placeholder */}
              <div className="h-64 bg-muted rounded-lg flex items-center justify-center">
                <div className="text-center">
                  <BarChart3 className="w-12 h-12 mx-auto text-muted-foreground mb-2" />
                  <p className="text-sm text-muted-foreground">Win Rate Trend Chart</p>
                  <p className="text-xs text-muted-foreground">Chart.js integration would go here</p>
                </div>
              </div>

              {/* Key Metrics */}
              <div className="grid grid-cols-3 gap-4 text-center">
                <div>
                  <p className="text-2xl font-bold text-green-500">↑ 5.2%</p>
                  <p className="text-xs text-muted-foreground">Win Rate Change</p>
                </div>
                <div>
                  <p className="text-2xl font-bold text-blue-500">127</p>
                  <p className="text-xs text-muted-foreground">Avg Points/Match</p>
                </div>
                <div>
                  <p className="text-2xl font-bold text-orange-500">15</p>
                  <p className="text-xs text-muted-foreground">Matches This Month</p>
                </div>
              </div>
            </div>
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
            <div className="space-y-4">
              {analyticsData.surfacePerformance.map((surface) => (
                <div key={surface.surface} className="border rounded-lg p-4">
                  <div className="flex items-center justify-between mb-2">
                    <h4 className="font-medium">{surface.surface} Court</h4>
                    <span className="text-sm text-muted-foreground">
                      {surface.matches} matches
                    </span>
                  </div>

                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <span className="text-muted-foreground">Win Rate</span>
                      <p className="font-bold text-lg">{surface.winRate}%</p>
                      <div className="w-full bg-secondary rounded-full h-2 mt-1">
                        <div
                          className="bg-green-500 h-2 rounded-full"
                          style={{ width: `${surface.winRate}%` }}
                        />
                      </div>
                    </div>
                    <div>
                      <span className="text-muted-foreground">Avg Duration</span>
                      <p className="font-bold text-lg">{surface.avgDuration}m</p>
                      <div className="w-full bg-secondary rounded-full h-2 mt-1">
                        <div
                          className="bg-blue-500 h-2 rounded-full"
                          style={{ width: `${(surface.avgDuration / 150) * 100}%` }}
                        />
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
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
          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
            {Object.entries(analyticsData.shotAnalysis).map(([shotType, data]) => {
              const successRate = 'winners' in data ? ((data.winners / data.total) * 100).toFixed(1) : '0'
              const errorRate = 'errors' in data ? ((data.errors / data.total) * 100).toFixed(1) : '0'

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
                        <span className="text-green-600">Winners</span>
                        <span>{'winners' in data ? data.winners : 0} ({successRate}%)</span>
                      </div>
                      <div className="w-full bg-secondary rounded-full h-1.5">
                        <div
                          className="bg-green-500 h-1.5 rounded-full"
                          style={{ width: `${successRate}%` }}
                        />
                      </div>
                    </div>

                    <div className="space-y-2">
                      <div className="flex justify-between text-sm">
                        <span className="text-red-600">Errors</span>
                        <span>{'errors' in data ? data.errors : 0} ({errorRate}%)</span>
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
  )
}

export default Analytics