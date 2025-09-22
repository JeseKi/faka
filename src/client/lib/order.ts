// 定义与后端 OrderCreate 对应的 TypeScript 类型
interface OrderCreate {
  code: string;
  channel_id?: number | null;
  remarks?: string;
}

// 定义与后端 OrderOut 对应的 TypeScript 类型
interface OrderOut {
  id: number;
  activation_code: string;
  status: 'pending' | 'processing' | 'completed';
  created_at: string; // ISO 8601 格式日期时间字符串
  completed_at?: string | null; // ISO 8601 格式日期时间字符串或 null
  remarks?: string | null;
}

import api from './api'

// 检查卡密是否可用
export async function checkActivationCode(code: string): Promise<{ available: boolean; channel_id: number | null }> {
  const response = await api.get<{ available: boolean; channel_id: number | null }>(`/activation-codes/check`, {
    params: { code }
  })
  return response.data
}

// 创建订单
export async function createOrder(orderData: OrderCreate): Promise<OrderOut> {
  console.log('【订单 API】准备创建订单', { 卡密: orderData.code, 渠道ID: orderData.channel_id })
  const response = await api.post<OrderOut>('/orders/create', orderData)
  console.log('【订单 API】订单创建成功', { 订单ID: response.data.id })
  return response.data
}