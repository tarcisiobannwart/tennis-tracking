import { useState } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { Home, BarChart3, Plus, TrendingUp, Settings, Video, Upload, Dumbbell, ScanLine, X } from 'lucide-react'
import { cn } from '@/utils/cn'

interface NavItem {
  id: string
  label: string
  icon: React.ReactNode
  path: string
}

interface FABAction {
  id: string
  label: string
  icon: React.ReactNode
  onClick: () => void
}

const navItems: NavItem[] = [
  { id: 'home', label: 'Home', icon: <Home className="w-5 h-5" />, path: '/dashboard' },
  { id: 'analysis', label: 'Analysis', icon: <BarChart3 className="w-5 h-5" />, path: '/analytics' },
  { id: 'fab', label: '', icon: null, path: '' }, // Placeholder for FAB
  { id: 'statistics', label: 'Statistics', icon: <TrendingUp className="w-5 h-5" />, path: '/matches' },
  { id: 'settings', label: 'Settings', icon: <Settings className="w-5 h-5" />, path: '/training' }
]

interface BottomNavProps {
  className?: string
  hideOnScroll?: boolean
}

export const BottomNav = ({ className, hideOnScroll = false }: BottomNavProps) => {
  const location = useLocation()
  const [fabOpen, setFabOpen] = useState(false)
  const [isVisible] = useState(true)

  const fabActions: FABAction[] = [
    {
      id: 'new-match',
      label: 'Nova Partida',
      icon: <Video className="w-5 h-5" />,
      onClick: () => {
        console.log('Nova Partida')
        setFabOpen(false)
      }
    },
    {
      id: 'upload-video',
      label: 'Upload Video',
      icon: <Upload className="w-5 h-5" />,
      onClick: () => {
        console.log('Upload Video')
        setFabOpen(false)
      }
    },
    {
      id: 'start-training',
      label: 'Iniciar Treino',
      icon: <Dumbbell className="w-5 h-5" />,
      onClick: () => {
        console.log('Iniciar Treino')
        setFabOpen(false)
      }
    },
    {
      id: 'scan-court',
      label: 'Scanner de Quadra',
      icon: <ScanLine className="w-5 h-5" />,
      onClick: () => {
        console.log('Scanner de Quadra')
        setFabOpen(false)
      }
    }
  ]

  const isActive = (path: string) => {
    if (path === '/dashboard') {
      return location.pathname === '/' || location.pathname === '/dashboard'
    }
    return location.pathname.startsWith(path)
  }

  return (
    <>
      {/* Overlay */}
      {fabOpen && (
        <div
          className="fixed inset-0 bg-black/50 z-40 lg:hidden backdrop-blur-sm"
          onClick={() => setFabOpen(false)}
        />
      )}

      {/* FAB Action Menu */}
      {fabOpen && (
        <div className="fixed bottom-24 left-1/2 -translate-x-1/2 z-50 lg:hidden">
          <div className="flex flex-col gap-3 items-center animate-in fade-in slide-in-from-bottom-4 duration-300">
            {fabActions.map((action, index) => (
              <button
                key={action.id}
                onClick={action.onClick}
                className="flex items-center gap-3 bg-card border border-border rounded-full px-4 py-3 shadow-lg hover:shadow-xl transition-all hover:scale-105"
                style={{
                  animationDelay: `${index * 50}ms`
                }}
              >
                <div className="p-2 rounded-full bg-court-accent/10 text-court-accent">
                  {action.icon}
                </div>
                <span className="text-sm font-medium pr-2">{action.label}</span>
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Bottom Navigation */}
      <nav
        className={cn(
          'fixed bottom-0 left-0 right-0 z-30 lg:hidden',
          'bg-card border-t border-border',
          'transition-transform duration-300',
          !isVisible && hideOnScroll && 'translate-y-full',
          className
        )}
      >
        <div className="relative flex items-center justify-around h-16 px-2">
          {navItems.map((item) => {
            // FAB placeholder
            if (item.id === 'fab') {
              return (
                <button
                  key="fab"
                  onClick={() => setFabOpen(!fabOpen)}
                  className={cn(
                    'absolute left-1/2 -translate-x-1/2 -top-6',
                    'w-14 h-14 rounded-full',
                    'bg-court-accent hover:bg-court-accent-hover',
                    'text-white shadow-lg hover:shadow-xl',
                    'flex items-center justify-center',
                    'transition-all duration-300',
                    'hover:scale-110 active:scale-95'
                  )}
                >
                  {fabOpen ? (
                    <X className="w-6 h-6 rotate-90 transition-transform duration-300" />
                  ) : (
                    <Plus className="w-6 h-6" />
                  )}
                </button>
              )
            }

            const active = isActive(item.path)

            return (
              <Link
                key={item.id}
                to={item.path}
                className={cn(
                  'flex flex-col items-center justify-center',
                  'min-w-[60px] h-full px-2',
                  'transition-colors duration-200',
                  active ? 'text-court-accent' : 'text-muted-foreground hover:text-foreground'
                )}
              >
                <div className={cn('transition-transform duration-200', active && 'scale-110')}>
                  {item.icon}
                </div>
                <span className="text-xs mt-1 font-medium">{item.label}</span>
                {active && (
                  <div className="absolute bottom-0 w-12 h-1 bg-court-accent rounded-t-full" />
                )}
              </Link>
            )
          })}
        </div>
      </nav>

      {/* Spacer for content */}
      <div className="h-16 lg:hidden" />
    </>
  )
}

export default BottomNav
