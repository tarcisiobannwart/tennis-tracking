import { Routes, Route } from 'react-router-dom'
import { useEffect } from 'react'
import { useThemeStore } from './stores/themeStore'
import Layout from './components/layout/Layout'
import Dashboard from './pages/Dashboard'
import LiveAnalysis from './pages/LiveAnalysis'
import Matches from './pages/Matches'
import MatchDetail from './pages/MatchDetail'
import Players from './pages/Players'
import Analytics from './pages/Analytics'
import Training from './pages/Training'
import Login from './pages/Login'

function App() {
  const { theme } = useThemeStore()

  useEffect(() => {
    const root = window.document.documentElement
    root.classList.remove('light', 'dark')
    root.classList.add(theme)
  }, [theme])

  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route element={<Layout />}>
        <Route path="/" element={<Dashboard />} />
        <Route path="/live" element={<LiveAnalysis />} />
        <Route path="/matches" element={<Matches />} />
        <Route path="/match/:id" element={<MatchDetail />} />
        <Route path="/players" element={<Players />} />
        <Route path="/analytics" element={<Analytics />} />
        <Route path="/training" element={<Training />} />
      </Route>
    </Routes>
  )
}

export default App