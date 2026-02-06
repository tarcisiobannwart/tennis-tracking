import { useState, useCallback } from 'react'
import { useTranslation } from 'react-i18next'
import {
  Camera,
  Maximize2,
  Minimize2,
  Circle,
  Wifi,
  WifiOff,
  MonitorPlay,
} from 'lucide-react'
import { LiveStream } from '@/types'
import { streamService } from '@/services/streamService'
import HlsPlayer from './HlsPlayer'

interface MultiCameraGridProps {
  streams: LiveStream[]
  onStreamSelect?: (stream: LiveStream) => void
}

const MultiCameraGrid = ({ streams, onStreamSelect }: MultiCameraGridProps) => {
  const { t } = useTranslation()
  const [primaryStreamId, setPrimaryStreamId] = useState<string | null>(
    streams.find((s) => s.status === 'live')?.id || streams[0]?.id || null
  )
  const [expandedView, setExpandedView] = useState(false)
  const [streamStatuses, setStreamStatuses] = useState<
    Record<string, 'loading' | 'playing' | 'error' | 'ended'>
  >({})

  const primaryStream = streams.find((s) => s.id === primaryStreamId)
  const secondaryStreams = streams.filter((s) => s.id !== primaryStreamId)

  const handleStreamClick = useCallback(
    (stream: LiveStream) => {
      setPrimaryStreamId(stream.id)
      onStreamSelect?.(stream)
    },
    [onStreamSelect]
  )

  const handleStatusChange = useCallback(
    (streamId: string, status: 'loading' | 'playing' | 'error' | 'ended') => {
      setStreamStatuses((prev) => ({ ...prev, [streamId]: status }))
    },
    []
  )

  const getStatusColor = (status: LiveStream['status']) => {
    switch (status) {
      case 'live':
        return 'text-red-500'
      case 'waiting':
        return 'text-yellow-500'
      case 'ended':
        return 'text-gray-500'
    }
  }

  const getStatusIcon = (stream: LiveStream) => {
    const hlsStatus = streamStatuses[stream.id]
    if (stream.status === 'live' && hlsStatus === 'playing') {
      return <Wifi className="w-3 h-3 text-green-500" />
    }
    if (stream.status === 'live' && hlsStatus === 'loading') {
      return <Wifi className="w-3 h-3 text-yellow-500 animate-pulse" />
    }
    if (stream.status === 'waiting') {
      return <WifiOff className="w-3 h-3 text-yellow-500" />
    }
    return <WifiOff className="w-3 h-3 text-gray-500" />
  }

  if (streams.length === 0) {
    return (
      <div className="aspect-video bg-muted rounded-lg flex flex-col items-center justify-center">
        <MonitorPlay className="w-16 h-16 text-muted-foreground mb-4" />
        <p className="text-lg font-medium mb-2">Nenhuma camera ativa</p>
        <p className="text-sm text-muted-foreground">
          Conecte um dispositivo movel para iniciar o streaming
        </p>
      </div>
    )
  }

  return (
    <div className="space-y-3">
      {/* Primary Camera View */}
      <div className="relative rounded-lg overflow-hidden bg-black">
        <div className="aspect-video">
          {primaryStream && primaryStream.status === 'live' ? (
            <HlsPlayer
              src={streamService.getPublicHlsUrl(primaryStream.hls_url)}
              className="w-full h-full object-contain"
              onStatusChange={(status) =>
                handleStatusChange(primaryStream.id, status)
              }
            />
          ) : (
            <div className="w-full h-full flex items-center justify-center">
              <div className="text-center">
                <Camera className="w-12 h-12 text-muted-foreground mx-auto mb-2" />
                <p className="text-sm text-muted-foreground">
                  {primaryStream?.camera_label || 'Camera'} - Aguardando sinal
                </p>
              </div>
            </div>
          )}
        </div>

        {/* Primary Camera Overlay */}
        <div className="absolute top-3 left-3 flex items-center gap-2">
          <div className="bg-black/70 rounded-md px-2.5 py-1 flex items-center gap-1.5">
            {primaryStream && primaryStream.status === 'live' && (
              <Circle className="w-2.5 h-2.5 text-red-500 fill-red-500 animate-pulse" />
            )}
            <span className="text-xs font-medium text-white">
              {primaryStream?.camera_label || 'Camera'}
            </span>
          </div>
          {primaryStream && (
            <div className="bg-black/70 rounded-md px-2 py-1">
              <span className={`text-xs font-medium ${getStatusColor(primaryStream.status)}`}>
                {primaryStream.status.toUpperCase()}
              </span>
            </div>
          )}
        </div>

        {/* Expand/Collapse button */}
        <button
          onClick={() => setExpandedView(!expandedView)}
          className="absolute top-3 right-3 bg-black/70 rounded-md p-1.5 hover:bg-black/90 transition-colors"
        >
          {expandedView ? (
            <Minimize2 className="w-4 h-4 text-white" />
          ) : (
            <Maximize2 className="w-4 h-4 text-white" />
          )}
        </button>
      </div>

      {/* Secondary Cameras (Thumbnails) */}
      {!expandedView && secondaryStreams.length > 0 && (
        <div className="grid grid-cols-3 gap-2">
          {secondaryStreams.map((stream) => (
            <button
              key={stream.id}
              onClick={() => handleStreamClick(stream)}
              className="relative rounded-lg overflow-hidden bg-black aspect-video hover:ring-2 hover:ring-primary transition-all cursor-pointer"
            >
              {stream.status === 'live' ? (
                <HlsPlayer
                  src={streamService.getPublicHlsUrl(stream.hls_url)}
                  className="w-full h-full object-cover"
                  onStatusChange={(status) =>
                    handleStatusChange(stream.id, status)
                  }
                />
              ) : (
                <div className="w-full h-full flex items-center justify-center">
                  <Camera className="w-6 h-6 text-muted-foreground" />
                </div>
              )}

              {/* Thumbnail Overlay */}
              <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/80 to-transparent p-1.5">
                <div className="flex items-center justify-between">
                  <span className="text-[10px] font-medium text-white truncate">
                    {stream.camera_label}
                  </span>
                  {getStatusIcon(stream)}
                </div>
              </div>
            </button>
          ))}
        </div>
      )}
    </div>
  )
}

export default MultiCameraGrid
