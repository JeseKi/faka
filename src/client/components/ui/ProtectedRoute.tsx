import { type ReactNode } from 'react'
import { Navigate, useLocation } from 'react-router-dom'
import { useAuth } from '../../hooks/useAuth'

interface ProtectedRouteProps {
  children: ReactNode
  requiredRoles?: string[]
  fallbackPath?: string
}

export default function ProtectedRoute({
  children,
  requiredRoles = [],
  fallbackPath = '/login'
}: ProtectedRouteProps) {
  const { isAuthenticated, loading, user } = useAuth()
  const location = useLocation()

  if (loading) {
    return (
      <div className="flex h-screen items-center justify-center text-slate-600">
        正在验证登录状态...
      </div>
    )
  }

  if (!isAuthenticated) {
    return <Navigate to={fallbackPath} state={{ from: location }} replace />
  }

  // 如果指定了需要的角色，检查用户是否拥有其中任一角色
  if (requiredRoles.length > 0) {
    const hasRequiredRole = requiredRoles.some(role => user?.role === role)
    if (!hasRequiredRole) {
      // 根据用户角色重定向到相应的页面
      if (user?.role === 'admin') {
        return <Navigate to="/admin" replace />
      } else if (user?.role === 'staff') {
        return <Navigate to="/staff/orders" replace />
      } else {
        return <Navigate to="/" replace />
      }
    }
  }

  return <>{children}</>
}