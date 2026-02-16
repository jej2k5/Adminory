import { useEffect } from 'react'
import { useAuthStore } from '@/stores/authStore'
import { apiClient } from '@/lib/api'

export function useAuth() {
  const {
    user,
    isAuthenticated,
    isLoading,
    error,
    login,
    register,
    logout,
    refreshToken,
    setUser,
    setError,
  } = useAuthStore()

  // Fetch current user on mount if authenticated
  useEffect(() => {
    const fetchCurrentUser = async () => {
      if (isAuthenticated && !user) {
        try {
          const currentUser = await apiClient.get<any>('/api/auth/me')
          setUser(currentUser)
        } catch (error) {
          console.error('Failed to fetch current user:', error)
          // Token might be expired, try refresh
          await refreshToken()
        }
      }
    }

    fetchCurrentUser()
  }, [isAuthenticated, user, setUser, refreshToken])

  return {
    user,
    isAuthenticated,
    isLoading,
    error,
    login,
    register,
    logout,
    setError,
    // Computed properties
    isAdmin: user?.role === 'admin' || user?.role === 'super_admin',
    isSuperAdmin: user?.role === 'super_admin',
    isEmailVerified: !!user?.email_verified_at,
  }
}
