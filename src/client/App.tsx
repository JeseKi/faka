import { BrowserRouter as Router, Navigate, Route, Routes } from 'react-router-dom'
import MainLayout from './components/layout/MainLayout'
import AdminLayout from './components/layout/AdminLayout'
import StaffLayout from './components/layout/StaffLayout'
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
import LandingPage from './pages/LandingPage'
import RechargePlusPage from './pages/RechargePlusPage'
import ChannelManagementPage from './pages/admin/ChannelManagementPage'
import PersonnelManagementPage from './pages/admin/PersonnelManagementPage'
import ProxyLayout from './components/layout/ProxyLayout'
import SalesRevenuePage from './pages/proxy/SalesRevenuePage'

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
              <Route path="channels" element={<ChannelManagementPage />} />
              <Route path="proxies" element={<PersonnelManagementPage />} />
              <Route path="personnel" element={<PersonnelManagementPage />} />
              <Route path="sales" element={<SalesRecordPage />} />
              <Route path="order-processing" element={<OrderProcessingPage />} />
            </Route>

            {/* 工作人员后台（需要 staff 角色） */}
            <Route
              path="/staff"
              element={
                <ProtectedRoute requiredRoles={['staff', 'admin']}>
                  <StaffLayout />
                </ProtectedRoute>
              }
            >
              <Route path="order-processing" element={<OrderProcessingPage />} />
            </Route>

            {/* 代理商后台（需要 proxy 角色） */}
            <Route
              path="/proxy"
              element={
                <ProtectedRoute requiredRoles={['proxy', 'admin']}>
                  <ProxyLayout />
                </ProtectedRoute>
              }
            >
              <Route path="sales-revenue" element={<SalesRevenuePage />} />
            </Route>
            {/* 首页 */}
            <Route path="/" element={<LandingPage />} />
            {/* 充值 Plus 页面 */}
            <Route path="/recharge-plus" element={<RechargePlusPage />} />

            {/* 博客页面 */}
            <Route path="/blog" element={<Navigate to="/blog/index.html" replace />} />

            {/* 默认重定向 */}
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </AuthProvider>
      </SWRProvider>
    </Router>
  )
}