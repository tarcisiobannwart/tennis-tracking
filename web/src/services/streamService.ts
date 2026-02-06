import api from './api'
import { LiveStream, StreamListResponse, StreamDeviceInfo } from '@/types'

interface CreateStreamRequest {
  match_id?: string
  camera_label?: string
  device_info?: StreamDeviceInfo
}

export const streamService = {
  async createStream(data: CreateStreamRequest): Promise<LiveStream> {
    const response = await api.post('/streams', data)
    return response.data
  },

  async listStreams(params?: {
    status?: string
    match_id?: string
  }): Promise<StreamListResponse> {
    const response = await api.get('/streams', { params })
    return response.data
  },

  async getActiveStreams(): Promise<StreamListResponse> {
    const response = await api.get('/streams/active')
    return response.data
  },

  async getStream(streamId: string): Promise<LiveStream> {
    const response = await api.get(`/streams/${streamId}`)
    return response.data
  },

  async getMatchStreams(matchId: string): Promise<StreamListResponse> {
    const response = await api.get(`/streams/match/${matchId}`)
    return response.data
  },

  async endStream(streamId: string): Promise<void> {
    await api.delete(`/streams/${streamId}`)
  },

  async toggleRecording(
    streamId: string,
    action: 'start' | 'stop'
  ): Promise<{ is_recording: boolean }> {
    const response = await api.post(`/streams/${streamId}/record`, { action })
    return response.data
  },

  async syncStatus(streamId: string): Promise<LiveStream> {
    const response = await api.post(`/streams/${streamId}/sync`)
    return response.data
  },

  getPublicHlsUrl(hlsUrl: string): string {
    // Convert internal MediaMTX URL to public-facing URL
    const mediamtxHlsBase = import.meta.env.VITE_MEDIAMTX_HLS_URL || 'http://localhost:8888'
    // The hlsUrl from API uses internal docker URL, replace with public
    const path = hlsUrl.replace(/^https?:\/\/[^/]+/, '')
    return `${mediamtxHlsBase}${path}`
  },
}
