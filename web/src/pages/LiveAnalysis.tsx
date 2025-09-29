import { useState } from 'react'
import {
  Play,
  Pause,
  Square,
  Settings,
  Maximize,
  RotateCcw,
  Activity,
  Radio,
  Video,
  Eye,
  Target,
  Upload
} from 'lucide-react'
import { useTranslation } from 'react-i18next'
import { useLiveStore } from '@/stores/liveStore'
import { useUIStore } from '@/stores/uiStore'
import { useWebSocket } from '@/hooks/useWebSocket'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import VideoPlayer from '@/components/video/VideoPlayer'
import CourtView from '@/components/court/CourtView'
import LiveStats from '@/components/stats/LiveStats'
import ScoreBoard from '@/components/stats/ScoreBoard'
import EventTimeline from '@/components/stats/EventTimeline'
import VideoUploadModal from '@/components/modals/VideoUploadModal'

const LiveAnalysis = () => {
  const { t } = useTranslation()
  const [selectedCamera, setSelectedCamera] = useState<string | null>(null)
  const [isFullscreen, setIsFullscreen] = useState(false)
  const [showUploadModal, setShowUploadModal] = useState(false)

  const {
    isConnected,
    currentMatch,
    currentFrame,
    isRecording,
    isAnalyzing,
    videoUrl,
    setIsRecording,
    setIsAnalyzing,
    reset
  } = useLiveStore()

  const { setModal } = useUIStore()

  // WebSocket connection for live data (temporarily disabled to prevent infinite loop)
  const { send } = useWebSocket({
    url: 'ws://localhost:8000/ws/live',
    enabled: false, // Disabled until WebSocket endpoint is properly configured
    onConnect: () => {
      console.log('Connected to live analysis')
    },
    onDisconnect: () => {
      console.log('Disconnected from live analysis')
    },
    onError: (error) => {
      console.error('WebSocket error:', error)
    }
  })

  // Camera selection
  const selectCamera = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: {
          width: 1280,
          height: 720,
          facingMode: 'environment' // Back camera on mobile
        }
      })

      const videoElement = document.getElementById('live-video') as HTMLVideoElement
      if (videoElement) {
        videoElement.srcObject = stream
        setSelectedCamera('camera')
      }
    } catch (error) {
      console.error('Error accessing camera:', error)
    }
  }

  // Control functions
  const startRecording = () => {
    setIsRecording(true)
    send({ type: 'start_recording' })
  }

  const stopRecording = () => {
    setIsRecording(false)
    send({ type: 'stop_recording' })
  }

  const startAnalysis = () => {
    setIsAnalyzing(true)
    send({ type: 'start_analysis' })
  }

  const stopAnalysis = () => {
    setIsAnalyzing(false)
    send({ type: 'stop_analysis' })
  }

  const resetSession = () => {
    reset()
    send({ type: 'reset_session' })
  }

  return (
    <div className="min-h-screen bg-background p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2">
            <Radio className={`w-5 h-5 ${isConnected ? 'text-green-500' : 'text-red-500'}`} />
            <span className="text-sm font-medium">
              {isConnected ? t('liveAnalysis.status.connected') : t('liveAnalysis.status.disconnected')}
            </span>
          </div>
          {currentMatch && (
            <div className="text-sm text-muted-foreground">
              {currentMatch.player1.name} vs {currentMatch.player2.name}
            </div>
          )}
        </div>

        <div className="flex items-center space-x-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => setModal('matchSettings', true)}
          >
            <Settings className="w-4 h-4 mr-2" />
            {t('liveAnalysis.controls.settings')}
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={() => setIsFullscreen(!isFullscreen)}
          >
            <Maximize className="w-4 h-4 mr-2" />
            {isFullscreen ? t('liveAnalysis.controls.exitFullscreen') : t('liveAnalysis.controls.fullscreen')}
          </Button>
        </div>
      </div>

      {/* Main Layout */}
      <div className={`grid gap-6 ${isFullscreen ? 'grid-cols-1' : 'grid-cols-12'}`}>
        {/* Video Feed - Main Area */}
        <div className={`${isFullscreen ? 'col-span-1' : 'col-span-8'} space-y-4`}>
          {/* Video Player */}
          <Card className="relative">
            <CardContent className="p-0">
              {videoUrl || selectedCamera ? (
                <VideoPlayer
                  src={videoUrl || undefined}
                  showOverlays={true}
                  currentFrame={currentFrame}
                  onTimeUpdate={(_time) => {
                    // Handle time updates
                  }}
                />
              ) : (
                <div className="aspect-video bg-muted rounded-lg flex flex-col items-center justify-center">
                  <Video className="w-16 h-16 text-muted-foreground mb-4" />
                  <p className="text-lg font-medium mb-2">{t('liveAnalysis.analysis.noVideoSource')}</p>
                  <p className="text-sm text-muted-foreground mb-6">
                    {t('liveAnalysis.analysis.selectSourceMessage')}
                  </p>
                  <div className="flex space-x-2">
                    <Button onClick={selectCamera}>
                      <Video className="w-4 h-4 mr-2" />
                      {t('liveAnalysis.buttons.useCamera')}
                    </Button>
                    <Button variant="outline" onClick={() => setShowUploadModal(true)}>
                      <Upload className="w-4 h-4 mr-2" />
                      {t('liveAnalysis.controls.uploadVideo')}
                    </Button>
                  </div>
                </div>
              )}

              {/* Hidden video element for camera feed */}
              <video
                id="live-video"
                autoPlay
                muted
                className="hidden"
              />
            </CardContent>
          </Card>

          {/* Controls */}
          <Card>
            <CardContent className="p-4">
              <div className="flex items-center justify-center space-x-4">
                {!isRecording ? (
                  <Button onClick={startRecording} size="lg">
                    <Play className="w-5 h-5 mr-2" />
                    {t('liveAnalysis.controls.startRecording')}
                  </Button>
                ) : (
                  <Button onClick={stopRecording} variant="destructive" size="lg">
                    <Square className="w-5 h-5 mr-2" />
                    {t('liveAnalysis.controls.stopRecording')}
                  </Button>
                )}

                {!isAnalyzing ? (
                  <Button onClick={startAnalysis} variant="court" size="lg">
                    <Activity className="w-5 h-5 mr-2" />
                    {t('liveAnalysis.buttons.startAnalysis')}
                  </Button>
                ) : (
                  <Button onClick={stopAnalysis} variant="outline" size="lg">
                    <Pause className="w-5 h-5 mr-2" />
                    {t('liveAnalysis.buttons.stopAnalysis')}
                  </Button>
                )}

                <Button onClick={resetSession} variant="outline">
                  <RotateCcw className="w-4 h-4 mr-2" />
                  {t('liveAnalysis.buttons.reset')}
                </Button>
              </div>

              {/* Status indicators */}
              <div className="flex items-center justify-center space-x-6 mt-4 text-sm">
                <div className="flex items-center space-x-2">
                  <div className={`w-2 h-2 rounded-full ${isRecording ? 'bg-red-500 animate-pulse' : 'bg-gray-300'}`} />
                  <span className={isRecording ? 'text-red-500' : 'text-muted-foreground'}>
                    {t('liveAnalysis.recording.recording')}
                  </span>
                </div>
                <div className="flex items-center space-x-2">
                  <div className={`w-2 h-2 rounded-full ${isAnalyzing ? 'bg-green-500 animate-pulse' : 'bg-gray-300'}`} />
                  <span className={isAnalyzing ? 'text-green-500' : 'text-muted-foreground'}>
                    {t('liveAnalysis.analysis.analyzing')}
                  </span>
                </div>
                <div className="flex items-center space-x-2">
                  <Target className="w-4 h-4" />
                  <span className="text-muted-foreground">
                    {t('liveAnalysis.analysis.ballTracking')}: {currentFrame?.ballPosition ? t('liveAnalysis.analysis.active') : t('liveAnalysis.analysis.inactive')}
                  </span>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Court View */}
          {!isFullscreen && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <Eye className="w-5 h-5 mr-2" />
                  {t('liveAnalysis.analysis.courtView')}
                </CardTitle>
              </CardHeader>
              <CardContent>
                <CourtView
                  ballPosition={currentFrame?.ballPosition}
                  player1Position={currentFrame?.player1Position}
                  player2Position={currentFrame?.player2Position}
                  courtDetection={currentFrame?.courtDetection}
                />
              </CardContent>
            </Card>
          )}
        </div>

        {/* Right Panel - Stats and Controls */}
        {!isFullscreen && (
          <div className="col-span-4 space-y-4">
            {/* Score Board */}
            {currentMatch && (
              <ScoreBoard match={currentMatch} />
            )}

            {/* Live Statistics */}
            <LiveStats
              currentFrame={currentFrame}
              isAnalyzing={isAnalyzing}
            />

            {/* Event Timeline */}
            <EventTimeline
              events={currentMatch?.statistics.events || []}
              currentTime={currentFrame?.timestamp || 0}
            />
          </div>
        )}
      </div>

      {/* Video Upload Modal */}
      <VideoUploadModal
        isOpen={showUploadModal}
        onClose={() => setShowUploadModal(false)}
        onUploadSuccess={(data) => {
          console.log('Upload success:', data)
          // Aqui você pode processar o resultado do upload
          // Por exemplo, iniciar a análise do vídeo
        }}
      />
    </div>
  )
}

export default LiveAnalysis