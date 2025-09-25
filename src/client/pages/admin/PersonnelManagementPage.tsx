import { useState, useEffect, useCallback } from 'react'
import {
  Table,
  Button,
  Modal,
  Form,
  Input,
  Switch,
  Space,
  Typography,
  App,
  Popconfirm,
  Tag,
  Card as AntCard,
  Row,
  Col,
  Statistic,
  Select,
} from 'antd'
import {
  PlusOutlined,
  EditOutlined,
  DeleteOutlined,
  ReloadOutlined,
} from '@ant-design/icons'
import { isAxiosError } from 'axios'
import { getUsers, createUser, updateUser, deleteUser } from '../../lib/user'
import { getChannels } from '../../lib/channel'
import type { UserProfile, AdminUserCreate, AdminUserUpdate, Role, Channel } from '../../lib/types'

const { Title } = Typography
const { Option } = Select

interface PersonnelFormData {
  username: string
  email: string
  password: string
  name: string
  role: Role
  status: string
  channel_id: number | null
}

function resolveErrorMessage(error: unknown): string {
  if (isAxiosError(error)) {
    const payload = error.response?.data as { detail?: string; message?: string } | undefined
    return payload?.detail ?? payload?.message ?? '操作失败，请稍后重试。'
  }
  if (error instanceof Error) {
    return error.message
  }
  return '操作失败，请稍后重试。'
}

