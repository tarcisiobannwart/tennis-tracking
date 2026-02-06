import { Bell, Moon, Sun, Search, Upload, Settings } from 'lucide-react'
import { useTranslation } from 'react-i18next'
import { useThemeStore } from '@/stores/themeStore'
import { useUIStore } from '@/stores/uiStore'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import LanguageSelector from '../LanguageSelector'

const Header = () => {
  const { theme, toggleTheme } = useThemeStore()
  const { setModal } = useUIStore()
  const { t } = useTranslation()

  return (
    <header className="sticky top-0 z-30 h-16 bg-slate-900/95 backdrop-blur supports-[backdrop-filter]:bg-slate-900/80 border-b border-slate-700">
      <div className="flex items-center justify-between h-full px-4 md:px-6">
        {/* Search */}
        <div className="flex items-center space-x-4 flex-1 max-w-md">
          <div className="relative w-full">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-slate-500" />
            <Input
              type="text"
              placeholder={t('common.search')}
              className="pl-10 pr-4 h-9 w-full bg-slate-800 border-slate-700 text-slate-100 text-sm"
            />
          </div>
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
          <Button
            variant="ghost"
            size="icon"
            className="relative hover:bg-slate-800"
          >
            <Bell className="w-4 h-4 text-slate-400" />
            <div className="absolute top-1.5 right-1.5 w-2 h-2 bg-red-500 rounded-full animate-pulse shadow-lg shadow-red-500/50"></div>
          </Button>

          {/* Settings */}
          <Button
            variant="ghost"
            size="icon"
            onClick={() => setModal('matchSettings', true)}
            className="hover:bg-slate-800"
          >
            <Settings className="w-4 h-4 text-slate-400" />
          </Button>

          {/* User profile */}
          <div className="hidden md:flex items-center space-x-2 ml-2 pl-2 border-l border-slate-700">
            <div className="w-9 h-9 bg-gradient-to-br from-court-accent to-court-accent-hover rounded-full flex items-center justify-center shadow-lg shadow-court-accent/20">
              <span className="text-sm font-semibold text-white">
                CT
              </span>
            </div>
            <div className="hidden lg:block">
              <p className="text-sm font-medium text-slate-100">Treinador</p>
              <p className="text-xs text-slate-400">Administrador</p>
            </div>
          </div>
        </div>
      </div>
    </header>
  )
}

export default Header