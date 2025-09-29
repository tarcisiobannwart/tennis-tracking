import axios, { AxiosResponse } from 'axios'
import { ApiResponse, PaginatedResponse } from '@/types'

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
    // Check for token in localStorage
    const token = localStorage.getItem('token') || localStorage.getItem('auth_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

// Response interceptor for error handling
api.interceptors.response.use(
  (response: AxiosResponse<ApiResponse<any>>) => {
    return response
  },
  async (error) => {
    if (error.response?.status === 401) {
      // Handle unauthorized - redirect to login
      localStorage.removeItem('auth_token')
      window.location.href = '/login'
    }

    // Handle network errors
    if (!error.response) {
      console.error('Network error:', error.message)
    }

    return Promise.reject(error)
  }
)

// Generic API functions
export const apiGet = async <T>(url: string, params?: Record<string, any>): Promise<T> => {
  const response = await api.get<ApiResponse<T>>(url, { params })
  return response.data.data
}

export const apiPost = async <T>(url: string, data?: any): Promise<T> => {
  const response = await api.post<ApiResponse<T>>(url, data)
  return response.data.data
}

export const apiPut = async <T>(url: string, data?: any): Promise<T> => {
  const response = await api.put<ApiResponse<T>>(url, data)
  return response.data.data
}

export const apiDelete = async <T>(url: string): Promise<T> => {
  const response = await api.delete<ApiResponse<T>>(url)
  return response.data.data
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

  // Create a new instance without the default JSON content-type
  const uploadApi = axios.create({
    baseURL: '/api',
    timeout: 300000, // 5 minutes for uploads
  })

  // Add auth token if exists
  const token = localStorage.getItem('token') || localStorage.getItem('auth_token')
  if (token) {
    uploadApi.defaults.headers.common['Authorization'] = `Bearer ${token}`
  }

  const response = await uploadApi.post(url, formData, {
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