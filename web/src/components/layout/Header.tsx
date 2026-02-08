import { useState, useRef, useEffect } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { Bell, Moon, Sun, Search, Upload, User, LogOut, CreditCard } from 'lucide-react'
import { useTranslation } from 'react-i18next'
import { useThemeStore } from '@/stores/themeStore'
import { useUIStore } from '@/stores/uiStore'
import { useAuthStore } from '@/stores/authStore'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { authService } from '@/services/authService'
import LanguageSelector from '../LanguageSelector'
import { NotificationBell } from '@/components/notifications/NotificationBell'
import { GlobalSearch } from '@/components/search/GlobalSearch'
import { NotificationBell } from '@/components/notifications/NotificationBell'

const Header = () => {
  const { theme, toggleTheme } = useThemeStore()
  const { setModal } = useUIStore()
  const { user, logout } = useAuthStore()
  const { t } = useTranslation()
  const navigate = useNavigate()
  const [dropdownOpen, setDropdownOpen] = useState(false)
  const dropdownRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target as Node)) {
        setDropdownOpen(false)
      }
    }
    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  const handleLogout = async () => {
    await authService.logout()
    logout()
    navigate('/login')
  }

  const initials = user?.fullName
    ? user.fullName.split(' ').map(n => n[0]).join('').slice(0, 2).toUpperCase()
    : 'U'

  const planBadge = user?.subscription?.plan?.replace('_', ' ') || 'rally'

  return (
    <header className="sticky top-0 z-30 h-16 bg-slate-900/95 backdrop-blur supports-[backdrop-filter]:bg-slate-900/80 border-b border-slate-700">
      <div className="flex items-center justify-between h-full px-4 md:px-6">
        {/* Search */}
        <div className="flex items-center space-x-4 flex-1 max-w-md">
          <GlobalSearch />
        </div>

        {/* Actions */}
        <div className="flex items-center space-x-1 md:space-x-2">
          {/* Upload button */}
          <Button
            variant="outline"
            size="sm"
            onClick={() => setModal('uploadVideo', true)}
            className="hidden md:flex border-slate-700 hover:border-court-accent"
          >
            <Upload className="w-4 h-4 mr-2" />
            {t('dashboard.quickActions.uploadVideo')}
          </Button>

          {/* Language Selector */}
          <LanguageSelector />

          {/* Theme toggle */}
          <Button
            variant="ghost"
            size="icon"
            onClick={toggleTheme}
            className="hover:bg-slate-800"
          >
            {theme === 'dark' ? (
              <Sun className="w-4 h-4 text-slate-400" />
            ) : (
              <Moon className="w-4 h-4 text-slate-400" />
            )}
          </Button>

          {/* Notifications */}
          <NotificationBell />

          {/* User dropdown */}
          <div className="relative" ref={dropdownRef}>
            <button
              onClick={() => setDropdownOpen(!dropdownOpen)}
              className="hidden md:flex items-center space-x-2 ml-2 pl-2 border-l border-slate-700 hover:opacity-80 transition-opacity"
            >
              <div className="w-9 h-9 bg-gradient-to-br from-court-accent to-court-accent-hover rounded-full flex items-center justify-center shadow-lg shadow-court-accent/20">
                <span className="text-sm font-semibold text-white">{initials}</span>
              </div>
              <div className="hidden lg:block text-left">
                <p className="text-sm font-medium text-slate-100">{user?.fullName || 'Usuario'}</p>
                <p className="text-xs text-slate-400 capitalize">{planBadge}</p>
              </div>
            </button>

            {dropdownOpen && (
              <div className="absolute right-0 mt-2 w-56 bg-slate-800 border border-slate-700 rounded-lg shadow-xl py-1 z-50">
                <div className="px-4 py-2 border-b border-slate-700">
                  <p className="text-sm font-medium text-slate-100">{user?.fullName}</p>
                  <p className="text-xs text-slate-400">{user?.email}</p>
                </div>

                <Link
                  to="/app/profile"
                  onClick={() => setDropdownOpen(false)}
                  className="flex items-center gap-2 px-4 py-2 text-sm text-slate-300 hover:bg-slate-700"
                >
                  <User className="w-4 h-4" />
                  {t('navigation.profile')}
                </Link>

                <Link
                  to="/app/settings"
                  onClick={() => setDropdownOpen(false)}
                  className="flex items-center gap-2 px-4 py-2 text-sm text-slate-300 hover:bg-slate-700"
                >
                  <CreditCard className="w-4 h-4" />
                  {t('navigation.settings')}
                </Link>

                <div className="border-t border-slate-700 mt-1 pt-1">
                  <button
                    onClick={handleLogout}
                    className="flex items-center gap-2 px-4 py-2 text-sm text-red-400 hover:bg-slate-700 w-full text-left"
                  >
                    <LogOut className="w-4 h-4" />
                    {t('navigation.logout')}
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </header>
  )
}

export default Header
