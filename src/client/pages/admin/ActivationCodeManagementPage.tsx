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
  DeleteOutlined,
  ReloadOutlined,
  SearchOutlined,
  EyeOutlined,
  CopyOutlined,
  DownloadOutlined,
} from '@ant-design/icons'
import { isAxiosError } from 'axios'
import api from '../../lib/api'
import { getUsers } from '../../lib/user'
import type { ActivationCode, Card, UserProfile } from '../../lib/types'

const { Title } = Typography
const { Option } = Select

interface CodeFormData {
  card_id: number
  count: number
  proxy_user_id: number
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
  const { message } = App.useApp()
  const [codes, setCodes] = useState<ActivationCode[]>([])
  const [cards, setCards] = useState<Card[]>([])
  const [proxies, setProxies] = useState<UserProfile[]>([])
  const [loading, setLoading] = useState(false)
  const [modalVisible, setModalVisible] = useState(false)
  const [filterModalVisible, setFilterModalVisible] = useState(false)
  const [searchCard, setSearchCard] = useState<string>('')
  const [searchProxy, setSearchProxy] = useState<string>('')
  const [status, setStatus] = useState<string>('available')
  const [exported, setExported] = useState<boolean | null>(null)

  // 临时筛选状态，用于模态框
  const [tempSearchCard, setTempSearchCard] = useState<string>('')
  const [tempSearchProxy, setTempSearchProxy] = useState<string>('')
  const [tempStatus, setTempStatus] = useState<string>('available')
  const [tempExported, setTempExported] = useState<boolean | null>(null)
  const [stats, setStats] = useState({
    total: 0,
    used: 0,
    unused: 0,
  })
  const [selectedRowKeys, setSelectedRowKeys] = useState<string[]>([])

  const [form] = Form.useForm<CodeFormData>()

  // 获取充值卡列表
  const fetchCards = useCallback(async () => {
    try {
      const { data } = await api.get<Card[]>('/cards')
      setCards(data)
    } catch (error) {
      console.error('获取充值卡列表失败:', error)
    }
  }, [])

  // 获取代理商列表
  const fetchProxies = useCallback(async () => {
    try {
      const { users } = await getUsers('proxy')
      // 按照 ID 倒序排序，最新的代理商在前面
      const sortedUsers = users.sort((a, b) => b.id - a.id)
      setProxies(sortedUsers)
    } catch (error) {
      console.error('获取代理商列表失败:', error)
    }
  }, [])

