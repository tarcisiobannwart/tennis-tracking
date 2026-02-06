import { api } from './api'

export interface Plan {
  id: string
  name: string
  price: number
  currency: string
  interval: string
  features: {
    videos_per_month: number
    max_video_duration: number
    models: string[]
    history_days: number
    max_team_members: number
    api_access: boolean
  }
}

export const subscriptionService = {
  async getPlans(): Promise<Plan[]> {
    const response = await api.get<Plan[]>('/subscriptions/plans')
    return response.data
  },

  async createCheckout(plan: string): Promise<string> {
    const response = await api.post<{ url: string }>('/subscriptions/checkout', { plan })
    return response.data.url
  },

  async createPortal(): Promise<string> {
    const response = await api.post<{ url: string }>('/subscriptions/portal')
    return response.data.url
  },
}
