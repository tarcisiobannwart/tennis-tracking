import { api } from './api'
import { User } from '@/stores/authStore'

export const userService = {
  async getMe(): Promise<User> {
    const response = await api.get<User>('/users/me')
    return response.data
  },

  async updateMe(data: Partial<User>): Promise<User> {
    const response = await api.put<User>('/users/me', data)
    return response.data
  },

  async getUsage(): Promise<{
    videos_this_month: number
    videos_limit: number
    max_video_duration: number
    models: string[]
    history_days: number
    max_team_members: number
    api_access: boolean
  }> {
    const response = await api.get('/users/me/usage')
    return response.data
  },

  async changePassword(currentPassword: string, newPassword: string): Promise<void> {
    await api.post('/users/me/change-password', {
      current_password: currentPassword,
      new_password: newPassword,
    })
  },
}