  // 获取卡密列表
  const fetchCodes = useCallback(async (cardId?: string) => {
    if (!cardId && !searchCard) return

    const targetCardId = cardId || searchCard
    if (!targetCardId) return

    try {
      setLoading(true)
      // 构建查询参数
      const params = new URLSearchParams()
      if (searchProxy) {
        params.append('proxy_user_id', searchProxy)
      }
      if (status !== 'all') {
        params.append('status', status)
      }
      if (exported !== null) {
        params.append('exported', exported.toString())
      }

      const { data } = await api.get<ActivationCode[]>(`/activation-codes/${targetCardId}?${params.toString()}`)
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
  }, [searchCard, searchProxy, status, exported, message])

  useEffect(() => {
    fetchCards()
    fetchProxies()
  }, [fetchCards, fetchProxies])

  useEffect(() => {
    if (searchCard) {
      // 清空之前的选中状态
      setSelectedRowKeys([])
      fetchCodes()
    } else {
      // 清空数据和统计信息
      setCodes([])
      setStats({ total: 0, used: 0, unused: 0 })
      setSelectedRowKeys([])
    }
  }, [status, searchCard, searchProxy, exported, fetchCodes])

  // 处理表单提交
  const handleSubmit = async (values: CodeFormData) => {
    try {
      await api.post('/activation-codes/generate', values)
      message.success(`成功生成 ${values.count} 个卡密`)
      setModalVisible(false)
      form.resetFields()
      fetchCodes(values.card_id.toString())
    } catch (error) {
      console.error('生成卡密失败:', error)
      message.error(resolveErrorMessage(error))
    }
  }

  // 删除所有卡密
  const handleDeleteAll = async (cardId: string) => {
    try {
      await api.delete(`/activation-codes/${cardId}`)
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

  // 打开筛选模态框
  const handleOpenFilter = () => {
    // 初始化临时筛选状态为当前筛选状态
    setTempSearchCard(searchCard)
    setTempSearchProxy(searchProxy)
    setTempStatus(status)
    setTempExported(exported)
    setFilterModalVisible(true)
  }

  // 应用筛选条件
  const handleApplyFilter = () => {
    setSearchCard(tempSearchCard)
    setSearchProxy(tempSearchProxy)
    setStatus(tempStatus)
    setExported(tempExported)
    setSelectedRowKeys([]) // 清空选中状态
    setFilterModalVisible(false)
  }

  // 取消筛选
  const handleCancelFilter = () => {
    setFilterModalVisible(false)
  }

  // 重置筛选条件
  const handleResetFilter = () => {
    setTempSearchCard('')
    setTempSearchProxy('')
    setTempStatus('available')
    setTempExported(null)
  }

  // 计算当前已选中的卡密（仅限当前列表内）
  const selectedCodes = codes.filter(code => selectedRowKeys.includes(code.id.toString()))

  // 导出卡密
  const handleExportCodes = async () => {
    // 优先导出已选；如未选择，则导出当前筛选结果（即当前列表）
    const exportTargets = selectedCodes.length > 0 ? selectedCodes : codes

    if (exportTargets.length === 0) {
      message.warning('当前列表为空，无法导出')
      return
    }

    // DEBUG：导出前记录关键数据，便于定位问题
    console.log('导出调试：已选 keys =', selectedRowKeys, '当前列表长度 =', codes.length, '实际导出数量 =', exportTargets.length)

    // 先生成并下载 CSV，不阻塞于后端标记逻辑
    const header = ['ID', '卡密', '使用状态', '导出状态'].join(',')
    const rows = exportTargets.map(code => [
      code.id,
      code.code,
      code.status === 'available' ? '未使用' : code.status === 'consuming' ? '消费中' : '已消费',
      code.exported ? '已导出' : '未导出'
    ].join(','))
    // 为了更好兼容 Excel，加入 UTF-8 BOM
    const csvContent = '\ufeff' + [header, ...rows].join('\n')

    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
    const link = document.createElement('a')
    const url = URL.createObjectURL(blob)
    link.setAttribute('href', url)
    link.setAttribute('download', `activation_codes_${new Date().toISOString().split('T')[0]}.csv`)
    link.style.visibility = 'hidden'
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)

    message.success(`成功导出 ${exportTargets.length} 个卡密`)

    // 后台标记为已导出（不阻塞下载）
    api
      .post('/activation-codes/export', { code_ids: exportTargets.map(code => code.id) })
      .then(() => {
        setSelectedRowKeys([])
        fetchCodes()
      })
      .catch((error) => {
        console.error('导出标记失败:', error)
        message.warning(`导出文件已下载，但标记失败：${resolveErrorMessage(error)}`)
      })
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

      {/* 筛选和操作区域 */}
      <AntCard style={{ marginBottom: 24 }}>
        <Row gutter={[16, 16]} align="middle">
          {/* 左侧筛选标签区域 */}
          <Col flex="auto">
            <Row gutter={[16, 8]} align="middle">
              <Col>
                <span style={{ fontWeight: 500, color: '#262626', marginRight: 8 }}>当前筛选：</span>
              </Col>
              {searchCard && (
                <Col>
                  <Tag
                    closable
                    onClose={() => setSearchCard('')}
                    color="blue"
                  >
                    充值卡：{cards.find(c => c.id.toString() === searchCard)?.name || searchCard}
                  </Tag>
                </Col>
              )}
              {searchProxy && (
                <Col>
                  <Tag
                    closable
                    onClose={() => setSearchProxy('')}
                    color="green"
                  >
                    代理商：{proxies.find(p => p.id.toString() === searchProxy)?.username || searchProxy}
                  </Tag>
                </Col>
              )}
              {status !== 'available' && (
                <Col>
                  <Tag
                    closable
                    onClose={() => setStatus('available')}
                    color="orange"
                  >
                    状态：{status === 'all' ? '全部' : status === 'consuming' ? '消费中' : '已消费'}
                  </Tag>
                </Col>
              )}
              {exported !== null && (
                <Col>
                  <Tag
                    closable
                    onClose={() => setExported(null)}
                    color="purple"
                  >
                    导出状态：{exported ? '已导出' : '未导出'}
                  </Tag>
                </Col>
              )}
              {(!searchCard && !searchProxy && status === 'available' && exported === null) && (
                <Col>
                  <span style={{ color: '#999' }}>暂无筛选条件</span>
                </Col>
              )}
            </Row>
          </Col>

          {/* 右侧操作区域 */}
          <Col>
            <Space>
              <Button
                icon={<SearchOutlined />}
                onClick={handleOpenFilter}
                disabled={loading}
              >
                高级筛选
              </Button>
              <Button
                type="primary"
                icon={<PlusOutlined />}
                onClick={handleGenerate}
                disabled={loading}
              >
                批量生成卡密
              </Button>
              <Button
                icon={<ReloadOutlined />}
                onClick={() => fetchCodes()}
                loading={loading}
                disabled={!searchCard}
              >
                刷新
              </Button>
              <Button
                type="primary"
                icon={<DownloadOutlined />}
                onClick={handleExportCodes}
                disabled={codes.length === 0 || loading}
              >
                {selectedCodes.length > 0 ? `导出已选 (${selectedCodes.length})` : `导出当前列表 (${codes.length})`}
              </Button>
              {searchCard && (
                <Popconfirm
                  title={`确定要删除 ${cards.find(c => c.id.toString() === searchCard)?.name || searchCard} 的所有卡密吗？`}
                  description="此操作不可恢复，请谨慎操作。"
                  onConfirm={() => handleDeleteAll(searchCard)}
                  okText="确定"
                  cancelText="取消"
                >
                  <Button danger icon={<DeleteOutlined />} disabled={loading}>
                    删除所有卡密
                  </Button>
                </Popconfirm>
              )}
            </Space>
          </Col>
        </Row>
      </AntCard>

      {/* 卡密表格 */}
      <Table
        columns={columns}
        dataSource={codes}
        rowKey={(record) => record.id.toString()}
        loading={loading}
        rowSelection={{
          selectedRowKeys,
          onChange: (keys) => setSelectedRowKeys(keys.map(String)),
          preserveSelectedRowKeys: false,
        }}
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
            name="card_id"
            rules={[{ required: true, message: '请选择充值卡' }]}
          >
            <Select placeholder="请选择要生成卡密的充值卡">
              {cards.map((card) => (
                <Option key={card.id} value={card.id}>
                  {card.name} - ¥{card.price}
                </Option>
              ))}
            </Select>
          </Form.Item>

          <Form.Item
            label="选择代理商"
            name="proxy_user_id"
            rules={[{ required: true, message: '请选择代理商' }]}
          >
            <Select placeholder="请选择要分配卡密的代理商">
              {proxies.map((proxy) => (
                <Option key={proxy.id} value={proxy.id}>
                  {proxy.username} ({proxy.name || '未设置姓名'})
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

      {/* 高级筛选模态框 */}
      <Modal
        title="高级筛选"
        open={filterModalVisible}
        onCancel={handleCancelFilter}
        footer={[
          <Button key="reset" onClick={handleResetFilter}>
            重置
          </Button>,
          <Button key="cancel" onClick={handleCancelFilter}>
            取消
          </Button>,
          <Button key="apply" type="primary" onClick={handleApplyFilter}>
            应用筛选
          </Button>,
        ]}
        width={600}
      >
        <Form layout="vertical">
          <Form.Item label="选择充值卡">
            <Select
              placeholder="请选择充值卡"
              style={{ width: '100%' }}
              value={tempSearchCard}
              onChange={setTempSearchCard}
              showSearch
              filterOption={(input, option) =>
                (option?.children as unknown as string)?.toLowerCase().includes(input.toLowerCase())
              }
            >
              {cards.map((card) => (
                <Option key={card.id} value={card.id.toString()}>
                  {card.name} - ¥{card.price}
                </Option>
              ))}
            </Select>
          </Form.Item>

          <Form.Item label="选择代理商（可选）">
            <Select
              placeholder="选择代理商（可选）"
              style={{ width: '100%' }}
              value={tempSearchProxy}
              onChange={setTempSearchProxy}
              allowClear
              showSearch
              filterOption={(input, option) =>
                (option?.children as unknown as string)?.toLowerCase().includes(input.toLowerCase())
              }
            >
              {proxies.map((proxy) => (
                <Option key={proxy.id} value={proxy.id.toString()}>
                  {proxy.username} ({proxy.name || '未设置姓名'})
                </Option>
              ))}
            </Select>
          </Form.Item>

          <Form.Item label="筛选状态">
            <Select
              placeholder="筛选状态"
              style={{ width: '100%' }}
              value={tempStatus}
              onChange={setTempStatus}
            >
              <Option value="all">显示全部</Option>
              <Option value="available">未使用</Option>
              <Option value="consuming">消费中</Option>
              <Option value="consumed">已消费</Option>
            </Select>
          </Form.Item>

          <Form.Item label="筛选导出状态">
            <Select
              placeholder="筛选导出状态"
              style={{ width: '100%' }}
              value={tempExported}
              onChange={setTempExported}
              allowClear
            >
              <Option value={null}>显示全部</Option>
              <Option value={false}>未导出</Option>
              <Option value={true}>已导出</Option>
            </Select>
          </Form.Item>
        </Form>
      </Modal>
    </div>
  )
}