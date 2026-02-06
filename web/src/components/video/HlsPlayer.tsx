import { useEffect, useRef, useState } from 'react'
import Hls from 'hls.js'

interface HlsPlayerProps {
  src: string
  autoPlay?: boolean
  muted?: boolean
  className?: string
  onStatusChange?: (status: 'loading' | 'playing' | 'error' | 'ended') => void
}

const HlsPlayer = ({
  src,
  autoPlay = true,
  muted = true,
  className = '',
  onStatusChange,
}: HlsPlayerProps) => {
  const videoRef = useRef<HTMLVideoElement>(null)
  const hlsRef = useRef<Hls | null>(null)
  const [status, setStatus] = useState<'loading' | 'playing' | 'error' | 'ended'>('loading')

  useEffect(() => {
    const video = videoRef.current
    if (!video || !src) return

    const updateStatus = (s: typeof status) => {
      setStatus(s)
      onStatusChange?.(s)
    }

    updateStatus('loading')

    if (Hls.isSupported()) {
      const hls = new Hls({
        enableWorker: true,
        lowLatencyMode: true,
        liveSyncDurationCount: 3,
        liveMaxLatencyDurationCount: 6,
        liveDurationInfinity: true,
        highBufferWatchdogPeriod: 1,
      })

      hls.loadSource(src)
      hls.attachMedia(video)

      hls.on(Hls.Events.MANIFEST_PARSED, () => {
        if (autoPlay) {
          video.play().catch(() => {
            // Autoplay blocked, try muted
            video.muted = true
            video.play().catch(() => {})
          })
        }
      })

      hls.on(Hls.Events.FRAG_CHANGED, () => {
        updateStatus('playing')
      })

      hls.on(Hls.Events.ERROR, (_event, data) => {
        if (data.fatal) {
          switch (data.type) {
            case Hls.ErrorTypes.NETWORK_ERROR:
              hls.startLoad()
              break
            case Hls.ErrorTypes.MEDIA_ERROR:
              hls.recoverMediaError()
              break
            default:
              updateStatus('error')
              hls.destroy()
              break
          }
        }
      })

      hlsRef.current = hls

      return () => {
        hls.destroy()
        hlsRef.current = null
      }
    } else if (video.canPlayType('application/vnd.apple.mpegurl')) {
      // Native HLS support (Safari)
      video.src = src
      video.addEventListener('loadedmetadata', () => {
        if (autoPlay) {
          video.play().catch(() => {})
        }
      })
      video.addEventListener('playing', () => updateStatus('playing'))
      video.addEventListener('error', () => updateStatus('error'))
    }
  }, [src, autoPlay])

  return (
    <video
      ref={videoRef}
      className={className}
      autoPlay={autoPlay}
      muted={muted}
      playsInline
      controls={false}
    />
  )
}

export default HlsPlayer
