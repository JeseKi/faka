import { useState, useEffect, useCallback } from 'react'
import {
  Table,
  Button,
  Modal,
  Space,
  Typography,
  App,
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
import { useAuth } from '../../hooks/useAuth'
import type { Order } from '../../lib/types'

const { Title, Text } = Typography
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
  const { message } = App.useApp()
  const { user } = useAuth()
  const [orders, setOrders] = useState<Order[]>([])
  const [loading, setLoading] = useState(false)
  const [detailModalVisible, setDetailModalVisible] = useState(false)
  const [confirmModalVisible, setConfirmModalVisible] = useState(false)
  const [selectedOrder, setSelectedOrder] = useState<Order | null>(null)
  const [statusFilter, setStatusFilter] = useState<string>('')
  const [stats, setStats] = useState({
    total: 0,
    pending: 0,
    processing: 0,
    completed: 0,
  })

  const isAdmin = user?.role === 'admin'

  // 获取订单列表
  const fetchOrders = useCallback(async () => {
    try {
      setLoading(true)
      
      if (isAdmin) {
        // 管理员获取所有订单
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
      } else {
        // 员工只获取处理中的订单
        const { data } = await api.get<Order[]>('/orders/processing')
        setOrders(data)
        // 员工不显示统计信息
        setStats({ total: 0, pending: 0, processing: 0, completed: 0 })
      }
    } catch (error) {
      console.error('获取订单列表失败:', error)
      message.error(resolveErrorMessage(error))
    } finally {
      setLoading(false)
    }
  }, [statusFilter, message, isAdmin])

  useEffect(() => {
    fetchOrders()
  }, [fetchOrders])

  // 完成订单
  const handleCompleteOrder = async (orderId: number) => {
    // 找到对应的订单对象
    const order = orders.find(o => o.id === orderId) || selectedOrder;
    if (order) {
      setSelectedOrder(order);
      setConfirmModalVisible(true);
    }
  }

  // 确认完成订单
  const confirmCompleteOrder = async () => {
    if (!selectedOrder) return;
    try {
      await api.put(`/orders/${selectedOrder.id}/complete`)
      message.success('订单完成成功')
      setConfirmModalVisible(false);
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

  // 获取待处理订单 - 已移除，员工角色直接使用 fetchOrders

  const columns = [
    {
      title: '订单ID',
      dataIndex: 'id',
      key: 'id',
      width: 80,
    },
    ...(isAdmin ? [{
      title: '渠道 ID',
      dataIndex: 'channel_id',
      key: 'channel_id',
      width: 80,
      render: (channelId: number | null) => channelId || '-',
    }] : []),
    {
      title: '卡密',
      dataIndex: 'activation_code',
      key: 'activation_code',
      width: 160,
      render: (activation_code: string) => {
        const maskedCode = activation_code
          ? activation_code.replace(/./g, '*').slice(0, 6) + '...'
          : '-'
        return (
          <Space size="small">
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
      title: '充值卡名称',
      dataIndex: 'card_name',
      key: 'card_name',
      width: 120,
      ellipsis: true,
      render: (card_name: string | null) => card_name || '-',
    },
    {
      title: '价格',
      dataIndex: 'pricing',
      key: 'pricing',
      width: 80,
      render: (pricing: number) => `¥${pricing.toFixed(2)}`,
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      width: 80,
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
      width: 140,
      ellipsis: true,
      render: (date: string) => new Date(date).toLocaleString('zh-CN'),
    },
    {
      title: '完成时间',
      dataIndex: 'completed_at',
      key: 'completed_at',
      width: 140,
      ellipsis: true,
      render: (date: string | null) => date ? new Date(date).toLocaleString('zh-CN') : '-',
    },
    {
      title: '备注',
      dataIndex: 'remarks',
      key: 'remarks',
      width: 120,
      ellipsis: true,
      render: (remarks: string | null) => {
        if (!remarks) return '-'
        const displayText = remarks.length > 15 ? `${remarks.slice(0, 15)}...` : remarks
        return (
          <Space size="small">
            <Tooltip title={remarks} placement="topLeft">
              <span>{displayText}</span>
            </Tooltip>
            <Button
              type="text"
              icon={<CopyOutlined />}
              size="small"
              onClick={() => {
                navigator.clipboard.writeText(remarks)
                message.success('备注已复制到剪贴板')
              }}
            />
          </Space>
        )
      },
    },
    {
      title: '操作',
      key: 'action',
      width: 150,
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
          {(record.status === 'pending' || record.status === 'processing') && (
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

      {/* 统计信息 - 仅管理员可见 */}
      {isAdmin && (
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
      )}

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
          {/* 移除仅显示待处理按钮 */}
          {isAdmin && (
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
          )}
        </Space>
      </div>

      {/* 订单表格 */}
      <Table
        columns={columns}
        dataSource={orders}
        rowKey="id"
        loading={loading}
        scroll={{ x: 1200 }}
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
          (selectedOrder?.status === 'pending' || selectedOrder?.status === 'processing') ? (
            <Button
              key="complete"
              type="primary"
              icon={<CheckCircleOutlined />}
              onClick={() => {
                if (selectedOrder) {
                  handleCompleteOrder(selectedOrder.id)
                  setDetailModalVisible(false)
                }
              }}
            >
              完成订单
            </Button>
          ) : null,
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
              <div style={{ marginTop: '4px' }}>
                {(() => {
                  const activation_code = selectedOrder.activation_code
                  if (!activation_code) return '-'
                  const displayText = activation_code.length > 20 ? `${activation_code.slice(0, 20)}...` : activation_code
                  return (
                    <Space size="middle">
                      <Tooltip title={activation_code} placement="topLeft">
                        <span>{displayText}</span>
                      </Tooltip>
                      <Button
                        type="text"
                        icon={<CopyOutlined />}
                        size="small"
                        onClick={() => {
                          navigator.clipboard.writeText(activation_code)
                          message.success('卡密已复制到剪贴板')
                        }}
                      />
                    </Space>
                  )
                })()}
              </div>
            </div>

            <div style={{ marginBottom: 16 }}>
              <Text strong>充值卡名称：</Text>
              <br />
              <Text>{selectedOrder.card_name || '未设置'}</Text>
            </div>

            <div style={{ marginBottom: 16 }}>
              <Text strong>价格：</Text>
              <br />
              <Text>¥{selectedOrder.pricing.toFixed(2)}</Text>
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
                <div style={{ marginTop: '4px' }}>
                  {(() => {
                    const remarks = selectedOrder.remarks
                    if (!remarks) return null
                    const displayText = remarks.length > 20 ? `${remarks.slice(0, 20)}...` : remarks
                    return (
                      <Space size="middle">
                        <Tooltip title={remarks} placement="topLeft">
                          <span>{displayText}</span>
                        </Tooltip>
                        <Button
                          type="text"
                          icon={<CopyOutlined />}
                          size="small"
                          onClick={() => {
                            navigator.clipboard.writeText(remarks)
                            message.success('备注已复制到剪贴板')
                          }}
                        />
                      </Space>
                    )
                  })()}
                </div>
              </div>
            )}
          </div>
        )}
      </Modal>

      {/* 确认完成订单模态框 */}
      <Modal
        title="确认完成订单"
        open={confirmModalVisible}
        onOk={confirmCompleteOrder}
        onCancel={() => setConfirmModalVisible(false)}
        okText="确认"
        cancelText="取消"
      >
        <p>您确定要将此订单标记为已完成吗？此操作不可撤销。</p>
      </Modal>
    </div>
  )
}