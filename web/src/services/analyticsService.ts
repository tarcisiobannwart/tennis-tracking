/**
 * Analytics Service - TT-149
 * Service para consumir API de analytics avancadas
 */

import { apiGet } from './api'

// ===== Performance Analytics =====
export interface PerformanceMetrics {
  serve_percentage: number
  ace_percentage: number
  double_fault_percentage: number
  first_serve_points_won: number
  second_serve_points_won: number
  break_points_saved: number
  break_points_converted: number
  winners: number
  unforced_errors: number
  forced_errors: number
  net_points_won: number
  baseline_points_won: number
  average_rally_length: number
  distance_covered?: number
  average_speed?: number
  max_speed?: number
}

export interface PerformanceAnalytics {
  match_id: string
  player_id: string
  metrics: PerformanceMetrics
  shot_analysis: Record<string, any>
  movement_analysis: Record<string, any>
  tactical_analysis: Record<string, any>
  comparison_to_average: Record<string, number>
  strengths: string[]
  weaknesses: string[]
  recommendations: string[]
}

// ===== Player Stats =====
export interface AdvancedPlayerStats {
  player_id: string
  period: string
  surface?: string
  total_matches: number
  wins: number
  losses: number
  win_rate: number
  avg_match_duration: number
  total_points: number
  serve_stats: {
    first_serve_pct: number
    second_serve_pct: number
    aces: number
    double_faults: number
    first_serve_won: number
    second_serve_won: number
  }
  return_stats: {
    first_return_won: number
    second_return_won: number
    break_points_converted: number
  }
  shot_breakdown: {
    forehand: { total: number; winners: number; errors: number }
    backhand: { total: number; winners: number; errors: number }
    serve: { total: number; aces: number; double_faults: number }
    volley: { total: number; winners: number; errors: number }
  }
}

// ===== Trends =====
export interface TrendDataPoint {
  date: string
  value: number
  match_id?: string
  context?: Record<string, any>
}

export interface TrendAnalysis {
  player_id: string
  metric: string
  period: string
  data_points: TrendDataPoint[]
  trend_direction: 'improving' | 'declining' | 'stable'
  trend_strength: number
  statistical_significance: boolean
  insights: string[]
  predictions?: Record<string, any>
}

// ===== Heatmap =====
export interface HeatmapPoint {
  x: number
  y: number
  intensity: number
  count: number
}

export interface HeatmapData {
  match_id: string
  player_id: string
  data_type: string
  points: HeatmapPoint[]
  court_dimensions: Record<string, number>
  metadata: Record<string, any>
}

// ===== Serve Analysis =====
export interface ServeAnalysis {
  match_id: string
  player_id?: string
  first_serve: {
    percentage_in: number
    points_won: number
    avg_speed: number
    max_speed: number
  }
  second_serve: {
    percentage_won: number
    avg_speed: number
  }
  aces: number
  double_faults: number
  serve_direction: {
    wide: number
    body: number
    t: number
  }
}

// ===== Rally Analysis =====
export interface RallyAnalysis {
  match_id: string
  total_rallies: number
  avg_rally_length: number
  max_rally_length: number
  distribution: {
    short: number // 0-4 shots
    medium: number // 5-9 shots
    long: number // 10-19 shots
    very_long: number // 20+ shots
  }
  winner_by_length: Record<string, number>
  outcome_types: {
    winner: number
    unforced_error: number
    forced_error: number
    ace: number
  }
}

// ===== Momentum =====
export interface MomentumAnalysis {
  match_id: string
  momentum_timeline: Array<{
    point_number: number
    momentum_score: number // -100 to 100
  }>
  turning_points: Array<{
    point_number: number
    description: string
    momentum_shift: number
  }>
  phases: {
    player1_dominant: number
    player2_dominant: number
    balanced: number
  }
  final_momentum: number
}

// ===== Court Coverage =====
export interface CourtCoverageAnalysis {
  match_id: string
  player_id?: string
  total_distance: number
  area_covered: number
  zone_frequency: Record<string, number>
  most_frequented_zone: string
  avg_position: { x: number; y: number }
}

// ===== Player Efficiency =====
export interface PlayerEfficiency {
  player_id: string
  match_id?: string
  period: string
  first_serve_pct: number
  second_serve_pct: number
  return_win_pct: number
  break_conversion: number
  consistency_score: number
  unforced_error_ratio: number
}

// ===== Movement Analysis =====
export interface MovementAnalysis {
  match_id: string
  player_id?: string
  average_speed: number
  max_speed: number
  total_distance: number
  sprints: number
  time_in_zones: Record<string, number>
  agility_score: number
}

// ===== Match Insights =====
export interface MatchInsights {
  match_id: string
  key_moments: Array<Record<string, any>>
  turning_points: Array<Record<string, any>>
  momentum_shifts: Array<Record<string, any>>
  tactical_patterns: Array<Record<string, any>>
  performance_highlights: Array<Record<string, any>>
  areas_for_improvement: Array<Record<string, any>>
}

