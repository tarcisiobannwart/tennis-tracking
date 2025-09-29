import { useRef, useEffect, useState } from 'react'
import {
  Play,
  Pause,
  SkipBack,
  SkipForward,
  Volume2,
  VolumeX,
  Maximize,
  Settings,
  Eye,
  EyeOff
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { LiveFrame } from '@/types'
import { cn } from '@/utils/cn'

interface VideoPlayerProps {
  src?: string
  showOverlays?: boolean
  currentFrame?: LiveFrame | null
  onTimeUpdate?: (time: number) => void
  onPlay?: () => void
  onPause?: () => void
  className?: string
}

const VideoPlayer = ({
  src,
  showOverlays = true,
  currentFrame,
  onTimeUpdate,
  onPlay,
  onPause,
  className
}: VideoPlayerProps) => {
  const videoRef = useRef<HTMLVideoElement>(null)
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const containerRef = useRef<HTMLDivElement>(null)

  const [isPlaying, setIsPlaying] = useState(false)
  const [currentTime, setCurrentTime] = useState(0)
  const [duration, setDuration] = useState(0)
  const [volume, setVolume] = useState(1)
  const [isMuted, setIsMuted] = useState(false)
  const [isFullscreen] = useState(false)
  const [playbackRate, setPlaybackRate] = useState(1)
  const [overlaysVisible, setOverlaysVisible] = useState(showOverlays)

  // Update canvas overlays when frame changes
  useEffect(() => {
    if (!currentFrame || !canvasRef.current || !videoRef.current) return

    const canvas = canvasRef.current
    const ctx = canvas.getContext('2d')
    if (!ctx) return

    // Set canvas size to match video
    const video = videoRef.current
    canvas.width = video.videoWidth || 1280
    canvas.height = video.videoHeight || 720

    // Clear previous drawings
    ctx.clearRect(0, 0, canvas.width, canvas.height)

    if (!overlaysVisible) return

    // Draw ball position
    if (currentFrame.ballPosition) {
      const { x, y } = currentFrame.ballPosition
      ctx.beginPath()
      ctx.arc(x, y, 8, 0, 2 * Math.PI)
      ctx.fillStyle = '#FFEB3B'
      ctx.fill()
      ctx.strokeStyle = '#FF9800'
      ctx.lineWidth = 2
      ctx.stroke()

      // Ball trail
      ctx.beginPath()
      ctx.arc(x, y, 15, 0, 2 * Math.PI)
      ctx.strokeStyle = 'rgba(255, 235, 59, 0.3)'
      ctx.lineWidth = 1
      ctx.stroke()
    }

    // Draw player positions
    if (currentFrame.player1Position) {
      drawPlayer(ctx, currentFrame.player1Position, '#2196F3', 'P1')
    }
    if (currentFrame.player2Position) {
      drawPlayer(ctx, currentFrame.player2Position, '#F44336', 'P2')
    }

    // Draw court lines
    if (currentFrame.courtDetection?.lines) {
      ctx.strokeStyle = 'rgba(255, 255, 255, 0.8)'
      ctx.lineWidth = 2
      currentFrame.courtDetection.lines.forEach(line => {
        ctx.beginPath()
        ctx.moveTo(line.start.x, line.start.y)
        ctx.lineTo(line.end.x, line.end.y)
        ctx.stroke()
      })
    }

    // Draw predictions
    if (currentFrame.predictions.ballBounce && currentFrame.predictions.ballBounce.probability > 0.7) {
      const { position } = currentFrame.predictions.ballBounce
      ctx.beginPath()
      ctx.arc(position.x, position.y, 12, 0, 2 * Math.PI)
      ctx.strokeStyle = '#FF5722'
      ctx.lineWidth = 3
      ctx.setLineDash([5, 5])
      ctx.stroke()
      ctx.setLineDash([])

      // Bounce indicator text
      ctx.fillStyle = '#FF5722'
      ctx.font = '12px Arial'
      ctx.fillText('BOUNCE', position.x - 20, position.y - 20)
    }
  }, [currentFrame, overlaysVisible])

  const drawPlayer = (ctx: CanvasRenderingContext2D, position: { x: number; y: number }, color: string, label: string) => {
    // Player circle
    ctx.beginPath()
    ctx.arc(position.x, position.y, 20, 0, 2 * Math.PI)
    ctx.fillStyle = color
    ctx.fill()
    ctx.strokeStyle = 'white'
    ctx.lineWidth = 2
    ctx.stroke()

    // Player label
    ctx.fillStyle = 'white'
    ctx.font = 'bold 12px Arial'
    ctx.textAlign = 'center'
    ctx.fillText(label, position.x, position.y + 4)
  }

  const handlePlay = () => {
    if (videoRef.current) {
      videoRef.current.play()
      setIsPlaying(true)
      onPlay?.()
    }
  }

  const handlePause = () => {
    if (videoRef.current) {
      videoRef.current.pause()
      setIsPlaying(false)
      onPause?.()
    }
  }

  const handleTimeUpdate = () => {
    if (videoRef.current) {
      const time = videoRef.current.currentTime
      setCurrentTime(time)
      onTimeUpdate?.(time)
    }
  }

  const handleSeek = (time: number) => {
    if (videoRef.current) {
      videoRef.current.currentTime = time
      setCurrentTime(time)
    }
  }

  const handleVolumeChange = (newVolume: number) => {
    if (videoRef.current) {
      videoRef.current.volume = newVolume
      setVolume(newVolume)
      setIsMuted(newVolume === 0)
    }
  }

  const toggleMute = () => {
    if (videoRef.current) {
      const newMuted = !isMuted
      videoRef.current.muted = newMuted
      setIsMuted(newMuted)
    }
  }

  const toggleFullscreen = () => {
    if (!containerRef.current) return

    if (!isFullscreen) {
      containerRef.current.requestFullscreen()
    } else {
      document.exitFullscreen()
    }
  }

  const formatTime = (time: number) => {
    const minutes = Math.floor(time / 60)
    const seconds = Math.floor(time % 60)
    return `${minutes}:${seconds.toString().padStart(2, '0')}`
  }

  return (
    <div
      ref={containerRef}
      className={cn("relative bg-black rounded-lg overflow-hidden", className)}
    >
      {/* Video Element */}
      <video
        ref={videoRef}
        src={src}
        className="w-full h-full object-contain"
        onTimeUpdate={handleTimeUpdate}
        onLoadedMetadata={() => {
          if (videoRef.current) {
            setDuration(videoRef.current.duration)
          }
        }}
        onPlay={() => setIsPlaying(true)}
        onPause={() => setIsPlaying(false)}
        onVolumeChange={() => {
          if (videoRef.current) {
            setVolume(videoRef.current.volume)
            setIsMuted(videoRef.current.muted)
          }
        }}
      />

      {/* Canvas Overlay */}
      <canvas
        ref={canvasRef}
        className="absolute top-0 left-0 w-full h-full pointer-events-none"
        style={{ zIndex: 1 }}
      />

      {/* Controls Overlay */}
      <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/80 to-transparent p-4">
        {/* Progress Bar */}
        <div className="mb-4">
          <input
            type="range"
            min={0}
            max={duration}
            value={currentTime}
            onChange={(e) => handleSeek(Number(e.target.value))}
            className="w-full h-1 bg-white/20 rounded-lg appearance-none cursor-pointer"
          />
          <div className="flex justify-between text-xs text-white/70 mt-1">
            <span>{formatTime(currentTime)}</span>
            <span>{formatTime(duration)}</span>
          </div>
        </div>

        {/* Control Buttons */}
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            {/* Play/Pause */}
            <Button
              variant="ghost"
              size="icon"
              onClick={isPlaying ? handlePause : handlePlay}
              className="text-white hover:bg-white/20"
            >
              {isPlaying ? <Pause className="w-5 h-5" /> : <Play className="w-5 h-5" />}
            </Button>

            {/* Skip buttons */}
            <Button
              variant="ghost"
              size="icon"
              onClick={() => handleSeek(Math.max(0, currentTime - 10))}
              className="text-white hover:bg-white/20"
            >
              <SkipBack className="w-4 h-4" />
            </Button>

            <Button
              variant="ghost"
              size="icon"
              onClick={() => handleSeek(Math.min(duration, currentTime + 10))}
              className="text-white hover:bg-white/20"
            >
              <SkipForward className="w-4 h-4" />
            </Button>

            {/* Volume */}
            <div className="flex items-center space-x-2">
              <Button
                variant="ghost"
                size="icon"
                onClick={toggleMute}
                className="text-white hover:bg-white/20"
              >
                {isMuted ? <VolumeX className="w-4 h-4" /> : <Volume2 className="w-4 h-4" />}
              </Button>
              <input
                type="range"
                min={0}
                max={1}
                step={0.1}
                value={isMuted ? 0 : volume}
                onChange={(e) => handleVolumeChange(Number(e.target.value))}
                className="w-16 h-1"
              />
            </div>

            {/* Playback rate */}
            <select
              value={playbackRate}
              onChange={(e) => {
                const rate = Number(e.target.value)
                setPlaybackRate(rate)
                if (videoRef.current) {
                  videoRef.current.playbackRate = rate
                }
              }}
              className="bg-transparent text-white text-sm border border-white/20 rounded px-2 py-1"
            >
              <option value={0.25}>0.25x</option>
              <option value={0.5}>0.5x</option>
              <option value={1}>1x</option>
              <option value={1.25}>1.25x</option>
              <option value={1.5}>1.5x</option>
              <option value={2}>2x</option>
            </select>
          </div>

          <div className="flex items-center space-x-2">
            {/* Toggle overlays */}
            <Button
              variant="ghost"
              size="icon"
              onClick={() => setOverlaysVisible(!overlaysVisible)}
              className="text-white hover:bg-white/20"
            >
              {overlaysVisible ? <Eye className="w-4 h-4" /> : <EyeOff className="w-4 h-4" />}
            </Button>

            {/* Settings */}
            <Button
              variant="ghost"
              size="icon"
              className="text-white hover:bg-white/20"
            >
              <Settings className="w-4 h-4" />
            </Button>

            {/* Fullscreen */}
            <Button
              variant="ghost"
              size="icon"
              onClick={toggleFullscreen}
              className="text-white hover:bg-white/20"
            >
              <Maximize className="w-4 h-4" />
            </Button>
          </div>
        </div>
      </div>

      {/* Frame info overlay */}
      {currentFrame && (
        <div className="absolute top-4 right-4 bg-black/60 text-white p-2 rounded text-xs">
          Frame: {currentFrame.frameNumber} | Time: {(currentFrame.timestamp / 1000).toFixed(2)}s
        </div>
      )}
    </div>
  )
}

export default VideoPlayer