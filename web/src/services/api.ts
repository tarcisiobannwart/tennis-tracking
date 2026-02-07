import axios, { AxiosResponse } from 'axios'
import { ApiResponse, PaginatedResponse } from '@/types'
import { useAuthStore } from '@/stores/authStore'
import { captureApiError } from '@/services/errorReporter'

// Create axios instance with default config
export const api = axios.create({
  baseURL: '/api',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor for auth tokens
api.interceptors.request.use(
  (config) => {
    const { accessToken } = useAuthStore.getState()
    if (accessToken) {
      config.headers.Authorization = `Bearer ${accessToken}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

// Response interceptor for error handling and token refresh
api.interceptors.response.use(
  (response: AxiosResponse) => {
    return response
  },
  async (error) => {
    const originalRequest = error.config

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true

      const { refreshToken, setTokens, setUser, logout } = useAuthStore.getState()

      if (refreshToken) {
        try {
          const response = await axios.post('/api/auth/refresh', null, {
            params: { refresh_token: refreshToken },
          })

          const { access_token, refresh_token: newRefresh, user } = response.data
          setTokens(access_token, newRefresh)
          if (user) setUser(user)

          originalRequest.headers.Authorization = `Bearer ${access_token}`
          return api(originalRequest)
        } catch {
          logout()
          window.location.href = '/login'
          return Promise.reject(error)
        }
      }

      logout()
      window.location.href = '/login'
    }

    // Handle network errors and 5xx - report to error tracking
    const url = error.config?.url || 'unknown'
    const method = error.config?.method || 'unknown'
    if (!error.response) {
      console.error('Network error:', error.message)
      captureApiError(undefined, url, method, error.message || 'Network error')
    } else if (error.response.status >= 500) {
      captureApiError(error.response.status, url, method, error.response.data?.message || `HTTP ${error.response.status}`)
    }

    return Promise.reject(error)
  }
)

// Generic API functions
export const apiGet = async <T>(url: string, params?: Record<string, any>): Promise<T> => {
  const response = await api.get<T>(url, { params })
  return response.data
}

export const apiPost = async <T>(url: string, data?: any): Promise<T> => {
  const response = await api.post<T>(url, data)
  return response.data
}

export const apiPut = async <T>(url: string, data?: any): Promise<T> => {
  const response = await api.put<T>(url, data)
  return response.data
}

export const apiDelete = async <T>(url: string): Promise<T> => {
  const response = await api.delete<T>(url)
  return response.data
}

export const apiGetPaginated = async <T>(
  url: string,
  params?: Record<string, any>
): Promise<PaginatedResponse<T>> => {
  const response = await api.get<ApiResponse<PaginatedResponse<T>>>(url, { params })
  return response.data.data
}

// Upload file with progress
export const uploadFile = async (
  url: string,
  file: File,
  onProgress?: (progress: number) => void
): Promise<any> => {
  const formData = new FormData()
  formData.append('file', file)

  const { accessToken } = useAuthStore.getState()

  const response = await api.post(url, formData, {
    timeout: 300000, // 5 minutes for uploads
    headers: {
      'Content-Type': 'multipart/form-data',
      ...(accessToken ? { Authorization: `Bearer ${accessToken}` } : {}),
    },
    onUploadProgress: (progressEvent) => {
      if (onProgress && progressEvent.total) {
        const progress = (progressEvent.loaded / progressEvent.total) * 100
        onProgress(progress)
      }
    },
  })

  return response.data
}

export default api
