import { create } from 'zustand'
import { persist } from 'zustand/middleware'

export type CourtColor = 'hard' | 'clay' | 'grass' | 'red_clay'

interface ThemeStore {
  theme: 'light' | 'dark'
  courtColor: CourtColor
  setTheme: (theme: 'light' | 'dark') => void
  toggleTheme: () => void
  setCourtColor: (courtColor: CourtColor) => void
}

const courtThemes = {
  hard: {
    accent: '33, 150, 243',       // #2196F3
    accentHover: '21, 101, 192',  // #1565C0
    accentBg: '33, 150, 243',     // rgba(33,150,243,0.12)
  },
  clay: {
    accent: '212, 163, 115',      // #D4A373
    accentHover: '139, 94, 60',   // #8B5E3C
    accentBg: '212, 163, 115',    // rgba(212,163,115,0.12)
  },
  grass: {
    accent: '76, 175, 80',        // #4CAF50
    accentHover: '46, 125, 50',   // #2E7D32
    accentBg: '76, 175, 80',      // rgba(76,175,80,0.12)
  },
  red_clay: {
    accent: '229, 57, 53',        // #E53935
    accentHover: '183, 28, 28',   // #B71C1C
    accentBg: '229, 57, 53',      // rgba(229,57,53,0.12)
  },
}

const applyCourtTheme = (courtColor: CourtColor) => {
  const theme = courtThemes[courtColor]
  const root = document.documentElement

  root.style.setProperty('--court-accent', theme.accent)
  root.style.setProperty('--court-accent-hover', theme.accentHover)
  root.style.setProperty('--court-accent-bg', theme.accentBg)
}

export const useThemeStore = create<ThemeStore>()(
  persist(
    (set, get) => ({
      theme: 'dark',
      courtColor: 'hard',
      setTheme: (theme) => set({ theme }),
      toggleTheme: () => set({ theme: get().theme === 'light' ? 'dark' : 'light' }),
      setCourtColor: (courtColor) => {
        applyCourtTheme(courtColor)
        set({ courtColor })
      },
    }),
    {
      name: 'tennis-theme-storage',
      onRehydrateStorage: () => (state) => {
        // Aplicar tema de quadra após recarregar do localStorage
        if (state?.courtColor) {
          applyCourtTheme(state.courtColor)
        }
      },
    }
  )
)