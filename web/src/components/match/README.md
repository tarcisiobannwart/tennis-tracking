# Match Components

This directory contains components for live match display and interaction.

## Components

### EventTimeline

A real-time event timeline component for displaying match events chronologically.

**Features:**
- Chronological list of events (ace, winner, break point, etc.)
- Distinct icons and colors by event type
- Player color coding (player 1 = blue, player 2 = rose)
- Visual grouping by set and game
- Auto-scroll to most recent event
- Integration with game-control API
- WebSocket support for real-time updates
- Relative timestamps (e.g., "2 min ago", "30s ago")
- Compact mode for sidebar use

**API Integration:**
- GET `/api/game-control/events/recent/{match_id}` - Fetch initial events
- GET `/api/events/match/{match_id}/history` - Fetch full event history with filters
- WebSocket `/ws/live/{match_id}` - Real-time event updates

**Props:**
```typescript
interface EventTimelineProps {
  matchId: string              // Required: Match ID to fetch events for
  events?: GameEvent[]         // Optional: External events (e.g., from WebSocket)
  onNewEvent?: (event: GameEvent) => void  // Optional: Callback when new event arrives
  compact?: boolean            // Optional: Compact mode for sidebar (default: false)
  maxHeight?: string           // Optional: Max height for scrollable area (default: '80vh')
}
```

**Usage:**

```tsx
import { EventTimeline } from '@/components/match'

// Basic usage
<EventTimeline matchId="match-123" />

// Compact mode for sidebar
<EventTimeline
  matchId="match-123"
  compact={true}
  maxHeight="calc(100vh - 140px)"
/>

// With WebSocket integration
<EventTimeline
  matchId={matchId}
  events={wsEvents}
  onNewEvent={(event) => console.log('New event:', event)}
/>
```

**Event Types:**
- `ace` - Ace by player
- `double_fault` - Double fault
- `winner` - Winner shot
- `unforced_error` - Unforced error
- `break_point` - Break point opportunity
- `set_point` - Set point
- `match_point` - Match point
- `game_won` - Game won
- `set_won` - Set won
- `match_won` - Match won
- `challenge` - Challenge by player
- `medical_timeout` - Medical timeout
- And more...

**Color Scheme:**
- Critical events (match_point, match_won): Red
- High priority events (set_point, break_point): Orange
- Player 1 events: Blue
- Player 2 events: Rose
- Positive events (ace, winner): Green
- Negative events (double_fault, error): Red
- Game/Set conclusions: Purple

**Example Files:**
- `EventTimeline.example.tsx` - Comprehensive usage examples including WebSocket integration

## Development

To add a new match component:

1. Create the component file in this directory
2. Add export to `index.ts`
3. Follow existing patterns for styling (Tailwind CSS, Framer Motion)
4. Use Lucide icons for consistency
5. Create example file showing usage patterns

## Related Services

- `/services/gameControlService.ts` - Game control API methods
- `/services/websocketService.ts` - WebSocket connection management
- `/types/index.ts` - Type definitions

## Issue References

- TT-150: Timeline de eventos durante partida ao vivo
- TT-148: WebSocket para atualizações em tempo real
- TT-33: Endpoint de eventos recentes
