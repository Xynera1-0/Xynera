import axios from 'axios'

const BASE_URL = import.meta.env.VITE_API_URL ?? ''

export const apiClient = axios.create({
  baseURL: BASE_URL,
  headers: { 'Content-Type': 'application/json' },
})

// Attach access token from memory on every request
apiClient.interceptors.request.use((config) => {
  const token = tokenStore.getAccessToken()
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// On 401, attempt a silent refresh then retry once
apiClient.interceptors.response.use(
  (res) => res,
  async (error) => {
    const original = error.config
    if (error.response?.status === 401 && !original._retry) {
      original._retry = true
      try {
        const refreshToken = tokenStore.getRefreshToken()
        if (!refreshToken) throw new Error('No refresh token')

        const { data } = await axios.post(`${BASE_URL}/auth/refresh`, {
          refresh_token: refreshToken,
        })
        tokenStore.setTokens(data.access_token, data.refresh_token)
        original.headers.Authorization = `Bearer ${data.access_token}`
        return apiClient(original)
      } catch {
        tokenStore.clear()
        window.location.href = '/login'
      }
    }
    return Promise.reject(error)
  },
)

// ── In-memory token store ──────────────────────────────────────────────────
// Access token: memory only (never persisted to localStorage)
// Refresh token: localStorage (acceptable trade-off for UX, rotated on use)
const _REFRESH_KEY = 'xynera_rt'

export const tokenStore = {
  _accessToken: null as string | null,

  getAccessToken(): string | null {
    return this._accessToken
  },

  getRefreshToken(): string | null {
    return localStorage.getItem(_REFRESH_KEY)
  },

  setTokens(access: string, refresh: string) {
    this._accessToken = access
    localStorage.setItem(_REFRESH_KEY, refresh)
  },

  clear() {
    this._accessToken = null
    localStorage.removeItem(_REFRESH_KEY)
  },
}
