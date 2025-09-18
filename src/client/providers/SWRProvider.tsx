import { type ReactNode } from 'react'
import { SWRConfig } from 'swr'
import api from '../lib/api'

interface SWRProviderProps {
  children: ReactNode
}

export function SWRProvider({ children }: SWRProviderProps) {
  return (
    <SWRConfig
      value={{
        // 自定义 fetcher，使用已配置的 axios 实例
        fetcher: (url: string) => api.get(url).then(res => res.data),

        // 错误重试配置
        errorRetryCount: 3,
        errorRetryInterval: 1000,

        // 重新验证配置
        revalidateOnFocus: false,
        revalidateOnReconnect: true,

        // 缓存配置
        dedupingInterval: 2000,
      }}
    >
      {children}
    </SWRConfig>
  )
}