import { Routes, Route } from 'react-router-dom'
import { useEffect } from 'react'
import { useThemeStore } from './stores/themeStore'
import Layout from './components/layout/Layout'
import LandingPage from './pages/LandingPage'
import Dashboard from './pages/Dashboard'
import LiveAnalysis from './pages/LiveAnalysis'
import Matches from './pages/Matches'
import MatchDetail from './pages/MatchDetail'
import Players from './pages/Players'
import Analytics from './pages/Analytics'
import Training from './pages/Training'
import Login from './pages/Login'
import Onboarding from './pages/Onboarding'

function App() {
  const { theme } = useThemeStore()

  useEffect(() => {
    const root = window.document.documentElement
    root.classList.remove('light', 'dark')
    root.classList.add(theme)
  }, [theme])

  return (
    <Routes>
      {/* Public Pages */}
      <Route path="/" element={<LandingPage />} />
      <Route path="/login" element={<Login />} />
      <Route path="/onboarding" element={<Onboarding />} />

      {/* Protected Pages (App) */}
      <Route element={<Layout />}>
        <Route path="/app" element={<Dashboard />} />
        <Route path="/app/live" element={<LiveAnalysis />} />
        <Route path="/app/matches" element={<Matches />} />
        <Route path="/app/match/:id" element={<MatchDetail />} />
        <Route path="/app/players" element={<Players />} />
        <Route path="/app/analytics" element={<Analytics />} />
        <Route path="/app/training" element={<Training />} />
      </Route>
    </Routes>
  )
}

export default App