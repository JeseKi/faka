import api from './api'
import type { UserListResponse, AdminUserCreate, AdminUserUpdate, UserProfile, Role } from './types'

/**
 * 用户管理 API 库
 *
 * 公开接口：
 * - getUsers: 获取用户列表（支持按角色筛选）
 * - createUser: 创建新用户
 * - updateUser: 更新用户信息
 * - deleteUser: 删除用户
 * - getUserById: 获取指定用户详情
 *
 * 内部方法：
 * - 无内部方法，所有方法都是公开接口
 *
 * 公开接口的 pydantic 模型：
 * - UserListResponse: 用户列表响应模型
 * - AdminUserCreate: 用户创建模型
 * - AdminUserUpdate: 用户更新模型
 * - UserProfile: 用户资料模型
 * - Role: 用户角色枚举
 */
export async function getUsers(
  role?: Role,
  page: number = 1,
  pageSize: number = 50
): Promise<UserListResponse> {
  console.log('【User API】准备获取用户列表', { role, page, pageSize })
  const { data } = await api.get<UserListResponse>('/auth/admin/users', {
    params: {
      role: role || undefined,
      page,
      page_size: pageSize,
    },
  })
  console.log('【User API】获取用户列表成功', { total: data.total_count })
  return data
}

export async function createUser(payload: AdminUserCreate): Promise<UserProfile> {
  console.log('【User API】准备创建用户', { username: payload.username, role: payload.role })
  const { data } = await api.post<UserProfile>('/auth/admin/users', payload)
  console.log('【User API】创建用户成功', { id: data.id })
  return data
}

export async function updateUser(userId: number, payload: AdminUserUpdate): Promise<UserProfile> {
  console.log('【User API】准备更新用户', { userId })
  const { data } = await api.put<UserProfile>(`/auth/admin/users/${userId}`, payload)
  console.log('【User API】更新用户成功', { userId })
  return data
}

export async function deleteUser(userId: number): Promise<{ message: string }> {
  console.log('【User API】准备删除用户', { userId })
  const { data } = await api.delete<{ message: string }>(`/auth/admin/users/${userId}`)
  console.log('【User API】删除用户成功', { userId })
  return data
}

export async function getUserById(userId: number): Promise<UserProfile> {
  console.log('【User API】准备获取用户详情', { userId })
  const { data } = await api.get<UserProfile>(`/auth/admin/users/${userId}`)
  console.log('【User API】获取用户详情成功', { userId })
  return data
}