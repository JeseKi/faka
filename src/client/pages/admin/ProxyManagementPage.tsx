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
} from 'antd'
import {
  PlusOutlined,
  EditOutlined,
  DeleteOutlined,
  ReloadOutlined,
} from '@ant-design/icons'
import { isAxiosError } from 'axios'
import { getProxies, createProxy, updateProxy, deleteProxy } from '../../lib/proxy'
import type { UserProfile, AdminUserCreate, AdminUserUpdate } from '../../lib/types'

const { Title } = Typography

interface ProxyFormData {
  username: string
  email: string
  password: string
  name: string
  status: string
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

export default function ProxyManagementPage() {
  const { message } = App.useApp()
  const [proxies, setProxies] = useState<UserProfile[]>([])
  const [loading, setLoading] = useState(false)
  const [modalVisible, setModalVisible] = useState(false)
  const [editingProxy, setEditingProxy] = useState<UserProfile | null>(null)
  const [stats, setStats] = useState({
    total: 0,
    active: 0,
    inactive: 0,
  })

  const [form] = Form.useForm<ProxyFormData>()

  // 获取代理商列表
  const fetchProxies = useCallback(async () => {
    try {
      setLoading(true)
      const { users } = await getProxies()
      // 按照 ID 倒序排序，最新的代理商在前面
      const sortedUsers = users.sort((a, b) => b.id - a.id)
      setProxies(sortedUsers)

      // 计算统计信息
      const total = sortedUsers.length
      const active = sortedUsers.filter(proxy => proxy.status === 'active').length
      const inactive = total - active
      setStats({ total, active, inactive })
    } catch (error) {
      console.error('获取代理商列表失败:', error)
      message.error(resolveErrorMessage(error))
    } finally {
      setLoading(false)
    }
  }, [message])

  useEffect(() => {
    fetchProxies()
  }, [fetchProxies])

  // 处理表单提交
  const handleSubmit = async (values: ProxyFormData) => {
    try {
      if (editingProxy) {
        // 更新代理商
        const updateData: AdminUserUpdate = {
          email: values.email,
          name: values.name,
          status: values.status,
        }
        await updateProxy(editingProxy.id, updateData)
        message.success('代理商更新成功')
      } else {
        // 创建新代理商
        const createData: AdminUserCreate = {
          username: values.username,
          email: values.email,
          password: values.password,
          role: 'proxy',
        }
        await createProxy(createData)
        message.success('代理商创建成功')
      }

      setModalVisible(false)
      form.resetFields()
      setEditingProxy(null)
      fetchProxies()
    } catch (error) {
      console.error('保存代理商失败:', error)
      message.error(resolveErrorMessage(error))
    }
  }

  // 删除代理商
  const handleDelete = async (proxy: UserProfile) => {
    try {
      await deleteProxy(proxy.id)
      message.success('代理商删除成功')
      fetchProxies()
    } catch (error) {
      console.error('删除代理商失败:', error)
      message.error(resolveErrorMessage(error))
    }
  }

  // 打开编辑模态框
  const handleEdit = (proxy: UserProfile) => {
    setEditingProxy(proxy)
    form.setFieldsValue({
      username: proxy.username,
      email: proxy.email,
      name: proxy.name || '',
      status: proxy.status,
    })
    setModalVisible(true)
  }

  // 打开创建模态框
  const handleCreate = () => {
    setEditingProxy(null)
    form.resetFields()
    form.setFieldsValue({ status: 'active' })
    setModalVisible(true)
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
            title="确定要删除这个代理商吗？"
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
        <Title level={4}>代理商管理</Title>
      </div>

      {/* 统计信息 */}
      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col span={8}>
          <AntCard>
            <Statistic title="总代理商数" value={stats.total} />
          </AntCard>
        </Col>
        <Col span={8}>
          <AntCard>
            <Statistic title="活跃代理商" value={stats.active} />
          </AntCard>
        </Col>
        <Col span={8}>
          <AntCard>
            <Statistic title="停用代理商" value={stats.inactive} />
          </AntCard>
        </Col>
      </Row>

      {/* 操作按钮 */}
      <div style={{ marginBottom: 16 }}>
        <Space>
          <Button
            type="primary"
            icon={<PlusOutlined />}
            onClick={handleCreate}
          >
            新建代理商
          </Button>
          <Button
            icon={<ReloadOutlined />}
            onClick={fetchProxies}
            loading={loading}
          >
            刷新
          </Button>
        </Space>
      </div>

      {/* 代理商表格 */}
      <Table
        columns={columns}
        dataSource={proxies}
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
        title={editingProxy ? '编辑代理商' : '新建代理商'}
        open={modalVisible}
        onCancel={() => {
          setModalVisible(false)
          form.resetFields()
          setEditingProxy(null)
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
              disabled={!!editingProxy}
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
              disabled={!!editingProxy}
            />
          </Form.Item>

          {!editingProxy && (
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
                  setEditingProxy(null)
                }}
              >
                取消
              </Button>
              <Button type="primary" htmlType="submit">
                {editingProxy ? '更新' : '创建'}
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>
    </div>
  )
}