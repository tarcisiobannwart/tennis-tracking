import { Bell, Moon, Sun, Search, Upload, Settings } from 'lucide-react'
import { useTranslation } from 'react-i18next'
import { useThemeStore } from '@/stores/themeStore'
import { useUIStore } from '@/stores/uiStore'
import { Button } from '@/components/ui/button'
import LanguageSelector from '../LanguageSelector'

const Header = () => {
  const { theme, toggleTheme } = useThemeStore()
  const { setModal } = useUIStore()
  const { t } = useTranslation()

  return (
    <header className="sticky top-0 z-30 h-16 bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60 border-b border-border">
      <div className="flex items-center justify-between h-full px-6">
        {/* Search */}
        <div className="flex items-center space-x-4">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-muted-foreground" />
            <input
              type="text"
              placeholder={t('common.search')}
              className="pl-10 pr-4 py-2 w-80 bg-accent border border-input rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-ring"
            />
          </div>
        </div>

        {/* Actions */}
        <div className="flex items-center space-x-2">
          {/* Upload button */}
          <Button
            variant="outline"
            size="sm"
            onClick={() => setModal('uploadVideo', true)}
            className="hidden sm:flex"
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
          >
            {theme === 'dark' ? (
              <Sun className="w-4 h-4" />
            ) : (
              <Moon className="w-4 h-4" />
            )}
          </Button>

          {/* Notifications */}
          <Button variant="ghost" size="icon" className="relative">
            <Bell className="w-4 h-4" />
            <div className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full"></div>
          </Button>

          {/* Settings */}
          <Button
            variant="ghost"
            size="icon"
            onClick={() => setModal('matchSettings', true)}
          >
            <Settings className="w-4 h-4" />
          </Button>

          {/* User profile */}
          <div className="flex items-center space-x-2 ml-4">
            <div className="w-8 h-8 bg-primary rounded-full flex items-center justify-center">
              <span className="text-sm font-medium text-primary-foreground">
                CT
              </span>
            </div>
            <div className="hidden sm:block">
              <p className="text-sm font-medium">Treinador</p>
              <p className="text-xs text-muted-foreground">Administrador</p>
            </div>
          </div>
        </div>
      </div>
    </header>
  )
}

export default Header