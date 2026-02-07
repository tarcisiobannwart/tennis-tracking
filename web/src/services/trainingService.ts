import { api } from './api'

export interface DrillType {
  id: string
  name: string
  description?: string
  category: string
  difficulty: string
  duration_minutes?: number
  equipment_needed?: string[]
  instructions?: string
  created_at: string
}

export interface TrainingDrill {
  id?: string
  drill_type_id: string
  drill_name?: string
  order_in_session: number
  duration_minutes?: number
  repetitions?: number
  sets?: number
  success_rate?: number
  accuracy_score?: number
  started_at?: string
  finished_at?: string
  notes?: string
}

export interface TrainingSession {
  id: string
  user_id: string
  title: string
  description?: string
  session_type: string
  scheduled_at: string
  status: string
  started_at?: string
  finished_at?: string
  duration_minutes?: number
  objectives?: string[]
  focus_areas?: string[]
  coach_name?: string
  coach_notes?: string
  intensity_level?: number
  effort_rating?: number
  fatigue_level?: number
  session_notes?: string
  player_feedback?: string
  drills: TrainingDrill[]
  created_at: string
  updated_at?: string
}

export interface TrainingSessionCreate {
  title: string
  description?: string
  session_type: string
  scheduled_at: string
  objectives?: string[]
  focus_areas?: string[]
  coach_name?: string
}

export interface TrainingSessionUpdate {
  title?: string
  description?: string
  session_type?: string
  scheduled_at?: string
  status?: string
  objectives?: string[]
  focus_areas?: string[]
  coach_name?: string
  coach_notes?: string
  intensity_level?: number
  effort_rating?: number
  fatigue_level?: number
  session_notes?: string
  player_feedback?: string
}

export interface TrainingProgress {
  period: string
  total_sessions: number
  completed_sessions: number
  completion_rate: number
  total_duration_minutes: number
  average_session_duration: number
  session_types_breakdown: Record<string, number>
  average_effort_rating: number
  recent_sessions: {
    id: string
    title: string
    date: string
    status: string
    duration?: number
  }[]
}

export interface TrainingAnalytics {
  period: string
  session_type?: string
  total_sessions: number
  completed_sessions: number
  weekly_distribution: Record<string, number>
  focus_areas_frequency: Record<string, number>
  performance_metrics: {
    consistency: number
    improvement_trend: string
    intensity_data: { date: string; intensity: number }[]
  }
}

export interface TrainingRecommendations {
  next_session_type: string
  weak_areas: string[]
  total_recent: number
  suggestions: string[]
  weekly_plan: Record<string, string>
}

export interface TrainingCalendar {
  start_date: string
  end_date: string
  events: {
    id: string
    title: string
    start: string
    end: string
    type: string
    status: string
    coach?: string
    description?: string
  }[]
  summary: {
    total_sessions: number
    completed: number
    planned: number
    in_progress: number
  }
}

export const trainingService = {
  // Drill Types
  async getDrillTypes(params?: { category?: string; difficulty?: string }): Promise<DrillType[]> {
    const response = await api.get<DrillType[]>('/training/drills', { params })
    return response.data
  },

  // Sessions
  async getSessions(params?: { status?: string; session_type?: string }): Promise<TrainingSession[]> {
    const response = await api.get<TrainingSession[]>('/training/sessions', { params })
    return response.data
  },

  async getSession(id: string): Promise<TrainingSession> {
    const response = await api.get<TrainingSession>(`/training/sessions/${id}`)
    return response.data
  },

  async createSession(data: TrainingSessionCreate): Promise<TrainingSession> {
    const response = await api.post<TrainingSession>('/training/sessions', data)
    return response.data
  },

  async updateSession(id: string, data: TrainingSessionUpdate): Promise<TrainingSession> {
    const response = await api.put<TrainingSession>(`/training/sessions/${id}`, data)
    return response.data
  },

  async deleteSession(id: string): Promise<void> {
    await api.delete(`/training/sessions/${id}`)
  },

  async startSession(id: string): Promise<TrainingSession> {
    const response = await api.post<TrainingSession>(`/training/sessions/${id}/start`)
    return response.data
  },

  async finishSession(id: string): Promise<TrainingSession> {
    const response = await api.post<TrainingSession>(`/training/sessions/${id}/finish`)
    return response.data
  },

  // Drills within session
  async addDrill(sessionId: string, data: { drill_type_id: string; drill_name?: string; order_in_session: number; duration_minutes?: number; repetitions?: number; sets?: number }): Promise<TrainingSession> {
    const response = await api.post<TrainingSession>(`/training/sessions/${sessionId}/drills`, data)
    return response.data
  },

  async removeDrill(sessionId: string, drillId: string): Promise<TrainingSession> {
    const response = await api.delete<TrainingSession>(`/training/sessions/${sessionId}/drills/${drillId}`)
    return response.data
  },

  // Progress & Analytics
  async getProgress(period?: string): Promise<TrainingProgress> {
    const response = await api.get<TrainingProgress>('/training/progress', { params: { period } })
    return response.data
  },

  async getAnalytics(params?: { session_type?: string; period?: string }): Promise<TrainingAnalytics> {
    const response = await api.get<TrainingAnalytics>('/training/analytics', { params })
    return response.data
  },

  async getRecommendations(): Promise<TrainingRecommendations> {
    const response = await api.get<TrainingRecommendations>('/training/recommendations')
    return response.data
  },

  async getCalendar(params?: { start_date?: string; end_date?: string }): Promise<TrainingCalendar> {
    const response = await api.get<TrainingCalendar>('/training/calendar', { params })
    return response.data
  },
}
