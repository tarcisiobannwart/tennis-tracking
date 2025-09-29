import { useEffect, useRef, useCallback } from 'react'
import { useLiveStore } from '@/stores/liveStore'
import { WebSocketMessage } from '@/types'
import WebSocketService from '@/services/websocketService'

interface UseWebSocketOptions {
  url: string
  enabled?: boolean
  onMessage?: (message: WebSocketMessage) => void
  onConnect?: () => void
  onDisconnect?: () => void
  onError?: (error: Event) => void
}

export const useWebSocket = ({
  url,
  enabled = true,
  onMessage,
  onConnect,
  onDisconnect,
  onError,
}: UseWebSocketOptions) => {
  const websocketRef = useRef<WebSocketService | null>(null)
  const { setSocket, setConnectionStatus, handleWebSocketMessage } = useLiveStore()

  const connect = useCallback(async () => {
    // Exit early if disabled
    if (!enabled) {
      setConnectionStatus('disconnected')
      return
    }

    if (websocketRef.current?.isConnected()) {
      return
    }

    try {
      setConnectionStatus('connecting')

      const websocket = new WebSocketService()
      await websocket.connect({
        url,
        onMessage: (message) => {
          handleWebSocketMessage(message)
          onMessage?.(message)
        },
        onConnect: () => {
          setConnectionStatus('connected')
          onConnect?.()
        },
        onDisconnect: () => {
          setConnectionStatus('disconnected')
          onDisconnect?.()
        },
        onError: (error) => {
          setConnectionStatus('error')
          onError?.(error)
        },
      })

      websocketRef.current = websocket
      setSocket(websocket as any) // Store reference in Zustand
    } catch (error) {
      console.error('WebSocket connection failed:', error)
      setConnectionStatus('error')
    }
  }, [url, enabled, onMessage, onConnect, onDisconnect, onError, setConnectionStatus, setSocket, handleWebSocketMessage])

  const disconnect = useCallback(() => {
    if (websocketRef.current) {
      websocketRef.current.disconnect()
      websocketRef.current = null
      setSocket(null)
      setConnectionStatus('disconnected')
    }
  }, [setSocket, setConnectionStatus])

  const send = useCallback((message: any) => {
    if (!enabled) {
      console.log('WebSocket is disabled. Message not sent:', message)
      return
    }

    if (websocketRef.current?.isConnected()) {
      websocketRef.current.send(message)
    } else {
      console.warn('WebSocket is not connected')
    }
  }, [enabled])

  useEffect(() => {
    if (enabled) {
      connect()
    } else {
      disconnect()
    }

    return () => {
      disconnect()
    }
  }, [connect, disconnect, enabled])

  return {
    isConnected: websocketRef.current?.isConnected() || false,
    send,
    connect,
    disconnect,
  }
}