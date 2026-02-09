import { apiGet, apiPost } from './api'

export interface ScoreDisplay {
  match_id: string
  player1: {
    current_points: string
    games: number[]
    sets_won: number
    serving: boolean
  }
  player2: {
    current_points: string
    games: number[]
    sets_won: number
    serving: boolean
  }
  current_set: number
  is_complete: boolean
}

export interface GameSituation {
  is_break_point: boolean
  is_set_point: boolean
  is_match_point: boolean
  is_deuce: boolean
  is_advantage: boolean
  is_tiebreak: boolean
  is_bagel_possible: boolean
  is_breadstick_possible: boolean
  situation_text: string
  advantage_player?: string
  break_point_player?: string
  set_point_player?: string
  match_point_player?: string
}

export interface LiveBroadcastData {
  scoreboard: {
    player1: {
      name: string
      abbreviated: string
      ranking?: number
      country?: string
      current_points: string
      games: number[]
      sets_won: number
      serving: boolean
    }
    player2: {
      name: string
      abbreviated: string
      ranking?: number
      country?: string
      current_points: string
      games: number[]
      sets_won: number
      serving: boolean
    }
    current_set: number
    is_complete: boolean
  }
  situation: GameSituation
  last_points: Array<{
    point_number: number
    winner_id: string
    server_id: string
    score_after: string
    events: string[]
    timestamp: string
  }>
  key_stats: {
    player1: {
      aces: number
      double_faults: number
      winners: number
      unforced_errors: number
      break_points_converted: number
      break_points_total: number
    }
    player2: {
      aces: number
      double_faults: number
      winners: number
      unforced_errors: number
      break_points_converted: number
      break_points_total: number
    }
  }
  timestamp: string
}

export interface AddPointResponse {
  message: string
  match_id: string
  point_winner_id: string
  timestamp: string
  events: string[]
  situation: GameSituation | null
}

export type PointType = 'ace' | 'winner' | 'forced_error' | 'unforced_error' | 'double_fault'

class ScoringService {
  // Get current scoreboard state
  async getScoreboard(
    matchId: string,
    player1Name: string,
    player2Name: string,
    player1Ranking?: number,
    player2Ranking?: number,
    player1Country?: string,
    player2Country?: string
  ): Promise<any> {
    return apiGet(`/scoring/matches/${matchId}/scoreboard`, {
      player1_name: player1Name,
      player2_name: player2Name,
      player1_ranking: player1Ranking,
      player2_ranking: player2Ranking,
      player1_country: player1Country,
      player2_country: player2Country,
    })
  }

  // Get current score display
  async getCurrentScore(matchId: string): Promise<ScoreDisplay> {
    return apiGet<ScoreDisplay>(`/scoring/matches/${matchId}`)
  }

  // Get live broadcast data
  async getLiveBroadcastData(
    matchId: string,
    player1Name: string,
    player2Name: string,
    player1Ranking?: number,
    player2Ranking?: number,
    player1Country?: string,
    player2Country?: string,
    lastPoints: number = 5
  ): Promise<LiveBroadcastData> {
    return apiGet<LiveBroadcastData>(`/scoring/matches/${matchId}/live`, {
      player1_name: player1Name,
      player2_name: player2Name,
      player1_ranking: player1Ranking,
      player2_ranking: player2Ranking,
      player1_country: player1Country,
      player2_country: player2Country,
      last_points: lastPoints,
    })
  }

  // Get game situation
  async getGameSituation(matchId: string): Promise<GameSituation> {
    return apiGet<GameSituation>(`/scoring/matches/${matchId}/situation`)
  }

  // Add a point
  async addPoint(matchId: string, winnerPlayerId: string): Promise<AddPointResponse> {
    return apiPost<AddPointResponse>(`/scoring/matches/${matchId}/points`, {
      winner_player_id: winnerPlayerId,
    })
  }

  // Get match stats
  async getMatchStats(matchId: string): Promise<any> {
    return apiGet(`/scoring/matches/${matchId}/stats`)
  }

  // Export complete match data
  async exportMatchData(matchId: string): Promise<any> {
    return apiGet(`/scoring/matches/${matchId}/export`)
  }
}

export const scoringService = new ScoringService()
export default scoringService
