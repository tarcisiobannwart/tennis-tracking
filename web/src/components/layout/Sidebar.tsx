import { Link, useLocation } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import {
  BarChart3,
  Users,
  Trophy,
  Home,
  Menu,
  Activity,
  Video,
  Target
} from 'lucide-react'
import { useUIStore } from '@/stores/uiStore'
import { cn } from '@/utils/cn'
import { Button } from '@/components/ui/button'

const Sidebar = () => {
  const { sidebarOpen, toggleSidebar } = useUIStore()
  const location = useLocation()
  const { t } = useTranslation()

  const navigation = [
    {
      name: t('navigation.dashboard'),
      href: '/',
      icon: Home,
    },
    {
      name: t('navigation.analysis'),
      href: '/live',
      icon: Activity,
    },
    {
      name: t('navigation.matches'),
      href: '/matches',
      icon: Trophy,
    },
    {
      name: 'Jogadores',
      href: '/players',
      icon: Users,
    },
    {
      name: t('navigation.statistics'),
      href: '/analytics',
      icon: BarChart3,
    },
    {
      name: 'Treino',
      href: '/training',
      icon: Target,
    },
  ]

  const isActive = (href: string) => location.pathname === href

  return (
    <div
      className={cn(
        "fixed left-0 top-0 z-40 h-screen bg-card border-r border-border transition-all duration-300",
        sidebarOpen ? "w-64" : "w-16"
      )}
    >
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-border">
        {sidebarOpen && (
          <div className="flex items-center space-x-2">
            <div className="w-8 h-8 bg-court-green rounded-full flex items-center justify-center">
              <Video className="w-4 h-4 text-white" />
            </div>
            <span className="text-lg font-semibold">{t('common.appName')}</span>
          </div>
        )}
        <Button
          variant="ghost"
          size="icon"
          onClick={toggleSidebar}
          className="ml-auto"
        >
          <Menu className="w-4 h-4" />
        </Button>
      </div>

      {/* Navigation */}
      <nav className="p-2 space-y-1">
        {navigation.map((item) => {
          const Icon = item.icon
          return (
            <Link
              key={item.name}
              to={item.href}
              className={cn(
                "flex items-center px-3 py-2 text-sm font-medium rounded-md transition-colors",
                isActive(item.href)
                  ? "bg-primary text-primary-foreground"
                  : "text-muted-foreground hover:bg-accent hover:text-accent-foreground",
                !sidebarOpen && "justify-center"
              )}
            >
              <Icon className={cn("w-5 h-5", sidebarOpen && "mr-3")} />
              {sidebarOpen && item.name}
            </Link>
          )
        })}
      </nav>

      {/* Live indicator */}
      {sidebarOpen && (
        <div className="absolute bottom-4 left-4 right-4">
          <div className="bg-accent rounded-lg p-3">
            <div className="flex items-center space-x-2">
              <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
              <span className="text-xs text-muted-foreground">
                Sistema Ativo
              </span>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default Sidebar