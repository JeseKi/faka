import { BrowserRouter as Router, Navigate, Route, Routes } from 'react-router-dom'
import MainLayout from './components/layout/MainLayout'
import AdminLayout from './components/layout/AdminLayout'
import ProtectedRoute from './components/ui/ProtectedRoute'
import LoginPage from './pages/auth/LoginPage'
import RegisterPage from './pages/auth/RegisterPage'
import PurchasePage from './pages/user/PurchasePage'
import CardManagementPage from './pages/admin/CardManagementPage'
import ActivationCodeManagementPage from './pages/admin/ActivationCodeManagementPage'
import OrderProcessingPage from './pages/staff/OrderProcessingPage'
import AdminDashboardPage from './pages/admin/AdminDashboardPage'
import SalesRecordPage from './pages/admin/SalesRecordPage'
import { AuthProvider } from './providers/AuthProvider'
import { SWRProvider } from './providers/SWRProvider'
import PurchaseHistoryPage from './pages/user/PurchaseHistoryPage'

export default function App() {
  return (
    <Router>
      <SWRProvider>
        <AuthProvider>
          <Routes>
            {/* 认证页面 */}
            <Route path="/login" element={<LoginPage />} />
            <Route path="/register" element={<RegisterPage />} />

            {/* 用户购买页面（无需登录） */}
            <Route path="/purchase" element={<MainLayout />}>
              <Route index element={<PurchasePage />} />
            </Route>

            {/* 购买历史 */}
            <Route path="/history" element={<MainLayout />}>
              <Route
                index
                element={
                  <ProtectedRoute requiredRoles={['user', 'staff', 'admin']}>
                    <PurchaseHistoryPage />
                  </ProtectedRoute>
                }
              />
            </Route>

            {/* 管理员后台（需要 admin 角色） */}
            <Route
              path="/admin"
              element={
                <ProtectedRoute requiredRoles={['admin']}>
                  <AdminLayout />
                </ProtectedRoute>
              }
            >
              <Route index element={<AdminDashboardPage />} />
              <Route path="cards" element={<CardManagementPage />} />
              <Route path="codes" element={<ActivationCodeManagementPage />} />
              <Route path="sales" element={<SalesRecordPage />} />
            </Route>

            {/* 工作人员后台（需要 staff 或 admin 角色） */}
            <Route
              path="/staff"
              element={
                <ProtectedRoute requiredRoles={['staff', 'admin']}>
                  <AdminLayout />
                </ProtectedRoute>
              }
            >
              <Route path="orders" element={<OrderProcessingPage />} />
            </Route>

            {/* 默认重定向 */}
            <Route path="/" element={<Navigate to="/purchase" replace />} />
            <Route path="*" element={<Navigate to="/purchase" replace />} />
          </Routes>
        </AuthProvider>
      </SWRProvider>
    </Router>
  )
}