import { useEffect, useRef, useState, useCallback } from 'react'
import { Clock, Trophy, Target, AlertCircle, Award, Flag, UserX, Timer } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { formatDistanceToNow } from 'date-fns'
import { ptBR } from 'date-fns/locale'
import { gameControlService } from '@/services/gameControlService'

export interface GameEvent {
  id: string
  match_id: string
  event_type: string
  player_id?: string
  timestamp: string
  description?: string
  event_data?: Record<string, any>
  current_set?: number
  current_game?: number
  priority?: 'low' | 'normal' | 'high' | 'critical'
}

interface EventTimelineProps {
  matchId: string
  events?: GameEvent[]
  onNewEvent?: (event: GameEvent) => void
  compact?: boolean
  maxHeight?: string
}

const EventTimeline = ({
  matchId,
  events: externalEvents = [],
  onNewEvent: _onNewEvent,
  compact = false,
  maxHeight = '80vh'
}: EventTimelineProps) => {
  const [events, setEvents] = useState<GameEvent[]>(externalEvents)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const scrollRef = useRef<HTMLDivElement>(null)
  const prevEventsLengthRef = useRef(0)

  // Fetch initial events from API
  const fetchEvents = useCallback(async () => {
    try {
      setLoading(true)
      setError(null)
      const response = await gameControlService.getRecentEvents(matchId, 50)

      if (response.events && Array.isArray(response.events)) {
        setEvents(response.events)
        prevEventsLengthRef.current = response.events.length
      }
    } catch (err) {
      console.error('Failed to fetch events:', err)
      setError('Falha ao carregar eventos')
    } finally {
      setLoading(false)
    }
  }, [matchId])

  // Initial fetch
  useEffect(() => {
    fetchEvents()
  }, [fetchEvents])

  // Update events when external events change (WebSocket updates)
  useEffect(() => {
    if (externalEvents && externalEvents.length > 0) {
      setEvents(externalEvents)
    }
  }, [externalEvents])

  // Auto-scroll to bottom when new event arrives
  useEffect(() => {
    if (events.length > prevEventsLengthRef.current && scrollRef.current) {
      const lastEvent = scrollRef.current.lastElementChild
      if (lastEvent) {
        lastEvent.scrollIntoView({ behavior: 'smooth', block: 'nearest' })
      }
      prevEventsLengthRef.current = events.length
    }
  }, [events.length])

  // Get icon for event type
  const getEventIcon = (type: string) => {
    const iconMap: Record<string, any> = {
      'ace': Award,
      'double_fault': AlertCircle,
      'winner': Target,
      'unforced_error': UserX,
      'forced_error': AlertCircle,
      'break_point': Flag,
      'set_point': Trophy,
      'match_point': Trophy,
      'deuce': Timer,
      'advantage': Flag,
      'game_won': Trophy,
      'set_won': Trophy,
      'match_won': Trophy,
      'tiebreak_start': Flag,
      'challenge': Flag,
      'medical_timeout': Timer,
      'coaching_timeout': Timer,
      'point_start': Clock,
      'point_end': Target,
      'match_started': Flag,
      'match_paused': Timer,
      'match_resumed': Flag,
      'match_completed': Trophy,
    }
    return iconMap[type] || Clock
  }

  // Get color for event based on type and player
  const getEventColor = (event: GameEvent) => {
    const { event_type, player_id, priority } = event

    // Priority-based coloring (critical events)
    if (priority === 'critical' || event_type === 'match_point' || event_type === 'match_won') {
      return 'text-red-600 bg-red-50 dark:bg-red-900/20 border-red-300 dark:border-red-700'
    }
    if (priority === 'high' || event_type === 'set_point' || event_type === 'break_point') {
      return 'text-orange-600 bg-orange-50 dark:bg-orange-900/20 border-orange-300 dark:border-orange-700'
    }

    // Player-based coloring for regular events
    if (player_id) {
      // Assuming player_id can help determine player 1 vs player 2
      // This is simplified - in production you'd need actual player mapping
      const isPlayer1 = event.event_data?.player_number === 1
      if (isPlayer1) {
        return 'text-blue-600 bg-blue-50 dark:bg-blue-900/20 border-blue-300 dark:border-blue-700'
      } else {
        return 'text-rose-600 bg-rose-50 dark:bg-rose-900/20 border-rose-300 dark:border-rose-700'
      }
    }

    // Type-based coloring
    const colorMap: Record<string, string> = {
      'ace': 'text-green-600 bg-green-50 dark:bg-green-900/20 border-green-300 dark:border-green-700',
      'winner': 'text-green-600 bg-green-50 dark:bg-green-900/20 border-green-300 dark:border-green-700',
      'double_fault': 'text-red-600 bg-red-50 dark:bg-red-900/20 border-red-300 dark:border-red-700',
      'unforced_error': 'text-red-600 bg-red-50 dark:bg-red-900/20 border-red-300 dark:border-red-700',
      'game_won': 'text-purple-600 bg-purple-50 dark:bg-purple-900/20 border-purple-300 dark:border-purple-700',
      'set_won': 'text-purple-600 bg-purple-50 dark:bg-purple-900/20 border-purple-300 dark:border-purple-700',
    }

    return colorMap[event_type] || 'text-gray-600 bg-gray-50 dark:bg-gray-900/20 border-gray-300 dark:border-gray-700'
  }

  // Format event description
  const getEventDescription = (event: GameEvent) => {
    if (event.description) {
      return event.description
    }

    // Fallback: generate description from event type
    const type = event.event_type.replace(/_/g, ' ')
    return type.charAt(0).toUpperCase() + type.slice(1)
  }

  // Format relative timestamp
  const formatRelativeTime = (timestamp: string) => {
    try {
      const date = new Date(timestamp)
      return formatDistanceToNow(date, { addSuffix: true, locale: ptBR })
    } catch {
      return 'agora'
    }
  }

  // Group events by set and game
  const groupedEvents = events.reduce((acc, event) => {
    const setNum = event.current_set || 0
    const gameNum = event.current_game || 0
    const key = `set-${setNum}-game-${gameNum}`

    if (!acc[key]) {
      acc[key] = {
        set: setNum,
        game: gameNum,
        events: []
      }
    }
    acc[key].events.push(event)
    return acc
  }, {} as Record<string, { set: number; game: number; events: GameEvent[] }>)

  const sortedGroups = Object.values(groupedEvents).sort((a, b) => {
    if (a.set !== b.set) return b.set - a.set
    return b.game - a.game
  })

  if (loading && events.length === 0) {
    return (
      <Card className={compact ? '' : ''}>
        <CardHeader>
          <CardTitle className="flex items-center text-base">
            <Clock className="w-4 h-4 mr-2" />
            Timeline de Eventos
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center py-8 text-muted-foreground">
            <Clock className="w-12 h-12 mx-auto mb-4 opacity-50 animate-spin" />
            <p>Carregando eventos...</p>
          </div>
        </CardContent>
      </Card>
    )
  }

  if (error) {
    return (
      <Card className={compact ? '' : ''}>
        <CardHeader>
          <CardTitle className="flex items-center text-base">
            <Clock className="w-4 h-4 mr-2" />
            Timeline de Eventos
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center py-8 text-red-500">
            <AlertCircle className="w-12 h-12 mx-auto mb-4" />
            <p>{error}</p>
          </div>
        </CardContent>
      </Card>
    )
  }

  if (events.length === 0) {
    return (
      <Card className={compact ? '' : ''}>
        <CardHeader>
          <CardTitle className="flex items-center text-base">
            <Clock className="w-4 h-4 mr-2" />
            Timeline de Eventos
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center py-8 text-muted-foreground">
            <Clock className="w-12 h-12 mx-auto mb-4 opacity-50" />
            <p>Nenhum evento registrado</p>
            <p className="text-sm mt-2">Eventos aparecerão aqui durante a partida</p>
          </div>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card className={compact ? '' : ''}>
      <CardHeader className={compact ? 'pb-3' : ''}>
        <CardTitle className={`flex items-center justify-between ${compact ? 'text-sm' : 'text-base'}`}>
          <div className="flex items-center">
            <Clock className={`${compact ? 'w-4 h-4' : 'w-5 h-5'} mr-2`} />
            Timeline de Eventos
          </div>
          <div className={`${compact ? 'text-xs' : 'text-sm'} text-muted-foreground font-normal`}>
            {events.length} {events.length === 1 ? 'evento' : 'eventos'}
          </div>
        </CardTitle>
      </CardHeader>
      <CardContent className={compact ? 'px-3' : ''}>
        <div
          ref={scrollRef}
          className="space-y-4 overflow-y-auto pr-2 scrollbar-thin scrollbar-thumb-gray-300 dark:scrollbar-thumb-gray-700"
          style={{ maxHeight }}
        >
          {sortedGroups.map((group) => (
            <div key={`set-${group.set}-game-${group.game}`} className="space-y-2">
              {/* Set/Game header */}
              {(group.set > 0 || group.game > 0) && (
                <div className="sticky top-0 z-10 bg-background/80 backdrop-blur-sm py-1.5 px-2 rounded border border-border/50">
                  <div className={`${compact ? 'text-xs' : 'text-sm'} font-semibold text-muted-foreground`}>
                    {group.set > 0 && `Set ${group.set}`}
                    {group.set > 0 && group.game > 0 && ' • '}
                    {group.game > 0 && `Game ${group.game}`}
                  </div>
                </div>
              )}

              {/* Events in this set/game */}
              {group.events.map((event, index) => {
                const Icon = getEventIcon(event.event_type)
                const colorClasses = getEventColor(event)

                return (
                  <div
                    key={event.id}
                    className={`relative flex items-start space-x-3 ${compact ? 'p-2' : 'p-3'} rounded-lg border transition-all ${colorClasses}`}
                  >
                    {/* Timeline connector */}
                    {index < group.events.length - 1 && (
                      <div className="absolute left-5 top-10 w-px h-full bg-border/50" />
                    )}

                    {/* Event icon */}
                    <div className={`flex-shrink-0 ${compact ? 'w-6 h-6' : 'w-8 h-8'} rounded-full flex items-center justify-center bg-background border border-current`}>
                      <Icon className={compact ? 'w-3 h-3' : 'w-4 h-4'} />
                    </div>

                    {/* Event content */}
                    <div className="flex-1 min-w-0">
                      <div className="flex items-start justify-between gap-2">
                        <div className={`${compact ? 'text-xs' : 'text-sm'} font-medium flex-1`}>
                          {getEventDescription(event)}
                        </div>
                        <div className={`${compact ? 'text-[10px]' : 'text-xs'} text-muted-foreground flex-shrink-0`}>
                          {formatRelativeTime(event.timestamp)}
                        </div>
                      </div>

                      {/* Event type badge */}
                      {!compact && (
                        <div className="mt-1.5">
                          <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-secondary text-secondary-foreground">
                            {event.event_type.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                          </span>
                        </div>
                      )}

                      {/* Additional event data */}
                      {!compact && event.event_data && Object.keys(event.event_data).length > 0 && (
                        <div className="mt-2 text-xs text-muted-foreground space-y-0.5">
                          {Object.entries(event.event_data)
                            .filter(([key]) => !['player_number', 'importance'].includes(key))
                            .slice(0, 3)
                            .map(([key, value]) => (
                              <div key={key} className="flex justify-between">
                                <span className="capitalize">{key.replace(/_/g, ' ')}:</span>
                                <span className="font-mono">{String(value)}</span>
                              </div>
                            ))
                          }
                        </div>
                      )}
                    </div>
                  </div>
                )
              })}
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  )
}

export default EventTimeline
