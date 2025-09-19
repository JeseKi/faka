import { useState, useEffect, useCallback } from 'react'
import {
  Table,
  Button,
  Space,
  Typography,
  message,
  Card as AntCard,
  Row,
  Col,
  Input,
  DatePicker,
} from 'antd'
import { ReloadOutlined, SearchOutlined } from '@ant-design/icons'
import { isAxiosError } from 'axios'
import api from '../../lib/api'
import type { Sale } from '../../lib/types'
import dayjs from 'dayjs'

const { Title } = Typography
const { RangePicker } = DatePicker

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

export default function SalesRecordPage() {
  const [sales, setSales] = useState<Sale[]>([])
  const [loading, setLoading] = useState(false)
  const [cardNameFilter, setCardNameFilter] = useState('')
  const [dateRange, setDateRange] = useState<[dayjs.Dayjs | null, dayjs.Dayjs | null]>([null, null])
  const [pagination, setPagination] = useState({
    current: 1,
    pageSize: 10,
    total: 0,
  })

  // 获取销售记录列表
  const fetchSales = useCallback(async () => {
    try {
      setLoading(true)
      const params = new URLSearchParams()
      params.append('limit', pagination.pageSize.toString())
      params.append('offset', ((pagination.current - 1) * pagination.pageSize).toString())

      if (cardNameFilter) {
        params.append('card_name', cardNameFilter)
      }

      if (dateRange[0] && dateRange[1]) {
        params.append('start_date', dateRange[0].format('YYYY-MM-DD'))
        params.append('end_date', dateRange[1].format('YYYY-MM-DD'))
      }

      const response = await api.get<Sale[]>(`/sales?${params.toString()}`)
      const total = parseInt(response.headers['x-total-count'] || '0', 10)

      setSales(response.data)
      setPagination(prev => {
        if (prev.total === total) {
          return prev
        }
        return {
          ...prev,
          total: total
        }
      })
    } catch (error) {
      console.error('获取销售记录失败:', error)
      message.error(resolveErrorMessage(error))
    } finally {
      setLoading(false)
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [pagination.current, pagination.pageSize, cardNameFilter, dateRange])

  useEffect(() => {
    fetchSales()
  }, [fetchSales])

  const handleTableChange = (page: number, pageSize?: number) => {
    setPagination(prev => ({
      ...prev,
      current: page,
      pageSize: pageSize || prev.pageSize,
    }))
  }

  const handleSearch = () => {
    setPagination(prev => ({
      ...prev,
      current: 1,
    }))
  }

  const handleReset = () => {
    setCardNameFilter('')
    setDateRange([null, null])
    setPagination(prev => ({
      ...prev,
      current: 1,
    }))
  }

  const columns = [
    {
      title: 'ID',
      dataIndex: 'id',
      key: 'id',
      width: 80,
    },
    {
      title: '充值卡类型',
      dataIndex: 'card_name',
      key: 'card_name',
      width: 150,
    },
    {
      title: '卡密',
      dataIndex: 'activation_code',
      key: 'activation_code',
      width: 200,
      render: (code: string) => (
        <code style={{
          background: '#f5f5f5',
          padding: '2px 4px',
          borderRadius: '3px',
          fontFamily: 'monospace'
        }}>
          {code}
        </code>
      ),
    },
    {
      title: '用户邮箱',
      dataIndex: 'user_email',
      key: 'user_email',
      width: 200,
    },
    {
      title: '销售价格',
      dataIndex: 'sale_price',
      key: 'sale_price',
      width: 120,
      render: (price: number) => `¥${price.toFixed(2)}`,
    },
    {
      title: '购买时间',
      dataIndex: 'purchased_at',
      key: 'purchased_at',
      width: 180,
      render: (date: string) => dayjs(date).format('YYYY-MM-DD HH:mm:ss'),
    },
  ]

  return (
    <div>
      <div style={{ marginBottom: 24 }}>
        <Title level={4}>销售记录</Title>
      </div>

      {/* 搜索和筛选 */}
      <AntCard style={{ marginBottom: 16 }}>
        <Row gutter={[16, 16]} align="middle">
          <Col xs={24} md={6}>
            <Input
              placeholder="充值卡类型"
              value={cardNameFilter}
              onChange={e => setCardNameFilter(e.target.value)}
              prefix={<SearchOutlined />}
            />
          </Col>
          <Col xs={24} md={8}>
            <RangePicker
              value={dateRange}
              onChange={dates => setDateRange(dates as [dayjs.Dayjs | null, dayjs.Dayjs | null])}
              placeholder={['开始日期', '结束日期']}
              style={{ width: '100%' }}
            />
          </Col>
          <Col xs={24} md={10}>
            <Space>
              <Button type="primary" onClick={handleSearch}>
                搜索
              </Button>
              <Button onClick={handleReset}>
                重置
              </Button>
              <Button icon={<ReloadOutlined />} onClick={fetchSales} loading={loading}>
                刷新
              </Button>
            </Space>
          </Col>
        </Row>
      </AntCard>

      {/* 销售记录表格 */}
      <Table
        columns={columns}
        dataSource={sales}
        rowKey="id"
        loading={loading}
        pagination={{
          current: pagination.current,
          pageSize: pagination.pageSize,
          total: pagination.total,
          onChange: handleTableChange,
          showSizeChanger: true,
          showQuickJumper: true,
          showTotal: (total, range) => `第 ${range[0]}-${range[1]} 条，共 ${total} 条`,
        }}
        locale={{
          emptyText: '暂无销售记录数据',
        }}
      />
    </div>
  )
}