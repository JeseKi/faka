// 定义与后端 OrderCreate 对应的 TypeScript 类型
interface OrderCreate {
  code: string;
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
export async function checkActivationCode(code: string): Promise<{ available: boolean }> {
  const response = await api.get<{ available: boolean }>(`/activation-codes/check`, {
    params: { code }
  })
  return response.data
}

// 创建订单
export async function createOrder(orderData: OrderCreate): Promise<OrderOut> {
  const response = await api.post<OrderOut>('/orders/create', orderData)
  return response.data
}