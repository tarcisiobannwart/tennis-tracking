/**
 * EventTimeline Component - Usage Examples
 *
 * This component displays a chronological timeline of match events in real-time.
 * It integrates with the game-control API and WebSocket for live updates.
 *
 * Features:
 * - Fetches events from GET /api/game-control/events/recent/{match_id}
 * - Auto-scrolls to most recent event
 * - Groups events by set and game
 * - Distinct icons and colors by event type
 * - Player color coding (blue for player 1, rose for player 2)
 * - Relative timestamps (e.g., "2 min ago", "30s ago")
 * - Compact mode for sidebar use
 * - WebSocket integration for real-time updates
 */

import EventTimeline from './EventTimeline'
import { useEffect, useState } from 'react'
import { liveWebSocket, connectToLiveAnalysis } from '@/services/websocketService'
import type { GameEvent } from './EventTimeline'

// Example 1: Basic usage with just matchId
export function BasicExample() {
  return (
    <div className="container mx-auto p-4">
      <EventTimeline matchId="match-123" />
    </div>
  )
}

// Example 2: Compact mode for sidebar
export function SidebarExample() {
  return (
    <div className="w-80 h-screen p-4 bg-background border-l">
      <EventTimeline
        matchId="match-123"
        compact={true}
        maxHeight="calc(100vh - 120px)"
      />
    </div>
  )
}

// Example 3: With WebSocket integration
export function LiveMatchExample() {
  const [events, setEvents] = useState<GameEvent[]>([])
  const matchId = "match-123"

  useEffect(() => {
    // Connect to WebSocket for live updates
    const connect = async () => {
      try {
        await connectToLiveAnalysis(
          matchId,
          (message) => {
            // Handle incoming WebSocket messages
            if (message.type === 'match_event' && message.data) {
              const newEvent: GameEvent = {
                id: message.data.id || `${Date.now()}`,
                match_id: matchId,
                event_type: message.data.event_type,
                player_id: message.data.player_id,
                timestamp: message.data.timestamp || new Date().toISOString(),
                description: message.data.description,
                event_data: message.data.event_data,
                current_set: message.data.current_set,
                current_game: message.data.current_game,
                priority: message.data.priority,
              }
              setEvents(prev => [newEvent, ...prev])
            }
          },
          () => console.log('WebSocket connected'),
          () => console.log('WebSocket disconnected'),
          (error) => console.error('WebSocket error:', error)
        )
      } catch (error) {
        console.error('Failed to connect to WebSocket:', error)
      }
    }

    connect()

    return () => {
      liveWebSocket.disconnect()
    }
  }, [matchId])

  const handleNewEvent = (event: GameEvent) => {
    console.log('New event received:', event)
    // You can trigger notifications, sound effects, etc.
  }

  return (
    <div className="container mx-auto p-4">
      <EventTimeline
        matchId={matchId}
        events={events}
        onNewEvent={handleNewEvent}
      />
    </div>
  )
}

// Example 4: Integration in Live Scoring Page
export function LiveScoringWithTimeline() {
  const [events, setEvents] = useState<GameEvent[]>([])
  const matchId = "match-123"

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 p-4">
      {/* Main content - Scoreboard and video */}
      <div className="lg:col-span-2 space-y-4">
        <div className="aspect-video bg-black rounded-lg">
          {/* Video player */}
        </div>
        <div>
          {/* ScoreBoard component */}
        </div>
      </div>

      {/* Sidebar - Event Timeline */}
      <div className="lg:col-span-1">
        <EventTimeline
          matchId={matchId}
          events={events}
          onNewEvent={(event) => setEvents(prev => [event, ...prev])}
          compact={true}
          maxHeight="calc(100vh - 140px)"
        />
      </div>
    </div>
  )
}

/**
 * Event Types Supported:
 *
 * Point Events:
 * - ace: Ace by player
 * - double_fault: Double fault
 * - winner: Winner shot
 * - unforced_error: Unforced error
 * - forced_error: Forced error
 *
 * Critical Situations:
 * - break_point: Break point opportunity
 * - set_point: Set point
 * - match_point: Match point
 * - deuce: Deuce situation
 * - advantage: Advantage for player
 *
 * Tiebreak:
 * - tiebreak_start: Tiebreak started
 *
 * Conclusions:
 * - game_won: Game won
 * - set_won: Set won
 * - match_won: Match won
 *
 * Interruptions:
 * - challenge: Challenge by player
 * - medical_timeout: Medical timeout
 * - coaching_timeout: Coaching timeout
 *
 * Match Control:
 * - match_started: Match started
 * - match_paused: Match paused
 * - match_resumed: Match resumed
 * - match_completed: Match completed
 */
