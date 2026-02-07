import { Routes, Route } from 'react-router-dom'
import { useEffect } from 'react'
import { useThemeStore } from './stores/themeStore'
import Layout from './components/layout/Layout'
import ProtectedRoute from './components/auth/ProtectedRoute'
import RoleGuard from './components/auth/RoleGuard'
import LandingPage from './pages/LandingPage'
import Dashboard from './pages/Dashboard'
import LiveAnalysis from './pages/LiveAnalysis'
import Matches from './pages/Matches'
import MatchDetail from './pages/MatchDetail'
import Players from './pages/Players'
import Analytics from './pages/Analytics'
import Training from './pages/Training'
import Login from './pages/Login'
import Register from './pages/Register'
import ForgotPassword from './pages/ForgotPassword'
import ResetPassword from './pages/ResetPassword'
import Onboarding from './pages/Onboarding'
import Profile from './pages/Profile'
import Settings from './pages/Settings'
import Organization from './pages/Organization'
import AcceptInvite from './pages/AcceptInvite'
import PlayerProfile from './pages/PlayerProfile'
import AdminDashboard from './pages/admin/AdminDashboard'
import AdminUsers from './pages/admin/AdminUsers'
import AdminSubscriptions from './pages/admin/AdminSubscriptions'
import AdminLogs from './pages/admin/AdminLogs'

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
      <Route path="/register" element={<Register />} />
      <Route path="/forgot-password" element={<ForgotPassword />} />
      <Route path="/reset-password" element={<ResetPassword />} />
      <Route path="/onboarding" element={<Onboarding />} />

      {/* Public Player Profile - accessible without auth */}
      <Route path="/@:username" element={<PlayerProfile />} />

      {/* Protected Pages (App) */}
      <Route element={
        <ProtectedRoute>
          <Layout />
        </ProtectedRoute>
      }>
        <Route path="/app" element={<Dashboard />} />
        <Route path="/app/live" element={<LiveAnalysis />} />
        <Route path="/app/matches" element={<Matches />} />
        <Route path="/app/match/:id" element={<MatchDetail />} />
        <Route path="/app/players" element={<Players />} />
        <Route path="/app/analytics" element={<Analytics />} />
        <Route path="/app/training" element={<Training />} />
        <Route path="/app/profile" element={<Profile />} />
        <Route path="/app/settings" element={<Settings />} />
        <Route path="/app/organization" element={<Organization />} />
        <Route path="/app/accept-invite" element={<AcceptInvite />} />

        {/* Admin routes */}
        <Route path="/app/admin" element={
          <RoleGuard roles={['admin']}>
            <AdminDashboard />
          </RoleGuard>
        } />
        <Route path="/app/admin/users" element={
          <RoleGuard roles={['admin']}>
            <AdminUsers />
          </RoleGuard>
        } />
        <Route path="/app/admin/subscriptions" element={
          <RoleGuard roles={['admin']}>
            <AdminSubscriptions />
          </RoleGuard>
        } />
        <Route path="/app/admin/logs" element={
          <RoleGuard roles={['admin']}>
            <AdminLogs />
          </RoleGuard>
        } />
      </Route>
    </Routes>
  )
}

export default App
