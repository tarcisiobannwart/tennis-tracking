import { Clock, Trophy, Target, Zap, AlertCircle } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { MatchEvent } from '@/types'

interface EventTimelineProps {
  events: MatchEvent[]
  currentTime: number
  maxEvents?: number
}

const EventTimeline = ({ events, currentTime, maxEvents = 10 }: EventTimelineProps) => {
  // Sort events by timestamp (most recent first) and limit
  const recentEvents = [...events]
    .sort((a, b) => b.timestamp - a.timestamp)
    .slice(0, maxEvents)

  const formatTime = (timestamp: number) => {
    const seconds = Math.floor(timestamp / 1000)
    const minutes = Math.floor(seconds / 60)
    const remainingSeconds = seconds % 60
    return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`
  }

  const getEventIcon = (type: string) => {
    switch (type) {
      case 'point_start':
      case 'point_end':
        return Trophy
      case 'ace':
        return Zap
      case 'double_fault':
        return AlertCircle
      case 'break_point':
        return Target
      case 'game_end':
      case 'set_end':
      case 'match_end':
        return Trophy
      default:
        return Clock
    }
  }

  const getEventColor = (type: string, importance?: string) => {
    if (importance === 'high') return 'text-red-500 bg-red-50 dark:bg-red-900/20 border-red-200 dark:border-red-800'
    if (importance === 'medium') return 'text-yellow-500 bg-yellow-50 dark:bg-yellow-900/20 border-yellow-200 dark:border-yellow-800'

    switch (type) {
      case 'ace':
        return 'text-green-500 bg-green-50 dark:bg-green-900/20 border-green-200 dark:border-green-800'
      case 'double_fault':
        return 'text-red-500 bg-red-50 dark:bg-red-900/20 border-red-200 dark:border-red-800'
      case 'break_point':
        return 'text-orange-500 bg-orange-50 dark:bg-orange-900/20 border-orange-200 dark:border-orange-800'
      case 'point_end':
        return 'text-blue-500 bg-blue-50 dark:bg-blue-900/20 border-blue-200 dark:border-blue-800'
      default:
        return 'text-gray-500 bg-gray-50 dark:bg-gray-900/20 border-gray-200 dark:border-gray-800'
    }
  }

  const getEventDescription = (event: MatchEvent) => {
    let description = event.description

    // Add player indication if available
    if (event.player) {
      description = `P${event.player}: ${description}`
    }

    return description
  }

  const isCurrentEvent = (event: MatchEvent) => {
    return Math.abs(event.timestamp - currentTime) < 5000 // Within 5 seconds
  }

  if (events.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <Clock className="w-5 h-5 mr-2" />
            Event Timeline
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center py-8 text-muted-foreground">
            <Clock className="w-12 h-12 mx-auto mb-4 opacity-50" />
            <p>No events recorded</p>
            <p className="text-sm">Events will appear here during analysis</p>
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center justify-between">
          <div className="flex items-center">
            <Clock className="w-5 h-5 mr-2" />
            Event Timeline
          </div>
          <div className="text-sm text-muted-foreground">
            {events.length} events
          </div>
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-3 max-h-80 overflow-y-auto">
          {recentEvents.map((event, index) => {
            const Icon = getEventIcon(event.type)
            const colorClasses = getEventColor(event.type, event.data?.importance)
            const isCurrent = isCurrentEvent(event)

            return (
              <div
                key={event.id}
                className={`relative flex items-start space-x-3 p-3 rounded-lg border transition-all ${
                  isCurrent
                    ? 'ring-2 ring-primary bg-primary/5'
                    : colorClasses
                }`}
              >
                {/* Timeline connector */}
                {index < recentEvents.length - 1 && (
                  <div className="absolute left-6 top-12 w-px h-8 bg-border" />
                )}

                {/* Event icon */}
                <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
                  isCurrent ? 'bg-primary text-primary-foreground' : 'bg-background'
                }`}>
                  <Icon className="w-4 h-4" />
                </div>

                {/* Event content */}
                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between">
                    <div className="text-sm font-medium">
                      {getEventDescription(event)}
                    </div>
                    <div className="text-xs text-muted-foreground flex-shrink-0 ml-2">
                      {formatTime(event.timestamp)}
                    </div>
                  </div>

                  {/* Event type badge */}
                  <div className="mt-1">
                    <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-secondary text-secondary-foreground">
                      {event.type.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                    </span>
                  </div>

                  {/* Additional data */}
                  {event.data && Object.keys(event.data).length > 0 && (
                    <div className="mt-2 text-xs text-muted-foreground">
                      {Object.entries(event.data)
                        .filter(([key]) => key !== 'importance')
                        .map(([key, value]) => (
                          <div key={key} className="flex justify-between">
                            <span className="capitalize">{key.replace(/_/g, ' ')}:</span>
                            <span>{String(value)}</span>
                          </div>
                        ))
                      }
                    </div>
                  )}
                </div>

                {/* Current indicator */}
                {isCurrent && (
                  <div className="flex-shrink-0">
                    <div className="w-2 h-2 bg-primary rounded-full animate-pulse" />
                  </div>
                )}
              </div>
            )
          })}
        </div>

        {/* Show more indicator */}
        {events.length > maxEvents && (
          <div className="mt-4 text-center">
            <button className="text-sm text-muted-foreground hover:text-foreground transition-colors">
              View all {events.length} events
            </button>
          </div>
        )}

        {/* Current time indicator */}
        <div className="mt-4 pt-4 border-t">
          <div className="flex items-center justify-between text-xs text-muted-foreground">
            <span>Current Time</span>
            <span className="font-mono">{formatTime(currentTime)}</span>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}

export default EventTimeline