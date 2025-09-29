import { create } from 'zustand'
import { VideoPlayerState, CourtViewConfig, AnalyticsFilter } from '@/types'

interface UIStore {
  // Sidebar state
  sidebarOpen: boolean

  // Video player state
  videoPlayer: VideoPlayerState

  // Court view configuration
  courtView: CourtViewConfig

  // Analytics filters
  analyticsFilter: AnalyticsFilter

  // Loading states
  isLoading: boolean
  loadingMessage: string

  // Notifications
  notifications: Notification[]

  // Modal states
  modals: {
    uploadVideo: boolean
    playerProfile: boolean
    matchSettings: boolean
    analyticsExport: boolean
  }

  // Actions
  setSidebarOpen: (open: boolean) => void
  toggleSidebar: () => void

  setVideoPlayerState: (state: Partial<VideoPlayerState>) => void

  setCourtViewConfig: (config: Partial<CourtViewConfig>) => void

  setAnalyticsFilter: (filter: Partial<AnalyticsFilter>) => void

  setLoading: (loading: boolean, message?: string) => void

  addNotification: (notification: Omit<Notification, 'id'>) => void
  removeNotification: (id: string) => void
  clearNotifications: () => void

  setModal: (modal: keyof UIStore['modals'], open: boolean) => void
  closeAllModals: () => void
}

interface Notification {
  id: string
  type: 'success' | 'error' | 'warning' | 'info'
  title: string
  message: string
  duration?: number
}

export const useUIStore = create<UIStore>((set, get) => ({
  // Initial state
  sidebarOpen: true,

  videoPlayer: {
    isPlaying: false,
    currentTime: 0,
    duration: 0,
    playbackRate: 1,
    volume: 1,
    isFullscreen: false,
    showOverlays: true,
    selectedOverlays: ['ball', 'players', 'court'],
  },

  courtView: {
    view: '2d',
    showTrajectory: true,
    showHeatmap: false,
    showPlayerMovement: true,
    timeRange: [0, 100],
    selectedZones: [],
  },

  analyticsFilter: {
    dateRange: [new Date(Date.now() - 30 * 24 * 60 * 60 * 1000), new Date()], // Last 30 days
    surface: [],
    opponent: [],
    tournament: [],
    round: [],
  },

  isLoading: false,
  loadingMessage: '',

  notifications: [],

  modals: {
    uploadVideo: false,
    playerProfile: false,
    matchSettings: false,
    analyticsExport: false,
  },

  // Actions
  setSidebarOpen: (open) => set({ sidebarOpen: open }),

  toggleSidebar: () => set({ sidebarOpen: !get().sidebarOpen }),

  setVideoPlayerState: (state) => set({
    videoPlayer: { ...get().videoPlayer, ...state }
  }),

  setCourtViewConfig: (config) => set({
    courtView: { ...get().courtView, ...config }
  }),

  setAnalyticsFilter: (filter) => set({
    analyticsFilter: { ...get().analyticsFilter, ...filter }
  }),

  setLoading: (loading, message = '') => set({
    isLoading: loading,
    loadingMessage: message
  }),

  addNotification: (notification) => {
    const id = Math.random().toString(36).substr(2, 9)
    const newNotification = { ...notification, id }

    set({ notifications: [...get().notifications, newNotification] })

    // Auto remove after duration
    if (notification.duration !== 0) {
      setTimeout(() => {
        get().removeNotification(id)
      }, notification.duration || 5000)
    }
  },

  removeNotification: (id) => set({
    notifications: get().notifications.filter(n => n.id !== id)
  }),

  clearNotifications: () => set({ notifications: [] }),

  setModal: (modal, open) => set({
    modals: { ...get().modals, [modal]: open }
  }),

  closeAllModals: () => set({
    modals: {
      uploadVideo: false,
      playerProfile: false,
      matchSettings: false,
      analyticsExport: false,
    }
  }),
}))