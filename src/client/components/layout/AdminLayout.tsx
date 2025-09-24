import { useMemo } from 'react'
import {
  Avatar,
  Dropdown,
  Flex,
  Layout,
  Menu,
  type MenuProps,
  Typography,
  theme,
} from 'antd'
import {
  LogoutOutlined,
  UserOutlined,
  DashboardOutlined,
  CreditCardOutlined,
  KeyOutlined,
  ShoppingCartOutlined,
  ApiOutlined,
  TeamOutlined,
} from '@ant-design/icons'
import { Link, Outlet, useLocation, useNavigate } from 'react-router-dom'
import { useAuth } from '../../hooks/useAuth'

const { Header, Sider, Content } = Layout

export default function AdminLayout() {
  const navigate = useNavigate()
  const location = useLocation()
  const { token } = theme.useToken()
  const { user, logout } = useAuth()

  const selectedKeys = useMemo(() => {
    const path = location.pathname
    if (path.startsWith('/admin/cards')) return ['cards']
    if (path.startsWith('/admin/codes')) return ['codes']
    if (path.startsWith('/admin/channels')) return ['channels']
    if (path.startsWith('/admin/sales')) return ['sales']
    if (path.startsWith('/admin/personnel')) return ['personnel']
    if (path.startsWith('/admin/order-processing')) return ['orders']
    return ['dashboard']
  }, [location.pathname])

  const navItems = useMemo<MenuProps['items']>(() => {
    const isAdmin = user?.role === 'admin'

    const items: MenuProps['items'] = []

    if (isAdmin) {
      items.push(
        {
          key: 'dashboard',
          icon: <DashboardOutlined />,
          label: <Link to="/admin">管理员首页</Link>,
        },
        {
          key: 'cards',
          icon: <CreditCardOutlined />,
          label: <Link to="/admin/cards">充值卡管理</Link>,
        },
        {
          key: 'codes',
          icon: <KeyOutlined />,
          label: <Link to="/admin/codes">卡密管理</Link>,
        },
        {
          key: 'channels',
          icon: <ApiOutlined />,
          label: <Link to="/admin/channels">渠道管理</Link>,
        },
        {
          key: 'personnel',
          icon: <TeamOutlined />,
          label: <Link to="/admin/personnel">人员管理</Link>,
        },
        {
          key: 'sales',
          icon: <ShoppingCartOutlined />,
          label: <Link to="/admin/sales">销售记录</Link>,
        },
        {
          key: 'orders',
          icon: <ShoppingCartOutlined />,
          label: <Link to="/admin/order-processing">订单处理</Link>,
        },
      )
    }

    return items
  }, [user?.role])

  const handleLogout = () => {
    logout()
    navigate('/login', { replace: true })
  }

  const userMenu = useMemo<MenuProps['items']>(
    () => [
      {
        key: 'profile',
        label: (
          <Flex vertical gap={2} style={{ minWidth: 180 }}>
            <Typography.Text type="secondary">当前用户</Typography.Text>
            <Typography.Text strong>{user?.username ?? '未登录'}</Typography.Text>
            <Typography.Text type="secondary" style={{ fontSize: '12px' }}>
              角色: {user?.role === 'admin' ? '管理员' : user?.role === 'staff' ? '工作人员' : '未知'}
            </Typography.Text>
          </Flex>
        ),
        disabled: true,
      },
      { type: 'divider' },
      {
        key: 'logout',
        icon: <LogoutOutlined />,
        label: '退出登录',
      },
    ],
    [user?.username, user?.role],
  )

  const handleUserMenuClick: MenuProps['onClick'] = ({ key }) => {
    if (key === 'logout') {
      handleLogout()
    }
  }

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Sider
        style={{
          background: token.colorBgElevated,
          borderRight: `1px solid ${token.colorBorderSecondary}`,
        }}
        width={240}
      >
        <div
          style={{
            padding: '16px',
            borderBottom: `1px solid ${token.colorBorderSecondary}`,
          }}
        >
          <Typography.Title level={4} style={{ margin: 0, color: token.colorText }}>
            发卡站管理系统
          </Typography.Title>
        </div>
        <Menu
          mode="inline"
          selectedKeys={selectedKeys}
          items={navItems}
          style={{
            borderRight: 'none',
            background: 'transparent',
          }}
        />
      </Sider>
      <Layout>
        <Header
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            paddingInline: 24,
            background: token.colorBgElevated,
            boxShadow: '0 2px 12px rgba(15, 23, 42, 0.06)',
          }}
        >
          <Typography.Title level={5} style={{ margin: 0, color: token.colorText }}>
            {user?.role === 'admin' ? '管理员后台' : '工作人员后台'}
          </Typography.Title>
          <Dropdown
            menu={{ items: userMenu, onClick: handleUserMenuClick }}
            placement="bottomRight"
            arrow
            trigger={["hover"]}
            getPopupContainer={() => document.body}
            overlayStyle={{ zIndex: 1000 }}
          >
            <Avatar
              size="large"
              icon={<UserOutlined />}
              style={{ background: token.colorPrimary, cursor: 'pointer' }}
            />
          </Dropdown>
        </Header>
        <Content style={{ padding: '24px', background: token.colorBgLayout }}>
          <div
            style={{
              margin: '0 auto',
              maxWidth: 1200,
              width: '100%',
            }}
          >
            <Outlet />
          </div>
        </Content>
      </Layout>
    </Layout>
  )
}