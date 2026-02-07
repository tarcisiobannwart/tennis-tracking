import { useState, useEffect } from 'react'
import { useTranslation } from 'react-i18next'
import {
  Target,
  Play,
  Square,
  Dumbbell,
  Calendar,
  Brain,
  Activity,
  Clock,
  CheckCircle,
  Plus,
  Trash2,
  ChevronRight,
  TrendingUp,
  BarChart3,
  Loader2,
  Zap,
  Footprints,
  Crosshair,
  Shield,
  Heart,
} from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { PageTransition } from '@/components/animations'
import toast from 'react-hot-toast'
import {
  trainingService,
  TrainingSession,
  DrillType,
  TrainingProgress,
  TrainingRecommendations,
  TrainingCalendar,
} from '@/services/trainingService'

const SESSION_TYPES = ['practice', 'technique', 'tactical', 'fitness', 'match_prep', 'recovery']

const CATEGORY_ICONS: Record<string, React.ElementType> = {
  technique: Target,
  fitness: Dumbbell,
  tactical: Brain,
  serve: Zap,
  return: Shield,
  volley: Crosshair,
  footwork: Footprints,
  mental: Heart,
}

const STATUS_COLORS: Record<string, string> = {
  planned: 'bg-blue-500/20 text-blue-400',
  in_progress: 'bg-yellow-500/20 text-yellow-400',
  completed: 'bg-green-500/20 text-green-400',
  cancelled: 'bg-red-500/20 text-red-400',
}

const DIFFICULTY_COLORS: Record<string, string> = {
  beginner: 'bg-green-500/20 text-green-400',
  intermediate: 'bg-yellow-500/20 text-yellow-400',
  advanced: 'bg-orange-500/20 text-orange-400',
  professional: 'bg-red-500/20 text-red-400',
}

const TYPE_COLORS: Record<string, string> = {
  practice: 'bg-blue-500/20 text-blue-400',
  technique: 'bg-purple-500/20 text-purple-400',
  tactical: 'bg-cyan-500/20 text-cyan-400',
  fitness: 'bg-orange-500/20 text-orange-400',
  match_prep: 'bg-green-500/20 text-green-400',
  recovery: 'bg-pink-500/20 text-pink-400',
}

type TabId = 'sessions' | 'drills' | 'progress' | 'calendar' | 'recommendations'

