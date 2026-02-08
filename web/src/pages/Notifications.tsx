/**
 * Notifications Page - Pagina de feed de notificacoes.
 *
 * Implementado para TT-137: Sistema de notificacoes com feed cronologico,
 * scroll infinito e marcar como lida.
 */

import { useState, useEffect, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import { CheckCheck, Loader2 } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { NotificationCard } from '@/components/notifications/NotificationCard'
import {
  getNotifications,
  markAsRead,
  markAllAsRead,
  Notification,
} from '@/services/notificationService'

const Notifications = () => {
  const [notifications, setNotifications] = useState<Notification[]>([])
  const [loading, setLoading] = useState<boolean>(true)
  const [loadingMore, setLoadingMore] = useState<boolean>(false)
  const [markingAllRead, setMarkingAllRead] = useState<boolean>(false)
  const [hasMore, setHasMore] = useState<boolean>(true)
  const [offset, setOffset] = useState<number>(0)
  const [unreadCount, setUnreadCount] = useState<number>(0)
  const limit = 20
  const navigate = useNavigate()

  const fetchNotifications = useCallback(async (isLoadMore = false) => {
    try {
      if (isLoadMore) {
        setLoadingMore(true)
      } else {
        setLoading(true)
      }

      const response = await getNotifications({
        offset: isLoadMore ? offset : 0,
        limit,
      })

      if (isLoadMore) {
        setNotifications((prev) => [...prev, ...response.data])
      } else {
        setNotifications(response.data)
      }

      setUnreadCount(response.unread_count)
      setHasMore(response.data.length === limit)

      if (isLoadMore) {
        setOffset((prev) => prev + limit)
      } else {
        setOffset(limit)
      }
    } catch (error) {
      console.error('Erro ao buscar notificacoes:', error)
    } finally {
      setLoading(false)
      setLoadingMore(false)
    }
  }, [offset])

  useEffect(() => {
    fetchNotifications()
  }, [])

  const handleMarkAsRead = async (notificationId: string) => {
    try {
      await markAsRead(notificationId)
      setNotifications((prev) =>
        prev.map((n) => (n.id === notificationId ? { ...n, is_read: true } : n))
      )
      setUnreadCount((prev) => Math.max(0, prev - 1))

      // Atualizar badge no header
      // @ts-ignore
      if (window.updateNotificationCount) {
        // @ts-ignore
        window.updateNotificationCount(Math.max(0, unreadCount - 1))
      }
    } catch (error) {
      console.error('Erro ao marcar notificacao como lida:', error)
    }
  }

  const handleMarkAllAsRead = async () => {
    try {
      setMarkingAllRead(true)
      await markAllAsRead()
      setNotifications((prev) => prev.map((n) => ({ ...n, is_read: true })))
      setUnreadCount(0)

      // Atualizar badge no header
      // @ts-ignore
      if (window.updateNotificationCount) {
        // @ts-ignore
        window.updateNotificationCount(0)
      }
    } catch (error) {
      console.error('Erro ao marcar todas as notificacoes como lidas:', error)
    } finally {
      setMarkingAllRead(false)
    }
  }

  const handleNotificationClick = (notification: Notification) => {
    // Navegar para a referencia se existir
    if (notification.reference_id && notification.reference_type) {
      switch (notification.reference_type) {
        case 'match':
          navigate(`/app/matches/${notification.reference_id}`)
          break
        case 'user':
          navigate(`/app/players/${notification.reference_id}`)
          break
        case 'tournament':
          navigate(`/app/tournaments/${notification.reference_id}`)
          break
        case 'ranking':
          navigate(`/app/rankings/${notification.reference_id}`)
          break
        default:
          break
      }
    }
  }

  const handleLoadMore = () => {
    fetchNotifications(true)
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-[calc(100vh-4rem)]">
        <Loader2 className="w-8 h-8 text-court-accent animate-spin" />
      </div>
    )
  }

  return (
    <div className="max-w-3xl mx-auto p-4 md:p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-slate-100">Notificacoes</h1>
          {unreadCount > 0 && (
            <p className="text-sm text-slate-400 mt-1">
              {unreadCount} nao {unreadCount === 1 ? 'lida' : 'lidas'}
            </p>
          )}
        </div>

        {unreadCount > 0 && (
          <Button
            variant="outline"
            size="sm"
            onClick={handleMarkAllAsRead}
            disabled={markingAllRead}
            className="border-slate-700 hover:border-court-accent"
          >
            {markingAllRead ? (
              <Loader2 className="w-4 h-4 mr-2 animate-spin" />
            ) : (
              <CheckCheck className="w-4 h-4 mr-2" />
            )}
            Marcar todas como lidas
          </Button>
        )}
      </div>

      {/* Lista de notificacoes */}
      {notifications.length === 0 ? (
        <div className="text-center py-12">
          <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-slate-800 flex items-center justify-center">
            <CheckCheck className="w-8 h-8 text-slate-500" />
          </div>
          <p className="text-lg font-medium text-slate-300">Nenhuma notificacao</p>
          <p className="text-sm text-slate-500 mt-2">
            Voce esta em dia! Nao ha notificacoes no momento.
          </p>
        </div>
      ) : (
        <div className="space-y-2">
          {notifications.map((notification) => (
            <NotificationCard
              key={notification.id}
              notification={notification}
              onRead={handleMarkAsRead}
              onClick={handleNotificationClick}
            />
          ))}

          {/* Load more */}
          {hasMore && (
            <div className="flex justify-center pt-4">
              <Button
                variant="outline"
                onClick={handleLoadMore}
                disabled={loadingMore}
                className="border-slate-700 hover:border-court-accent"
              >
                {loadingMore ? (
                  <>
                    <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                    Carregando...
                  </>
                ) : (
                  'Carregar mais'
                )}
              </Button>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

export default Notifications
