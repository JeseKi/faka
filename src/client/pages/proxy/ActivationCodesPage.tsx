import { useState, useEffect, useCallback } from 'react'
import {
  Table,
  Button,
  Switch,
  Space,
  Typography,
  App,
  Tag,
  Card as AntCard,
  Row,
  Col,
  Statistic,
  Tooltip
} from 'antd'
import {
  DownloadOutlined,
  ReloadOutlined,
  EyeOutlined,
  CopyOutlined,
} from '@ant-design/icons'
import { isAxiosError } from 'axios'
import api from '../../lib/api'
import type { ActivationCode } from '../../lib/types'

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

export default function ActivationCodesPage() {
  const { message } = App.useApp()
  const [codes, setCodes] = useState<ActivationCode[]>([])
  const [loading, setLoading] = useState(false)
  const [showExported, setShowExported] = useState(false)
  const [stats, setStats] = useState({
    total: 0,
    available: 0,
    exported: 0,
  })

  // 获取可用卡密列表
  const fetchCodes = useCallback(async () => {
    try {
      setLoading(true)
      const { data } = await api.get('/activation-codes/available')
      setCodes(data.codes)

      // 计算统计信息
      const total = data.codes.length
      const available = data.codes.filter((code: ActivationCode) => code.status === 'available').length
      const exported = data.codes.filter((code: ActivationCode) => code.exported).length
      setStats({ total, available, exported })
    } catch (error) {
      console.error('获取卡密列表失败:', error)
      message.error(resolveErrorMessage(error))
    } finally {
      setLoading(false)
    }
  }, [message])

  useEffect(() => {
    fetchCodes()
  }, [fetchCodes])

  // 导出CSV
  const handleExportCSV = async () => {
    try {
      // 获取当前显示的卡密ID
      const visibleCodes = showExported
        ? codes
        : codes.filter(code => !code.exported)

      if (visibleCodes.length === 0) {
        message.warning('没有可导出的卡密')
        return
      }

      const codeIds = visibleCodes.map(code => code.id)

      // 调用导出API
      await api.post('/activation-codes/export', { code_ids: codeIds })

      // 生成CSV内容
      const csvContent = [
        ['ID', '卡密', '使用状态'].join(','),
        ...visibleCodes.map(code => [
          code.id,
          code.code,
          code.status === 'available' ? '未使用' : code.status === 'consuming' ? '消费中' : '已消费'
        ].join(','))
      ].join('\n')

      // 创建并下载CSV文件
      const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
      const link = document.createElement('a')
      const url = URL.createObjectURL(blob)
      link.setAttribute('href', url)
      link.setAttribute('download', `activation_codes_${new Date().toISOString().split('T')[0]}.csv`)
      link.style.visibility = 'hidden'
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)

      message.success(`成功导出 ${visibleCodes.length} 个卡密`)
      fetchCodes() // 刷新列表
    } catch (error) {
      console.error('导出卡密失败:', error)
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
      dataIndex: ['card', 'name'],
      key: 'card_name',
      width: 150,
    },
    {
      title: '价格',
      dataIndex: ['card', 'price'],
      key: 'card_price',
      width: 100,
      render: (price: number) => `¥${price.toFixed(2)}`,
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
      title: '导出状态',
      dataIndex: 'exported',
      key: 'exported',
      width: 100,
      render: (exported: boolean) => (
        <Tag color={exported ? 'blue' : 'default'}>
          {exported ? '已导出' : '未导出'}
        </Tag>
      ),
    },
    {
      title: '创建时间',
      dataIndex: 'created_at',
      key: 'created_at',
      width: 180,
      render: (date: string) => new Date(date).toLocaleString('zh-CN'),
    },
  ]

  // 过滤显示的卡密
  const visibleCodes = showExported
    ? codes
    : codes.filter(code => !code.exported)

  return (
    <div>
      <div style={{ marginBottom: 24 }}>
        <Title level={4}>我的卡密</Title>
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
            <Statistic title="可用卡密" value={stats.available} />
          </AntCard>
        </Col>
        <Col span={8}>
          <AntCard>
            <Statistic title="已导出" value={stats.exported} />
          </AntCard>
        </Col>
      </Row>

      {/* 操作按钮 */}
      <div style={{ marginBottom: 16 }}>
        <Space>
          <Button
            type="primary"
            icon={<DownloadOutlined />}
            onClick={handleExportCSV}
            disabled={visibleCodes.length === 0}
          >
            导出CSV ({visibleCodes.length})
          </Button>
          <Button
            icon={<ReloadOutlined />}
            onClick={fetchCodes}
            loading={loading}
          >
            刷新
          </Button>
          <Switch
            checked={showExported}
            onChange={setShowExported}
            checkedChildren="显示全部"
            unCheckedChildren="仅未导出"
          />
        </Space>
      </div>

      {/* 卡密表格 */}
      <Table
        columns={columns}
        dataSource={visibleCodes}
        rowKey="id"
        loading={loading}
        pagination={{
          showSizeChanger: true,
          showQuickJumper: true,
          showTotal: (total, range) => `第 ${range[0]}-${range[1]} 条，共 ${total} 条`,
        }}
        locale={{
          emptyText: '暂无卡密数据',
        }}
      />
    </div>
  )
}