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
  Select,
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

interface SearchParams {
  start_date?: string
  end_date?: string
  username?: string
  name?: string
}

export default function SalesRevenuePage() {
  const { message } = App.useApp()
  const { user } = useAuth()
  const [loading, setLoading] = useState(false)
  const [revenueData, setRevenueData] = useState<RevenueData | null>(null)
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
        if (values.searchType && values.searchValue) {
          if (values.searchType === 'username') {
            params.username = values.searchValue
          } else if (values.searchType === 'name') {
            params.name = values.searchValue
          }
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
          initialValues={{
            searchType: 'username',
          }}
        >
          <Form.Item label="查询时间范围" name="dateRange">
            <RangePicker
              showTime
              format="YYYY-MM-DD HH:mm:ss"
              placeholder={['开始时间', '结束时间']}
            />
          </Form.Item>

          {isAdmin && (
            <>
              <Form.Item label="搜索类型" name="searchType">
                <Select style={{ width: 120 }}>
                  <Select.Option value="username">用户名</Select.Option>
                  <Select.Option value="name">姓名</Select.Option>
                </Select>
              </Form.Item>
              <Form.Item label="搜索内容" name="searchValue">
                <Input
                  placeholder="请输入用户名或姓名"
                  style={{ width: 200 }}
                />
              </Form.Item>
            </>
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
      {revenueData && (
        <Row gutter={16} style={{ marginBottom: 24 }}>
          <Col span={8}>
            <AntCard>
              <Statistic
                title="代理商用户名"
                value={revenueData.proxy_username}
                prefix={<UserOutlined />}
              />
            </AntCard>
          </Col>
          <Col span={8}>
            <AntCard>
              <Statistic
                title="总销售额"
                value={revenueData.total_revenue}
                precision={2}
                prefix={<DollarOutlined />}
                suffix="元"
              />
            </AntCard>
          </Col>
          <Col span={8}>
            <AntCard>
              <Statistic
                title="已消费卡密数"
                value={revenueData.consumed_count}
                prefix={<SearchOutlined />}
              />
            </AntCard>
          </Col>
        </Row>
      )}

      {/* 查询结果详情 */}
      {revenueData && (
        <AntCard title="查询详情">
          <Space direction="vertical" size="middle" style={{ width: '100%' }}>
            <div>
              <strong>代理商姓名：</strong>
              {revenueData.proxy_name || '未设置'}
            </div>
            <div>
              <strong>查询时间范围：</strong>
              {revenueData.query_time_range}
            </div>
            <div>
              <strong>代理商ID：</strong>
              {revenueData.proxy_user_id}
            </div>
          </Space>
        </AntCard>
      )}

      {/* 空状态提示 */}
      {!revenueData && !loading && (
        <AntCard>
          <div style={{ textAlign: 'center', padding: '40px 0' }}>
            <DollarOutlined style={{ fontSize: 48, color: '#d9d9d9', marginBottom: 16 }} />
            <p style={{ color: '#666' }}>请设置查询条件并点击查询按钮</p>
          </div>
        </AntCard>
      )}
    </div>
  )
}