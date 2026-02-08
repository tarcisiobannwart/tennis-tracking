/**
 * H2H Service - TT-134
 * Service para consumir API de Head to Head
 */

import { apiGet } from './api'

export interface PlayerProfile {
  id: string
  name: string
  avatar_url?: string
  age?: number
  height?: number
  dominant_hand?: string
  country?: string
  ranking?: number
  skill_level?: string
}

export interface H2HScore {
  player_wins: number
  opponent_wins: number
}

export interface ComparisonItem {
  attribute: string
  label: string
  player_value?: string
  opponent_value?: string
}

export interface SetDetail {
  set_number: number
  player_games: number
  opponent_games: number
  player_tiebreak?: number
  opponent_tiebreak?: number
}

export interface H2HMatchItem {
  match_id: string
  date?: string
  result: 'win' | 'loss'
  player_sets: number
  opponent_sets: number
  sets_detail: SetDetail[]
  tournament?: string
  surface?: string
  venue?: string
  duration_minutes?: number
}

export interface SetsGamesOverTime {
  match_date: string
  match_label: string
  player_sets: number
  opponent_sets: number
  player_games: number
  opponent_games: number
}

export interface H2HResponse {
  player: PlayerProfile
  opponent: PlayerProfile
  h2h_score: H2HScore
  comparison: ComparisonItem[]
  sets_games_over_time: SetsGamesOverTime[]
  match_history: H2HMatchItem[]
  total_matches: number
  total_sets_player: number
  total_sets_opponent: number
  total_games_player: number
  total_games_opponent: number
}

export interface OpponentSummary {
  id: string
  name: string
  avatar_url?: string
  total_matches: number
  player_wins: number
  opponent_wins: number
  last_match_date?: string
}

export const h2hService = {
  /**
   * Busca dados completos do H2H entre dois jogadores
   */
  async getH2H(playerId: string, opponentId: string): Promise<H2HResponse> {
    return apiGet<H2HResponse>(`/h2h/${playerId}/${opponentId}`)
  },

  /**
   * Lista todos os adversarios com H2H resumido
   */
  async getOpponents(playerId: string): Promise<{ opponents: OpponentSummary[] }> {
    return apiGet<{ opponents: OpponentSummary[] }>(`/h2h/${playerId}/opponents`)
  },

  /**
   * Busca historico de confrontos diretos
   */
  async getH2HMatches(
    playerId: string,
    opponentId: string,
    skip: number = 0,
    limit: number = 20,
  ): Promise<{ matches: H2HMatchItem[]; total: number; h2h_score: H2HScore }> {
    return apiGet<{ matches: H2HMatchItem[]; total: number; h2h_score: H2HScore }>(
      `/h2h/${playerId}/${opponentId}/matches`,
      { skip, limit },
    )
  },
}
