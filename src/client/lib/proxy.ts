import api from './api'
import type { UserListResponse, AdminUserCreate, AdminUserUpdate, UserProfile } from './types'

export async function getProxies(page: number = 1, pageSize: number = 50): Promise<UserListResponse> {
  console.log('【Proxy API】准备获取代理商列表', { page, pageSize })
  const { data } = await api.get<UserListResponse>('/auth/admin/users', {
    params: {
      role: 'proxy',
      page,
      page_size: pageSize,
    },
  })
  console.log('【Proxy API】获取代理商列表成功', { total: data.total_count })
  return data
}

export async function createProxy(payload: AdminUserCreate): Promise<UserProfile> {
  console.log('【Proxy API】准备创建代理商', { username: payload.username })
  const { data } = await api.post<UserProfile>('/auth/admin/users', payload)
  console.log('【Proxy API】创建代理商成功', { id: data.id })
  return data
}

export async function updateProxy(userId: number, payload: AdminUserUpdate): Promise<UserProfile> {
  console.log('【Proxy API】准备更新代理商', { userId })
  const { data } = await api.put<UserProfile>(`/auth/admin/users/${userId}`, payload)
  console.log('【Proxy API】更新代理商成功', { userId })
  return data
}

export async function deleteProxy(userId: number): Promise<{ message: string }> {
  console.log('【Proxy API】准备删除代理商', { userId })
  const { data } = await api.delete<{ message: string }>(`/auth/admin/users/${userId}`)
  console.log('【Proxy API】删除代理商成功', { userId })
  return data
}