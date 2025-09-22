import api from './api'
import type {
  Channel,
  ChannelCreate,
  ChannelUpdate,
} from './types'

/**
 * 渠道管理 API 模块
 *
 * 公开接口：
 * - createChannel: 创建新渠道
 * - getChannel: 获取单个渠道详情
 * - getChannels: 获取渠道列表
 * - updateChannel: 更新渠道信息
 * - deleteChannel: 删除渠道
 *
 * 内部方法：
 * - 无内部方法
 *
 * 公开接口的 pydantic 模型：
 * - Channel: 渠道数据模型
 * - ChannelCreate: 创建渠道请求模型
 * - ChannelUpdate: 更新渠道请求模型
 *
 * 一般认为，一个文件中只应包含一个主要的功能类用于其他文件或模块使用。
 */

/**
 * 创建新渠道
 * @param payload 渠道创建数据
 * @returns 创建的渠道信息
 */
export async function createChannel(payload: ChannelCreate): Promise<Channel> {
  console.log('【渠道 API】准备创建渠道', { 渠道名称: payload.name })
  const { data } = await api.post<Channel>('/channels', payload)
  console.log('【渠道 API】渠道创建成功', { 渠道ID: data.id })
  return data
}

/**
 * 获取单个渠道详情
 * @param channelId 渠道ID
 * @returns 渠道详情信息
 */
export async function getChannel(channelId: number): Promise<Channel> {
  console.log('【渠道 API】准备获取渠道详情', { 渠道ID: channelId })
  const { data } = await api.get<Channel>(`/channels/${channelId}`)
  console.log('【渠道 API】渠道详情获取成功', { 渠道名称: data.name })
  return data
}

/**
 * 获取渠道列表
 * @param skip 跳过的记录数
 * @param limit 返回的记录数
 * @returns 渠道列表
 */
export async function getChannels(skip: number = 0, limit: number = 100): Promise<Channel[]> {
  console.log('【渠道 API】准备获取渠道列表', { skip, limit })
  const params = new URLSearchParams()
  params.append('skip', skip.toString())
  params.append('limit', limit.toString())
  const { data } = await api.get<Channel[]>(`/channels/?${params.toString()}`)
  console.log('【渠道 API】渠道列表获取成功', { 渠道数量: data.length })
  return data
}

/**
 * 更新渠道信息
 * @param channelId 渠道ID
 * @param payload 渠道更新数据
 * @returns 更新后的渠道信息
 */
export async function updateChannel(channelId: number, payload: ChannelUpdate): Promise<Channel> {
  console.log('【渠道 API】准备更新渠道', { 渠道ID: channelId, 更新数据: payload })
  const { data } = await api.put<Channel>(`/channels/${channelId}`, payload)
  console.log('【渠道 API】渠道更新成功', { 渠道名称: data.name })
  return data
}

/**
 * 删除渠道
 * @param channelId 渠道ID
 * @returns 删除的渠道信息
 */
export async function deleteChannel(channelId: number): Promise<Channel> {
  console.log('【渠道 API】准备删除渠道', { 渠道ID: channelId })
  const { data } = await api.delete<Channel>(`/channels/${channelId}`)
  console.log('【渠道 API】渠道删除成功', { 渠道ID: channelId })
  return data
}