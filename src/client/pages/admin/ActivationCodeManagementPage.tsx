import { useState, useEffect, useCallback } from 'react'
import {
  Table,
  Button,
  Modal,
  Form,
  InputNumber,
  Select,
  Space,
  Typography,
  message,
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
  DeleteOutlined,
  ReloadOutlined,
  SearchOutlined,
  EyeOutlined,
  CopyOutlined,
} from '@ant-design/icons'
import { isAxiosError } from 'axios'
import api from '../../lib/api'
import type { ActivationCode, Card } from '../../lib/types'

const { Title } = Typography
const { Option } = Select

interface CodeFormData {
  card_name: string
  count: number
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

export default function ActivationCodeManagementPage() {
  const [codes, setCodes] = useState<ActivationCode[]>([])
  const [cards, setCards] = useState<Card[]>([])
  const [loading, setLoading] = useState(false)
  const [modalVisible, setModalVisible] = useState(false)
  const [searchCard, setSearchCard] = useState<string>('')
  const [includeUsed, setIncludeUsed] = useState(false)
  const [stats, setStats] = useState({
    total: 0,
    used: 0,
    unused: 0,
  })

  const [form] = Form.useForm<CodeFormData>()

  // 获取充值卡列表
  const fetchCards = useCallback(async () => {
    try {
      const { data } = await api.get<Card[]>('/cards?include_inactive=false')
      setCards(data)
    } catch (error) {
      console.error('获取充值卡列表失败:', error)
    }
  }, [])

  // 获取卡密列表
  const fetchCodes = useCallback(async (cardName?: string) => {
    if (!cardName && !searchCard) return

    const targetCard = cardName || searchCard
    if (!targetCard) return

    try {
      setLoading(true)
      const { data } = await api.get<ActivationCode[]>(`/activation-codes/${targetCard}?include_used=${includeUsed}`)
      setCodes(data)

      // 计算统计信息
      const total = data.length
      const used = data.filter(code => code.status !== 'available').length
      const unused = total - used
      setStats({ total, used, unused })
    } catch (error) {
      console.error('获取卡密列表失败:', error)
      message.error(resolveErrorMessage(error))
      setCodes([])
      setStats({ total: 0, used: 0, unused: 0 })
    } finally {
      setLoading(false)
    }
  }, [searchCard, includeUsed])

  useEffect(() => {
    fetchCards()
  }, [fetchCards])

  useEffect(() => {
    if (searchCard) {
      fetchCodes()
    }
  }, [includeUsed, searchCard, fetchCodes])

  // 处理表单提交
  const handleSubmit = async (values: CodeFormData) => {
    try {
      await api.post('/activation-codes/generate', values)
      message.success(`成功生成 ${values.count} 个卡密`)
      setModalVisible(false)
      form.resetFields()
      fetchCodes(values.card_name)
    } catch (error) {
      console.error('生成卡密失败:', error)
      message.error(resolveErrorMessage(error))
    }
  }

  // 删除所有卡密
  const handleDeleteAll = async (cardName: string) => {
    try {
      await api.delete(`/activation-codes/${cardName}`)
      message.success('所有卡密删除成功')
      setCodes([])
      setStats({ total: 0, used: 0, unused: 0 })
    } catch (error) {
      console.error('删除卡密失败:', error)
      message.error(resolveErrorMessage(error))
    }
  }

  // 打开生成模态框
  const handleGenerate = () => {
    form.resetFields()
    setModalVisible(true)
  }

  // 搜索卡密
  const handleSearch = () => {
    if (searchCard) {
      fetchCodes()
    } else {
      message.warning('请选择要查看的充值卡')
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
      dataIndex: 'card_name',
      key: 'card_name',
      width: 150,
    },
    {
      title: '卡密',
      dataIndex: 'code',
      key: 'code',
      width: 200,
      render: (code: string) => {
        const maskedCode = code
          ? code.replace(/./g, '*').slice(0, 8) + '...'
          : '-'
        return (
          <Space size="middle">
            <span>{maskedCode}</span>
            <Tooltip title={code || '-'} placement="topLeft">
              <Button
                type="text"
                icon={<EyeOutlined />}
                size="small"
                style={{ padding: 0 }}
              />
            </Tooltip>
            <Button
              type="text"
              icon={<CopyOutlined />}
              size="small"
              onClick={() => {
                navigator.clipboard.writeText(code || '')
                message.success('卡密已复制到剪贴板')
              }}
            />
          </Space>
        )
      },
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      width: 100,
      render: (status: 'available' | 'consuming' | 'consumed') => {
        let color = 'green'
        let text = '未使用'
        if (status === 'consuming') {
          color = 'orange'
          text = '消费中'
        } else if (status === 'consumed') {
          color = 'red'
          text = '已消费'
        }
        return <Tag color={color}>{text}</Tag>
      },
    },
    {
      title: '创建时间',
      dataIndex: 'created_at',
      key: 'created_at',
      width: 180,
      render: (date: string) => new Date(date).toLocaleString('zh-CN'),
    },
    {
      title: '使用时间',
      dataIndex: 'used_at',
      key: 'used_at',
      width: 180,
      render: (date: string | null) => date ? new Date(date).toLocaleString('zh-CN') : '-',
    },
  ]

  return (
    <div>
      <div style={{ marginBottom: 24 }}>
        <Title level={4}>卡密管理</Title>
      </div>

      {/* 统计信息 */}
      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col span={8}>
          <AntCard>
            <Statistic title="总卡密数" value={stats.total} />
          </AntCard>
        </Col>
        <Col span={8}>
          <AntCard>
            <Statistic title="已使用" value={stats.used} />
          </AntCard>
        </Col>
        <Col span={8}>
          <AntCard>
            <Statistic title="未使用" value={stats.unused} />
          </AntCard>
        </Col>
      </Row>

      {/* 操作按钮 */}
      <div style={{ marginBottom: 16 }}>
        <Space>
          <Button
            type="primary"
            icon={<PlusOutlined />}
            onClick={handleGenerate}
          >
            批量生成卡密
          </Button>
          <Select
            placeholder="选择充值卡"
            style={{ width: 200 }}
            value={searchCard}
            onChange={setSearchCard}
          >
            {cards.map((card) => (
              <Option key={card.name} value={card.name}>
                {card.name} - ¥{card.price}
              </Option>
            ))}
          </Select>
          <Button
            icon={<SearchOutlined />}
            onClick={handleSearch}
            type="primary"
          >
            查看卡密
          </Button>
          <Button
            icon={<ReloadOutlined />}
            onClick={() => fetchCodes()}
            loading={loading}
          >
            刷新
          </Button>
          <Button
            onClick={() => setIncludeUsed(!includeUsed)}
            type={includeUsed ? 'primary' : 'default'}
          >
            {includeUsed ? '显示全部' : '仅未使用'}
          </Button>
          {searchCard && (
            <Popconfirm
              title={`确定要删除 ${searchCard} 的所有卡密吗？`}
              description="此操作不可恢复，请谨慎操作。"
              onConfirm={() => handleDeleteAll(searchCard)}
              okText="确定"
              cancelText="取消"
            >
              <Button danger icon={<DeleteOutlined />}>
                删除所有卡密
              </Button>
            </Popconfirm>
          )}
        </Space>
      </div>

      {/* 卡密表格 */}
      <Table
        columns={columns}
        dataSource={codes}
        rowKey="id"
        loading={loading}
        pagination={{
          showSizeChanger: true,
          showQuickJumper: true,
          showTotal: (total, range) => `第 ${range[0]}-${range[1]} 条，共 ${total} 条`,
        }}
        locale={{
          emptyText: searchCard ? '该充值卡暂无卡密' : '请选择充值卡查看卡密',
        }}
      />

      {/* 生成卡密模态框 */}
      <Modal
        title="批量生成卡密"
        open={modalVisible}
        onCancel={() => {
          setModalVisible(false)
          form.resetFields()
        }}
        footer={null}
        width={500}
      >
        <Form
          form={form}
          layout="vertical"
          onFinish={handleSubmit}
          autoComplete="off"
        >
          <Form.Item
            label="选择充值卡"
            name="card_name"
            rules={[{ required: true, message: '请选择充值卡' }]}
          >
            <Select placeholder="请选择要生成卡密的充值卡">
              {cards.map((card) => (
                <Option key={card.name} value={card.name}>
                  {card.name} - ¥{card.price}
                </Option>
              ))}
            </Select>
          </Form.Item>

          <Form.Item
            label="生成数量"
            name="count"
            rules={[
              { required: true, message: '请输入生成数量' },
              { type: 'number', min: 1, max: 1000, message: '数量必须在1-1000之间' },
            ]}
          >
            <InputNumber
              placeholder="请输入要生成的卡密数量"
              min={1}
              max={1000}
              style={{ width: '100%' }}
            />
          </Form.Item>

          <Form.Item style={{ marginBottom: 0, textAlign: 'right' }}>
            <Space>
              <Button
                onClick={() => {
                  setModalVisible(false)
                  form.resetFields()
                }}
              >
                取消
              </Button>
              <Button type="primary" htmlType="submit">
                生成
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>
    </div>
  )
}