// ===== Player Comparison =====
export interface PlayerComparison {
  player1_id: string
  player2_id: string
  comparison_period: string
  metrics_comparison: Record<string, Record<string, number>>
  head_to_head: Record<string, any>
  surface_performance: Record<string, Record<string, number>>
  recent_form: Record<string, string[]>
  statistical_insights: string[]
}

export const analyticsService = {
  /**
   * Get performance analytics for a match
   */
  async getMatchPerformance(
    matchId: string,
    playerId?: string
  ): Promise<PerformanceAnalytics[]> {
    const params = playerId ? { player_id: playerId } : {}
    return apiGet<PerformanceAnalytics[]>(`/analytics/performance/${matchId}`, params)
  },

  /**
   * Get advanced player stats with filters
   */
  async getPlayerStats(
    playerId: string,
    period: string = 'all',
    surface?: string,
    opponentRanking?: number
  ): Promise<AdvancedPlayerStats> {
    const params: Record<string, any> = { period }
    if (surface) params.surface = surface
    if (opponentRanking) params.opponent_ranking = opponentRanking
    return apiGet<AdvancedPlayerStats>(`/analytics/player-stats/${playerId}`, params)
  },

  /**
   * Get trend analysis for a player
   */
  async getPlayerTrends(
    playerId: string,
    metrics: string[] = ['win_percentage', 'serve_percentage', 'unforced_errors'],
    period: string = 'month'
  ): Promise<TrendAnalysis[]> {
    return apiGet<TrendAnalysis[]>(`/analytics/trends/${playerId}`, {
      metrics,
      period,
    })
  },

  /**
   * Get heatmap data for a match
   */
  async getMatchHeatmap(
    matchId: string,
    playerId?: string,
    dataType: string = 'position'
  ): Promise<HeatmapData[]> {
    const params: Record<string, any> = { data_type: dataType }
    if (playerId) params.player_id = playerId
    return apiGet<HeatmapData[]>(`/analytics/heatmap/${matchId}`, params)
  },

  /**
   * Get serve analysis for a match
   */
  async getServeAnalysis(
    matchId: string,
    playerId?: string,
    serveType?: 'first' | 'second'
  ): Promise<ServeAnalysis> {
    const params: Record<string, any> = {}
    if (playerId) params.player_id = playerId
    if (serveType) params.serve_type = serveType
    return apiGet<ServeAnalysis>(`/analytics/serve-analysis/${matchId}`, params)
  },

  /**
   * Get rally analysis for a match
   */
  async getRallyAnalysis(
    matchId: string,
    minLength: number = 3,
    maxLength?: number
  ): Promise<RallyAnalysis> {
    const params: Record<string, any> = { min_length: minLength }
    if (maxLength) params.max_length = maxLength
    return apiGet<RallyAnalysis>(`/analytics/rally-analysis/${matchId}`, params)
  },

  /**
   * Get momentum analysis for a match
   */
  async getMomentumAnalysis(matchId: string): Promise<MomentumAnalysis> {
    return apiGet<MomentumAnalysis>(`/analytics/momentum/${matchId}`)
  },

  /**
   * Get court coverage analysis for a match
   */
  async getCourtCoverage(matchId: string, playerId?: string): Promise<CourtCoverageAnalysis> {
    const params = playerId ? { player_id: playerId } : {}
    return apiGet<CourtCoverageAnalysis>(`/analytics/court-coverage/${matchId}`, params)
  },

  /**
   * Get player efficiency metrics
   */
  async getPlayerEfficiency(
    playerId: string,
    matchId?: string,
    period: string = 'all'
  ): Promise<PlayerEfficiency> {
    const params: Record<string, any> = { period }
    if (matchId) params.match_id = matchId
    return apiGet<PlayerEfficiency>(`/analytics/player-efficiency/${playerId}`, params)
  },

  /**
   * Get movement analysis for a match
   */
  async getMovementAnalysis(matchId: string, playerId?: string): Promise<MovementAnalysis> {
    const params = playerId ? { player_id: playerId } : {}
    return apiGet<MovementAnalysis>(`/analytics/movement-analysis/${matchId}`, params)
  },

  /**
   * Get match insights
   */
  async getMatchInsights(matchId: string): Promise<MatchInsights> {
    return apiGet<MatchInsights>(`/analytics/insights/${matchId}`)
  },

  /**
   * Compare two players
   */
  async comparePlayers(
    player1Id: string,
    player2Id: string,
    period: string = 'career',
    surface?: string
  ): Promise<PlayerComparison> {
    const params: Record<string, any> = {
      player1_id: player1Id,
      player2_id: player2Id,
      period,
    }
    if (surface) params.surface = surface
    return apiGet<PlayerComparison>('/analytics/comparison', params)
  },

  /**
   * Get performance forecast
   */
  async getPerformanceForecast(
    playerId: string,
    opponentId?: string,
    surface?: string
  ): Promise<any> {
    const params: Record<string, any> = {}
    if (opponentId) params.opponent_id = opponentId
    if (surface) params.surface = surface
    return apiGet(`/analytics/performance-forecast/${playerId}`, params)
  },
}
