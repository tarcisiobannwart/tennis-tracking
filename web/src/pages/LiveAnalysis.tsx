import { useState, useEffect, useCallback, useMemo, useRef } from 'react'
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
  Upload,
  PlusCircle,
  RefreshCw,
} from 'lucide-react'
import { useTranslation } from 'react-i18next'
import toast from 'react-hot-toast'
import { useLiveStore } from '@/stores/liveStore'
import { useUIStore } from '@/stores/uiStore'
import { useWebSocket } from '@/hooks/useWebSocket'
import { getWebSocketUrl } from '@/services/websocketService'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import VideoPlayer from '@/components/video/VideoPlayer'
import MultiCameraGrid from '@/components/video/MultiCameraGrid'
import CourtView from '@/components/court/CourtView'
import LiveStats from '@/components/stats/LiveStats'
import ScoreBoard from '@/components/stats/ScoreBoard'
import EventTimeline from '@/components/stats/EventTimeline'
import VideoUploadModal from '@/components/modals/VideoUploadModal'
import { PageTransition } from '@/components/animations'
import { streamService } from '@/services/streamService'
import { LiveStream } from '@/types'

const LiveAnalysis = () => {
  const { t } = useTranslation()
  const [cameraStream, setCameraStream] = useState<MediaStream | null>(null)
  const [isFullscreen, setIsFullscreen] = useState(false)
  const [showUploadModal, setShowUploadModal] = useState(false)
  const [viewMode, setViewMode] = useState<'camera' | 'multi-stream' | 'upload'>('multi-stream')
  const [streams, setStreams] = useState<LiveStream[]>([])
  const [loadingStreams, setLoadingStreams] = useState(false)
  const cameraVideoRef = useRef<HTMLVideoElement>(null)

  const {
    connectionStatus,
    currentMatch,
    currentFrame,
    scoreboard,
    lastScoringEvent,
    isRecording,
    isAnalyzing,
    videoUrl,
    setIsRecording,
    setIsAnalyzing,
    reset
  } = useLiveStore()

  const { setModal } = useUIStore()

  // Get match ID from currentMatch or use a default for testing
  const matchId = currentMatch?.id || 'test-match-id'

  // WebSocket connection for live scoring
  const wsUrl = useMemo(
    () => getWebSocketUrl(`/ws/live/${matchId}`),
    [matchId]
  )
  const { send } = useWebSocket({
    url: wsUrl,
    enabled: true,
    matchId,
    enablePollingFallback: true,
    pollingInterval: 5000,
    onConnect: () => {
      console.log('Connected to live match WebSocket', matchId)
    },
    onDisconnect: () => {
      console.log('Disconnected from live match WebSocket')
    },
    onError: (error) => {
      console.error('WebSocket error:', error)
    }
  })

  // Fetch active streams
  const fetchStreams = useCallback(async () => {
    setLoadingStreams(true)
    try {
      const response = await streamService.listStreams()
      setStreams(response.streams)
    } catch (error) {
      console.error('Error fetching streams:', error)
    } finally {
      setLoadingStreams(false)
    }
  }, [])

  useEffect(() => {
    fetchStreams()
    // Refresh streams every 10 seconds
    const interval = setInterval(fetchStreams, 10000)
    return () => clearInterval(interval)
  }, [fetchStreams])

  // Handle scoring events with visual notifications
  useEffect(() => {
    if (!lastScoringEvent) return

    const { event_type, data } = lastScoringEvent

    switch (event_type) {
      case 'point_scored':
        // Just update scoreboard, no toast for every point
        break

      case 'game_won':
        if (data.winner_player_id) {
          toast.success(`Game won!`, {
            icon: '🎾',
            duration: 3000,
          })
        }
        break

      case 'set_won':
        if (data.winner_player_id) {
          toast.success(`Set won!`, {
            icon: '🏆',
            duration: 4000,
          })
        }
        break

      case 'match_completed':
        if (data.winner_player_id) {
          toast.success(`Match completed!`, {
            icon: '🎉',
            duration: 5000,
          })
        }
        break

      case 'match_paused':
        toast(`Match paused${data.reason ? `: ${data.reason}` : ''}`, {
          icon: '⏸️',
          duration: 3000,
        })
        break

      case 'match_resumed':
        toast('Match resumed', {
          icon: '▶️',
          duration: 2000,
        })
        break
    }
  }, [lastScoringEvent])

  // Camera selection (local camera)
  const selectCamera = async () => {
    try {
      // Parar stream anterior se existir
      if (cameraStream) {
        cameraStream.getTracks().forEach(track => track.stop())
      }

      const stream = await navigator.mediaDevices.getUserMedia({
        video: {
          width: 1280,
          height: 720,
          facingMode: 'environment'
        }
      })

      setCameraStream(stream)
      setViewMode('camera')
    } catch (error) {
      console.error('Error accessing camera:', error)
      toast.error('Erro ao acessar a camera. Verifique as permissoes.')
    }
  }

  // Atribuir stream ao video element quando disponivel
  useEffect(() => {
    if (cameraVideoRef.current && cameraStream) {
      cameraVideoRef.current.srcObject = cameraStream
    }
  }, [cameraStream, viewMode])

  // Limpar camera ao desmontar
  useEffect(() => {
    return () => {
      if (cameraStream) {
        cameraStream.getTracks().forEach(track => track.stop())
      }
    }
  }, [cameraStream])

  // Control functions
  const startRecording = async () => {
    // Se nao tem camera ativa, iniciar camera primeiro
    if (!cameraStream) {
      await selectCamera()
    }
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

  const activeStreams = streams.filter((s) => s.status !== 'ended')
  const liveCount = streams.filter((s) => s.status === 'live').length

  return (
    <PageTransition>
      <div className="min-h-screen bg-background p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2">
            <Radio className={`w-5 h-5 ${
              liveCount > 0
                ? 'text-green-500'
                : connectionStatus === 'connected'
                  ? 'text-green-500'
                  : connectionStatus === 'connecting'
                    ? 'text-yellow-500'
                    : 'text-red-500'
            }`} />
            <span className="text-sm font-medium">
              {liveCount > 0
                ? `${liveCount} camera${liveCount > 1 ? 's' : ''} ao vivo`
                : connectionStatus === 'connected'
                ? t('liveAnalysis.status.connected')
                : connectionStatus === 'connecting'
                ? 'Conectando...'
                : connectionStatus === 'error'
                ? 'Erro (usando polling)'
                : t('liveAnalysis.status.disconnected')}
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
            onClick={fetchStreams}
            disabled={loadingStreams}
          >
            <RefreshCw className={`w-4 h-4 mr-2 ${loadingStreams ? 'animate-spin' : ''}`} />
            Atualizar
          </Button>
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
          {/* Video Player / Multi-Camera Grid */}
          <Card className="relative">
            <CardContent className="p-0">
              {viewMode === 'multi-stream' && activeStreams.length > 0 ? (
                <div className="p-3">
                  <MultiCameraGrid
                    streams={activeStreams}
                    onStreamSelect={(stream) => {
                      console.log('Selected stream:', stream.camera_label)
                    }}
                  />
                </div>
              ) : viewMode === 'camera' && cameraStream ? (
                <div className="relative aspect-video bg-black rounded-lg overflow-hidden">
                  <video
                    ref={cameraVideoRef}
                    autoPlay
                    playsInline
                    muted
                    className="w-full h-full object-contain"
                  />
                  {isRecording && (
                    <div className="absolute top-4 left-4 flex items-center gap-2 bg-red-600/80 text-white px-3 py-1.5 rounded-full text-sm">
                      <div className="w-2 h-2 rounded-full bg-white animate-pulse" />
                      REC
                    </div>
                  )}
                </div>
              ) : videoUrl ? (
                <VideoPlayer
                  src={videoUrl}
                  showOverlays={true}
                  currentFrame={currentFrame}
                  onTimeUpdate={(_time) => {}}
                />
              ) : (
                <div className="aspect-video bg-muted rounded-lg flex flex-col items-center justify-center">
                  <Video className="w-16 h-16 text-muted-foreground mb-4" />
                  <p className="text-lg font-medium mb-2">{t('liveAnalysis.analysis.noVideoSource')}</p>
                  <p className="text-sm text-muted-foreground mb-6">
                    Conecte cameras moveis ou selecione um video
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
            </CardContent>
          </Card>

          {/* View Mode Toggle + Controls */}
          <Card>
            <CardContent className="p-4">
              {/* View mode tabs */}
              <div className="flex items-center justify-center gap-2 mb-4">
                <Button
                  variant={viewMode === 'multi-stream' ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => setViewMode('multi-stream')}
                >
                  <PlusCircle className="w-4 h-4 mr-1.5" />
                  Multi-Camera ({activeStreams.length})
                </Button>
                <Button
                  variant={viewMode === 'camera' ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => {
                    setViewMode('camera')
                    selectCamera()
                  }}
                >
                  <Video className="w-4 h-4 mr-1.5" />
                  Camera Local
                </Button>
                <Button
                  variant={viewMode === 'upload' ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => {
                    setViewMode('upload')
                    setShowUploadModal(true)
                  }}
                >
                  <Upload className="w-4 h-4 mr-1.5" />
                  Video
                </Button>
              </div>

              {/* Recording/Analysis Controls */}
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
                  <div className={`w-2 h-2 rounded-full ${isRecording ? 'bg-red-500 animate-pulse' : 'bg-slate-300'}`} />
                  <span className={isRecording ? 'text-red-500' : 'text-muted-foreground'}>
                    {t('liveAnalysis.recording.recording')}
                  </span>
                </div>
                <div className="flex items-center space-x-2">
                  <div className={`w-2 h-2 rounded-full ${isAnalyzing ? 'bg-green-500 animate-pulse' : 'bg-slate-300'}`} />
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
            {/* Active Streams Info */}
            {activeStreams.length > 0 && (
              <Card>
                <CardHeader className="pb-3">
                  <CardTitle className="text-sm flex items-center">
                    <Radio className="w-4 h-4 mr-2 text-red-500" />
                    Cameras Conectadas
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-2">
                  {activeStreams.map((stream) => (
                    <div
                      key={stream.id}
                      className="flex items-center justify-between text-sm p-2 rounded-md bg-muted/50"
                    >
                      <div className="flex items-center gap-2">
                        <div
                          className={`w-2 h-2 rounded-full ${
                            stream.status === 'live'
                              ? 'bg-red-500 animate-pulse'
                              : 'bg-yellow-500'
                          }`}
                        />
                        <span className="font-medium">{stream.camera_label}</span>
                      </div>
                      <span className="text-xs text-muted-foreground capitalize">
                        {stream.device_info.platform}
                      </span>
                    </div>
                  ))}
                </CardContent>
              </Card>
            )}

            {/* Score Board */}
            {(currentMatch || scoreboard) && (
              currentMatch ? (
                <ScoreBoard match={currentMatch} />
              ) : scoreboard ? (
                <Card className="bg-gradient-to-br from-slate-900 to-slate-800 text-white">
                  <CardContent className="p-4">
                    <div className="text-sm text-center text-slate-400 mb-2">Live Score</div>
                    <div className="grid grid-cols-3 gap-2 text-center">
                      <div className={scoreboard.player1.serving ? 'font-bold' : ''}>
                        Player 1
                      </div>
                      <div>Score</div>
                      <div className={scoreboard.player2.serving ? 'font-bold' : ''}>
                        Player 2
                      </div>
                    </div>
                    <div className="grid grid-cols-3 gap-2 text-center mt-2 text-2xl font-mono">
                      <div>{scoreboard.player1.current_points}</div>
                      <div className="text-slate-400">-</div>
                      <div>{scoreboard.player2.current_points}</div>
                    </div>
                    <div className="grid grid-cols-3 gap-2 text-center mt-2">
                      <div className="text-sm">
                        {scoreboard.player1.games.map((g, i) => (
                          <span key={i} className="mx-1">{g}</span>
                        ))}
                      </div>
                      <div className="text-xs text-slate-400">Sets</div>
                      <div className="text-sm">
                        {scoreboard.player2.games.map((g, i) => (
                          <span key={i} className="mx-1">{g}</span>
                        ))}
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ) : null
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
          setViewMode('upload')
        }}
      />
    </div>
    </PageTransition>
  )
}

export default LiveAnalysis
