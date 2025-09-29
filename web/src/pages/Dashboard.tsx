import {
  Activity,
  Users,
  Trophy,
  Play,
  BarChart3,
  Calendar,
  Clock
} from 'lucide-react'
import { useTranslation } from 'react-i18next'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { useLiveMatches, useRecentMatches } from '@/hooks/useMatchData'
import { Link } from 'react-router-dom'

const Dashboard = () => {
  const { t } = useTranslation()
  const { data: liveMatchesData, isLoading: liveLoading } = useLiveMatches()
  const { data: recentMatchesData, isLoading: recentLoading } = useRecentMatches(5)

  // Verificação defensiva dos dados
  const liveMatches = Array.isArray(liveMatchesData) ? liveMatchesData : []
  const recentMatches = Array.isArray(recentMatchesData) ? recentMatchesData : []

  const stats = [
    {
      title: t('dashboard.liveMatches'),
      value: liveMatches.length,
      change: '+2 from yesterday',
      icon: Activity,
      color: 'text-green-600',
    },
    {
      title: t('dashboard.statistics.totalMatches'),
      value: '1,234',
      change: '+12% from last month',
      icon: Trophy,
      color: 'text-blue-600',
    },
    {
      title: 'Jogadores Rastreados',
      value: '156',
      change: '+8 new this week',
      icon: Users,
      color: 'text-purple-600',
    },
    {
      title: t('dashboard.statistics.totalHours'),
      value: '2,847h',
      change: '+15% from last month',
      icon: BarChart3,
      color: 'text-orange-600',
    },
  ]

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">{t('dashboard.title')}</h1>
          <p className="text-muted-foreground">
            {t('dashboard.welcome', { name: 'Treinador' })}
          </p>
        </div>
        <div className="flex space-x-2">
          <Link to="/live">
            <Button>
              <Play className="w-4 h-4 mr-2" />
              {t('dashboard.quickActions.newAnalysis')}
            </Button>
          </Link>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
        {stats.map((stat) => {
          const Icon = stat.icon
          return (
            <Card key={stat.title}>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">
                  {stat.title}
                </CardTitle>
                <Icon className={`h-4 w-4 ${stat.color}`} />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{stat.value}</div>
                <p className="text-xs text-muted-foreground">
                  {stat.change}
                </p>
              </CardContent>
            </Card>
          )
        })}
      </div>

      {/* Main Content Grid */}
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        {/* Live Matches */}
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle className="flex items-center">
              <Activity className="w-5 h-5 mr-2 text-green-600" />
              {t('dashboard.liveMatches')}
            </CardTitle>
            <CardDescription>
              Partidas ativas com análise em tempo real
            </CardDescription>
          </CardHeader>
          <CardContent>
            {liveLoading ? (
              <div className="flex items-center justify-center h-32">
                <div className="loading-spinner"></div>
              </div>
            ) : liveMatches.length ? (
              <div className="space-y-4">
                {liveMatches.map((match: any) => (
                  <div
                    key={match.id}
                    className="flex items-center justify-between p-4 border rounded-lg"
                  >
                    <div className="flex items-center space-x-4">
                      <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                      <div>
                        <p className="font-medium">
                          {match.player1.name} vs {match.player2.name}
                        </p>
                        <p className="text-sm text-muted-foreground">
                          {match.tournament} • {match.round}
                        </p>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className="font-mono">
                        {match.score || 'N/A'}
                      </p>
                      <Link to={`/match/${match.id}`}>
                        <Button variant="outline" size="sm">
                          Ver ao Vivo
                        </Button>
                      </Link>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-8">
                <Activity className="w-12 h-12 mx-auto text-muted-foreground mb-4" />
                <p className="text-muted-foreground">No live matches</p>
                <Link to="/live">
                  <Button variant="outline" className="mt-4">
                    Start Analysis
                  </Button>
                </Link>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Recent Activity */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <Clock className="w-5 h-5 mr-2" />
              Recent Activity
            </CardTitle>
          </CardHeader>
          <CardContent>
            {recentLoading ? (
              <div className="flex items-center justify-center h-32">
                <div className="loading-spinner"></div>
              </div>
            ) : (
              <div className="space-y-4">
                {recentMatches.slice(0, 5).map((match: any) => (
                  <div key={match.id} className="flex items-center space-x-3">
                    <div className="w-8 h-8 bg-muted rounded-full flex items-center justify-center">
                      <Trophy className="w-4 h-4" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium truncate">
                        {match.player1.name} vs {match.player2.name}
                      </p>
                      <p className="text-xs text-muted-foreground">
                        {new Date(match.date).toLocaleDateString()}
                      </p>
                    </div>
                    <div className="text-xs text-muted-foreground">
                      {match.status}
                    </div>
                  </div>
                ))}
                <Link to="/matches">
                  <Button variant="outline" className="w-full mt-4">
                    View All Matches
                  </Button>
                </Link>
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Quick Actions */}
      <Card>
        <CardHeader>
          <CardTitle>Quick Actions</CardTitle>
          <CardDescription>
            Common tasks and shortcuts
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
            <Link to="/live">
              <Button variant="outline" className="w-full">
                <Play className="w-4 h-4 mr-2" />
                Start Live Analysis
              </Button>
            </Link>
            <Button variant="outline" className="w-full">
              <Calendar className="w-4 h-4 mr-2" />
              Schedule Match
            </Button>
            <Link to="/players">
              <Button variant="outline" className="w-full">
                <Users className="w-4 h-4 mr-2" />
                Manage Players
              </Button>
            </Link>
            <Link to="/analytics">
              <Button variant="outline" className="w-full">
                <BarChart3 className="w-4 h-4 mr-2" />
                View Reports
              </Button>
            </Link>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

export default Dashboard