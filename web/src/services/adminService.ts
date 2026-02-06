import { api } from './api'

export const adminService = {
  async getMetrics() {
    const response = await api.get('/admin/metrics')
    return response.data
  },

  async getUsers(params: { skip?: number; limit?: number; role?: string; plan?: string; search?: string } = {}) {
    const response = await api.get('/admin/users', { params })
    return response.data
  },

  async updateUserRole(userId: string, role: string) {
    await api.put(`/admin/users/${userId}/role`, { role })
  },

  async updateUserPlan(userId: string, plan: string) {
    await api.put(`/admin/users/${userId}/plan`, { plan })
  },

  async toggleUserActive(userId: string, isActive: boolean) {
    await api.put(`/admin/users/${userId}/active`, { is_active: isActive })
  },

  async getSubscriptionStats() {
    const response = await api.get('/admin/subscriptions')
    return response.data
  },

  async getLogs(params: { skip?: number; limit?: number; action?: string; user_id?: string } = {}) {
    const response = await api.get('/admin/logs', { params })
    return response.data
  },
}
