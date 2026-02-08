/**
 * Notification Service - API client para sistema de notificacoes.
 *
 * Implementado para TT-137: Sistema de notificacoes com feed cronologico,
 * contador de nao-lidas e push notifications via WebSocket.
 */

import { apiGet, apiPut, apiDelete } from './api'

export type NotificationType =
  | 'match_result'
  | 'friendship'
  | 'game_scheduled'
  | 'ranking_round'
  | 'tournament'
  | 'system'

export interface Notification {
  id: string
  user_id: string
  notification_type: NotificationType
  title: string
  message: string
  sender_id?: string
  reference_id?: string
  reference_type?: string
  is_read: boolean
  read_at?: string
  created_at: string
}

export interface NotificationListResponse {
  data: Notification[]
  total: number
  offset: number
  limit: number
  unread_count: number
}

export interface UnreadCountResponse {
  unread_count: number
}

/**
 * Obtem lista paginada de notificacoes do usuario autenticado.
 */
export const getNotifications = async (params?: {
  offset?: number
  limit?: number
}): Promise<NotificationListResponse> => {
  return apiGet<NotificationListResponse>('/notifications', params)
}

/**
 * Obtem contador de notificacoes nao-lidas do usuario autenticado.
 */
export const getUnreadCount = async (): Promise<UnreadCountResponse> => {
  return apiGet<UnreadCountResponse>('/notifications/unread-count')
}

/**
 * Marca uma notificacao como lida.
 */
export const markAsRead = async (notificationId: string): Promise<Notification> => {
  return apiPut<Notification>(`/notifications/${notificationId}/read`)
}

/**
 * Marca todas as notificacoes como lidas.
 */
export const markAllAsRead = async (): Promise<{ updated_count: number; message: string }> => {
  return apiPut<{ updated_count: number; message: string }>('/notifications/read-all')
}

/**
 * Deleta uma notificacao.
 */
export const deleteNotification = async (notificationId: string): Promise<{ message: string }> => {
  return apiDelete<{ message: string }>(`/notifications/${notificationId}`)
}
