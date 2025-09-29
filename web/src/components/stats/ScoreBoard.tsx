import { Match } from '@/types'
import { Card, CardContent } from '@/components/ui/card'
import { Clock, Trophy } from 'lucide-react'

interface ScoreBoardProps {
  match: Match
  compact?: boolean
}

const ScoreBoard = ({ match, compact = false }: ScoreBoardProps) => {
  const { player1, player2, score, status, duration } = match

  const getCurrentScore = () => {
    if (!score.currentGame) return { p1: 0, p2: 0 }

    const pointMap: Record<number, string> = {
      0: '0',
      1: '15',
      2: '30',
      3: '40'
    }

    const p1Points = score.currentGame.player1Points
    const p2Points = score.currentGame.player2Points

    // Handle deuce and advantage
    if (p1Points >= 3 && p2Points >= 3) {
      if (p1Points === p2Points) {
        return { p1: 'DEUCE', p2: 'DEUCE' }
      } else if (p1Points > p2Points) {
        return { p1: 'ADV', p2: '' }
      } else {
        return { p1: '', p2: 'ADV' }
      }
    }

    return {
      p1: pointMap[p1Points] || p1Points.toString(),
      p2: pointMap[p2Points] || p2Points.toString()
    }
  }

  const currentScore = getCurrentScore()

  const formatTime = (seconds: number) => {
    const hours = Math.floor(seconds / 3600)
    const minutes = Math.floor((seconds % 3600) / 60)
    const secs = seconds % 60

    if (hours > 0) {
      return `${hours}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
    }
    return `${minutes}:${secs.toString().padStart(2, '0')}`
  }

  if (compact) {
    return (
      <Card className="bg-gradient-to-r from-court-green to-green-600 text-white">
        <CardContent className="p-4">
          <div className="flex items-center justify-between">
            <div className="text-sm">
              <div className="font-medium">{player1.name}</div>
              <div className="font-medium">{player2.name}</div>
            </div>
            <div className="text-right">
              {score.sets.map((set, index) => (
                <div key={index} className="text-sm font-mono">
                  {set.player1Games}-{set.player2Games}
                  {set.player1Tiebreak !== undefined && (
                    <span className="text-xs ml-1">
                      ({set.player1Tiebreak}-{set.player2Tiebreak})
                    </span>
                  )}
                </div>
              ))}
            </div>
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card className="bg-gradient-to-br from-slate-900 to-slate-800 text-white">
      <CardContent className="p-6">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center space-x-2">
            <Trophy className="w-5 h-5 text-yellow-400" />
            <span className="text-sm font-medium text-slate-300">
              {match.tournament} • {match.round}
            </span>
          </div>
          <div className="flex items-center space-x-4">
            {status === 'live' && (
              <div className="flex items-center space-x-2">
                <div className="w-2 h-2 bg-red-500 rounded-full animate-pulse" />
                <span className="text-sm text-red-400">LIVE</span>
              </div>
            )}
            {duration && (
              <div className="flex items-center space-x-1 text-sm text-slate-300">
                <Clock className="w-4 h-4" />
                <span>{formatTime(duration)}</span>
              </div>
            )}
          </div>
        </div>

        {/* Players and Score */}
        <div className="space-y-4">
          {/* Player 1 */}
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="w-12 h-12 bg-blue-600 rounded-full flex items-center justify-center">
                <span className="text-lg font-bold">
                  {player1.name.split(' ').map(n => n[0]).join('')}
                </span>
              </div>
              <div>
                <div className="text-lg font-semibold">{player1.name}</div>
                <div className="text-sm text-slate-400">
                  {player1.country} • #{player1.ranking}
                </div>
              </div>
            </div>

            {/* Sets for Player 1 */}
            <div className="flex items-center space-x-4">
              {score.sets.map((set, index) => (
                <div
                  key={index}
                  className={`w-12 h-12 rounded-lg flex items-center justify-center text-lg font-bold border-2 ${
                    set.player1Games > set.player2Games
                      ? 'bg-green-600 border-green-500'
                      : set.player1Games < set.player2Games
                      ? 'bg-red-600 border-red-500'
                      : 'bg-slate-600 border-slate-500'
                  }`}
                >
                  {set.player1Games}
                  {set.player1Tiebreak !== undefined && (
                    <sup className="text-xs">{set.player1Tiebreak}</sup>
                  )}
                </div>
              ))}
              {/* Current game score */}
              {score.currentGame && status === 'live' && (
                <div className="w-16 h-12 rounded-lg bg-yellow-600 border-2 border-yellow-500 flex items-center justify-center">
                  <span className="text-lg font-bold">{currentScore.p1}</span>
                </div>
              )}
            </div>
          </div>

          {/* Player 2 */}
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="w-12 h-12 bg-red-600 rounded-full flex items-center justify-center">
                <span className="text-lg font-bold">
                  {player2.name.split(' ').map(n => n[0]).join('')}
                </span>
              </div>
              <div>
                <div className="text-lg font-semibold">{player2.name}</div>
                <div className="text-sm text-slate-400">
                  {player2.country} • #{player2.ranking}
                </div>
              </div>
            </div>

            {/* Sets for Player 2 */}
            <div className="flex items-center space-x-4">
              {score.sets.map((set, index) => (
                <div
                  key={index}
                  className={`w-12 h-12 rounded-lg flex items-center justify-center text-lg font-bold border-2 ${
                    set.player2Games > set.player1Games
                      ? 'bg-green-600 border-green-500'
                      : set.player2Games < set.player1Games
                      ? 'bg-red-600 border-red-500'
                      : 'bg-slate-600 border-slate-500'
                  }`}
                >
                  {set.player2Games}
                  {set.player2Tiebreak !== undefined && (
                    <sup className="text-xs">{set.player2Tiebreak}</sup>
                  )}
                </div>
              ))}
              {/* Current game score */}
              {score.currentGame && status === 'live' && (
                <div className="w-16 h-12 rounded-lg bg-yellow-600 border-2 border-yellow-500 flex items-center justify-center">
                  <span className="text-lg font-bold">{currentScore.p2}</span>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Server indicator */}
        {score.currentGame && status === 'live' && (
          <div className="mt-4 text-center">
            <span className="text-sm text-slate-300">
              {score.currentGame.server === 1 ? player1.name : player2.name} serving
            </span>
          </div>
        )}

        {/* Match status */}
        <div className="mt-4 text-center">
          <span className={`px-3 py-1 rounded-full text-xs font-medium ${
            status === 'live' ? 'bg-red-600' :
            status === 'completed' ? 'bg-green-600' :
            status === 'scheduled' ? 'bg-yellow-600' :
            'bg-gray-600'
          }`}>
            {status.toUpperCase()}
          </span>
        </div>
      </CardContent>
    </Card>
  )
}

export default ScoreBoard