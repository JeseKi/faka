import { useState, useEffect, useCallback } from 'react'
import {
  Table,
  Button,
  Modal,
  Form,
  Input,
  InputNumber,
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
  Tooltip,
} from 'antd'
import {
  PlusOutlined,
  EditOutlined,
  DeleteOutlined,
  KeyOutlined,
  ReloadOutlined,
  EyeOutlined,
  CopyOutlined,
} from '@ant-design/icons'
import { isAxiosError } from 'axios'
import api from '../../lib/api'
import type { Card, CardCreate, CardUpdate } from '../../lib/types'

const { Title } = Typography
const { TextArea } = Input

interface CardFormData {
  name: string
  description: string
  price: number
  is_active: boolean
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

export default function CardManagementPage() {
  const { message } = App.useApp()
  const [cards, setCards] = useState<Card[]>([])
  const [loading, setLoading] = useState(false)
  const [modalVisible, setModalVisible] = useState(false)
  const [editingCard, setEditingCard] = useState<Card | null>(null)
  const [includeInactive, setIncludeInactive] = useState(false)
  const [stats, setStats] = useState({
    total: 0,
    active: 0,
    inactive: 0,
  })

  const [form] = Form.useForm<CardFormData>()

  // 获取充值卡列表
  const fetchCards = useCallback(async () => {
    try {
      setLoading(true)
      const { data } = await api.get<Card[]>(`/cards?include_inactive=${includeInactive}`)
      setCards(data)

      // 计算统计信息
      const total = data.length
      const active = data.filter(card => card.is_active).length
      const inactive = total - active
      setStats({ total, active, inactive })
    } catch (error) {
      console.error('获取充值卡列表失败:', error)
      message.error(resolveErrorMessage(error))
    } finally {
      setLoading(false)
    }
  }, [includeInactive])

  useEffect(() => {
    fetchCards()
  }, [fetchCards])

  

  // 处理表单提交
  const handleSubmit = async (values: CardFormData) => {
    try {
      if (editingCard) {
        // 更新充值卡
        const updateData: CardUpdate = {
          name: values.name,
          description: values.description,
          price: values.price,
          is_active: values.is_active,
        }
        await api.put(`/cards/${editingCard.id}`, updateData)
        message.success('充值卡更新成功')
      } else {
        // 创建新充值卡
        const createData: CardCreate = {
          name: values.name,
          description: values.description,
          price: values.price,
          is_active: values.is_active,
        }
        await api.post('/cards', createData)
        message.success('充值卡创建成功')
      }

      setModalVisible(false)
      form.resetFields()
      setEditingCard(null)
      fetchCards()
    } catch (error) {
      console.error('保存充值卡失败:', error)
      message.error(resolveErrorMessage(error))
    }
  }

  // 删除充值卡
  const handleDelete = async (card: Card) => {
    try {
      await api.delete(`/cards/${card.id}`)
      message.success('充值卡删除成功')
      fetchCards()
    } catch (error) {
      console.error('删除充值卡失败:', error)
      message.error(resolveErrorMessage(error))
    }
  }

  // 打开编辑模态框
  const handleEdit = (card: Card) => {
    setEditingCard(card)
    form.setFieldsValue({
      name: card.name,
      description: card.description,
      price: card.price,
      is_active: card.is_active,
    })
    setModalVisible(true)
  }

  // 打开创建模态框
  const handleCreate = () => {
    setEditingCard(null)
    form.resetFields()
    form.setFieldsValue({ is_active: true })
    setModalVisible(true)
  }

  // 生成卡密
  const handleGenerateCodes = async (cardName: string) => {
    try {
      await api.post(`/cards/${cardName}/generate-codes`, { count: 10 })
      message.success('卡密生成成功')
    } catch (error) {
      console.error('生成卡密失败:', error)
      message.error(resolveErrorMessage(error))
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
      title: '卡名',
      dataIndex: 'name',
      key: 'name',
      width: 150,
    },
    {
      title: '描述',
      dataIndex: 'description',
      key: 'description',
      ellipsis: true,
    },
    {
      title: '价格',
      dataIndex: 'price',
      key: 'price',
      width: 100,
      render: (price: number) => `¥${price}`,
    },
    {
      title: '状态',
      dataIndex: 'is_active',
      key: 'is_active',
      width: 100,
      render: (isActive: boolean) => (
        <Tag color={isActive ? 'green' : 'red'}>
          {isActive ? '活跃' : '停用'}
        </Tag>
      ),
    },
    {
      title: '操作',
      key: 'action',
      width: 200,
      render: (_: unknown, record: Card) => (
        <Space size="small">
          <Button
            type="link"
            size="small"
            icon={<EditOutlined />}
            onClick={() => handleEdit(record)}
          >
            编辑
          </Button>
          <Button
            type="link"
            size="small"
            icon={<KeyOutlined />}
            onClick={() => handleGenerateCodes(record.name)}
          >
            生成卡密
          </Button>
          <Popconfirm
            title="确定要删除这个充值卡吗？"
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
        <Title level={4}>充值卡管理</Title>
      </div>

      {/* 统计信息 */}
      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col span={8}>
          <AntCard>
            <Statistic title="总卡种数" value={stats.total} />
          </AntCard>
        </Col>
        <Col span={8}>
          <AntCard>
            <Statistic title="活跃卡种" value={stats.active} />
          </AntCard>
        </Col>
        <Col span={8}>
          <AntCard>
            <Statistic title="停用卡种" value={stats.inactive} />
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
            新建充值卡
          </Button>
          <Button
            icon={<ReloadOutlined />}
            onClick={fetchCards}
            loading={loading}
          >
            刷新
          </Button>
          <Switch
            checked={includeInactive}
            onChange={setIncludeInactive}
            checkedChildren="显示停用"
            unCheckedChildren="仅活跃"
          />
        </Space>
      </div>

      {/* 充值卡表格 */}
      <Table
        columns={columns}
        dataSource={cards}
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
        title={editingCard ? '编辑充值卡' : '新建充值卡'}
        open={modalVisible}
        onCancel={() => {
          setModalVisible(false)
          form.resetFields()
          setEditingCard(null)
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
            label="卡名"
            name="name"
            rules={[
              { required: true, message: '请输入卡名' },
              { max: 100, message: '卡名不能超过100个字符' },
            ]}
          >
            <Input placeholder="请输入充值卡名称" />
          </Form.Item>

          <Form.Item
            label="描述"
            name="description"
            rules={[
              { required: true, message: '请输入描述' },
              { max: 500, message: '描述不能超过500个字符' },
            ]}
          >
            <TextArea
              placeholder="请输入充值卡描述"
              rows={3}
            />
          </Form.Item>

          <Form.Item
            label="价格"
            name="price"
            rules={[
              { required: true, message: '请输入价格' },
              { type: 'number', min: 0, message: '价格必须大于等于0' },
            ]}
          >
            <InputNumber
              placeholder="请输入价格"
              min={0}
              step={0.01}
              precision={2}
              style={{ width: '100%' }}
              prefix="¥"
            />
          </Form.Item>

          <Form.Item
            label="是否激活"
            name="is_active"
            valuePropName="checked"
          >
            <Switch checkedChildren="激活" unCheckedChildren="停用" />
          </Form.Item>

          <Form.Item style={{ marginBottom: 0, textAlign: 'right' }}>
            <Space>
              <Button
                onClick={() => {
                  setModalVisible(false)
                  form.resetFields()
                  setEditingCard(null)
                }}
              >
                取消
              </Button>
              <Button type="primary" htmlType="submit">
                {editingCard ? '更新' : '创建'}
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>
    </div>
  )
}