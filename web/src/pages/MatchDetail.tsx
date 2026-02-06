import { useState } from 'react'
import { useParams, Link, useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import {
  ArrowLeft,
  Play,
  ChevronLeft,
  ChevronRight,
  ChevronDown,
  Clock,
  Trophy,
  MapPin,
  Calendar,
  User,
  TrendingUp,
  Video,
  Target
} from 'lucide-react'
import { useMatch, useMatchStatistics, useMatchHighlights } from '@/hooks/useMatchData'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'

const MatchDetail = () => {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const [showReplays, setShowReplays] = useState(false)

  const { data: match, isLoading: matchLoading } = useMatch(id!)
  const { data: statistics } = useMatchStatistics(id!)
  const { data: highlights } = useMatchHighlights(id!)

  const highlightsList = Array.isArray(highlights?.highlights) ? highlights.highlights : []

  if (matchLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="loading-spinner"></div>
      </div>
    )
  }

  if (!match) {
    return (
      <div className="flex flex-col items-center justify-center min-h-screen text-center px-4">
        <Trophy className="w-16 h-16 text-slate-600 mb-4" />
        <h3 className="text-xl font-semibold mb-2 text-slate-100">Partida não encontrada</h3>
        <p className="text-slate-400 mb-6">A partida solicitada não pôde ser encontrada.</p>
        <Link to="/matches">
          <Button>Voltar para Partidas</Button>
        </Link>
      </div>
    )
  }

  const formatDuration = (duration: number) => {
    const hours = Math.floor(duration / 3600)
    const minutes = Math.floor((duration % 3600) / 60)
    return `${hours}h ${minutes}m`
  }

  const getSurfaceEmoji = (surface: string) => {
    switch (surface) {
      case 'clay': return '🟠'
      case 'grass': return '🟢'
      case 'hard': return '🔵'
      default: return '⚪'
    }
  }

  const getSurfaceLabel = (surface: string) => {
    switch (surface) {
      case 'clay': return 'Saibro'
      case 'grass': return 'Grama'
      case 'hard': return 'Duro'
      case 'carpet': return 'Carpete'
      default: return surface
    }
  }

  const getFinalScore = () => {
    if (!match.score?.sets) return 'N/A'
    return match.score.sets.map(set =>
      `${set.player1Games}-${set.player2Games}`
    ).join(', ')
  }

  const renderStatBar = (label: string, value1: number, value2: number) => {
    const total = value1 + value2 || 1
    const percent1 = (value1 / total) * 100
    const percent2 = (value2 / total) * 100

    return (
      <div className="space-y-2">
        <div className="flex justify-between items-center text-sm">
          <span className="text-slate-300">{label}</span>
          <span className="text-slate-400 font-mono">{value1} - {value2}</span>
        </div>
        <div className="flex gap-2 h-2">
          <div
            className="bg-court-accent rounded-full transition-all duration-500"
            style={{ width: `${percent1}%` }}
          />
          <div
            className="bg-slate-500 rounded-full transition-all duration-500"
            style={{ width: `${percent2}%` }}
          />
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-slate-900">
      {/* Back Button */}
      <div className="bg-slate-800/50 border-b border-slate-700">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <Link to="/matches">
            <Button variant="outline" size="sm" className="gap-2">
              <ArrowLeft className="w-4 h-4" />
              Voltar
            </Button>
          </Link>
        </div>
      </div>

      {/* Hero Section */}
      <div className="relative bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 border-b border-slate-700">
        <div className="absolute inset-0 bg-gradient-to-t from-slate-900 via-transparent to-transparent opacity-60" />
        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            className="text-center"
          >
            <h1 className="text-4xl md:text-5xl lg:text-6xl font-bold text-slate-100 mb-6">
              {match.player1.name} <span className="text-court-accent">vs</span> {match.player2.name}
            </h1>

            <div className="flex flex-wrap items-center justify-center gap-3 mb-8">
              <Badge variant="neutral" className="text-base px-4 py-2">
                <Clock className="w-4 h-4 mr-2" />
                {match.duration ? formatDuration(match.duration) : 'Em andamento'}
              </Badge>
              <Badge variant="neutral" className="text-base px-4 py-2">
                <Trophy className="w-4 h-4 mr-2" />
                {match.score?.sets?.length || 0} Sets
              </Badge>
              <Badge variant="neutral" className="text-base px-4 py-2">
                {getSurfaceEmoji(match.surface)} {getSurfaceLabel(match.surface)}
              </Badge>
              {match.status === 'live' && (
                <Badge variant="success" className="text-base px-4 py-2 animate-pulse">
                  <div className="w-2 h-2 bg-green-400 rounded-full mr-2" />
                  AO VIVO
                </Badge>
              )}
            </div>
          </motion.div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
        {/* Info Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="bg-slate-800 border border-slate-700 rounded-xl p-6"
          >
            <div className="flex items-center gap-3 mb-2">
              <div className="w-10 h-10 bg-court-accent-soft rounded-lg flex items-center justify-center">
                <MapPin className="w-5 h-5 text-court-accent" />
              </div>
              <div>
                <p className="text-sm text-slate-400">Superfície</p>
                <p className="text-lg font-semibold text-slate-100">{getSurfaceLabel(match.surface)}</p>
              </div>
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="bg-slate-800 border border-slate-700 rounded-xl p-6"
          >
            <div className="flex items-center gap-3 mb-2">
              <div className="w-10 h-10 bg-court-accent-soft rounded-lg flex items-center justify-center">
                <Trophy className="w-5 h-5 text-court-accent" />
              </div>
              <div>
                <p className="text-sm text-slate-400">Placar Final</p>
                <p className="text-lg font-semibold text-slate-100">{getFinalScore()}</p>
              </div>
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="bg-slate-800 border border-slate-700 rounded-xl p-6"
          >
            <div className="flex items-center gap-3 mb-2">
              <div className="w-10 h-10 bg-court-accent-soft rounded-lg flex items-center justify-center">
                <Clock className="w-5 h-5 text-court-accent" />
              </div>
              <div>
                <p className="text-sm text-slate-400">Duração</p>
                <p className="text-lg font-semibold text-slate-100">
                  {match.duration ? formatDuration(match.duration) : 'N/A'}
                </p>
              </div>
            </div>
          </motion.div>
        </div>

        {/* About Section */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="bg-slate-800 border border-slate-700 rounded-xl p-6"
        >
          <h2 className="text-2xl font-bold text-slate-100 mb-4 flex items-center gap-2">
            <Calendar className="w-6 h-6 text-court-accent" />
            Sobre a Partida
          </h2>
          <div className="space-y-2 text-slate-300">
            <p><span className="font-semibold text-slate-100">Torneio:</span> {match.tournament}</p>
            <p><span className="font-semibold text-slate-100">Rodada:</span> {match.round}</p>
            <p><span className="font-semibold text-slate-100">Data:</span> {new Date(match.date).toLocaleDateString('pt-BR', {
              day: 'numeric',
              month: 'long',
              year: 'numeric'
            })}</p>
          </div>
        </motion.div>

        {/* Replays Section */}
        {highlightsList.length > 0 && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.5 }}
            className="bg-slate-800 border border-slate-700 rounded-xl overflow-hidden"
          >
            <button
              onClick={() => setShowReplays(!showReplays)}
              className="w-full px-6 py-4 flex items-center justify-between hover:bg-slate-700/50 transition-colors"
            >
              <h2 className="text-2xl font-bold text-slate-100 flex items-center gap-2">
                <Video className="w-6 h-6 text-court-accent" />
                Replays e Highlights
              </h2>
              <ChevronDown className={`w-6 h-6 text-slate-400 transition-transform ${showReplays ? 'rotate-180' : ''}`} />
            </button>

            {showReplays && (
              <div className="px-6 pb-6 space-y-3">
                {highlightsList.map((highlight, index) => (
                  <motion.div
                    key={index}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: index * 0.1 }}
                    className="flex items-center justify-between p-4 bg-slate-700/50 border border-slate-600 rounded-lg hover:border-court-accent hover:court-glow transition-all cursor-pointer"
                  >
                    <div className="flex-1">
                      <p className="font-medium text-slate-100">{highlight.description}</p>
                      <p className="text-sm text-slate-400 mt-1">
                        {Math.floor(highlight.timestamp / 60)}:{(highlight.timestamp % 60).toString().padStart(2, '0')}
                      </p>
                    </div>
                    <div className="flex items-center gap-3">
                      <Badge variant="neutral">{highlight.type}</Badge>
                      <Button variant="outline" size="sm">
                        <Play className="w-4 h-4" />
                      </Button>
                    </div>
                  </motion.div>
                ))}
              </div>
            )}
          </motion.div>
        )}

        {/* Players Section */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.6 }}
          className="bg-slate-800 border border-slate-700 rounded-xl p-6"
        >
          <h2 className="text-2xl font-bold text-slate-100 mb-6 flex items-center gap-2">
            <User className="w-6 h-6 text-court-accent" />
            Jogadores
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Player 1 */}
            <div className="bg-slate-700/50 border border-slate-600 rounded-xl p-6 hover:border-court-accent hover:court-glow transition-all">
              <div className="flex items-center gap-4 mb-4">
                <div className="w-16 h-16 bg-gradient-to-br from-court-accent to-court-accent/70 rounded-full flex items-center justify-center text-2xl font-bold text-white">
                  {match.player1.name.split(' ').map(n => n[0]).join('')}
                </div>
                <div>
                  <h3 className="text-xl font-bold text-slate-100">{match.player1.name}</h3>
                  <p className="text-slate-400">{match.player1.country}</p>
                </div>
              </div>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-slate-400">Ranking</span>
                  <span className="font-semibold text-slate-100">#{match.player1.ranking}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-400">Idade</span>
                  <span className="font-semibold text-slate-100">{match.player1.age} anos</span>
                </div>
              </div>
            </div>

            {/* Player 2 */}
            <div className="bg-slate-700/50 border border-slate-600 rounded-xl p-6 hover:border-court-accent hover:court-glow transition-all">
              <div className="flex items-center gap-4 mb-4">
                <div className="w-16 h-16 bg-gradient-to-br from-slate-500 to-slate-600 rounded-full flex items-center justify-center text-2xl font-bold text-white">
                  {match.player2.name.split(' ').map(n => n[0]).join('')}
                </div>
                <div>
                  <h3 className="text-xl font-bold text-slate-100">{match.player2.name}</h3>
                  <p className="text-slate-400">{match.player2.country}</p>
                </div>
              </div>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-slate-400">Ranking</span>
                  <span className="font-semibold text-slate-100">#{match.player2.ranking}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-400">Idade</span>
                  <span className="font-semibold text-slate-100">{match.player2.age} anos</span>
                </div>
              </div>
            </div>
          </div>
        </motion.div>

        {/* Statistics Section */}
        {statistics && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.7 }}
            className="bg-slate-800 border border-slate-700 rounded-xl p-6"
          >
            <h2 className="text-2xl font-bold text-slate-100 mb-6 flex items-center gap-2">
              <TrendingUp className="w-6 h-6 text-court-accent" />
              Estatísticas
            </h2>
            <div className="space-y-6">
              {renderStatBar('Aces', statistics.player1Stats.aces, statistics.player2Stats.aces)}
              {renderStatBar('Winners', statistics.player1Stats.winners, statistics.player2Stats.winners)}
              {renderStatBar('Erros Não Forçados', statistics.player1Stats.unforcedErrors, statistics.player2Stats.unforcedErrors)}

              <div className="space-y-2">
                <div className="flex justify-between items-center text-sm">
                  <span className="text-slate-300">1º Saque %</span>
                  <span className="text-slate-400 font-mono">
                    {((statistics.player1Stats.firstServeIn / statistics.player1Stats.firstServeAttempts) * 100).toFixed(0)}% - {' '}
                    {((statistics.player2Stats.firstServeIn / statistics.player2Stats.firstServeAttempts) * 100).toFixed(0)}%
                  </span>
                </div>
                <div className="flex gap-2 h-2">
                  <div
                    className="bg-court-accent rounded-full"
                    style={{
                      width: `${(statistics.player1Stats.firstServeIn / statistics.player1Stats.firstServeAttempts) * 100}%`
                    }}
                  />
                  <div
                    className="bg-slate-500 rounded-full"
                    style={{
                      width: `${(statistics.player2Stats.firstServeIn / statistics.player2Stats.firstServeAttempts) * 100}%`
                    }}
                  />
                </div>
              </div>
            </div>
          </motion.div>
        )}

        {/* Points/Games Timeline */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.8 }}
          className="bg-slate-800 border border-slate-700 rounded-xl p-6"
        >
          <h2 className="text-2xl font-bold text-slate-100 mb-6 flex items-center gap-2">
            <Target className="w-6 h-6 text-court-accent" />
            Pontos e Games
          </h2>
          <div className="overflow-x-auto">
            <div className="flex gap-2 pb-4">
              {match.score?.sets?.map((set, index) => (
                <div key={index} className="flex-shrink-0 bg-slate-700/50 border border-slate-600 rounded-lg p-4 min-w-[120px]">
                  <p className="text-xs text-slate-400 mb-2">Set {index + 1}</p>
                  <div className="flex justify-between items-center">
                    <span className="text-2xl font-bold text-court-accent">{set.player1Games}</span>
                    <span className="text-slate-500">-</span>
                    <span className="text-2xl font-bold text-slate-400">{set.player2Games}</span>
                  </div>
                  {set.player1Tiebreak !== undefined && (
                    <p className="text-xs text-slate-400 mt-2 text-center">
                      TB: {set.player1Tiebreak}-{set.player2Tiebreak}
                    </p>
                  )}
                </div>
              ))}
            </div>
          </div>
        </motion.div>

        {/* Navigation Buttons */}
        <div className="flex justify-between items-center pt-4">
          <Button
            variant="outline"
            onClick={() => navigate(`/matches/${parseInt(id!) - 1}`)}
            className="gap-2"
          >
            <ChevronLeft className="w-4 h-4" />
            Partida Anterior
          </Button>
          <Button
            variant="outline"
            onClick={() => navigate(`/matches/${parseInt(id!) + 1}`)}
            className="gap-2"
          >
            Próxima Partida
            <ChevronRight className="w-4 h-4" />
          </Button>
        </div>
      </div>
    </div>
  )
}

export default MatchDetail