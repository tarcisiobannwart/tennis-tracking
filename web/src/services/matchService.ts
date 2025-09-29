import { apiGet, apiPost, apiPut, apiDelete, apiGetPaginated, uploadFile } from './api'
import { Match, MatchStatistics, PaginatedResponse } from '@/types'

export interface MatchFilters {
  player?: string
  tournament?: string
  surface?: string
  status?: string
  dateFrom?: string
  dateTo?: string
  page?: number
  limit?: number
}

export interface CreateMatchData {
  player1Id: string
  player2Id: string
  tournament: string
  round: string
  surface: 'hard' | 'clay' | 'grass' | 'carpet'
  scheduledDate: string
}

export interface UploadVideoData {
  matchId: string
  file: File
}

class MatchService {
  // Get all matches with optional filters
  async getMatches(filters?: MatchFilters): Promise<PaginatedResponse<Match>> {
    return apiGetPaginated<Match>('/matches', filters)
  }

  // Get single match by ID
  async getMatch(id: string): Promise<Match> {
    return apiGet<Match>(`/matches/${id}`)
  }

  // Create new match
  async createMatch(data: CreateMatchData): Promise<Match> {
    return apiPost<Match>('/matches', data)
  }

  // Update match
  async updateMatch(id: string, data: Partial<Match>): Promise<Match> {
    return apiPut<Match>(`/matches/${id}`, data)
  }

  // Delete match
  async deleteMatch(id: string): Promise<void> {
    return apiDelete<void>(`/matches/${id}`)
  }

  // Get match statistics
  async getMatchStatistics(id: string): Promise<MatchStatistics> {
    return apiGet<MatchStatistics>(`/matches/${id}/statistics`)
  }

  // Upload video for match
  async uploadVideo(
    matchId: string,
    file: File,
    onProgress?: (progress: number) => void
  ): Promise<{ videoUrl: string }> {
    return uploadFile(`/matches/${matchId}/video`, file, onProgress)
  }

  // Start live analysis
  async startLiveAnalysis(matchId: string): Promise<{ analysisId: string }> {
    return apiPost<{ analysisId: string }>(`/matches/${matchId}/analysis/start`)
  }

  // Stop live analysis
  async stopLiveAnalysis(matchId: string): Promise<void> {
    return apiPost<void>(`/matches/${matchId}/analysis/stop`)
  }

  // Get live matches
  async getLiveMatches(): Promise<Match[]> {
    return apiGet<Match[]>('/matches/live')
  }

  // Get recent matches
  async getRecentMatches(limit = 10): Promise<Match[]> {
    return apiGet<Match[]>('/matches/recent', { limit })
  }

  // Get match highlights
  async getMatchHighlights(id: string): Promise<{
    highlights: Array<{
      timestamp: number
      description: string
      type: string
      videoUrl?: string
    }>
  }> {
    return apiGet(`/matches/${id}/highlights`)
  }

  // Export match data
  async exportMatchData(id: string, format: 'json' | 'csv' | 'pdf'): Promise<Blob> {
    const response = await fetch(`/api/matches/${id}/export?format=${format}`, {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('auth_token')}`,
      },
    })

    if (!response.ok) {
      throw new Error('Export failed')
    }

    return response.blob()
  }
}

export const matchService = new MatchService()
export default matchService