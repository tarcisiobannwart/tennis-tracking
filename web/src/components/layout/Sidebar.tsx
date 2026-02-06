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
    <>
      {/* Desktop Sidebar */}
      <div
        className={cn(
          "hidden md:flex fixed left-0 top-0 z-40 h-screen bg-slate-800 border-r border-slate-700 transition-all duration-300 flex-col",
          sidebarOpen ? "w-64" : "w-16"
        )}
      >
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-slate-700">
          {sidebarOpen && (
            <div className="flex items-center space-x-2">
              <div className="w-8 h-8 bg-court-accent rounded-lg flex items-center justify-center shadow-lg shadow-court-accent/20">
                <Video className="w-4 h-4 text-white" />
              </div>
              <span className="text-lg font-semibold text-slate-100">{t('common.appName')}</span>
            </div>
          )}
          <Button
            variant="ghost"
            size="icon"
            onClick={toggleSidebar}
            className="ml-auto hover:bg-slate-700"
          >
            <Menu className="w-4 h-4 text-slate-400" />
          </Button>
        </div>

        {/* Navigation */}
        <nav className="p-2 space-y-1 flex-1">
          {navigation.map((item) => {
            const Icon = item.icon
            const active = isActive(item.href)
            return (
              <Link
                key={item.name}
                to={item.href}
                className={cn(
                  "flex items-center px-3 py-3 text-sm font-medium rounded-lg transition-all duration-300 relative group",
                  active
                    ? "bg-court-accent-bg text-court-accent"
                    : "text-slate-400 hover:bg-slate-700 hover:text-slate-100",
                  !sidebarOpen && "justify-center"
                )}
              >
                {/* Active indicator */}
                {active && (
                  <div className="absolute left-0 w-1 h-8 bg-court-accent rounded-r-full" />
                )}
                <Icon className={cn("w-5 h-5", sidebarOpen && "mr-3")} />
                {sidebarOpen && item.name}
                {/* Tooltip for collapsed state */}
                {!sidebarOpen && (
                  <div className="absolute left-16 px-2 py-1 bg-slate-700 text-slate-100 text-xs rounded-md opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap pointer-events-none">
                    {item.name}
                  </div>
                )}
              </Link>
            )
          })}
        </nav>

        {/* Live indicator */}
        {sidebarOpen && (
          <div className="p-4 border-t border-slate-700">
            <div className="bg-slate-700/50 rounded-lg p-3 border border-slate-600">
              <div className="flex items-center space-x-2">
                <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse shadow-lg shadow-green-500/50"></div>
                <span className="text-xs text-slate-400">
                  Sistema Ativo
                </span>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Mobile Bottom Navigation */}
      <div className="md:hidden fixed bottom-0 left-0 right-0 z-50 bg-slate-800 border-t border-slate-700 safe-area-inset-bottom">
        <nav className="flex items-center justify-around p-2">
          {navigation.slice(0, 5).map((item) => {
            const Icon = item.icon
            const active = isActive(item.href)
            return (
              <Link
                key={item.name}
                to={item.href}
                className={cn(
                  "flex flex-col items-center justify-center px-3 py-2 text-xs font-medium rounded-lg transition-all duration-300 min-w-[60px]",
                  active
                    ? "text-court-accent"
                    : "text-slate-400"
                )}
              >
                <Icon className="w-5 h-5 mb-1" />
                <span className="text-[10px]">{item.name.split(' ')[0]}</span>
                {/* Active indicator dot */}
                {active && (
                  <div className="absolute bottom-0 w-1 h-1 bg-court-accent rounded-full" />
                )}
              </Link>
            )
          })}
        </nav>
      </div>
    </>
  )
}

export default Sidebar