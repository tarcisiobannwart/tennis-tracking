import { create } from 'zustand'
import { persist } from 'zustand/middleware'

export interface UserSubscription {
  plan: 'rally' | 'match_point' | 'grand_slam'
  status: 'active' | 'trialing' | 'past_due' | 'canceled' | 'incomplete'
  stripeCustomerId?: string
  stripeSubscriptionId?: string
  currentPeriodStart?: string
  currentPeriodEnd?: string
  cancelAtPeriodEnd: boolean
  trialEnd?: string
}

export interface User {
  id: string
  email: string
  username: string
  fullName: string
  role: 'admin' | 'coach' | 'player' | 'analyst' | 'viewer'
  isActive: boolean
  profileImage?: string
  phone?: string
  country?: string
  language: string
  preferences: Record<string, any>
  createdAt: string
  updatedAt: string
  lastLogin?: string
  subscription?: UserSubscription
  organizationId?: string
  organizationRole?: string
  emailVerified: boolean
}

interface AuthState {
  user: User | null
  accessToken: string | null
  refreshToken: string | null
  isAuthenticated: boolean
  isLoading: boolean

  setAuth: (user: User, accessToken: string, refreshToken: string) => void
  setUser: (user: User) => void
  setTokens: (accessToken: string, refreshToken: string) => void
  logout: () => void
  setLoading: (loading: boolean) => void
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      accessToken: null,
      refreshToken: null,
      isAuthenticated: false,
      isLoading: false,

      setAuth: (user, accessToken, refreshToken) =>
        set({
          user,
          accessToken,
          refreshToken,
          isAuthenticated: true,
          isLoading: false,
        }),

      setUser: (user) =>
        set({ user }),

      setTokens: (accessToken, refreshToken) =>
        set({ accessToken, refreshToken }),

      logout: () =>
        set({
          user: null,
          accessToken: null,
          refreshToken: null,
          isAuthenticated: false,
          isLoading: false,
        }),

      setLoading: (isLoading) =>
        set({ isLoading }),
    }),
    {
      name: 'tennis-auth',
      partialize: (state) => ({
        user: state.user,
        accessToken: state.accessToken,
        refreshToken: state.refreshToken,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
)
