import { useEffect, useRef, useCallback } from 'react'
import { useLiveStore } from '@/stores/liveStore'
import { WebSocketMessage } from '@/types'
import WebSocketService from '@/services/websocketService'

interface UseWebSocketOptions {
  url: string
  enabled?: boolean
  matchId?: string
  enablePollingFallback?: boolean
  pollingInterval?: number
  onMessage?: (message: WebSocketMessage) => void
  onConnect?: () => void
  onDisconnect?: () => void
  onError?: (error: Event) => void
}

export const useWebSocket = ({
  url,
  enabled = true,
  matchId,
  enablePollingFallback = true,
  pollingInterval = 5000,
  onMessage,
  onConnect,
  onDisconnect,
  onError,
}: UseWebSocketOptions) => {
  const websocketRef = useRef<WebSocketService | null>(null)
  const pollingTimerRef = useRef<number | null>(null)
  const reconnectFailedRef = useRef(false)
  const onMessageRef = useRef(onMessage)
  const onConnectRef = useRef(onConnect)
  const onDisconnectRef = useRef(onDisconnect)
  const onErrorRef = useRef(onError)
  const { setSocket, setConnectionStatus, handleWebSocketMessage, fetchScoreboardData } = useLiveStore()

  // Manter refs atualizados sem causar re-render
  onMessageRef.current = onMessage
  onConnectRef.current = onConnect
  onDisconnectRef.current = onDisconnect
  onErrorRef.current = onError

  const startPolling = useCallback(() => {
    if (!enablePollingFallback || !matchId) return

    // Stop any existing polling
    if (pollingTimerRef.current) {
      clearInterval(pollingTimerRef.current)
    }

    console.log('Starting polling fallback...')
    setConnectionStatus('disconnected') // Show as disconnected when polling

    // Start polling
    pollingTimerRef.current = setInterval(() => {
      if (matchId) {
        fetchScoreboardData(matchId).catch((error) => {
          console.error('Polling failed:', error)
        })
      }
    }, pollingInterval)
  }, [matchId, enablePollingFallback, pollingInterval, setConnectionStatus, fetchScoreboardData])

  const stopPolling = useCallback(() => {
    if (pollingTimerRef.current) {
      clearInterval(pollingTimerRef.current)
      pollingTimerRef.current = null
    }
  }, [])

  const connect = useCallback(async () => {
    if (!enabled) {
      setConnectionStatus('disconnected')
      return
    }

    if (websocketRef.current?.isConnected()) {
      return
    }

    try {
      setConnectionStatus('connecting')
      reconnectFailedRef.current = false

      const websocket = new WebSocketService()
      await websocket.connect({
        url,
        reconnectAttempts: 5,
        reconnectInterval: 1000,
        onMessage: (message) => {
          handleWebSocketMessage(message)
          onMessageRef.current?.(message)
        },
        onConnect: () => {
          setConnectionStatus('connected')
          stopPolling() // Stop polling when WebSocket connects
          reconnectFailedRef.current = false
          onConnectRef.current?.()
        },
        onDisconnect: () => {
          setConnectionStatus('disconnected')
          onDisconnectRef.current?.()

          // Start polling fallback after max reconnection attempts
          if (reconnectFailedRef.current && enablePollingFallback) {
            startPolling()
          }
        },
        onError: (error) => {
          setConnectionStatus('error')
          reconnectFailedRef.current = true
          onErrorRef.current?.(error)
        },
      })

      websocketRef.current = websocket
      setSocket(websocket as any)
    } catch (error) {
      console.error('WebSocket connection failed:', error)
      setConnectionStatus('error')
      reconnectFailedRef.current = true

      // Start polling fallback if WebSocket fails
      if (enablePollingFallback && matchId) {
        startPolling()
      }
    }
  }, [url, enabled, matchId, enablePollingFallback, setConnectionStatus, setSocket, handleWebSocketMessage, startPolling, stopPolling])

  const disconnect = useCallback(() => {
    stopPolling()
    if (websocketRef.current) {
      websocketRef.current.disconnect()
      websocketRef.current = null
      setSocket(null)
      setConnectionStatus('disconnected')
    }
  }, [setSocket, setConnectionStatus, stopPolling])

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
