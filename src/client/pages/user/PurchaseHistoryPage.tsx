import { useState, useEffect } from 'react'
import {
  Card,
  Button,
  Table,
  Space,
  Typography,
  Alert,
  message,
  Spin,
  Row,
  Col,
} from 'antd'
import { CreditCardOutlined, HistoryOutlined } from '@ant-design/icons'
import { isAxiosError } from 'axios'
import api from '../../lib/api'
import type { Order } from '../../lib/types'

const { Title, Text, Paragraph } = Typography

interface PurchaseHistoryPageProps {
  userId?: number
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

export default function PurchaseHistoryPage({ userId }: PurchaseHistoryPageProps) {
  const [orders, setOrders] = useState<Order[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchOrders = async () => {
      try {
        const response = await api.get<Order[]>('/orders/me')
        setOrders(response.data)
      } catch (err) {
        console.error('获取购买记录失败:', err)
        const errorMessage = resolveErrorMessage(err)
        setError(errorMessage)
        message.error(errorMessage)
      } finally {
        setLoading(false)
      }
    }

    fetchOrders()
  }, [userId])

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
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      render: (status: string) => (
        <Text type={status === 'completed' ? 'success' : 'warning'}>
          {status === 'completed' ? '已完成' : '待处理'}
        </Text>
      ),
    },
    {
      title: '创建时间',
      dataIndex: 'created_at',
      key: 'created_at',
      render: (date: string) => new Date(date).toLocaleString('zh-CN'),
    },
    {
      title: '完成时间',
      dataIndex: 'completed_at',
      key: 'completed_at',
      render: (date: string | null) => 
        date ? new Date(date).toLocaleString('zh-CN') : '-',
    },
    {
      title: '备注',
      dataIndex: 'remarks',
      key: 'remarks',
      render: (remarks: string | null) => remarks || '-',
    },
  ]

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '50px' }}>
        <Spin size="large" />
        <div style={{ marginTop: 16 }}>
          <Text type="secondary">正在加载购买记录...</Text>
        </div>
      </div>
    )
  }

  return (
    <div style={{ maxWidth: 1200, margin: '0 auto', padding: '24px' }}>
      <div style={{ textAlign: 'center', marginBottom: 32 }}>
        <Title level={2}>
          <HistoryOutlined style={{ marginRight: 8 }} />
          购买记录
        </Title>
        <Paragraph type="secondary" style={{ fontSize: '16px' }}>
          查看您的历史购买记录和订单状态
        </Paragraph>
      </div>

      {error && (
        <Alert
          message="获取数据失败"
          description={error}
          type="error"
          showIcon
          style={{ marginBottom: 24 }}
        />
      )}

      <Card bordered={false}>
        {orders.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '40px' }}>
            <CreditCardOutlined style={{ fontSize: 48, color: '#999' }} />
            <div style={{ marginTop: 16 }}>
              <Text type="secondary">暂无购买记录</Text>
            </div>
          </div>
        ) : (
          <Table
            dataSource={orders}
            columns={columns}
            rowKey="id"
            pagination={{
              pageSize: 10,
              showSizeChanger: false,
              showQuickJumper: true,
            }}
          />
        )}
      </Card>
    </div>
  )
}