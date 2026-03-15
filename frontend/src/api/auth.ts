import { apiClient, tokenStore } from './client'
import type { TokenResponse, User } from '@/types'

export async function register(
  email: string,
  password: string,
  fullName?: string,
): Promise<TokenResponse> {
  const { data } = await apiClient.post<TokenResponse>('/auth/register', {
    email,
    password,
    full_name: fullName ?? null,
  })
  tokenStore.setTokens(data.access_token, data.refresh_token)
  return data
}

export async function login(email: string, password: string): Promise<TokenResponse> {
  const { data } = await apiClient.post<TokenResponse>('/auth/login', { email, password })
  tokenStore.setTokens(data.access_token, data.refresh_token)
  return data
}

export async function logout(): Promise<void> {
  const refreshToken = tokenStore.getRefreshToken()
  if (refreshToken) {
    await apiClient.post('/auth/logout', { refresh_token: refreshToken }).catch(() => {})
  }
  tokenStore.clear()
}

export async function getMe(): Promise<User> {
  const { data } = await apiClient.get<User>('/auth/me')
  return data
}

export async function tryRestoreSession(): Promise<User | null> {
  const rt = tokenStore.getRefreshToken()
  if (!rt) return null
  try {
    const { data } = await apiClient.post<TokenResponse>('/auth/refresh', { refresh_token: rt })
    tokenStore.setTokens(data.access_token, data.refresh_token)
    return await getMe()
  } catch {
    tokenStore.clear()
    return null
  }
}
