// Core tennis domain types
export interface Player {
  id: string
  name: string
  ranking: number
  country: string
  age: number
  height: number
  weight: number
  playingHand: 'left' | 'right'
  backhand: 'one-handed' | 'two-handed'
  profileImage?: string
  statistics: PlayerStatistics
}

export interface PlayerStatistics {
  matchesPlayed: number
  matchesWon: number
  winPercentage: number
  acesPerMatch: number
  doubleFaultsPerMatch: number
  firstServePercentage: number
  firstServeWonPercentage: number
  secondServeWonPercentage: number
  breakPointsSaved: number
  returnPointsWon: number
  netPointsWon: number
}

export interface Match {
  id: string
  player1: Player
  player2: Player
  tournament: string
  round: string
  surface: 'hard' | 'clay' | 'grass' | 'carpet'
  date: string
  status: 'scheduled' | 'live' | 'completed' | 'cancelled'
  score: MatchScore
  duration?: number
  videoUrl?: string
  statistics: MatchStatistics
}

export interface MatchScore {
  sets: SetScore[]
  currentSet?: number
  currentGame?: GameScore
}

export interface SetScore {
  player1Games: number
  player2Games: number
  player1Tiebreak?: number
  player2Tiebreak?: number
}

export interface GameScore {
  player1Points: number
  player2Points: number
  server: 1 | 2
}

export interface MatchStatistics {
  player1Stats: PlayerMatchStats
  player2Stats: PlayerMatchStats
  rallies: Rally[]
  events: MatchEvent[]
}

export interface PlayerMatchStats {
  aces: number
  doubleFaults: number
  firstServeIn: number
  firstServeAttempts: number
  firstServeWon: number
  secondServeWon: number
  secondServeAttempts: number
  breakPointsConverted: number
  breakPointsTotal: number
  returnPointsWon: number
  returnPointsTotal: number
  netPoints: number
  netPointsWon: number
  winners: number
  unforcedErrors: number
  totalPoints: number
  distanceCovered: number
  averageSpeed: number
  maxSpeed: number
}

export interface Rally {
  id: string
  startTime: number
  endTime: number
  shots: Shot[]
  winner: 1 | 2 | null // null for unforced error
  winnerType: 'ace' | 'winner' | 'forced_error' | 'unforced_error'
  length: number // number of shots
}

export interface Shot {
  id: string
  playerId: string
  timestamp: number
  position: Position
  ballPosition: Position
  shotType: ShotType
  speed: number
  spin: number
  placement: CourtZone
  outcome: 'in' | 'out' | 'net' | 'winner'
}

export interface Position {
  x: number
  y: number
  z?: number
}

export interface MatchEvent {
  id: string
  type: 'point_start' | 'point_end' | 'game_end' | 'set_end' | 'match_end' | 'break_point' | 'ace' | 'double_fault'
  timestamp: number
  description: string
  player?: 1 | 2
  data?: Record<string, any>
}

export type ShotType =
  | 'serve'
  | 'forehand'
  | 'backhand'
  | 'forehand_volley'
  | 'backhand_volley'
  | 'overhead'
  | 'drop_shot'
  | 'lob'
  | 'slice'
  | 'topspin'

export type CourtZone =
  | 'service_box_1'
  | 'service_box_2'
  | 'service_box_3'
  | 'service_box_4'
  | 'baseline_center'
  | 'baseline_left'
  | 'baseline_right'
  | 'net_left'
  | 'net_center'
  | 'net_right'
  | 'sideline_left'
  | 'sideline_right'

// Real-time tracking types
export interface LiveFrame {
  frameNumber: number
  timestamp: number
  ballPosition?: Position
  player1Position?: Position
  player2Position?: Position
  courtDetection: CourtDetection
  predictions: FramePredictions
}

export interface CourtDetection {
  corners: Position[]
  lines: CourtLine[]
  confidence: number
}

export interface CourtLine {
  start: Position
  end: Position
  type: 'baseline' | 'service_line' | 'center_line' | 'sideline' | 'net'
  confidence: number
}

export interface FramePredictions {
  ballBounce?: {
    probability: number
    position: Position
  }
  shotType?: {
    type: ShotType
    confidence: number
  }
  ballInOut?: {
    status: 'in' | 'out'
    confidence: number
  }
}

// API Response types
export interface ApiResponse<T> {
  data: T
  message?: string
  success: boolean
}

export interface PaginatedResponse<T> {
  data: T[]
  total: number
  page: number
  limit: number
  hasNext: boolean
  hasPrev: boolean
}

// WebSocket message types
export interface WebSocketMessage {
  type: 'frame_update' | 'match_event' | 'score_update' | 'connection' | 'error'
  data: any
  timestamp: number
}

// UI State types
export interface VideoPlayerState {
  isPlaying: boolean
  currentTime: number
  duration: number
  playbackRate: number
  volume: number
  isFullscreen: boolean
  showOverlays: boolean
  selectedOverlays: string[]
}

export interface CourtViewConfig {
  view: '2d' | '3d'
  showTrajectory: boolean
  showHeatmap: boolean
  showPlayerMovement: boolean
  timeRange: [number, number]
  selectedZones: CourtZone[]
}

export interface AnalyticsFilter {
  dateRange: [Date, Date]
  surface: string[]
  opponent: string[]
  tournament: string[]
  round: string[]
}

// Chart data types
export interface ChartDataPoint {
  x: number | string
  y: number
  label?: string
  color?: string
}

export interface HeatmapData {
  zone: CourtZone
  value: number
  color: string
}

export interface TimelineEvent {
  timestamp: number
  type: string
  description: string
  importance: 'low' | 'medium' | 'high'
  player?: number
}