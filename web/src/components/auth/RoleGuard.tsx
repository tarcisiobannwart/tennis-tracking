import { Navigate } from 'react-router-dom'
import { useAuthStore } from '@/stores/authStore'

interface RoleGuardProps {
  children: React.ReactNode
  roles: string[]
  fallback?: string
}

const RoleGuard = ({ children, roles, fallback = '/app' }: RoleGuardProps) => {
  const { user } = useAuthStore()

  if (!user || !roles.includes(user.role)) {
    return <Navigate to={fallback} replace />
  }

  return <>{children}</>
}

export default RoleGuard
