import useSWR from 'swr'
import useSWRMutation from 'swr/mutation'
import api from '../lib/api'
import type { Card, CardCreate, CardUpdate } from '../lib/types'

// 获取充值卡列表
export function useCards(includeInactive = false) {
  const { data, error, isLoading, mutate } = useSWR<Card[]>(
    `/cards?include_inactive=${includeInactive}`,
    {
      revalidateOnFocus: false,
      dedupingInterval: 5000,
    }
  )

  return {
    cards: data || [],
    isLoading,
    error,
    mutate,
  }
}

// 创建充值卡
export function useCreateCard() {
  return useSWRMutation(
    '/cards',
    async (url: string, { arg }: { arg: CardCreate }) => {
      const { data } = await api.post<Card>(url, arg)
      return data
    }
  )
}

// 更新充值卡
export function useUpdateCard() {
  return useSWRMutation(
    '/cards',
    async (url: string, { arg }: { arg: { id: number; data: CardUpdate } }) => {
      const { data } = await api.put<Card>(`${url}/${arg.id}`, arg.data)
      return data
    }
  )
}

// 删除充值卡
export function useDeleteCard() {
  return useSWRMutation(
    '/cards',
    async (url: string, { arg }: { arg: number }) => {
      await api.delete(`${url}/${arg}`)
    }
  )
}

// 生成卡密
export function useGenerateCodes() {
  return useSWRMutation(
    '/cards',
    async (url: string, { arg }: { arg: { cardName: string; count: number } }) => {
      const { data } = await api.post(`${url}/${arg.cardName}/generate-codes`, {
        count: arg.count,
      })
      return data
    }
  )
}