const Training = () => {
  const { t } = useTranslation()
  const [activeTab, setActiveTab] = useState<TabId>('sessions')
  const [loading, setLoading] = useState(false)

  // Sessions state
  const [sessions, setSessions] = useState<TrainingSession[]>([])
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [selectedSession, setSelectedSession] = useState<TrainingSession | null>(null)
  const [sessionFilter, setSessionFilter] = useState<string>('')

  // Drills state
  const [drills, setDrills] = useState<DrillType[]>([])
  const [drillCategoryFilter, setDrillCategoryFilter] = useState<string>('')

  // Progress state
  const [progress, setProgress] = useState<TrainingProgress | null>(null)
  const [progressPeriod, setProgressPeriod] = useState('month')

  // Recommendations state
  const [recommendations, setRecommendations] = useState<TrainingRecommendations | null>(null)

  // Calendar state
  const [calendar, setCalendar] = useState<TrainingCalendar | null>(null)

  // Create session form
  const [newSession, setNewSession] = useState({
    title: '',
    description: '',
    session_type: 'practice',
    scheduled_at: new Date().toISOString().slice(0, 16),
    coach_name: '',
    focus_areas: '' as string,
  })

  useEffect(() => {
    loadTabData(activeTab)
  }, [activeTab, progressPeriod])

  const loadTabData = async (tab: TabId) => {
    setLoading(true)
    try {
      switch (tab) {
        case 'sessions':
          const sessionsData = await trainingService.getSessions(
            sessionFilter ? { status: sessionFilter } : undefined
          )
          setSessions(sessionsData)
          break
        case 'drills':
          const drillsData = await trainingService.getDrillTypes(
            drillCategoryFilter ? { category: drillCategoryFilter } : undefined
          )
          setDrills(drillsData)
          break
        case 'progress':
          const progressData = await trainingService.getProgress(progressPeriod)
          setProgress(progressData)
          break
        case 'recommendations':
          const recsData = await trainingService.getRecommendations()
          setRecommendations(recsData)
          break
        case 'calendar':
          const calData = await trainingService.getCalendar()
          setCalendar(calData)
          break
      }
    } catch {
      // silently fail - empty state will show
    } finally {
      setLoading(false)
    }
  }

  const handleCreateSession = async () => {
    try {
      const areas = newSession.focus_areas
        ? newSession.focus_areas.split(',').map(a => a.trim()).filter(Boolean)
        : []
      await trainingService.createSession({
        title: newSession.title,
        description: newSession.description || undefined,
        session_type: newSession.session_type,
        scheduled_at: new Date(newSession.scheduled_at).toISOString(),
        coach_name: newSession.coach_name || undefined,
        focus_areas: areas.length > 0 ? areas : undefined,
      })
      toast.success(t('training.sessions.created'))
      setShowCreateModal(false)
      setNewSession({
        title: '',
        description: '',
        session_type: 'practice',
        scheduled_at: new Date().toISOString().slice(0, 16),
        coach_name: '',
        focus_areas: '',
      })
      loadTabData('sessions')
    } catch {
      toast.error(t('errors.generic'))
    }
  }

  const handleStartSession = async (id: string) => {
    try {
      await trainingService.startSession(id)
      toast.success(t('training.sessions.started'))
      loadTabData('sessions')
    } catch {
      toast.error(t('errors.generic'))
    }
  }

  const handleFinishSession = async (id: string) => {
    try {
      await trainingService.finishSession(id)
      toast.success(t('training.sessions.finished'))
      loadTabData('sessions')
    } catch {
      toast.error(t('errors.generic'))
    }
  }

  const handleDeleteSession = async (id: string) => {
    try {
      await trainingService.deleteSession(id)
      toast.success(t('training.sessions.deleted'))
      setSelectedSession(null)
      loadTabData('sessions')
    } catch {
      toast.error(t('errors.generic'))
    }
  }

  const tabs: { id: TabId; label: string; icon: React.ElementType }[] = [
    { id: 'sessions', label: t('training.tabs.sessions'), icon: Activity },
    { id: 'drills', label: t('training.tabs.drills'), icon: Target },
    { id: 'progress', label: t('training.tabs.progress'), icon: TrendingUp },
    { id: 'calendar', label: t('training.tabs.calendar'), icon: Calendar },
    { id: 'recommendations', label: t('training.tabs.recommendations'), icon: Brain },
  ]

  const formatDate = (dateStr: string) => {
    return new Date(dateStr).toLocaleDateString('pt-BR', {
      day: '2-digit',
      month: 'short',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    })
  }

  const formatMinutes = (mins: number) => {
    if (mins < 60) return `${mins}min`
    const h = Math.floor(mins / 60)
    const m = mins % 60
    return m > 0 ? `${h}h ${m}min` : `${h}h`
  }

  // --- Render Functions ---

  const renderSessions = () => (
    <div className="space-y-4">
      {/* Filter + Create */}
      <div className="flex flex-wrap items-center gap-3">
        <div className="flex gap-2">
          {['', 'planned', 'in_progress', 'completed'].map(f => (
            <button
              key={f}
              onClick={() => { setSessionFilter(f); setTimeout(() => loadTabData('sessions'), 0) }}
              className={`px-3 py-1.5 text-xs rounded-full transition-colors ${
                sessionFilter === f
                  ? 'bg-blue-500 text-white'
                  : 'bg-slate-800 text-slate-400 hover:bg-slate-700'
              }`}
            >
              {f ? t(`training.status.${f}`) : t('common.filter') + ': ' + (t('statistics.overview') || 'Todos')}
            </button>
          ))}
        </div>
        <div className="ml-auto">
          <Button
            onClick={() => setShowCreateModal(true)}
            className="bg-blue-500 hover:bg-blue-600 text-white"
          >
            <Plus className="w-4 h-4 mr-2" />
            {t('training.sessions.create')}
          </Button>
        </div>
      </div>

      {/* Sessions List */}
      {sessions.length === 0 && !loading ? (
        <Card className="bg-slate-800/50 border-slate-700">
          <CardContent className="p-12 text-center">
            <Activity className="w-12 h-12 mx-auto text-slate-600 mb-4" />
            <h3 className="text-lg font-medium text-slate-300 mb-2">{t('training.sessions.empty')}</h3>
            <p className="text-sm text-slate-500 mb-6">{t('training.sessions.emptyDescription')}</p>
            <Button
              onClick={() => setShowCreateModal(true)}
              className="bg-blue-500 hover:bg-blue-600 text-white"
            >
              <Plus className="w-4 h-4 mr-2" />
              {t('training.sessions.create')}
            </Button>
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-3">
          {sessions.map(session => (
            <Card
              key={session.id}
              className="bg-slate-800/50 border-slate-700 hover:border-slate-600 transition-colors cursor-pointer"
              onClick={() => setSelectedSession(selectedSession?.id === session.id ? null : session)}
            >
              <CardContent className="p-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3 flex-1 min-w-0">
                    <div className={`w-10 h-10 rounded-lg flex items-center justify-center shrink-0 ${TYPE_COLORS[session.session_type] || 'bg-slate-700 text-slate-400'}`}>
                      {(() => {
                        const Icon = CATEGORY_ICONS[session.session_type] || Activity
                        return <Icon className="w-5 h-5" />
                      })()}
                    </div>
                    <div className="min-w-0">
                      <h4 className="font-medium text-slate-100 truncate">{session.title}</h4>
                      <div className="flex items-center gap-2 mt-1 flex-wrap">
                        <span className={`px-2 py-0.5 rounded-full text-xs ${STATUS_COLORS[session.status]}`}>
                          {t(`training.status.${session.status}`)}
                        </span>
                        <span className={`px-2 py-0.5 rounded-full text-xs ${TYPE_COLORS[session.session_type] || 'bg-slate-700 text-slate-400'}`}>
                          {t(`training.types.${session.session_type}`)}
                        </span>
                        <span className="text-xs text-slate-500 flex items-center gap-1">
                          <Clock className="w-3 h-3" />
                          {formatDate(session.scheduled_at)}
                        </span>
                        {session.duration_minutes && (
                          <span className="text-xs text-slate-500">
                            {formatMinutes(session.duration_minutes)}
                          </span>
                        )}
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center gap-2 shrink-0 ml-4">
                    {session.status === 'planned' && (
                      <Button
                        size="sm"
                        onClick={(e) => { e.stopPropagation(); handleStartSession(session.id) }}
                        className="bg-green-500/20 text-green-400 hover:bg-green-500/30 border-0"
                      >
                        <Play className="w-3.5 h-3.5 mr-1" />
                        {t('training.sessions.start')}
                      </Button>
                    )}
                    {session.status === 'in_progress' && (
                      <Button
                        size="sm"
                        onClick={(e) => { e.stopPropagation(); handleFinishSession(session.id) }}
                        className="bg-yellow-500/20 text-yellow-400 hover:bg-yellow-500/30 border-0"
                      >
                        <Square className="w-3.5 h-3.5 mr-1" />
                        {t('training.sessions.finish')}
                      </Button>
                    )}
                    <ChevronRight className={`w-4 h-4 text-slate-500 transition-transform ${selectedSession?.id === session.id ? 'rotate-90' : ''}`} />
                  </div>
                </div>

                {/* Expanded details */}
                {selectedSession?.id === session.id && (
                  <div className="mt-4 pt-4 border-t border-slate-700 space-y-3">
                    {session.description && (
                      <p className="text-sm text-slate-400">{session.description}</p>
                    )}
                    {session.focus_areas && session.focus_areas.length > 0 && (
                      <div className="flex flex-wrap gap-1.5">
                        {session.focus_areas.map(area => (
                          <span key={area} className="px-2 py-0.5 bg-slate-700 text-slate-300 rounded text-xs">
                            {area}
                          </span>
                        ))}
                      </div>
                    )}
                    {session.coach_name && (
                      <p className="text-sm text-slate-500">
                        {t('training.sessions.coach')}: <span className="text-slate-300">{session.coach_name}</span>
                      </p>
                    )}
                    {session.drills.length > 0 && (
                      <div className="space-y-1">
                        <p className="text-xs text-slate-500 uppercase tracking-wider">{t('training.tabs.drills')} ({session.drills.length})</p>
                        {session.drills.map((drill, i) => (
                          <div key={drill.id || i} className="flex items-center gap-2 text-sm text-slate-400 bg-slate-900/50 rounded px-3 py-1.5">
                            <span className="text-slate-500">{i + 1}.</span>
                            <span className="text-slate-300">{drill.drill_name || drill.drill_type_id}</span>
                            {drill.duration_minutes && <span className="text-slate-500 ml-auto">{drill.duration_minutes}min</span>}
                          </div>
                        ))}
                      </div>
                    )}
                    <div className="flex gap-2 pt-2">
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={(e) => { e.stopPropagation(); handleDeleteSession(session.id) }}
                        className="border-red-500/30 text-red-400 hover:bg-red-500/10"
                      >
                        <Trash2 className="w-3.5 h-3.5 mr-1" />
                        {t('training.sessions.delete')}
                      </Button>
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {/* Create Session Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4" onClick={() => setShowCreateModal(false)}>
          <Card className="bg-slate-800 border-slate-700 w-full max-w-lg" onClick={e => e.stopPropagation()}>
            <CardHeader className="border-b border-slate-700">
              <CardTitle className="text-slate-100">{t('training.sessions.create')}</CardTitle>
            </CardHeader>
            <CardContent className="p-6 space-y-4">
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-1.5">{t('training.sessions.sessionTitle')}</label>
                <Input
                  value={newSession.title}
                  onChange={e => setNewSession({ ...newSession, title: e.target.value })}
                  placeholder="Ex: Treino de saque"
                  className="bg-slate-900 border-slate-700 text-slate-100"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-1.5">{t('training.sessions.description')}</label>
                <Input
                  value={newSession.description}
                  onChange={e => setNewSession({ ...newSession, description: e.target.value })}
                  placeholder="Descricao do treino"
                  className="bg-slate-900 border-slate-700 text-slate-100"
                />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-1.5">{t('training.sessions.sessionType')}</label>
                  <select
                    value={newSession.session_type}
                    onChange={e => setNewSession({ ...newSession, session_type: e.target.value })}
                    className="w-full h-10 rounded-md border border-slate-700 bg-slate-900 text-slate-100 px-3 text-sm"
                  >
                    {SESSION_TYPES.map(type => (
                      <option key={type} value={type}>{t(`training.types.${type}`)}</option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-1.5">{t('training.sessions.scheduledAt')}</label>
                  <Input
                    type="datetime-local"
                    value={newSession.scheduled_at}
                    onChange={e => setNewSession({ ...newSession, scheduled_at: e.target.value })}
                    className="bg-slate-900 border-slate-700 text-slate-100"
                  />
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-1.5">{t('training.sessions.coach')}</label>
                <Input
                  value={newSession.coach_name}
                  onChange={e => setNewSession({ ...newSession, coach_name: e.target.value })}
                  placeholder="Nome do treinador"
                  className="bg-slate-900 border-slate-700 text-slate-100"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-300 mb-1.5">{t('training.sessions.focusAreas')}</label>
                <Input
                  value={newSession.focus_areas}
                  onChange={e => setNewSession({ ...newSession, focus_areas: e.target.value })}
                  placeholder="forehand, serve, footwork"
                  className="bg-slate-900 border-slate-700 text-slate-100"
                />
                <p className="text-xs text-slate-500 mt-1">Separar por virgula</p>
              </div>
              <div className="flex gap-3 pt-2">
                <Button
                  onClick={() => setShowCreateModal(false)}
                  variant="outline"
                  className="flex-1 border-slate-700 text-slate-300"
                >
                  {t('common.cancel')}
                </Button>
                <Button
                  onClick={handleCreateSession}
                  disabled={!newSession.title}
                  className="flex-1 bg-blue-500 hover:bg-blue-600 text-white"
                >
                  {t('common.save')}
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  )

  const renderDrills = () => (
    <div className="space-y-4">
      {/* Category filter */}
      <div className="flex flex-wrap gap-2">
        {['', 'technique', 'fitness', 'tactical', 'serve', 'return', 'volley', 'footwork', 'mental'].map(cat => (
          <button
            key={cat}
            onClick={() => { setDrillCategoryFilter(cat); setTimeout(() => loadTabData('drills'), 0) }}
            className={`px-3 py-1.5 text-xs rounded-full transition-colors flex items-center gap-1.5 ${
              drillCategoryFilter === cat
                ? 'bg-blue-500 text-white'
                : 'bg-slate-800 text-slate-400 hover:bg-slate-700'
            }`}
          >
            {cat ? (() => {
              const Icon = CATEGORY_ICONS[cat] || Target
              return <Icon className="w-3 h-3" />
            })() : null}
            {cat ? t(`training.drills.categories.${cat}`) : 'Todos'}
          </button>
        ))}
      </div>

      {/* Drills Grid */}
      {drills.length === 0 && !loading ? (
        <Card className="bg-slate-800/50 border-slate-700">
          <CardContent className="p-12 text-center">
            <Target className="w-12 h-12 mx-auto text-slate-600 mb-4" />
            <h3 className="text-lg font-medium text-slate-300">{t('training.drills.empty')}</h3>
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-3 md:grid-cols-2 lg:grid-cols-3">
          {drills.map(drill => {
            const Icon = CATEGORY_ICONS[drill.category] || Target
            return (
              <Card key={drill.id} className="bg-slate-800/50 border-slate-700 hover:border-slate-600 transition-colors">
                <CardContent className="p-4">
                  <div className="flex items-start gap-3">
                    <div className={`w-10 h-10 rounded-lg flex items-center justify-center shrink-0 ${TYPE_COLORS[drill.category] || 'bg-slate-700 text-slate-400'}`}>
                      <Icon className="w-5 h-5" />
                    </div>
                    <div className="min-w-0 flex-1">
                      <h4 className="font-medium text-slate-100 text-sm">{drill.name}</h4>
                      {drill.description && (
                        <p className="text-xs text-slate-500 mt-0.5 line-clamp-2">{drill.description}</p>
                      )}
                      <div className="flex items-center gap-2 mt-2 flex-wrap">
                        <span className={`px-2 py-0.5 rounded-full text-[10px] ${DIFFICULTY_COLORS[drill.difficulty]}`}>
                          {t(`training.drills.difficulty.${drill.difficulty}`)}
                        </span>
                        {drill.duration_minutes && (
                          <span className="text-[10px] text-slate-500 flex items-center gap-0.5">
                            <Clock className="w-2.5 h-2.5" />
                            {drill.duration_minutes}min
                          </span>
                        )}
                      </div>
                      {drill.equipment_needed && drill.equipment_needed.length > 0 && (
                        <p className="text-[10px] text-slate-600 mt-1.5">
                          {t('training.drills.equipment')}: {drill.equipment_needed.join(', ')}
                        </p>
                      )}
                    </div>
                  </div>
                </CardContent>
              </Card>
            )
          })}
        </div>
      )}
    </div>
  )

  const renderProgress = () => (
    <div className="space-y-4">
      {/* Period selector */}
      <div className="flex gap-2">
        {['week', 'month', 'quarter', 'year'].map(p => (
          <button
            key={p}
            onClick={() => setProgressPeriod(p)}
            className={`px-3 py-1.5 text-xs rounded-full transition-colors ${
              progressPeriod === p
                ? 'bg-blue-500 text-white'
                : 'bg-slate-800 text-slate-400 hover:bg-slate-700'
            }`}
          >
            {t(`training.progress.${p}`)}
          </button>
        ))}
      </div>

      {progress ? (
        <>
          {/* Stats Grid */}
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
            {[
              { label: t('training.progress.totalSessions'), value: progress.total_sessions, icon: Activity },
              { label: t('training.progress.completed'), value: progress.completed_sessions, icon: CheckCircle },
              { label: t('training.progress.completionRate'), value: `${progress.completion_rate}%`, icon: TrendingUp },
              { label: t('training.progress.totalTime'), value: formatMinutes(progress.total_duration_minutes), icon: Clock },
              { label: t('training.progress.avgDuration'), value: formatMinutes(Math.round(progress.average_session_duration)), icon: BarChart3 },
              { label: t('training.progress.avgEffort'), value: progress.average_effort_rating ? `${progress.average_effort_rating}/10` : '-', icon: Zap },
            ].map(stat => (
              <Card key={stat.label} className="bg-slate-800/50 border-slate-700">
                <CardContent className="p-4">
                  <div className="flex items-center gap-2 mb-2">
                    <stat.icon className="w-4 h-4 text-blue-400" />
                    <span className="text-xs text-slate-500">{stat.label}</span>
                  </div>
                  <p className="text-xl font-bold text-slate-100">{stat.value}</p>
                </CardContent>
              </Card>
            ))}
          </div>

          {/* By Type */}
          {Object.keys(progress.session_types_breakdown).length > 0 && (
            <Card className="bg-slate-800/50 border-slate-700">
              <CardHeader className="pb-3">
                <CardTitle className="text-sm text-slate-300">{t('training.progress.byType')}</CardTitle>
              </CardHeader>
              <CardContent className="pb-4">
                <div className="space-y-2">
                  {Object.entries(progress.session_types_breakdown).map(([type, count]) => {
                    const pct = progress.total_sessions > 0 ? (count / progress.total_sessions * 100) : 0
                    return (
                      <div key={type} className="flex items-center gap-3">
                        <span className={`px-2 py-0.5 rounded text-xs w-28 text-center ${TYPE_COLORS[type] || 'bg-slate-700 text-slate-400'}`}>
                          {t(`training.types.${type}`)}
                        </span>
                        <div className="flex-1 bg-slate-900 rounded-full h-2">
                          <div
                            className="h-2 rounded-full bg-blue-500"
                            style={{ width: `${pct}%` }}
                          />
                        </div>
                        <span className="text-xs text-slate-500 w-8 text-right">{count}</span>
                      </div>
                    )
                  })}
                </div>
              </CardContent>
            </Card>
          )}

          {/* Recent Sessions */}
          {progress.recent_sessions.length > 0 && (
            <Card className="bg-slate-800/50 border-slate-700">
              <CardHeader className="pb-3">
                <CardTitle className="text-sm text-slate-300">{t('training.progress.recentSessions')}</CardTitle>
              </CardHeader>
              <CardContent className="pb-4">
                <div className="space-y-2">
                  {progress.recent_sessions.map(s => (
                    <div key={s.id} className="flex items-center justify-between py-2 border-b border-slate-700/50 last:border-0">
                      <div>
                        <span className="text-sm text-slate-200">{s.title}</span>
                        <div className="text-xs text-slate-500">{s.date ? formatDate(s.date) : '-'}</div>
                      </div>
                      <div className="flex items-center gap-2">
                        {s.duration && <span className="text-xs text-slate-500">{formatMinutes(s.duration)}</span>}
                        <span className={`px-2 py-0.5 rounded-full text-xs ${STATUS_COLORS[s.status]}`}>
                          {t(`training.status.${s.status}`)}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}
        </>
      ) : !loading ? (
        <Card className="bg-slate-800/50 border-slate-700">
          <CardContent className="p-12 text-center">
            <TrendingUp className="w-12 h-12 mx-auto text-slate-600 mb-4" />
            <h3 className="text-lg font-medium text-slate-300">{t('training.sessions.empty')}</h3>
          </CardContent>
        </Card>
      ) : null}
    </div>
  )

  const renderCalendar = () => (
    <div className="space-y-4">
      {calendar ? (
        <>
          {/* Summary */}
          <div className="grid grid-cols-3 gap-3">
            <Card className="bg-slate-800/50 border-slate-700">
              <CardContent className="p-4 text-center">
                <p className="text-2xl font-bold text-blue-400">{calendar.summary.planned}</p>
                <p className="text-xs text-slate-500">{t('training.calendar.planned')}</p>
              </CardContent>
            </Card>
            <Card className="bg-slate-800/50 border-slate-700">
              <CardContent className="p-4 text-center">
                <p className="text-2xl font-bold text-yellow-400">{calendar.summary.in_progress}</p>
                <p className="text-xs text-slate-500">{t('training.calendar.inProgress')}</p>
              </CardContent>
            </Card>
            <Card className="bg-slate-800/50 border-slate-700">
              <CardContent className="p-4 text-center">
                <p className="text-2xl font-bold text-green-400">{calendar.summary.completed}</p>
                <p className="text-xs text-slate-500">{t('training.calendar.completed')}</p>
              </CardContent>
            </Card>
          </div>

          {/* Events List */}
          <Card className="bg-slate-800/50 border-slate-700">
            <CardHeader className="pb-3">
              <CardTitle className="text-sm text-slate-300">{t('training.calendar.title')}</CardTitle>
            </CardHeader>
            <CardContent className="pb-4">
              {calendar.events.length === 0 ? (
                <p className="text-sm text-slate-500 text-center py-8">{t('training.sessions.empty')}</p>
              ) : (
                <div className="space-y-2">
                  {calendar.events.map(event => (
                    <div key={event.id} className="flex items-center gap-3 py-2 border-b border-slate-700/50 last:border-0">
                      <div className={`w-2 h-8 rounded-full ${
                        event.status === 'completed' ? 'bg-green-500' :
                        event.status === 'in_progress' ? 'bg-yellow-500' : 'bg-blue-500'
                      }`} />
                      <div className="flex-1 min-w-0">
                        <p className="text-sm text-slate-200 truncate">{event.title}</p>
                        <p className="text-xs text-slate-500">{formatDate(event.start)}</p>
                      </div>
                      <span className={`px-2 py-0.5 rounded-full text-xs shrink-0 ${TYPE_COLORS[event.type] || 'bg-slate-700 text-slate-400'}`}>
                        {t(`training.types.${event.type}`)}
                      </span>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </>
      ) : !loading ? (
        <Card className="bg-slate-800/50 border-slate-700">
          <CardContent className="p-12 text-center">
            <Calendar className="w-12 h-12 mx-auto text-slate-600 mb-4" />
            <h3 className="text-lg font-medium text-slate-300">{t('training.sessions.empty')}</h3>
          </CardContent>
        </Card>
      ) : null}
    </div>
  )

  const renderRecommendations = () => (
    <div className="space-y-4">
      {recommendations ? (
        <>
          {/* Next Session */}
          <Card className="bg-gradient-to-r from-blue-500/10 to-purple-500/10 border-blue-500/30">
            <CardContent className="p-6">
              <div className="flex items-center gap-3 mb-4">
                <div className="w-10 h-10 rounded-lg bg-blue-500/20 flex items-center justify-center">
                  <Brain className="w-5 h-5 text-blue-400" />
                </div>
                <div>
                  <h3 className="font-medium text-slate-100">{t('training.recommendations.nextSession')}</h3>
                  <span className={`px-2 py-0.5 rounded-full text-xs ${TYPE_COLORS[recommendations.next_session_type] || 'bg-slate-700 text-slate-400'}`}>
                    {t(`training.types.${recommendations.next_session_type}`)}
                  </span>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Weak Areas */}
          {recommendations.weak_areas.length > 0 && (
            <Card className="bg-slate-800/50 border-slate-700">
              <CardHeader className="pb-3">
                <CardTitle className="text-sm text-slate-300 flex items-center gap-2">
                  <Target className="w-4 h-4 text-orange-400" />
                  {t('training.recommendations.weakAreas')}
                </CardTitle>
              </CardHeader>
              <CardContent className="pb-4">
                <div className="flex flex-wrap gap-2">
                  {recommendations.weak_areas.map(area => (
                    <span key={area} className="px-3 py-1.5 bg-orange-500/10 text-orange-400 rounded-lg text-sm border border-orange-500/20">
                      {area}
                    </span>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}

          {/* Suggestions */}
          <Card className="bg-slate-800/50 border-slate-700">
            <CardHeader className="pb-3">
              <CardTitle className="text-sm text-slate-300">{t('training.recommendations.suggestions')}</CardTitle>
            </CardHeader>
            <CardContent className="pb-4">
              <div className="space-y-3">
                {recommendations.suggestions.map((sug, i) => (
                  <div key={i} className="flex items-start gap-3">
                    <div className="w-6 h-6 rounded-full bg-blue-500/20 flex items-center justify-center shrink-0 mt-0.5">
                      <span className="text-xs text-blue-400 font-medium">{i + 1}</span>
                    </div>
                    <p className="text-sm text-slate-300">{sug}</p>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Weekly Plan */}
          <Card className="bg-slate-800/50 border-slate-700">
            <CardHeader className="pb-3">
              <CardTitle className="text-sm text-slate-300 flex items-center gap-2">
                <Calendar className="w-4 h-4 text-green-400" />
                {t('training.recommendations.weeklyPlan')}
              </CardTitle>
            </CardHeader>
            <CardContent className="pb-4">
              <div className="space-y-2">
                {Object.entries(recommendations.weekly_plan).map(([day, activity]) => (
                  <div key={day} className="flex items-center gap-3 py-2 border-b border-slate-700/50 last:border-0">
                    <span className="text-sm font-medium text-slate-400 w-24">
                      {t(`training.recommendations.days.${day}`)}
                    </span>
                    <span className="text-sm text-slate-300">{activity}</span>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </>
      ) : !loading ? (
        <Card className="bg-slate-800/50 border-slate-700">
          <CardContent className="p-12 text-center">
            <Brain className="w-12 h-12 mx-auto text-slate-600 mb-4" />
            <h3 className="text-lg font-medium text-slate-300">{t('training.sessions.empty')}</h3>
          </CardContent>
        </Card>
      ) : null}
    </div>
  )

  return (
    <PageTransition>
      <div className="space-y-6">
        {/* Header */}
        <div>
          <h1 className="text-2xl font-bold text-slate-100">{t('training.title')}</h1>
          <p className="text-sm text-slate-500 mt-1">{t('training.subtitle')}</p>
        </div>

        {/* Tabs */}
        <div className="flex gap-1 p-1 bg-slate-800/50 rounded-lg overflow-x-auto">
          {tabs.map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`flex items-center gap-2 px-4 py-2 text-sm rounded-md whitespace-nowrap transition-colors ${
                activeTab === tab.id
                  ? 'bg-blue-500 text-white'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-700/50'
              }`}
            >
              <tab.icon className="w-4 h-4" />
              {tab.label}
            </button>
          ))}
        </div>

        {/* Loading */}
        {loading && (
          <div className="flex items-center justify-center py-12">
            <Loader2 className="w-8 h-8 text-blue-400 animate-spin" />
          </div>
        )}

        {/* Tab Content */}
        {!loading && (
          <>
            {activeTab === 'sessions' && renderSessions()}
            {activeTab === 'drills' && renderDrills()}
            {activeTab === 'progress' && renderProgress()}
            {activeTab === 'calendar' && renderCalendar()}
            {activeTab === 'recommendations' && renderRecommendations()}
          </>
        )}
      </div>
    </PageTransition>
  )
}

export default Training
