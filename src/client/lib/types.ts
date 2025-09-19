export interface TokenResponse {
  access_token: string
  refresh_token: string
  token_type: string
}

export interface AuthTokens {
  accessToken: string
  refreshToken: string
}

export interface UserProfile {
  id: number
  username: string
  email: string
  name: string | null
  role: string
  status: string
}

export interface LoginPayload {
  username: string
  password: string
}

export interface RegisterPayload {
  username: string
  email: string
  password: string
}

export interface VerificationCodePayload {
  email: string
}

export interface RegisterWithCodePayload {
  username: string
  email: string
  password: string
  code: string
}

export interface UpdateProfilePayload {
  email?: string | null
  name?: string | null
}

export interface PasswordChangePayload {
  old_password: string
  new_password: string
}

export interface ItemPayload {
  name: string
}

export interface Item {
  id: number
  name: string
}

// 发卡站相关类型定义

// 充值卡类型
export interface Card {
  id: number
  name: string
  description: string
  price: number
  is_active: boolean
}

export interface CardCreate {
  name: string
  description: string
  price: number
  is_active?: boolean
}

export interface CardUpdate {
  name?: string
  description?: string
  price?: number
  is_active?: boolean
}

// 卡密类型
export interface ActivationCode {
  id: number
  card_name: string
  code: string
  is_used: boolean
  created_at: string
  used_at: string | null
}

export interface ActivationCodeCreate {
  card_name: string
  count: number
}

// 销售记录类型
export interface Sale {
  id: number
  activation_code: string
  user_email: string
  sale_price: number
  purchased_at: string
  card_name: string
}

// 销售统计类型
export interface SalesStats {
  total_sales: number
  total_revenue: number
  today_sales: number
  today_revenue: number
  total_stock: number
  pending_orders: number
}

export interface SaleCreate {
  card_name: string
  user_email: string
}

// 订单类型
export interface Order {
  id: number
  activation_code: string
  status: 'pending' | 'completed'
  created_at: string
  completed_at: string | null
  remarks: string | null
}

export interface OrderVerify {
  code: string
}

export interface OrderUpdate {
  status?: 'pending' | 'completed'
  remarks?: string
}
