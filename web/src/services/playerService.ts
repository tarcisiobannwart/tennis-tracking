import { apiGet } from './api'

export interface PlayerProfile {
  id: string
  username: string
  full_name: string
  avatar_url?: string
  cover_photo_url?: string
  gender?: string
  height_cm?: number
  laterality?: string
  backhand_type?: string
  bio?: string
  country?: string
  stats?: PlayerStats
}

export interface PlayerStats {
  total_matches: number
  wins: number
  losses: number
  win_percentage: number
  aces: number
  double_faults: number
  first_serve_percentage: number
  winners: number
  unforced_errors: number
  recent_form: string[]
}

export interface PlayerActivity {
  month: string
  matches: number
}

export interface WinLossStats {
  singles: { wins: number; losses: number }
  doubles: { wins: number; losses: number }
  ranking: { wins: number; losses: number }
  tournaments: { wins: number; losses: number }
  friendly: { wins: number; losses: number }
}

export interface RecentMatch {
  match_id: string
  date: string
  result: string
  score: string
  opponent_id: string
  opponent_name: string
  surface: string
  tournament?: string
}

export const playerService = {
  async getPlayerByUsername(username: string): Promise<PlayerProfile> {
    return apiGet(`/players/username/${username}`)
  },

  async getPlayerActivity(playerId: string, months: number = 12): Promise<PlayerActivity[]> {
    const response = await apiGet<{ activity: PlayerActivity[] }>(`/players/${playerId}/activity`, { months })
    return response.activity
  },

  async getWinLossByType(playerId: string): Promise<WinLossStats> {
    const response = await apiGet<{ stats: WinLossStats }>(`/players/${playerId}/win-loss-by-type`)
    return response.stats
  },

  async getRecentForm(playerId: string, matches: number = 20): Promise<RecentMatch[]> {
    const response = await apiGet<{ matches: RecentMatch[] }>(`/players/${playerId}/recent-form`, { matches })
    return response.matches
  }
}
