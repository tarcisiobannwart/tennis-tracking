import { apiGet } from './api'

export interface RankingFilters {
  page?: number
  limit?: number
  status?: string
  ranking_type?: string
  organization_id?: string
  my_rankings?: boolean
}

export interface RankingStats {
  points: number
  matches_played: number
  matches_won: number
  matches_lost: number
  win_rate: number
  position_history: number[]
}

export interface Ranking {
  id: string
  name: string
  description: string
  ranking_type: 'round_robin' | 'challenge'
  status: 'active' | 'inactive' | 'completed'
  venue: string
  location: string
  current_round: number
  total_rounds: number | null
  total_participants: number
  my_position?: number
  my_stats?: RankingStats
  start_date: string
  end_date: string
}

export interface RankingListResponse {
  data: Ranking[]
  total: number
  page: number
  limit: number
  total_pages: number
}

export interface StandingsEntry {
  position: number
  previous_position: number | null
  user_id: string
  user_name: string
  user_avatar?: string
  points: number
  matches_played: number
  matches_won: number
  matches_lost: number
  matches_drawn: number
  sets_won: number
  sets_lost: number
  games_won: number
  games_lost: number
  win_rate: number
  set_ratio: number
  position_history: number[]
  position_change?: number
}

export interface StandingsResponse {
  ranking_id: string
  current_round: number
  standings: StandingsEntry[]
  updated_at: string
}

export interface RankingRound {
  id: string
  ranking_id: string
  round_number: number
  name: string | null
  start_date: string | null
  end_date: string | null
  is_completed: boolean
  total_matches: number
  completed_matches: number
}

class RankingService {
  // Get all rankings with optional filters
  async getRankings(filters?: RankingFilters): Promise<RankingListResponse> {
    return apiGet<RankingListResponse>('/rankings', filters)
  }

  // Get single ranking by ID
  async getRanking(id: string): Promise<Ranking> {
    return apiGet<Ranking>(`/rankings/${id}`)
  }

  // Get standings for a ranking
  async getStandings(rankingId: string): Promise<StandingsResponse> {
    return apiGet<StandingsResponse>(`/rankings/${rankingId}/standings`)
  }

  // Get rounds for a ranking
  async getRounds(rankingId: string): Promise<RankingRound[]> {
    return apiGet<RankingRound[]>(`/rankings/${rankingId}/rounds`)
  }
}

export const rankingService = new RankingService()
