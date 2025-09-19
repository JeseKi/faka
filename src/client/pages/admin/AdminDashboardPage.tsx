import { useState, useEffect } from 'react'
import { Card, Row, Col, Statistic, Spin, Alert, Typography } from 'antd'
import { isAxiosError } from 'axios'
import api from '../../lib/api'
import type { SalesStats } from '../../lib/types'

const { Title } = Typography

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

export default function AdminDashboardPage() {
  const [stats, setStats] = useState<SalesStats | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchStats = async () => {
      try {
        setLoading(true)
        const { data } = await api.get<SalesStats>('/sales/stats')
        setStats(data)
      } catch (err) {
        console.error('获取统计数据失败:', err)
        const errorMessage = resolveErrorMessage(err)
        setError(errorMessage)
      } finally {
        setLoading(false)
      }
    }

    fetchStats()
  }, [])

  if (loading) {
    return (
      <div style={{ textAlign: 'center', padding: '50px' }}>
        <Spin size="large" />
        <div style={{ marginTop: 16 }}>
          <Typography.Text type="secondary">正在加载统计数据...</Typography.Text>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <Alert
        message="获取数据失败"
        description={error}
        type="error"
        showIcon
        style={{ margin: '24px' }}
      />
    )
  }

  return (
    <div>
      <div style={{ marginBottom: 24 }}>
        <Title level={4}>管理员首页</Title>
      </div>

      <Row gutter={[16, 16]}>
        <Col xs={24} sm={12} md={8} lg={6}>
          <Card>
            <Statistic title="总销售额" value={stats?.total_revenue ?? 0} precision={2} prefix="¥" />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={8} lg={6}>
          <Card>
            <Statistic title="总销量" value={stats?.total_sales ?? 0} suffix="笔" />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={8} lg={6}>
          <Card>
            <Statistic title="今日销售额" value={stats?.today_revenue ?? 0} precision={2} prefix="¥" />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={8} lg={6}>
          <Card>
            <Statistic title="今日销量" value={stats?.today_sales ?? 0} suffix="笔" />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={8} lg={6}>
          <Card>
            <Statistic title="总库存" value={stats?.total_stock ?? 0} suffix="张" />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={8} lg={6}>
          <Card>
            <Statistic title="待处理订单" value={stats?.pending_orders ?? 0} suffix="笔" />
          </Card>
        </Col>
      </Row>
    </div>
  )
}