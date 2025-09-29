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
  private reconnectInterval = 3000
  private reconnectTimer: number | null = null
  private isManuallyDisconnected = false

  connect(config: WebSocketConfig): Promise<void> {
    return new Promise((resolve, reject) => {
      this.config = config
      this.maxReconnectAttempts = config.reconnectAttempts || 5
      this.reconnectInterval = config.reconnectInterval || 3000
      this.isManuallyDisconnected = false

      try {
        this.socket = new WebSocket(config.url)

        this.socket.onopen = () => {
          console.log('WebSocket connected')
          this.reconnectAttempts = 0
          config.onConnect?.()
          resolve()
        }

        this.socket.onmessage = (event) => {
          try {
            const message: WebSocketMessage = JSON.parse(event.data)
            config.onMessage?.(message)
          } catch (error) {
            console.error('Failed to parse WebSocket message:', error)
          }
        }

        this.socket.onclose = (event) => {
          console.log('WebSocket disconnected', event)
          this.socket = null
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

    this.reconnectTimer = setTimeout(() => {
      if (this.config && !this.isManuallyDisconnected) {
        console.log(`Attempting to reconnect... (${this.reconnectAttempts + 1}/${this.maxReconnectAttempts})`)
        this.reconnectAttempts++
        this.connect(this.config).catch((error) => {
          console.error('Reconnection failed:', error)
        })
      }
    }, this.reconnectInterval)
  }

  private clearReconnectTimer(): void {
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer)
      this.reconnectTimer = null
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

// Utility function to connect to live analysis WebSocket
export const connectToLiveAnalysis = async (
  matchId: string,
  onMessage: (message: WebSocketMessage) => void,
  onConnect?: () => void,
  onDisconnect?: () => void,
  onError?: (error: Event) => void
): Promise<void> => {
  const wsUrl = `${window.location.protocol === 'https:' ? 'wss:' : 'ws:'}//${window.location.host}/ws/live/${matchId}`

  await liveWebSocket.connect({
    url: wsUrl,
    onMessage,
    onConnect,
    onDisconnect,
    onError,
    reconnectAttempts: 10,
    reconnectInterval: 2000,
  })
}

export default WebSocketService