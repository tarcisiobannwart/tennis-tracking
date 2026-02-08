/**
 * NotificationCard - Card individual de notificacao.
 *
 * Implementado para TT-137: Sistema de notificacoes.
 */

import { Trophy, UserPlus, Calendar, TrendingUp, Award, Bell } from 'lucide-react'
import { formatDistanceToNow } from 'date-fns'
import { ptBR } from 'date-fns/locale'
import { Notification, NotificationType } from '@/services/notificationService'

interface NotificationCardProps {
  notification: Notification
  onRead: (notificationId: string) => void
  onClick?: (notification: Notification) => void
}

const getNotificationIcon = (type: NotificationType) => {
  switch (type) {
    case 'match_result':
      return <Trophy className="w-5 h-5 text-yellow-500" />
    case 'friendship':
      return <UserPlus className="w-5 h-5 text-blue-500" />
    case 'game_scheduled':
      return <Calendar className="w-5 h-5 text-green-500" />
    case 'ranking_round':
      return <TrendingUp className="w-5 h-5 text-purple-500" />
    case 'tournament':
      return <Award className="w-5 h-5 text-orange-500" />
    default:
      return <Bell className="w-5 h-5 text-slate-500" />
  }
}

const getNotificationBgColor = (type: NotificationType, isRead: boolean) => {
  if (isRead) {
    return 'bg-slate-800/50'
  }

  switch (type) {
    case 'match_result':
      return 'bg-yellow-500/10 border-yellow-500/20'
    case 'friendship':
      return 'bg-blue-500/10 border-blue-500/20'
    case 'game_scheduled':
      return 'bg-green-500/10 border-green-500/20'
    case 'ranking_round':
      return 'bg-purple-500/10 border-purple-500/20'
    case 'tournament':
      return 'bg-orange-500/10 border-orange-500/20'
    default:
      return 'bg-slate-800/50'
  }
}

export const NotificationCard: React.FC<NotificationCardProps> = ({
  notification,
  onRead,
  onClick,
}) => {
  const handleClick = () => {
    if (!notification.is_read) {
      onRead(notification.id)
    }
    if (onClick) {
      onClick(notification)
    }
  }

  const timeAgo = formatDistanceToNow(new Date(notification.created_at), {
    addSuffix: true,
    locale: ptBR,
  })

  return (
    <div
      onClick={handleClick}
      className={`flex items-start gap-3 p-4 rounded-lg border transition-all cursor-pointer hover:shadow-md ${getNotificationBgColor(
        notification.notification_type,
        notification.is_read
      )} ${notification.is_read ? 'border-slate-700' : 'border'}`}
    >
      {/* Icone */}
      <div className="flex-shrink-0 mt-1">{getNotificationIcon(notification.notification_type)}</div>

      {/* Conteudo */}
      <div className="flex-1 min-w-0">
        <div className="flex items-start justify-between gap-2">
          <h4
            className={`text-sm font-semibold ${
              notification.is_read ? 'text-slate-300' : 'text-slate-100'
            }`}
          >
            {notification.title}
          </h4>
          {!notification.is_read && (
            <span className="flex-shrink-0 w-2 h-2 bg-blue-500 rounded-full mt-1"></span>
          )}
        </div>

        <p
          className={`text-sm mt-1 ${
            notification.is_read ? 'text-slate-500' : 'text-slate-400'
          }`}
        >
          {notification.message}
        </p>

        <p className="text-xs text-slate-500 mt-2">{timeAgo}</p>
      </div>
    </div>
  )
}

export default NotificationCard
