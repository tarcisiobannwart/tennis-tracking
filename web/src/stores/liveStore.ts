import { create } from 'zustand'
import { LiveFrame, Match, WebSocketMessage } from '@/types'

interface LiveStore {
  // Connection state
  isConnected: boolean
  connectionStatus: 'connecting' | 'connected' | 'disconnected' | 'error'

  // Current match data
  currentMatch: Match | null
  currentFrame: LiveFrame | null

  // Live tracking data
  frames: LiveFrame[]
  isRecording: boolean
  isAnalyzing: boolean

  // Video state
  videoUrl: string | null
  currentTime: number
  isPlaying: boolean

  // WebSocket
  socket: WebSocket | null

  // Actions
  setConnectionStatus: (status: LiveStore['connectionStatus']) => void
  setCurrentMatch: (match: Match | null) => void
  setCurrentFrame: (frame: LiveFrame | null) => void
  addFrame: (frame: LiveFrame) => void
  setIsRecording: (isRecording: boolean) => void
  setIsAnalyzing: (isAnalyzing: boolean) => void
  setVideoUrl: (url: string | null) => void
  setCurrentTime: (time: number) => void
  setIsPlaying: (isPlaying: boolean) => void
  setSocket: (socket: WebSocket | null) => void
  handleWebSocketMessage: (message: WebSocketMessage) => void
  clearFrames: () => void
  reset: () => void
}

export const useLiveStore = create<LiveStore>((set, get) => ({
  // Initial state
  isConnected: false,
  connectionStatus: 'disconnected',
  currentMatch: null,
  currentFrame: null,
  frames: [],
  isRecording: false,
  isAnalyzing: false,
  videoUrl: null,
  currentTime: 0,
  isPlaying: false,
  socket: null,

  // Actions
  setConnectionStatus: (status) => {
    set({
      connectionStatus: status,
      isConnected: status === 'connected'
    })
  },

  setCurrentMatch: (match) => set({ currentMatch: match }),

  setCurrentFrame: (frame) => set({ currentFrame: frame }),

  addFrame: (frame) => {
    const { frames } = get()
    const maxFrames = 1000 // Keep last 1000 frames for performance
    const newFrames = [...frames, frame].slice(-maxFrames)
    set({ frames: newFrames })
  },

  setIsRecording: (isRecording) => set({ isRecording }),

  setIsAnalyzing: (isAnalyzing) => set({ isAnalyzing }),

  setVideoUrl: (url) => set({ videoUrl: url }),

  setCurrentTime: (time) => set({ currentTime: time }),

  setIsPlaying: (isPlaying) => set({ isPlaying }),

  setSocket: (socket) => set({ socket }),

  handleWebSocketMessage: (message) => {
    const { type, data } = message

    switch (type) {
      case 'frame_update':
        get().setCurrentFrame(data)
        get().addFrame(data)
        break

      case 'match_event':
        // Handle match events (points, games, sets)
        if (data.match) {
          get().setCurrentMatch(data.match)
        }
        break

      case 'score_update':
        // Handle score updates
        const { currentMatch } = get()
        if (currentMatch && data.score) {
          get().setCurrentMatch({
            ...currentMatch,
            score: data.score
          })
        }
        break

      case 'connection':
        get().setConnectionStatus(data.status)
        break

      case 'error':
        console.error('WebSocket error:', data)
        get().setConnectionStatus('error')
        break

      default:
        console.warn('Unknown WebSocket message type:', type)
    }
  },

  clearFrames: () => set({ frames: [] }),

  reset: () => set({
    currentMatch: null,
    currentFrame: null,
    frames: [],
    isRecording: false,
    isAnalyzing: false,
    videoUrl: null,
    currentTime: 0,
    isPlaying: false,
  }),
}))