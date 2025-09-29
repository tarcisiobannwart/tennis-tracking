import { Activity, Target, Zap, TrendingUp } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { LiveFrame } from '@/types'

interface LiveStatsProps {
  currentFrame?: LiveFrame | null
  isAnalyzing: boolean
}

const LiveStats = ({ currentFrame, isAnalyzing }: LiveStatsProps) => {
  // Mock real-time statistics - in real app, these would come from frame analysis
  const stats = {
    ballSpeed: currentFrame?.ballPosition ? Math.floor(Math.random() * 50) + 80 : 0,
    ballHeight: currentFrame?.ballPosition?.z || 0,
    rallyLength: 8,
    shotCount: 12,
    bounceDetected: currentFrame?.predictions.ballBounce?.probability || 0,
    courtCoverage: {
      player1: 65,
      player2: 72
    },
    accuracy: {
      ballTracking: 94,
      playerTracking: 88,
      courtDetection: 92
    }
  }

  const StatCard = ({
    title,
    value,
    unit = '',
    icon: Icon,
    color = 'text-blue-500',
    trend = null as number | null
  }: {
    title: string
    value: number | string
    unit?: string
    icon: React.ElementType
    color?: string
    trend?: number | null
  }) => (
    <div className="bg-card border border-border rounded-lg p-4">
      <div className="flex items-center justify-between mb-2">
        <Icon className={`w-5 h-5 ${color}`} />
        {trend !== null && (
          <div className={`flex items-center text-xs ${trend >= 0 ? 'text-green-500' : 'text-red-500'}`}>
            <TrendingUp className="w-3 h-3 mr-1" />
            {trend >= 0 ? '+' : ''}{trend}%
          </div>
        )}
      </div>
      <div className="text-2xl font-bold mb-1">
        {value}{unit}
      </div>
      <div className="text-xs text-muted-foreground">{title}</div>
    </div>
  )

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center">
          <Activity className="w-5 h-5 mr-2" />
          Live Statistics
          {isAnalyzing && (
            <div className="ml-auto flex items-center text-green-500">
              <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse mr-2" />
              <span className="text-xs">Analyzing</span>
            </div>
          )}
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Ball Statistics */}
        <div>
          <h4 className="text-sm font-medium mb-3 text-muted-foreground">Ball Tracking</h4>
          <div className="grid grid-cols-2 gap-3">
            <StatCard
              title="Ball Speed"
              value={stats.ballSpeed}
              unit=" km/h"
              icon={Zap}
              color="text-yellow-500"
              trend={stats.ballSpeed > 0 ? 5 : null}
            />
            <StatCard
              title="Height"
              value={stats.ballHeight.toFixed(1)}
              unit="m"
              icon={Target}
              color="text-blue-500"
            />
          </div>
        </div>

        {/* Rally Statistics */}
        <div>
          <h4 className="text-sm font-medium mb-3 text-muted-foreground">Current Rally</h4>
          <div className="grid grid-cols-2 gap-3">
            <StatCard
              title="Rally Length"
              value={stats.rallyLength}
              unit=" shots"
              icon={Activity}
              color="text-green-500"
            />
            <StatCard
              title="Shot Count"
              value={stats.shotCount}
              icon={Target}
              color="text-purple-500"
            />
          </div>
        </div>

        {/* Bounce Detection */}
        {stats.bounceDetected > 0 && (
          <div>
            <h4 className="text-sm font-medium mb-3 text-muted-foreground">Predictions</h4>
            <div className="bg-orange-50 dark:bg-orange-900/20 border border-orange-200 dark:border-orange-800 rounded-lg p-3">
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium text-orange-800 dark:text-orange-200">
                  Bounce Detected
                </span>
                <span className="text-lg font-bold text-orange-600">
                  {(stats.bounceDetected * 100).toFixed(0)}%
                </span>
              </div>
              <div className="mt-2 bg-orange-200 dark:bg-orange-800 rounded-full h-2">
                <div
                  className="bg-orange-500 h-2 rounded-full transition-all"
                  style={{ width: `${stats.bounceDetected * 100}%` }}
                />
              </div>
            </div>
          </div>
        )}

        {/* Player Movement */}
        <div>
          <h4 className="text-sm font-medium mb-3 text-muted-foreground">Court Coverage</h4>
          <div className="space-y-3">
            <div>
              <div className="flex justify-between text-sm mb-1">
                <span>Player 1</span>
                <span>{stats.courtCoverage.player1}%</span>
              </div>
              <div className="bg-secondary rounded-full h-2">
                <div
                  className="bg-blue-500 h-2 rounded-full transition-all"
                  style={{ width: `${stats.courtCoverage.player1}%` }}
                />
              </div>
            </div>
            <div>
              <div className="flex justify-between text-sm mb-1">
                <span>Player 2</span>
                <span>{stats.courtCoverage.player2}%</span>
              </div>
              <div className="bg-secondary rounded-full h-2">
                <div
                  className="bg-red-500 h-2 rounded-full transition-all"
                  style={{ width: `${stats.courtCoverage.player2}%` }}
                />
              </div>
            </div>
          </div>
        </div>

        {/* System Accuracy */}
        <div>
          <h4 className="text-sm font-medium mb-3 text-muted-foreground">System Accuracy</h4>
          <div className="space-y-2">
            {Object.entries(stats.accuracy).map(([key, value]) => (
              <div key={key} className="flex justify-between items-center text-sm">
                <span className="capitalize">{key.replace(/([A-Z])/g, ' $1')}</span>
                <div className="flex items-center space-x-2">
                  <div className="w-16 bg-secondary rounded-full h-1.5">
                    <div
                      className={`h-1.5 rounded-full transition-all ${
                        value >= 90 ? 'bg-green-500' :
                        value >= 75 ? 'bg-yellow-500' :
                        'bg-red-500'
                      }`}
                      style={{ width: `${value}%` }}
                    />
                  </div>
                  <span className="text-xs font-medium w-8">{value}%</span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Frame Info */}
        {currentFrame && (
          <div className="border-t pt-4">
            <h4 className="text-sm font-medium mb-2 text-muted-foreground">Frame Info</h4>
            <div className="text-xs space-y-1 text-muted-foreground">
              <div>Frame: {currentFrame.frameNumber}</div>
              <div>Time: {(currentFrame.timestamp / 1000).toFixed(2)}s</div>
              {currentFrame.courtDetection && (
                <div>Court Confidence: {(currentFrame.courtDetection.confidence * 100).toFixed(0)}%</div>
              )}
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  )
}

export default LiveStats