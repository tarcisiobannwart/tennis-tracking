/**
 * NotificationBell - Icone de sino de notificacoes com badge de contador.
 *
 * Implementado para TT-137: Sistema de notificacoes.
 */

import { useState, useEffect, useRef } from 'react'
import { Bell } from 'lucide-react'
import { useNavigate } from 'react-router-dom'
import { Button } from '@/components/ui/button'
import { getUnreadCount } from '@/services/notificationService'

interface NotificationBellProps {
  className?: string
}

export const NotificationBell: React.FC<NotificationBellProps> = ({ className = '' }) => {
  const [unreadCount, setUnreadCount] = useState<number>(0)
  const navigate = useNavigate()
  const intervalRef = useRef<NodeJS.Timeout | null>(null)

  const fetchUnreadCount = async () => {
    try {
      const response = await getUnreadCount()
      setUnreadCount(response.unread_count)
    } catch (error) {
      console.error('Erro ao buscar contador de notificacoes:', error)
    }
  }

  useEffect(() => {
    // Buscar contador inicial
    fetchUnreadCount()

    // Atualizar a cada 30 segundos (fallback se WebSocket falhar)
    intervalRef.current = setInterval(fetchUnreadCount, 30000)

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current)
      }
    }
  }, [])

  // Funcao para atualizar contador externamente (ex: via WebSocket)
  const updateUnreadCount = (count: number) => {
    setUnreadCount(count)
  }

  // Expor funcao para componentes externos (via ref ou contexto)
  useEffect(() => {
    // @ts-ignore - adicionar ao window para acesso global
    window.updateNotificationCount = updateUnreadCount
    return () => {
      // @ts-ignore
      delete window.updateNotificationCount
    }
  }, [])

  const handleClick = () => {
    navigate('/app/notifications')
  }

  return (
    <Button
      variant="ghost"
      size="icon"
      className={`relative hover:bg-slate-800 ${className}`}
      onClick={handleClick}
    >
      <Bell className="w-4 h-4 text-slate-400" />
      {unreadCount > 0 && (
        <span className="absolute -top-1 -right-1 flex items-center justify-center min-w-[18px] h-[18px] text-[10px] font-bold text-white bg-red-500 rounded-full px-1">
          {unreadCount > 99 ? '99+' : unreadCount}
        </span>
      )}
    </Button>
  )
}

export default NotificationBell
