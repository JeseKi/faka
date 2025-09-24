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
  channel_id: number | null
}

export interface CardCreate {
  name: string
  description: string
  price: number
  is_active?: boolean
  channel_id?: number | null
}

export interface CardUpdate {
  name?: string
  description?: string
  price?: number
  is_active?: boolean
  channel_id?: number | null
}


export interface ActivationCodeCreate {
  card_id: number
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
  status: 'pending' | 'processing' | 'completed'
  created_at: string
  completed_at: string | null
  remarks: string | null
  channel_id: number | null
  card_name: string | null
}

export interface OrderVerify {
  code: string
}

export interface OrderUpdate {
  status?: 'pending' | 'processing' | 'completed'
  remarks?: string
}

// 渠道类型
export interface Channel {
  id: number
  name: string
  description: string | null
}

export interface ChannelCreate {
  name: string
  description?: string | null
}

export interface ChannelUpdate {
  name?: string
  description?: string | null
}

// 代理商相关类型
export interface UserListResponse {
  users: UserProfile[]
  total_count: number
}

export interface AdminUserCreate {
  username: string
  email: string
  password: string
  role: string
  channel_id?: number | null
}

export interface AdminUserUpdate {
  email?: string | null
  name?: string | null
  role?: string | null
  status?: string | null
  channel_id?: number | null
}

// 代理商卡密相关类型
export interface CardSummary {
  id: number
  name: string
  price: number
}

export interface ActivationCode {
  id: number
  card_id: number
  card: CardSummary
  code: string
  status: 'available' | 'consuming' | 'consumed'
  created_at: string
  used_at: string | null
  exported: boolean
}

export interface AvailableActivationCodesResponse {
  codes: ActivationCode[]
  total_count: number
}

export interface ActivationCodeExport {
  code_ids: number[]
}
