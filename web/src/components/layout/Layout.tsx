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
    <div className="min-h-screen bg-slate-900">
      {/* Sidebar */}
      {!hideSidebar && (
        <Sidebar />
      )}

      {/* Main content */}
      <div
        className={cn(
          "flex flex-col transition-all duration-300",
          !hideSidebar && sidebarOpen ? "md:ml-64" : !hideSidebar ? "md:ml-16" : "ml-0",
          !hideSidebar && "pb-16 md:pb-0" // Add padding bottom for mobile nav
        )}
      >
        {/* Header */}
        <Header />

        {/* Page content */}
        <main className="flex-1 p-4 md:p-6">
          <Outlet />
        </main>
      </div>
    </div>
  )
}

export default Layout