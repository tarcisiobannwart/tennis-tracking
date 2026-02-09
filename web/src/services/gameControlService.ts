import { apiPost, apiGet } from './api'

export interface StartMatchRequest {
  match_id: string
  server_player_id: string
  tournament_data?: {
    name?: string
    round?: string
    surface?: string
  }
}

export interface GameControlResponse {
  success: boolean
  message: string
  match_id: string
  state?: MatchState
}

export interface MatchState {
  match_id: string
  status: string
  current_set: number
  current_game: number
  server_player_id: string
  score: {
    player1_sets: number
    player2_sets: number
    sets: Array<{
      set_number: number
      player1_games: number
      player2_games: number
    }>
  }
}

export const gameControlService = {
  async startMatch(request: StartMatchRequest): Promise<GameControlResponse> {
    return apiPost<GameControlResponse>('/game-control/start', request)
  },

  async getMatchState(matchId: string): Promise<MatchState> {
    return apiGet<MatchState>(`/game-control/state/${matchId}`)
  },

  async pauseMatch(matchId: string, reason?: string): Promise<GameControlResponse> {
    return apiPost<GameControlResponse>('/game-control/pause', {
      match_id: matchId,
      reason,
    })
  },

  async resumeMatch(matchId: string): Promise<GameControlResponse> {
    return apiPost<GameControlResponse>('/game-control/resume', {
      match_id: matchId,
    })
  },
}

export default gameControlService
