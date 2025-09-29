import { useLocation, Outlet } from 'react-router-dom'
import Sidebar from './Sidebar'
import Header from './Header'
import { useUIStore } from '@/stores/uiStore'
import { cn } from '@/utils/cn'

const Layout = () => {
  const { sidebarOpen } = useUIStore()
  const location = useLocation()

  // Hide sidebar on certain pages
  const hideSidebar = location.pathname === '/live'

  return (
    <div className="min-h-screen bg-background">
      {/* Sidebar */}
      {!hideSidebar && (
        <Sidebar />
      )}

      {/* Main content */}
      <div
        className={cn(
          "flex flex-col transition-all duration-300",
          !hideSidebar && sidebarOpen ? "ml-64" : !hideSidebar ? "ml-16" : "ml-0"
        )}
      >
        {/* Header */}
        <Header />

        {/* Page content */}
        <main className="flex-1 p-6">
          <Outlet />
        </main>
      </div>
    </div>
  )
}

export default Layout