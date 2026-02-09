import { WebSocketMessage } from '@/types'

export interface WebSocketConfig {
  url: string
  reconnectAttempts?: number
  reconnectInterval?: number
  onMessage?: (message: WebSocketMessage) => void
  onConnect?: () => void
  onDisconnect?: () => void
  onError?: (error: Event) => void
}

class WebSocketService {
  private socket: WebSocket | null = null
  private config: WebSocketConfig | null = null
  private reconnectAttempts = 0
  private maxReconnectAttempts = 5
  private baseReconnectInterval = 1000 // Start with 1 second
  private reconnectTimer: number | null = null
  private isManuallyDisconnected = false
  private pingInterval: number | null = null

  connect(config: WebSocketConfig): Promise<void> {
    return new Promise((resolve, reject) => {
      this.config = config
      this.maxReconnectAttempts = config.reconnectAttempts || 5
      this.baseReconnectInterval = config.reconnectInterval || 1000
      this.isManuallyDisconnected = false

      try {
        this.socket = new WebSocket(config.url)

        this.socket.onopen = () => {
          console.log('WebSocket connected')
          this.reconnectAttempts = 0
          this.startPingInterval()
          config.onConnect?.()
          resolve()
        }

        this.socket.onmessage = (event) => {
          try {
            const message: WebSocketMessage = JSON.parse(event.data)

            // Handle ping/pong messages
            if (message.type === 'ping') {
              this.send({ type: 'pong', timestamp: Date.now() })
            } else {
              config.onMessage?.(message)
            }
          } catch (error) {
            console.error('Failed to parse WebSocket message:', error)
          }
        }

        this.socket.onclose = (event) => {
          console.log('WebSocket disconnected', event)
          this.socket = null
          this.stopPingInterval()
          config.onDisconnect?.()

          // Attempt to reconnect if not manually disconnected
          if (!this.isManuallyDisconnected && this.shouldReconnect()) {
            this.scheduleReconnect()
          }
        }

        this.socket.onerror = (event) => {
          console.error('WebSocket error:', event)
          config.onError?.(event)
          reject(new Error('WebSocket connection failed'))
        }
      } catch (error) {
        reject(error)
      }
    })
  }

  disconnect(): void {
    this.isManuallyDisconnected = true
    this.clearReconnectTimer()
    this.stopPingInterval()

    if (this.socket) {
      this.socket.close()
      this.socket = null
    }
  }

  send(message: any): void {
    if (this.socket && this.socket.readyState === WebSocket.OPEN) {
      try {
        const messageString = typeof message === 'string' ? message : JSON.stringify(message)
        this.socket.send(messageString)
      } catch (error) {
        console.error('Failed to send WebSocket message:', error)
      }
    } else {
      console.warn('WebSocket is not connected')
    }
  }

  isConnected(): boolean {
    return this.socket?.readyState === WebSocket.OPEN
  }

  getReadyState(): number | null {
    return this.socket?.readyState || null
  }

  private shouldReconnect(): boolean {
    return this.reconnectAttempts < this.maxReconnectAttempts
  }

  private scheduleReconnect(): void {
    this.clearReconnectTimer()

    // Exponential backoff: 1s, 2s, 4s, 8s, 16s
    const backoffDelay = this.baseReconnectInterval * Math.pow(2, this.reconnectAttempts)
    const maxDelay = 30000 // Cap at 30 seconds
    const delay = Math.min(backoffDelay, maxDelay)

    this.reconnectTimer = setTimeout(() => {
      if (this.config && !this.isManuallyDisconnected) {
        console.log(`Attempting to reconnect... (${this.reconnectAttempts + 1}/${this.maxReconnectAttempts})`)
        this.reconnectAttempts++
        this.connect(this.config).catch((error) => {
          console.error('Reconnection failed:', error)
        })
      }
    }, delay)
  }

  private clearReconnectTimer(): void {
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer)
      this.reconnectTimer = null
    }
  }

  private startPingInterval(): void {
    this.stopPingInterval()
    // Send ping every 25 seconds to keep connection alive
    this.pingInterval = setInterval(() => {
      if (this.socket?.readyState === WebSocket.OPEN) {
        this.send({ type: 'ping', timestamp: Date.now() })
      }
    }, 25000)
  }

  private stopPingInterval(): void {
    if (this.pingInterval) {
      clearInterval(this.pingInterval)
      this.pingInterval = null
    }
  }

  // Static method to create and connect WebSocket
  static async create(config: WebSocketConfig): Promise<WebSocketService> {
    const service = new WebSocketService()
    await service.connect(config)
    return service
  }
}

// Create singleton instance for live analysis
export const liveWebSocket = new WebSocketService()

// Helper to get WebSocket URL
export const getWebSocketUrl = (path: string): string => {
  // Check if there's an environment variable for WebSocket URL
  const wsBaseUrl = import.meta.env.VITE_WS_URL

  if (wsBaseUrl) {
    return `${wsBaseUrl}${path}`
  }

  // Auto-detect from current location
  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
  const host = window.location.host

  return `${protocol}//${host}${path}`
}

// Utility function to connect to live analysis WebSocket
export const connectToLiveAnalysis = async (
  matchId: string,
  onMessage: (message: WebSocketMessage) => void,
  onConnect?: () => void,
  onDisconnect?: () => void,
  onError?: (error: Event) => void
): Promise<void> => {
  const wsUrl = getWebSocketUrl(`/ws/live/${matchId}`)

  await liveWebSocket.connect({
    url: wsUrl,
    onMessage,
    onConnect,
    onDisconnect,
    onError,
    reconnectAttempts: 5,
    reconnectInterval: 1000,
  })
}

export default WebSocketService