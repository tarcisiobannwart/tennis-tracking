import { api } from './api'
import { useAuthStore, User } from '@/stores/authStore'

interface LoginResponse {
  access_token: string
  refresh_token: string
  token_type: string
  user: User
}

interface RegisterData {
  email: string
  username: string
  fullName: string
  password: string
}

export const authService = {
  async login(username: string, password: string): Promise<LoginResponse> {
    const formData = new URLSearchParams()
    formData.append('username', username)
    formData.append('password', password)

    const response = await api.post<LoginResponse>('/auth/login', formData, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    })
    return response.data
  },

  async register(data: RegisterData): Promise<LoginResponse> {
    const response = await api.post<LoginResponse>('/auth/register', data)
    return response.data
  },

  async refreshToken(refreshToken: string): Promise<LoginResponse> {
    const response = await api.post<LoginResponse>('/auth/refresh', null, {
      params: { refresh_token: refreshToken },
    })
    return response.data
  },

  async logout(): Promise<void> {
    try {
      await api.post('/auth/logout')
    } catch {
      // ignore errors on logout
    }
    useAuthStore.getState().logout()
  },

  async getMe(): Promise<User> {
    const response = await api.get<User>('/auth/me')
    return response.data
  },

  async forgotPassword(email: string): Promise<void> {
    await api.post('/auth/forgot-password', { email })
  },

  async resetPassword(token: string, newPassword: string): Promise<void> {
    await api.post('/auth/reset-password', {
      token,
      new_password: newPassword,
    })
  },

  async verifyEmail(token: string): Promise<void> {
    await api.post('/auth/verify-email', null, {
      params: { token },
    })
  },

  async changePassword(currentPassword: string, newPassword: string): Promise<void> {
    await api.post('/users/me/change-password', {
      current_password: currentPassword,
      new_password: newPassword,
    })
  },
}
