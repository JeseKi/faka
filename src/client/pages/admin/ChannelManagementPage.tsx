import { useState, useEffect, useCallback } from 'react'
import {
  Table,
  Button,
  Modal,
  Form,
  Input,
  Space,
  Typography,
  App,
  Popconfirm,
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
import { createChannel, getChannels, updateChannel, deleteChannel } from '../../lib/channel'
import type { Channel, ChannelCreate, ChannelUpdate } from '../../lib/types'

const { Title } = Typography
const { TextArea } = Input

interface ChannelFormData {
  name: string
  description: string | null
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

export default function ChannelManagementPage() {
  const { message } = App.useApp()
  const [channels, setChannels] = useState<Channel[]>([])
  const [loading, setLoading] = useState(false)
  const [modalVisible, setModalVisible] = useState(false)
  const [editingChannel, setEditingChannel] = useState<Channel | null>(null)
  const [stats, setStats] = useState({
    total: 0,
  })

  const [form] = Form.useForm<ChannelFormData>()

  // 获取渠道列表
  const fetchChannels = useCallback(async () => {
    try {
      setLoading(true)
      const data = await getChannels(0, 100)
      setChannels(data)

      // 计算统计信息
      const total = data.length
      setStats({ total })
    } catch (error) {
      console.error('获取渠道列表失败:', error)
      message.error(resolveErrorMessage(error))
    } finally {
      setLoading(false)
    }
  }, [message])

  useEffect(() => {
    fetchChannels()
  }, [fetchChannels])

  // 处理表单提交
  const handleSubmit = async (values: ChannelFormData) => {
    try {
      if (editingChannel) {
        // 更新渠道
        const updateData: ChannelUpdate = {
          name: values.name,
          description: values.description,
        }
        await updateChannel(editingChannel.id, updateData)
        message.success('渠道更新成功')
      } else {
        // 创建新渠道
        const createData: ChannelCreate = {
          name: values.name,
          description: values.description,
        }
        await createChannel(createData)
        message.success('渠道创建成功')
      }

      setModalVisible(false)
      form.resetFields()
      setEditingChannel(null)
      fetchChannels()
    } catch (error) {
      console.error('保存渠道失败:', error)
      message.error(resolveErrorMessage(error))
    }
  }

  // 删除渠道
  const handleDelete = async (channel: Channel) => {
    try {
      await deleteChannel(channel.id)
      message.success('渠道删除成功')
      fetchChannels()
    } catch (error) {
      console.error('删除渠道失败:', error)
      message.error(resolveErrorMessage(error))
    }
  }

  // 打开编辑模态框
  const handleEdit = (channel: Channel) => {
    setEditingChannel(channel)
    form.setFieldsValue({
      name: channel.name,
      description: channel.description,
    })
    setModalVisible(true)
  }

  // 打开创建模态框
  const handleCreate = () => {
    setEditingChannel(null)
    form.resetFields()
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
      title: '渠道名称',
      dataIndex: 'name',
      key: 'name',
      width: 150,
    },
    {
      title: '描述',
      dataIndex: 'description',
      key: 'description',
      ellipsis: true,
      render: (description: string | null) => description || '-',
    },
    {
      title: '操作',
      key: 'action',
      width: 200,
      render: (_: unknown, record: Channel) => (
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
            title="确定要删除这个渠道吗？"
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
        <Title level={4}>渠道管理</Title>
      </div>

      {/* 统计信息 */}
      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col span={24}>
          <AntCard>
            <Statistic title="总渠道数" value={stats.total} />
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
            新建渠道
          </Button>
          <Button
            icon={<ReloadOutlined />}
            onClick={fetchChannels}
            loading={loading}
          >
            刷新
          </Button>
        </Space>
      </div>

      {/* 渠道表格 */}
      <Table
        columns={columns}
        dataSource={channels}
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
        title={editingChannel ? '编辑渠道' : '新建渠道'}
        open={modalVisible}
        onCancel={() => {
          setModalVisible(false)
          form.resetFields()
          setEditingChannel(null)
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
            label="渠道名称"
            name="name"
            rules={[
              { required: true, message: '请输入渠道名称' },
              { max: 100, message: '渠道名称不能超过100个字符' },
            ]}
          >
            <Input placeholder="请输入渠道名称" />
          </Form.Item>

          <Form.Item
            label="描述"
            name="description"
            rules={[
              { max: 500, message: '描述不能超过500个字符' },
            ]}
          >
            <TextArea
              placeholder="请输入渠道描述（可选）"
              rows={3}
            />
          </Form.Item>

          <Form.Item style={{ marginBottom: 0, textAlign: 'right' }}>
            <Space>
              <Button
                onClick={() => {
                  setModalVisible(false)
                  form.resetFields()
                  setEditingChannel(null)
                }}
              >
                取消
              </Button>
              <Button type="primary" htmlType="submit">
                {editingChannel ? '更新' : '创建'}
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>
    </div>
  )
}