import { useParams, Link } from 'react-router-dom'
import {
  ArrowLeft,
  Play,
  Download,
  Share,
  BarChart3,
  Video,
  Map,
  Trophy,
  Target,
  Activity
} from 'lucide-react'
import { useMatch, useMatchStatistics, useMatchHighlights } from '@/hooks/useMatchData'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import ScoreBoard from '@/components/stats/ScoreBoard'
import VideoPlayer from '@/components/video/VideoPlayer'
import CourtView from '@/components/court/CourtView'

const MatchDetail = () => {
  const { id } = useParams<{ id: string }>()

  const { data: match, isLoading: matchLoading } = useMatch(id!)
  const { data: statistics } = useMatchStatistics(id!)
  const { data: highlights } = useMatchHighlights(id!)

  // Verificação defensiva dos dados
  const highlightsList = Array.isArray(highlights?.highlights) ? highlights.highlights : []

  if (matchLoading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="loading-spinner"></div>
      </div>
    )
  }

  if (!match) {
    return (
      <div className="text-center py-12">
        <Trophy className="w-16 h-16 mx-auto text-muted-foreground mb-4" />
        <h3 className="text-lg font-medium mb-2">Match not found</h3>
        <p className="text-muted-foreground">The requested match could not be found.</p>
        <Link to="/matches">
          <Button className="mt-4">Back to Matches</Button>
        </Link>
      </div>
    )
  }

  const formatDuration = (duration: number) => {
    const hours = Math.floor(duration / 3600)
    const minutes = Math.floor((duration % 3600) / 60)
    return `${hours}h ${minutes}m`
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <Link to="/matches">
            <Button variant="outline" size="icon">
              <ArrowLeft className="w-4 h-4" />
            </Button>
          </Link>
          <div>
            <h1 className="text-3xl font-bold tracking-tight">
              {match.player1.name} vs {match.player2.name}
            </h1>
            <p className="text-muted-foreground">
              {match.tournament} • {match.round} • {new Date(match.date).toLocaleDateString()}
            </p>
          </div>
        </div>

        <div className="flex items-center space-x-2">
          {match.status === 'live' && (
            <Link to={`/live?match=${match.id}`}>
              <Button>
                <Play className="w-4 h-4 mr-2" />
                Watch Live
              </Button>
            </Link>
          )}
          <Button variant="outline">
            <Download className="w-4 h-4 mr-2" />
            Export
          </Button>
          <Button variant="outline">
            <Share className="w-4 h-4 mr-2" />
            Share
          </Button>
        </div>
      </div>

      {/* Score Board */}
      <ScoreBoard match={match} />

      {/* Main Content */}
      <div className="grid gap-6 lg:grid-cols-3">
        {/* Video and Analysis */}
        <div className="lg:col-span-2 space-y-6">
          {/* Video Player */}
          {match.videoUrl && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <Video className="w-5 h-5 mr-2" />
                  Match Video
                </CardTitle>
              </CardHeader>
              <CardContent>
                <VideoPlayer src={match.videoUrl} showOverlays={true} />
              </CardContent>
            </Card>
          )}

          {/* Court Analysis */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <Map className="w-5 h-5 mr-2" />
                Court Analysis
              </CardTitle>
            </CardHeader>
            <CardContent>
              <CourtView showTrajectory={true} />
            </CardContent>
          </Card>

          {/* Match Highlights */}
          {highlightsList.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <Target className="w-5 h-5 mr-2" />
                  Match Highlights
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {highlightsList.map((highlight, index) => (
                    <div
                      key={index}
                      className="flex items-center justify-between p-3 border rounded-lg hover:bg-accent cursor-pointer"
                    >
                      <div>
                        <p className="font-medium">{highlight.description}</p>
                        <p className="text-sm text-muted-foreground">
                          {Math.floor(highlight.timestamp / 60)}:{(highlight.timestamp % 60).toString().padStart(2, '0')}
                        </p>
                      </div>
                      <div className="flex items-center space-x-2">
                        <span className="px-2 py-1 bg-secondary rounded text-xs">
                          {highlight.type}
                        </span>
                        <Button variant="outline" size="sm">
                          <Play className="w-3 h-3" />
                        </Button>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}
        </div>

        {/* Statistics Panel */}
        <div className="space-y-6">
          {/* Match Info */}
          <Card>
            <CardHeader>
              <CardTitle>Match Information</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-muted-foreground">Surface</span>
                <span className="font-medium capitalize">{match.surface}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-muted-foreground">Duration</span>
                <span className="font-medium">
                  {match.duration ? formatDuration(match.duration) : 'N/A'}
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-muted-foreground">Status</span>
                <span className={`px-2 py-1 rounded text-xs font-medium ${
                  match.status === 'live' ? 'bg-green-100 text-green-800' :
                  match.status === 'completed' ? 'bg-blue-100 text-blue-800' :
                  'bg-gray-100 text-gray-800'
                }`}>
                  {match.status.toUpperCase()}
                </span>
              </div>
            </CardContent>
          </Card>

          {/* Player Statistics */}
          {statistics && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <BarChart3 className="w-5 h-5 mr-2" />
                  Statistics
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-6">
                  {/* Aces */}
                  <div>
                    <div className="flex justify-between text-sm mb-2">
                      <span>Aces</span>
                      <span>{statistics.player1Stats.aces} - {statistics.player2Stats.aces}</span>
                    </div>
                    <div className="grid grid-cols-2 gap-2">
                      <div className="h-2 bg-blue-200 rounded">
                        <div
                          className="h-2 bg-blue-500 rounded"
                          style={{
                            width: `${(statistics.player1Stats.aces / Math.max(statistics.player1Stats.aces + statistics.player2Stats.aces, 1)) * 100}%`
                          }}
                        />
                      </div>
                      <div className="h-2 bg-red-200 rounded">
                        <div
                          className="h-2 bg-red-500 rounded"
                          style={{
                            width: `${(statistics.player2Stats.aces / Math.max(statistics.player1Stats.aces + statistics.player2Stats.aces, 1)) * 100}%`
                          }}
                        />
                      </div>
                    </div>
                  </div>

                  {/* Winners */}
                  <div>
                    <div className="flex justify-between text-sm mb-2">
                      <span>Winners</span>
                      <span>{statistics.player1Stats.winners} - {statistics.player2Stats.winners}</span>
                    </div>
                    <div className="grid grid-cols-2 gap-2">
                      <div className="h-2 bg-blue-200 rounded">
                        <div
                          className="h-2 bg-blue-500 rounded"
                          style={{
                            width: `${(statistics.player1Stats.winners / Math.max(statistics.player1Stats.winners + statistics.player2Stats.winners, 1)) * 100}%`
                          }}
                        />
                      </div>
                      <div className="h-2 bg-red-200 rounded">
                        <div
                          className="h-2 bg-red-500 rounded"
                          style={{
                            width: `${(statistics.player2Stats.winners / Math.max(statistics.player1Stats.winners + statistics.player2Stats.winners, 1)) * 100}%`
                          }}
                        />
                      </div>
                    </div>
                  </div>

                  {/* Unforced Errors */}
                  <div>
                    <div className="flex justify-between text-sm mb-2">
                      <span>Unforced Errors</span>
                      <span>{statistics.player1Stats.unforcedErrors} - {statistics.player2Stats.unforcedErrors}</span>
                    </div>
                    <div className="grid grid-cols-2 gap-2">
                      <div className="h-2 bg-blue-200 rounded">
                        <div
                          className="h-2 bg-blue-500 rounded"
                          style={{
                            width: `${(statistics.player1Stats.unforcedErrors / Math.max(statistics.player1Stats.unforcedErrors + statistics.player2Stats.unforcedErrors, 1)) * 100}%`
                          }}
                        />
                      </div>
                      <div className="h-2 bg-red-200 rounded">
                        <div
                          className="h-2 bg-red-500 rounded"
                          style={{
                            width: `${(statistics.player2Stats.unforcedErrors / Math.max(statistics.player1Stats.unforcedErrors + statistics.player2Stats.unforcedErrors, 1)) * 100}%`
                          }}
                        />
                      </div>
                    </div>
                  </div>

                  {/* First Serve Percentage */}
                  <div>
                    <div className="flex justify-between text-sm mb-2">
                      <span>First Serve %</span>
                      <span>
                        {((statistics.player1Stats.firstServeIn / statistics.player1Stats.firstServeAttempts) * 100).toFixed(0)}% - {' '}
                        {((statistics.player2Stats.firstServeIn / statistics.player2Stats.firstServeAttempts) * 100).toFixed(0)}%
                      </span>
                    </div>
                  </div>
                </div>

                <Button variant="outline" className="w-full mt-4">
                  <BarChart3 className="w-4 h-4 mr-2" />
                  Detailed Analytics
                </Button>
              </CardContent>
            </Card>
          )}

          {/* Quick Actions */}
          <Card>
            <CardHeader>
              <CardTitle>Actions</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              <Button variant="outline" className="w-full">
                <Video className="w-4 h-4 mr-2" />
                Download Video
              </Button>
              <Button variant="outline" className="w-full">
                <BarChart3 className="w-4 h-4 mr-2" />
                Export Statistics
              </Button>
              <Button variant="outline" className="w-full">
                <Activity className="w-4 h-4 mr-2" />
                Generate Report
              </Button>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}

export default MatchDetail