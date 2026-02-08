/**
 * Statistics Service - TT-133
 * Service para consumir API de estatisticas avancadas
 */

import { apiGet } from './api'

export interface OverallStats {
  total_matches: number
  wins: number
  losses: number
  win_rate: number
}

export interface BreakdownItem {
  label: string
  total: number
  wins: number
  losses: number
  win_rate: number
}

export interface MonthlyData {
  month: string
  label: string
  total: number
  wins: number
  losses: number
}

export interface SurfaceStats {
  surface: string
  label: string
  total: number
  wins: number
  losses: number
  win_rate: number
}

export interface AgeGroupStats {
  age_group: string
  total: number
  wins: number
  losses: number
  win_rate: number
}

export interface OpponentProfileStats {
  handedness: Array<{
    label: string
    total: number
    wins: number
    losses: number
    win_rate: number
  }>
  backhand: Array<{
    label: string
    total: number
    wins: number
    losses: number
    win_rate: number
  }>
  age_groups: AgeGroupStats[]
}

export interface StreakItem {
  match_id: string
  date: string
  result: 'V' | 'D'
  opponent_name: string
}

export interface ResultTypeStats {
  result_type: string
  label: string
  total: number
  wins: number
  losses: number
}

export interface DashboardResponse {
  overall: OverallStats
  by_type: BreakdownItem[]
  by_result_type: ResultTypeStats[]
  monthly: MonthlyData[]
  by_surface: SurfaceStats[]
  opponent_profile: OpponentProfileStats
  streak: StreakItem[]
}

export const statisticsService = {
  /**
   * Busca todos os dados do dashboard de estatisticas
   */
  async getDashboard(months: number = 12): Promise<DashboardResponse> {
    return apiGet<DashboardResponse>('/statistics/dashboard', { months })
  },

  /**
   * Busca dados mensais para grafico
   */
  async getMonthly(months: number = 12): Promise<{ monthly: MonthlyData[] }> {
    return apiGet<{ monthly: MonthlyData[] }>('/statistics/monthly', { months })
  },

  /**
   * Busca breakdown por tipo de jogo
   */
  async getBreakdown(): Promise<{ by_type: BreakdownItem[]; by_result_type: ResultTypeStats[] }> {
    return apiGet<{ by_type: BreakdownItem[]; by_result_type: ResultTypeStats[] }>('/statistics/breakdown')
  },

  /**
   * Busca estatisticas por superficie
   */
  async getSurfaceStats(): Promise<{ surfaces: SurfaceStats[] }> {
    return apiGet<{ surfaces: SurfaceStats[] }>('/statistics/surface')
  },

  /**
   * Busca estatisticas vs perfil do oponente
   */
  async getOpponentProfile(): Promise<OpponentProfileStats> {
    return apiGet<OpponentProfileStats>('/statistics/opponent-profile')
  },

  /**
   * Busca sequencia de resultados
   */
  async getStreak(limit: number = 30): Promise<{ streak: StreakItem[] }> {
    return apiGet<{ streak: StreakItem[] }>('/statistics/streak', { limit })
  },
}