export default function PersonnelManagementPage() {
  const { message } = App.useApp()
  const [users, setUsers] = useState<UserProfile[]>([])
  const [channels, setChannels] = useState<Channel[]>([])
  const [loading, setLoading] = useState(false)
  const [modalVisible, setModalVisible] = useState(false)
  const [editingUser, setEditingUser] = useState<UserProfile | null>(null)
  const [selectedRole, setSelectedRole] = useState<Role | undefined>(undefined)
  const [stats, setStats] = useState({
    total: 0,
    admin: 0,
    staff: 0,
    proxy: 0,
    user: 0,
  })

  const [form] = Form.useForm<PersonnelFormData>()
  const role = Form.useWatch('role', form)

  // 获取用户列表
  const fetchUsers = useCallback(async () => {
    try {
      setLoading(true)
      const { users } = await getUsers(selectedRole)
      // 按照 ID 倒序排序，最新的用户在前面
      const sortedUsers = users.sort((a, b) => b.id - a.id)
      setUsers(sortedUsers)

      // 计算统计信息
      const total = sortedUsers.length
      const admin = sortedUsers.filter(user => user.role === 'admin').length
      const staff = sortedUsers.filter(user => user.role === 'staff').length
      const proxy = sortedUsers.filter(user => user.role === 'proxy').length
      const user = sortedUsers.filter(user => user.role === 'user').length
      setStats({ total, admin, staff, proxy, user })
    } catch (error) {
      console.error('获取用户列表失败:', error)
      message.error(resolveErrorMessage(error))
    } finally {
      setLoading(false)
    }
  }, [message, selectedRole])

  // 获取渠道列表
  const fetchChannels = useCallback(async () => {
    try {
      const channelsData = await getChannels()
      setChannels(channelsData)
    } catch (error) {
      console.error('获取渠道列表失败:', error)
      message.error('获取渠道列表失败，请稍后重试')
    }
  }, [message])

  useEffect(() => {
    fetchUsers()
    fetchChannels()
  }, [fetchUsers, fetchChannels])

  // 处理表单提交
  const handleSubmit = async (values: PersonnelFormData) => {
    try {
      if (editingUser) {
        // 更新用户
        const updateData: AdminUserUpdate = {
          email: values.email,
          name: values.name,
          role: values.role,
          status: values.status,
          channel_id: values.role === 'staff' ? values.channel_id : null,
        }
        await updateUser(editingUser.id, updateData)
        message.success('用户更新成功')
      } else {
        // 创建新用户
        const createData: AdminUserCreate = {
          username: values.username,
          name: values.name,
          email: values.email,
          password: values.password,
          role: values.role,
          channel_id: values.role === 'staff' ? values.channel_id : null,
        }
        await createUser(createData)
        message.success('用户创建成功')
      }

      setModalVisible(false)
      form.resetFields()
      setEditingUser(null)
      fetchUsers()
    } catch (error) {
      console.error('保存用户失败:', error)
      message.error(resolveErrorMessage(error))
    }
  }

  // 删除用户
  const handleDelete = async (user: UserProfile) => {
    try {
      await deleteUser(user.id)
      message.success('用户删除成功')
      fetchUsers()
    } catch (error) {
      console.error('删除用户失败:', error)
      message.error(resolveErrorMessage(error))
    }
  }

  // 打开编辑模态框
  const handleEdit = (user: UserProfile) => {
    setEditingUser(user)
    form.setFieldsValue({
      username: user.username,
      email: user.email,
      name: user.name || '',
      role: user.role as Role,
      status: user.status,
      channel_id: user.channel_id || null,
    })
    setModalVisible(true)
  }

  // 打开创建模态框
  const handleCreate = () => {
    setEditingUser(null)
    form.resetFields()
    form.setFieldsValue({ status: 'active', role: 'user', channel_id: null })
    setModalVisible(true)
  }

  // 角色筛选器变化处理
  const handleRoleFilterChange = (role: Role | undefined) => {
    setSelectedRole(role)
  }

  const getRoleTagColor = (role: string) => {
    switch (role) {
      case 'admin':
        return 'red'
      case 'staff':
        return 'blue'
      case 'proxy':
        return 'green'
      case 'user':
        return 'default'
      default:
        return 'default'
    }
  }

  const getRoleText = (role: string) => {
    switch (role) {
      case 'admin':
        return '管理员'
      case 'staff':
        return '工作人员'
      case 'proxy':
        return '代理商'
      case 'user':
        return '用户'
      default:
        return role
    }
  }

  const columns = [
    {
      title: 'ID',
      dataIndex: 'id',
      key: 'id',
      width: 80,
    },
    {
      title: '用户名',
      dataIndex: 'username',
      key: 'username',
      width: 150,
    },
    {
      title: '邮箱',
      dataIndex: 'email',
      key: 'email',
      width: 200,
    },
    {
      title: '姓名',
      dataIndex: 'name',
      key: 'name',
      width: 150,
      render: (name: string | null) => name || '-',
    },
    {
      title: '角色',
      dataIndex: 'role',
      key: 'role',
      width: 120,
      render: (role: string) => (
        <Tag color={getRoleTagColor(role)}>
          {getRoleText(role)}
        </Tag>
      ),
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      width: 100,
      render: (status: string) => (
        <Tag color={status === 'active' ? 'green' : 'red'}>
          {status === 'active' ? '活跃' : '停用'}
        </Tag>
      ),
    },
    {
      title: '渠道',
      dataIndex: 'channel_id',
      key: 'channel_id',
      width: 120,
      render: (channelId: number | null) => {
        if (!channelId) return '-'
        const channel = channels.find(c => c.id === channelId)
        return channel ? channel.name : `ID: ${channelId}`
      },
    },
    {
      title: '操作',
      key: 'action',
      width: 200,
      render: (_: unknown, record: UserProfile) => (
        <Space size="small">
          <Button
            type="link"
            size="small"
            icon={<EditOutlined />}
            onClick={() => handleEdit(record)}
          >
            编辑
          </Button>
          <Popconfirm
            title="确定要删除这个用户吗？"
            description="删除后无法恢复，请谨慎操作。"
            onConfirm={() => handleDelete(record)}
            okText="确定"
            cancelText="取消"
          >
            <Button
              type="link"
              size="small"
              danger
              icon={<DeleteOutlined />}
            >
              删除
            </Button>
          </Popconfirm>
        </Space>
      ),
    },
  ]

  return (
    <div>
      <div style={{ marginBottom: 24 }}>
        <Title level={4}>人员管理</Title>
      </div>

      {/* 统计信息 */}
      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col span={4}>
          <AntCard>
            <Statistic title="总用户数" value={stats.total} />
          </AntCard>
        </Col>
        <Col span={4}>
          <AntCard>
            <Statistic title="管理员" value={stats.admin} />
          </AntCard>
        </Col>
        <Col span={4}>
          <AntCard>
            <Statistic title="工作人员" value={stats.staff} />
          </AntCard>
        </Col>
        <Col span={4}>
          <AntCard>
            <Statistic title="代理商" value={stats.proxy} />
          </AntCard>
        </Col>
        <Col span={4}>
          <AntCard>
            <Statistic title="普通用户" value={stats.user} />
          </AntCard>
        </Col>
      </Row>

      {/* 筛选和操作按钮 */}
      <div style={{ marginBottom: 16 }}>
        <Space>
          <Select
            placeholder="按角色筛选"
            allowClear
            style={{ width: 150 }}
            value={selectedRole}
            onChange={handleRoleFilterChange}
          >
            <Option value="admin">管理员</Option>
            <Option value="staff">工作人员</Option>
            <Option value="proxy">代理商</Option>
            <Option value="user">普通用户</Option>
          </Select>
          <Button
            type="primary"
            icon={<PlusOutlined />}
            onClick={handleCreate}
          >
            新建用户
          </Button>
          <Button
            icon={<ReloadOutlined />}
            onClick={fetchUsers}
            loading={loading}
          >
            刷新
          </Button>
        </Space>
      </div>

      {/* 用户表格 */}
      <Table
        columns={columns}
        dataSource={users}
        rowKey="id"
        loading={loading}
        pagination={{
          showSizeChanger: true,
          showQuickJumper: true,
          showTotal: (total, range) => `第 ${range[0]}-${range[1]} 条，共 ${total} 条`,
        }}
      />

      {/* 新建/编辑模态框 */}
      <Modal
        title={editingUser ? '编辑用户' : '新建用户'}
        open={modalVisible}
        onCancel={() => {
          setModalVisible(false)
          form.resetFields()
          setEditingUser(null)
        }}
        footer={null}
        width={600}
      >
        <Form
          form={form}
          layout="vertical"
          onFinish={handleSubmit}
          autoComplete="off"
        >
          <Form.Item
            label="用户名"
            name="username"
            rules={[
              { required: true, message: '请输入用户名' },
              { min: 3, message: '用户名至少3个字符' },
              { max: 50, message: '用户名不能超过50个字符' },
            ]}
          >
            <Input
              placeholder="请输入用户名"
              disabled={!!editingUser}
            />
          </Form.Item>

          <Form.Item
            label="邮箱"
            name="email"
            rules={[
              { required: true, message: '请输入邮箱' },
              { type: 'email', message: '请输入有效的邮箱地址' },
            ]}
          >
            <Input
              placeholder="请输入邮箱地址"
              disabled={!!editingUser}
            />
          </Form.Item>

          {!editingUser && (
            <Form.Item
              label="密码"
              name="password"
              rules={[
                { required: true, message: '请输入密码' },
                { min: 8, message: '密码至少8个字符' },
              ]}
            >
              <Input.Password placeholder="请输入密码" />
            </Form.Item>
          )}

          <Form.Item
            label="姓名"
            name="name"
            rules={[
              { max: 100, message: '姓名不能超过100个字符' },
            ]}
          >
            <Input placeholder="请输入姓名（可选）" />
          </Form.Item>

          <Form.Item
            label="角色"
            name="role"
            rules={[
              { required: true, message: '请选择用户角色' },
            ]}
          >
            <Select placeholder="请选择用户角色">
              <Option value="admin">管理员</Option>
              <Option value="staff">工作人员</Option>
              <Option value="proxy">代理商</Option>
              <Option value="user">普通用户</Option>
            </Select>
          </Form.Item>

          <Form.Item
            label="渠道"
            name="channel_id"
            rules={[
              { required: false, message: '请选择关联渠道' },
            ]}
          >
            <Select
              placeholder="请选择关联渠道"
              allowClear
              disabled={role !== 'staff'}
            >
              {channels.map((channel) => (
                <Option key={channel.id} value={channel.id}>
                  {channel.name}
                </Option>
              ))}
            </Select>
          </Form.Item>

          <Form.Item
            label="状态"
            name="status"
            valuePropName="checked"
          >
            <Switch checkedChildren="活跃" unCheckedChildren="停用" />
          </Form.Item>

          <Form.Item style={{ marginBottom: 0, textAlign: 'right' }}>
            <Space>
              <Button
                onClick={() => {
                  setModalVisible(false)
                  form.resetFields()
                  setEditingUser(null)
                }}
              >
                取消
              </Button>
              <Button type="primary" htmlType="submit">
                {editingUser ? '更新' : '创建'}
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>
    </div>
  )
}