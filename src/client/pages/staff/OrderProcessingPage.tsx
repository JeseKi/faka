import { useState, useEffect, useCallback } from 'react'
import {
  Table,
  Button,
  Modal,
  Space,
  Typography,
  message,
  Tag,
  Card as AntCard,
  Row,
  Col,
  Statistic,
  Select,
  Tooltip,
} from 'antd'
import {
  CheckCircleOutlined,
  EyeOutlined,
  ReloadOutlined,
  CopyOutlined,
} from '@ant-design/icons'
import { isAxiosError } from 'axios'
import api from '../../lib/api'
import type { Order } from '../../lib/types'

const { Title, Text, Paragraph } = Typography
const { Option } = Select

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

export default function OrderProcessingPage() {
  const [orders, setOrders] = useState<Order[]>([])
  const [loading, setLoading] = useState(false)
  const [detailModalVisible, setDetailModalVisible] = useState(false)
  const [selectedOrder, setSelectedOrder] = useState<Order | null>(null)
  const [statusFilter, setStatusFilter] = useState<string>('')
  const [stats, setStats] = useState({
    total: 0,
    pending: 0,
    processing: 0,
    completed: 0,
  })

  // 获取订单列表
  const fetchOrders = useCallback(async () => {
    try {
      setLoading(true)
      const params = new URLSearchParams()
      if (statusFilter) {
        params.append('status_filter', statusFilter)
      }
      params.append('limit', '100')
      params.append('offset', '0')

      const { data } = await api.get<Order[]>(`/orders?${params.toString()}`)
      setOrders(data)

      // 计算统计信息
      const total = data.length
      const pending = data.filter(order => order.status === 'pending').length
      const processing = data.filter(order => order.status === 'processing').length
      const completed = data.filter(order => order.status === 'completed').length
      setStats({ total, pending, processing, completed })
    } catch (error) {
      console.error('获取订单列表失败:', error)
      message.error(resolveErrorMessage(error))
    } finally {
      setLoading(false)
    }
  }, [statusFilter])

  useEffect(() => {
    fetchOrders()
  }, [fetchOrders])

  // 完成订单
  const handleCompleteOrder = async (orderId: number) => {
    try {
      await api.put(`/orders/${orderId}/complete`)
      message.success('订单完成成功')
      fetchOrders()
    } catch (error) {
      console.error('完成订单失败:', error)
      message.error(resolveErrorMessage(error))
    }
  }

  // 查看订单详情
  const handleViewDetail = (order: Order) => {
    setSelectedOrder(order)
    setDetailModalVisible(true)
  }

  // 获取待处理订单
  const fetchPendingOrders = useCallback(async () => {
    try {
      const { data } = await api.get<Order[]>('/orders/pending')
      setOrders(data)
      setStats({
        total: data.length,
        pending: data.length,
        processing: 0,
        completed: 0,
      })
    } catch (error) {
      console.error('获取待处理订单失败:', error)
      message.error(resolveErrorMessage(error))
    }
  }, [])

  const columns = [
    {
      title: '订单ID',
      dataIndex: 'id',
      key: 'id',
      width: 100,
    },
    {
      title: '卡密',
      dataIndex: 'activation_code',
      key: 'activation_code',
      width: 200,
      render: (activation_code: string) => {
        const maskedCode = activation_code
          ? activation_code.replace(/./g, '*').slice(0, 8) + '...'
          : '-'
        return (
          <Space size="middle">
            <span>{maskedCode}</span>
            <Tooltip title={activation_code || '-'} placement="topLeft">
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
                navigator.clipboard.writeText(activation_code || '')
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
      render: (status: string) => {
        const statusMap = {
          pending: { color: 'default', text: '未消费' },
          processing: { color: 'orange', text: '处理中' },
          completed: { color: 'green', text: '已完成' },
        }
        const statusInfo = statusMap[status as keyof typeof statusMap] || { color: 'default', text: status }
        return <Tag color={statusInfo.color}>{statusInfo.text}</Tag>
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
      title: '完成时间',
      dataIndex: 'completed_at',
      key: 'completed_at',
      width: 180,
      render: (date: string | null) => date ? new Date(date).toLocaleString('zh-CN') : '-',
    },
    {
      title: '备注',
      dataIndex: 'remarks',
      key: 'remarks',
      ellipsis: true,
      render: (remarks: string | null) => remarks || '-',
    },
    {
      title: '操作',
      key: 'action',
      width: 200,
      render: (_: unknown, record: Order) => (
        <Space size="small">
          <Button
            type="link"
            size="small"
            icon={<EyeOutlined />}
            onClick={() => handleViewDetail(record)}
          >
            详情
          </Button>
          {record.status === 'pending' || record.status === 'processing' && (
            <Button
              type="link"
              size="small"
              icon={<CheckCircleOutlined />}
              onClick={() => handleCompleteOrder(record.id)}
              style={{ color: '#52c41a' }}
            >
              完成
            </Button>
          )}
        </Space>
      ),
    },
  ]

  return (
    <div>
      <div style={{ marginBottom: 24 }}>
        <Title level={4}>订单处理</Title>
      </div>

      {/* 统计信息 */}
      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col span={8}>
          <AntCard>
            <Statistic title="总订单数" value={stats.total} />
          </AntCard>
        </Col>
        <Col span={8}>
          <AntCard>
            <Statistic title="待消费" value={stats.pending} />
          </AntCard>
        </Col>
        <Col span={8}>
          <AntCard>
            <Statistic title="处理中" value={stats.processing} />
          </AntCard>
        </Col>
        <Col span={8}>
          <AntCard>
            <Statistic title="已完成" value={stats.completed} />
          </AntCard>
        </Col>
      </Row>

      {/* 操作按钮 */}
      <div style={{ marginBottom: 16 }}>
        <Space>
          <Button
            type="primary"
            icon={<ReloadOutlined />}
            onClick={fetchOrders}
            loading={loading}
          >
            刷新订单
          </Button>
          <Button
            onClick={fetchPendingOrders}
            loading={loading}
          >
            仅显示待处理
          </Button>
          <Select
            placeholder="筛选状态"
            style={{ width: 120 }}
            value={statusFilter}
            onChange={setStatusFilter}
            allowClear
          >
            <Option value="pending">未消费</Option>
            <Option value="processing">处理中</Option>
            <Option value="completed">已完成</Option>
          </Select>
        </Space>
      </div>

      {/* 订单表格 */}
      <Table
        columns={columns}
        dataSource={orders}
        rowKey="id"
        loading={loading}
        pagination={{
          showSizeChanger: true,
          showQuickJumper: true,
          showTotal: (total, range) => `第 ${range[0]}-${range[1]} 条，共 ${total} 条`,
        }}
        locale={{
          emptyText: '暂无订单数据',
        }}
      />

      {/* 订单详情模态框 */}
      <Modal
        title="订单详情"
        open={detailModalVisible}
        onCancel={() => {
          setDetailModalVisible(false)
          setSelectedOrder(null)
        }}
        footer={[
          <Button
            key="close"
            onClick={() => {
              setDetailModalVisible(false)
              setSelectedOrder(null)
            }}
          >
            关闭
          </Button>,
          selectedOrder?.status === 'pending' || selectedOrder?.status === 'processing' && (
            <Button
              key="complete"
              type="primary"
              icon={<CheckCircleOutlined />}
              onClick={() => {
                if (selectedOrder) {
                  handleCompleteOrder(selectedOrder.id)
                  setDetailModalVisible(false)
                  setSelectedOrder(null)
                }
              }}
            >
              完成订单
            </Button>
          ),
        ]}
        width={600}
      >
        {selectedOrder && (
          <div>
            <Row gutter={16}>
              <Col span={12}>
                <div style={{ marginBottom: 16 }}>
                  <Text strong>订单ID：</Text>
                  <Text>{selectedOrder.id}</Text>
                </div>
              </Col>
              <Col span={12}>
                <div style={{ marginBottom: 16 }}>
                  <Text strong>状态：</Text>
                  <Tag color={selectedOrder.status === 'pending' || selectedOrder.status === 'processing' ? 'orange' : 'green'}>
                    {selectedOrder.status === 'pending' ? '未消费' : selectedOrder.status === 'processing' ? '处理中' : '已完成'}
                  </Tag>
                </div>
              </Col>
            </Row>

            <div style={{ marginBottom: 16 }}>
              <Text strong>卡密：</Text>
              <br />
              <Space>
                <code style={{
                  background: '#f5f5f5',
                  padding: '8px',
                  borderRadius: '4px',
                  fontFamily: 'monospace',
                  display: 'inline-block',
                  marginTop: '4px'
                }}>
                  {selectedOrder.activation_code}
                </code>
                <Button
                  type="text"
                  icon={<CopyOutlined />}
                  size="small"
                  onClick={() => {
                    navigator.clipboard.writeText(selectedOrder.activation_code || '')
                    message.success('卡密已复制到剪贴板')
                  }}
                />
              </Space>
            </div>

            <Row gutter={16}>
              <Col span={12}>
                <div style={{ marginBottom: 16 }}>
                  <Text strong>创建时间：</Text>
                  <br />
                  <Text>{new Date(selectedOrder.created_at).toLocaleString('zh-CN')}</Text>
                </div>
              </Col>
              <Col span={12}>
                <div style={{ marginBottom: 16 }}>
                  <Text strong>完成时间：</Text>
                  <br />
                  <Text>{selectedOrder.completed_at ? new Date(selectedOrder.completed_at).toLocaleString('zh-CN') : '未完成'}</Text>
                </div>
              </Col>
            </Row>

            {selectedOrder.remarks && (
              <div style={{ marginBottom: 16 }}>
                <Text strong>备注：</Text>
                <br />
                <Paragraph style={{ marginTop: '4px' }}>
                  {selectedOrder.remarks}
                </Paragraph>
              </div>
            )}
          </div>
        )}
      </Modal>
    </div>
  )
}