import React from 'react'
import { Card, Typography } from 'antd'
import ReactMarkdown from 'react-markdown'
import type { Card as CardType } from '../../lib/types'

const { Text } = Typography

interface ProductCardProps {
  card: CardType
  onClick: (card: CardType) => void
}

export default function ProductCard({ card, onClick }: ProductCardProps) {
  return (
    <Card
      size="small"
      style={{
        border: '1px solid #f0f0f0',
        background: '#fafafa',
        cursor: 'pointer',
        transition: 'all 0.3s ease',
      }}
      onClick={() => onClick(card)}
      hoverable
    >
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <div style={{ flex: 1, marginRight: 16 }}>
          <Text strong style={{ fontSize: '16px', display: 'block', marginBottom: 8 }}>
            {card.name}
          </Text>
          <div style={{ fontSize: '14px', color: '#666' }}>
            <ReactMarkdown
              components={{
                p: ({ children }) => <p style={{ margin: 0, lineHeight: 1.5 }}>{children}</p>,
                strong: ({ children }) => <strong style={{ color: '#1890ff' }}>{children}</strong>,
              }}
            >
              {card.description}
            </ReactMarkdown>
          </div>
        </div>
        <div style={{ textAlign: 'right', whiteSpace: 'nowrap' }}>
          <Text strong style={{ fontSize: '18px', color: '#1890ff' }}>
            ¥{card.price}
          </Text>
        </div>
      </div>
    </Card>
  )
}