import React, { createContext, useCallback, useContext, useEffect, useState } from 'react'
import { getMe, login, logout, register, tryRestoreSession } from '@/api/auth'
import type { User } from '@/types'

interface AuthState {
  user: User | null
  loading: boolean
}

interface AuthContextValue extends AuthState {
  login: (email: string, password: string) => Promise<void>
  register: (email: string, password: string, fullName?: string) => Promise<void>
  logout: () => Promise<void>
}

const AuthContext = createContext<AuthContextValue | null>(null)

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [state, setState] = useState<AuthState>({ user: null, loading: true })

  // Attempt to restore session from stored refresh token on mount
  useEffect(() => {
    tryRestoreSession()
      .then((user) => setState({ user, loading: false }))
      .catch(() => setState({ user: null, loading: false }))
  }, [])

  const handleLogin = useCallback(async (email: string, password: string) => {
    await login(email, password)
    const user = await getMe()
    setState({ user, loading: false })
  }, [])

  const handleRegister = useCallback(
    async (email: string, password: string, fullName?: string) => {
      await register(email, password, fullName)
      const user = await getMe()
      setState({ user, loading: false })
    },
    [],
  )

  const handleLogout = useCallback(async () => {
    await logout()
    setState({ user: null, loading: false })
  }, [])

  return (
    <AuthContext.Provider
      value={{
        user: state.user,
        loading: state.loading,
        login: handleLogin,
        register: handleRegister,
        logout: handleLogout,
      }}
    >
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used inside <AuthProvider>')
  return ctx
}
