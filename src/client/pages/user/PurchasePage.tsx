import { useState } from 'react'
import {
  Card,
  Button,
  Form,
  Input,
  Select,
  Space,
  Typography,
  Alert,
  App,
  Spin,
  Row,
  Col,
  Modal,
} from 'antd'
import { ShoppingCartOutlined, CreditCardOutlined } from '@ant-design/icons'
import { isAxiosError } from 'axios'
import { useNavigate } from 'react-router-dom'
import ReactMarkdown from 'react-markdown'
import api from '../../lib/api'
import { useCards } from '../../hooks/useCardAPI'
import { useAuth } from '../../hooks/useAuth' // 新增导入
import ProductCard from '../../components/ui/ProductCard'
import type { SaleCreate, Card as CardType } from '../../lib/types'

const { Title, Text, Paragraph } = Typography
const { Option } = Select

interface PurchaseFormData {
  card_name: string
  user_email: string
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

export default function PurchasePage() {
  const { message } = App.useApp()
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [selectedCard, setSelectedCard] = useState<CardType | null>(null)

  const [form] = Form.useForm<PurchaseFormData>()

  // 使用 SWR hook 获取充值卡数据
  const { cards, isLoading } = useCards(false)

  const navigate = useNavigate()
  const { isAuthenticated, loading } = useAuth() // 使用 useAuth hook

  const handleCardClick = (card: CardType) => {
    setSelectedCard(card)
  }

  const handleModalClose = () => {
    setSelectedCard(null)
  }

  const handlePurchase = async (values: PurchaseFormData) => {
    // 检查用户是否已登录
    if (!isAuthenticated) {
      navigate('/login')
      return
    }

    setSubmitting(true)
    setError(null)

    try {
      const purchaseData: SaleCreate = {
        card_name: values.card_name,
        user_email: values.user_email,
      }

      await api.post('/sales/purchase', purchaseData)

      message.success('购买成功！卡密已发送至您的邮箱，请查收。')
      navigate('/history')
      form.resetFields()
    } catch (err) {
      console.error('购买失败:', err)
      
      // 检查是否是401错误
      if (isAxiosError(err) && err.response?.status === 401) {
        Modal.confirm({
          title: '需要登录',
          content: '您需要登录后才能购买充值卡，是否前往登录页面？',
          okText: '去登录',
          cancelText: '取消',
          onOk: () => {
            navigate('/login')
          }
        })
        return
      }
      
      const errorMessage = resolveErrorMessage(err)
      setError(errorMessage)
      message.error(errorMessage)
    } finally {
      setSubmitting(false)
    }
  }

  if (isLoading) {
    return (
      <div style={{ textAlign: 'center', padding: '50px' }}>
        <Spin size="large" />
        <div style={{ marginTop: 16 }}>
          <Text type="secondary">正在加载充值卡列表...</Text>
        </div>
      </div>
    )
  }

  return (
    <div style={{ maxWidth: 1200, margin: '0 auto', padding: '24px' }}>
      <div style={{ textAlign: 'center', marginBottom: 48 }}>
        <Title level={2}>
          <CreditCardOutlined style={{ marginRight: 8 }} />
          发卡站
        </Title>
        <Paragraph type="secondary" style={{ fontSize: '16px' }}>
          选择您需要的充值卡，输入邮箱即可完成购买。卡密将通过邮件发送给您。
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

      <Row gutter={[24, 24]}>
        <Col xs={24} lg={12}>
          {/* 充值卡列表 */}
          <Card title="可购买的充值卡" bordered={false}>
            {cards.length === 0 ? (
              <div style={{ textAlign: 'center', padding: '40px' }}>
                <Text type="secondary">暂无可购买的充值卡</Text>
              </div>
            ) : (
              <Space direction="vertical" size="middle" style={{ width: '100%' }}>
                {cards.map((card) => (
                  <ProductCard
                    key={card.id}
                    card={card}
                    onClick={handleCardClick}
                  />
                ))}
              </Space>
            )}
          </Card>
        </Col>

        <Col xs={24} lg={12}>
          {/* 购买表单 */}
          <Card title="立即购买" variant={"outlined"}>
            <Form
              form={form}
              layout="vertical"
              onFinish={handlePurchase}
              requiredMark={false}
              autoComplete="off"
            >
              <Form.Item
                label="选择充值卡"
                name="card_name"
                rules={[{ required: true, message: '请选择要购买的充值卡' }]}
              >
                <Select
                  placeholder="请选择充值卡"
                  size="large"
                  disabled={cards.length === 0}
                >
                  {cards.map((card) => (
                    <Option key={card.name} value={card.name}>
                      {card.name} - ¥{card.price}
                    </Option>
                  ))}
                </Select>
              </Form.Item>

              <Form.Item
                label="邮箱地址"
                name="user_email"
                rules={[
                  { required: true, message: '请输入邮箱地址' },
                  { type: 'email', message: '请输入有效的邮箱地址' },
                ]}
              >
                <Input
                  size="large"
                  placeholder="请输入您的邮箱地址"
                  autoComplete="email"
                />
              </Form.Item>

              <Form.Item>
                <Button
                  type="primary"
                  htmlType="submit"
                  size="large"
                  icon={<ShoppingCartOutlined />}
                  loading={submitting}
                  block
                  disabled={cards.length === 0 || loading}
                >
                  {submitting ? '处理中...' : '立即购买'}
                </Button>
              </Form.Item>
            </Form>

            <div style={{ marginTop: 16, padding: 16, background: '#f6ffed', border: '1px solid #b7eb8f', borderRadius: 6 }}>
              <Text strong style={{ color: '#52c41a' }}>
                购买须知：
              </Text>
              <ul style={{ marginTop: 8, paddingLeft: 20, color: '#666' }}>
                <li>购买成功后，卡密将通过邮件发送至您提供的邮箱</li>
                <li>请确保邮箱地址正确，避免收不到卡密</li>
                <li>如有问题请联系客服</li>
              </ul>
            </div>
          </Card>
        </Col>
      </Row>

      {/* 商品详情模态框 */}
      <Modal
        title={selectedCard?.name}
        open={!!selectedCard}
        onCancel={handleModalClose}
        footer={null}
        width={600}
      >
        {selectedCard && (
          <div style={{ padding: '16px 0' }}>
            <div style={{ marginBottom: 24 }}>
              <Text strong style={{ fontSize: '18px', color: '#1890ff', marginRight: 16 }}>
                价格: ¥{selectedCard.price}
              </Text>
            </div>
            <div>
              <Text strong style={{ fontSize: '16px', marginBottom: 12, display: 'block' }}>
                商品详情:
              </Text>
              <div style={{ fontSize: '14px', lineHeight: 1.6 }}>
                <ReactMarkdown
                  components={{
                    p: ({ children }) => <p style={{ margin: '8px 0' }}>{children}</p>,
                    strong: ({ children }) => <strong style={{ color: '#1890ff' }}>{children}</strong>,
                    ul: ({ children }) => <ul style={{ paddingLeft: 20, margin: '8px 0' }}>{children}</ul>,
                    li: ({ children }) => <li style={{ margin: '4px 0' }}>{children}</li>,
                  }}
                >
                  {selectedCard.description}
                </ReactMarkdown>
              </div>
            </div>
          </div>
        )}
      </Modal>
    </div>
  )
}