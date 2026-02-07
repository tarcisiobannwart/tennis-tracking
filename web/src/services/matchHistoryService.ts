/**
 * Match History Service - TT-135
 * Service para buscar historico de partidas com placares detalhados
 */

import { apiGet } from './api'

export interface MatchHistoryFilters {
  match_type?: 'ranking' | 'amistoso' | 'torneio'
  opponent_name?: string
  surface?: 'clay' | 'grass' | 'hard' | 'carpet'
  start_date?: string // YYYY-MM-DD
  end_date?: string // YYYY-MM-DD
  skip?: number
  limit?: number
}

export interface MatchHistoryOpponent {
  id: string
  name: string
  avatar_url?: string
}

export interface SetScore {
  set_number: number
  user_games: number
  opponent_games: number
  user_tiebreak?: number
  opponent_tiebreak?: number
}

export interface MatchScore {
  sets: string // "2-1"
  user_sets: number
  opponent_sets: number
  sets_detail: SetScore[]
}

export interface MatchHistoryItem {
  id: string
  date: string
  opponent: MatchHistoryOpponent
  result: 'vitoria' | 'derrota'
  score: MatchScore
  match_type: 'ranking' | 'amistoso' | 'torneio'
  tournament: string
  venue?: string
  surface?: string
  duration_minutes?: number
}

export interface MatchHistoryResponse {
  matches: MatchHistoryItem[]
  total: number
  page: number
  limit: number
  total_pages: number
}

export interface GameDetail {
  game_number: number
  winner: 'user' | 'opponent'
  server: 'user' | 'opponent'
}

export interface SetDetail extends SetScore {
  winner: 'user' | 'opponent'
  is_tiebreak: boolean
  games: GameDetail[]
}

export interface MatchDetailScore {
  sets: string
  user_sets: number
  opponent_sets: number
  sets_detail: SetDetail[]
}

export interface MatchDetailPlayer {
  id: string
  name: string
  avatar_url?: string
}

export interface MatchDetail {
  id: string
  title: string
  date: string
  started_at?: string
  user: MatchDetailPlayer
  opponent: MatchDetailPlayer
  result: 'vitoria' | 'derrota'
  score: MatchDetailScore
  match_type: 'ranking' | 'amistoso' | 'torneio'
  tournament: string
  round_name?: string
  venue?: string
  court_number?: string
  surface?: string
  duration_minutes?: number
  best_of_sets: number
  weather_conditions?: Record<string, any>
  notes?: string
}

export const matchHistoryService = {
  /**
   * Lista historico de partidas com filtros e paginacao
   */
  async getMatchHistory(filters?: MatchHistoryFilters): Promise<MatchHistoryResponse> {
    const params = new URLSearchParams()

    if (filters?.match_type) {
      params.append('match_type', filters.match_type)
    }
    if (filters?.opponent_name) {
      params.append('opponent_name', filters.opponent_name)
    }
    if (filters?.surface) {
      params.append('surface', filters.surface)
    }
    if (filters?.start_date) {
      params.append('start_date', filters.start_date)
    }
    if (filters?.end_date) {
      params.append('end_date', filters.end_date)
    }
    if (filters?.skip !== undefined) {
      params.append('skip', filters.skip.toString())
    }
    if (filters?.limit !== undefined) {
      params.append('limit', filters.limit.toString())
    }

    const queryString = params.toString()
    const url = queryString ? `/match-history?${queryString}` : '/match-history'

    return apiGet<MatchHistoryResponse>(url)
  },

  /**
   * Busca detalhes completos de uma partida
   */
  async getMatchDetail(matchId: string): Promise<MatchDetail> {
    return apiGet<MatchDetail>(`/match-history/${matchId}/detail`)
  },
}
