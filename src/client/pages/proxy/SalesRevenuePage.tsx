import { useState, useCallback } from 'react'
import {
  Card as AntCard,
  Row,
  Col,
  Statistic,
  DatePicker,
  Button,
  Input,
  Space,
  Typography,
  App,
  Form,
} from 'antd'
import {
  DollarOutlined,
  SearchOutlined,
  ReloadOutlined,
  UserOutlined,
} from '@ant-design/icons'
import { isAxiosError } from 'axios'
import api from '../../lib/api'
import { useAuth } from '../../hooks/useAuth'

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

interface RevenueData {
  proxy_user_id: number
  proxy_username: string
  proxy_name?: string
  total_revenue: number
  consumed_count: number
  start_date?: string
  end_date?: string
  query_time_range: string
}

interface MultiRevenueResponse {
  revenues: RevenueData[]
  total_count: number
}

interface SearchParams {
  start_date?: string
  end_date?: string
  query?: string
}

export default function SalesRevenuePage() {
  const { message } = App.useApp()
  const { user } = useAuth()
  const [loading, setLoading] = useState(false)
  const [revenueData, setRevenueData] = useState<MultiRevenueResponse | null>(null)
  const [searchForm] = Form.useForm()

  // 判断是否为管理员
  const isAdmin = user?.role === 'admin'

  // 查询销售额
  const handleSearch = useCallback(async () => {
    try {
      setLoading(true)

      const values = await searchForm.validateFields()
      const params: SearchParams = {}

      // 添加日期范围
      if (values.dateRange) {
        params.start_date = values.dateRange[0].toISOString()
        params.end_date = values.dateRange[1].toISOString()
      }

      // 如果是管理员，添加搜索条件
      if (isAdmin) {
        if (values.searchValue) {
          params.query = values.searchValue
        }
      }

      const { data } = await api.get('/proxy/revenue', { params })
      setRevenueData(data)
    } catch (error) {
      console.error('查询销售额失败:', error)
      message.error(resolveErrorMessage(error))
    } finally {
      setLoading(false)
    }
  }, [searchForm, isAdmin, message])

  // 重置查询
  const handleReset = useCallback(() => {
    searchForm.resetFields()
    setRevenueData(null)
  }, [searchForm])

  return (
    <div>
      <div style={{ marginBottom: 24 }}>
        <Title level={4}>代理商销售额查询</Title>
      </div>

      {/* 搜索表单 */}
      <AntCard style={{ marginBottom: 24 }}>
        <Form
          form={searchForm}
          layout="inline"
        >
          <Form.Item label="查询时间范围" name="dateRange">
            <RangePicker
              showTime
              format="YYYY-MM-DD HH:mm:ss"
              placeholder={['开始时间', '结束时间']}
            />
          </Form.Item>

          {isAdmin && (
            <Form.Item label="代理商查询" name="searchValue">
              <Input
                placeholder="请输入代理商用户名或姓名"
                style={{ width: 200 }}
              />
            </Form.Item>
          )}

          <Form.Item>
            <Space>
              <Button
                type="primary"
                icon={<SearchOutlined />}
                onClick={handleSearch}
                loading={loading}
              >
                查询
              </Button>
              <Button
                icon={<ReloadOutlined />}
                onClick={handleReset}
              >
                重置
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </AntCard>

      {/* 统计信息 */}
      {revenueData && revenueData.revenues.length > 0 && (
        <div style={{ marginBottom: 24 }}>
          <div style={{ marginBottom: 16 }}>
            <strong>共找到 {revenueData.total_count} 个匹配的代理商</strong>
          </div>
          <Row gutter={16}>
            {revenueData.revenues.map((revenue) => (
              <Col span={24} key={revenue.proxy_user_id} style={{ marginBottom: 16 }}>
                <AntCard
                  title={`代理商: ${revenue.proxy_username} ${revenue.proxy_name ? `(${revenue.proxy_name})` : ''}`}
                  type="inner"
                >
                  <Row gutter={16}>
                    <Col span={6}>
                      <Statistic
                        title="代理商ID"
                        value={revenue.proxy_user_id}
                        prefix={<UserOutlined />}
                      />
                    </Col>
                    <Col span={6}>
                      <Statistic
                        title="总销售额"
                        value={revenue.total_revenue}
                        precision={2}
                        prefix={<DollarOutlined />}
                        suffix="元"
                      />
                    </Col>
                    <Col span={6}>
                      <Statistic
                        title="已消费卡密数"
                        value={revenue.consumed_count}
                        prefix={<SearchOutlined />}
                      />
                    </Col>
                    <Col span={6}>
                      <Statistic
                        title="查询时间范围"
                        value={revenue.query_time_range}
                      />
                    </Col>
                  </Row>
                </AntCard>
              </Col>
            ))}
          </Row>
        </div>
      )}

      {/* 空状态提示 */}
      {(!revenueData || revenueData.revenues.length === 0) && !loading && (
        <AntCard>
          <div style={{ textAlign: 'center', padding: '40px 0' }}>
            <DollarOutlined style={{ fontSize: 48, color: '#d9d9d9', marginBottom: 16 }} />
            <p style={{ color: '#666' }}>未找到匹配的代理商，请检查查询条件</p>
          </div>
        </AntCard>
      )}
    </div>
  )
}