/**
 * NewMatch - TT-145
 * Fluxo de criacao de partida com selecao de jogadores
 */

import { useState, useMemo, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import {
  Search,
  User,
  MapPin,
  Calendar,
  Target,
  Play,
  ArrowLeft,
  Clock,
  CheckCircle2,
} from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { PageTransition } from '@/components/animations'
import { playerService, PlayerProfile } from '@/services/playerService'
import { venueService, Venue } from '@/services/venueService'
import matchService from '@/services/matchService'
import gameControlService from '@/services/gameControlService'
import { useUIStore } from '@/stores/uiStore'

type MatchFormat = 'best_of_3' | 'best_of_5'
type SurfaceType = 'hard' | 'clay' | 'grass' | 'carpet'

const NewMatch = () => {
  const navigate = useNavigate()
  const { addNotification } = useUIStore()

  // Form state
  const [step, setStep] = useState<'players' | 'details' | 'confirm'>(
    'players'
  )
  const [player1, setPlayer1] = useState<PlayerProfile | null>(null)
  const [player2, setPlayer2] = useState<PlayerProfile | null>(null)
  const [venue, setVenue] = useState<Venue | null>(null)
  const [format, setFormat] = useState<MatchFormat>('best_of_3')
  const [surface, setSurface] = useState<SurfaceType>('hard')
  const [serverPlayer, setServerPlayer] = useState<'player1' | 'player2'>(
    'player1'
  )
  const [startImmediately, setStartImmediately] = useState(true)

  // Search states
  const [player1Search, setPlayer1Search] = useState('')
  const [player2Search, setPlayer2Search] = useState('')
  const [venueSearch, setVenueSearch] = useState('')
  const [players, setPlayers] = useState<PlayerProfile[]>([])
  const [venues, setVenues] = useState<Venue[]>([])
  const [loadingPlayers, setLoadingPlayers] = useState(false)
  const [loadingVenues, setLoadingVenues] = useState(false)
  const [isCreating, setIsCreating] = useState(false)

  // Debounced search for players
  useEffect(() => {
    const timer = setTimeout(async () => {
      if (player1Search.length >= 2 || player2Search.length >= 2) {
        setLoadingPlayers(true)
        try {
          const searchTerm = player1Search || player2Search
          const results = await playerService.getPlayers(
            { search: searchTerm },
            0,
            20
          )
          setPlayers(results)
        } catch (error) {
          console.error('Error fetching players:', error)
        } finally {
          setLoadingPlayers(false)
        }
      } else {
        setPlayers([])
      }
    }, 300)

    return () => clearTimeout(timer)
  }, [player1Search, player2Search])

  // Load venues
  useEffect(() => {
    const loadVenues = async () => {
      setLoadingVenues(true)
      try {
        const response = await venueService.listVenues({
          limit: 50,
          search: venueSearch || undefined,
        })
        setVenues(response.venues)
      } catch (error) {
        console.error('Error fetching venues:', error)
      } finally {
        setLoadingVenues(false)
      }
    }

    loadVenues()
  }, [venueSearch])

  // Filter players for autocomplete
  const filteredPlayer1Options = useMemo(() => {
    return players.filter((p) => p.id !== player2?.id)
  }, [players, player2])

  const filteredPlayer2Options = useMemo(() => {
    return players.filter((p) => p.id !== player1?.id)
  }, [players, player1])

  // Surface options
  const surfaceOptions: { value: SurfaceType; label: string; icon: string }[] =
    [
      { value: 'hard', label: 'Hard Court', icon: '🎾' },
      { value: 'clay', label: 'Clay', icon: '🟧' },
      { value: 'grass', label: 'Grass', icon: '🟩' },
      { value: 'carpet', label: 'Carpet', icon: '🏢' },
    ]

  // Handle create match
  const handleCreateMatch = async () => {
    if (!player1 || !player2) {
      addNotification({
        type: 'error',
        title: 'Erro',
        message: 'Selecione ambos os jogadores',
      })
      return
    }

    setIsCreating(true)
    try {
      // Create match
      const matchData = {
        player1Id: player1.id,
        player2Id: player2.id,
        tournament: venue?.name || 'Friendly Match',
        round: 'Match',
        surface,
        scheduledDate: new Date().toISOString(),
      }

      const createdMatch = await matchService.createMatch(matchData)

      if (startImmediately) {
        // Start match immediately
        const serverPlayerId = serverPlayer === 'player1' ? player1.id : player2.id

        await gameControlService.startMatch({
          match_id: createdMatch.id,
          server_player_id: serverPlayerId,
          tournament_data: {
            name: venue?.name,
            round: 'Match',
            surface,
          },
        })

        addNotification({
          type: 'success',
          title: 'Partida Iniciada',
          message: 'A partida foi criada e iniciada com sucesso',
        })

        // Redirect to live scoring page
        navigate(`/app/match/${createdMatch.id}`)
      } else {
        addNotification({
          type: 'success',
          title: 'Partida Criada',
          message: 'A partida foi agendada com sucesso',
        })

        // Redirect to matches list
        navigate('/app/matches')
      }
    } catch (error: any) {
      console.error('Error creating match:', error)
      addNotification({
        type: 'error',
        title: 'Erro ao Criar Partida',
        message:
          error.response?.data?.message || 'Ocorreu um erro ao criar a partida',
      })
    } finally {
      setIsCreating(false)
    }
  }

  // Render player selector
  const renderPlayerSelector = (
    playerNum: 1 | 2,
    selectedPlayer: PlayerProfile | null,
    setSelectedPlayer: (player: PlayerProfile | null) => void,
    searchValue: string,
    setSearchValue: (value: string) => void,
    options: PlayerProfile[]
  ) => (
    <div className="space-y-3">
      <label className="text-sm font-medium text-slate-300">
        Jogador {playerNum}
      </label>

      {selectedPlayer ? (
        <div className="flex items-center gap-3 p-3 bg-court-accent/10 border border-court-accent/30 rounded-lg">
          <div className="w-10 h-10 rounded-full bg-slate-600 flex items-center justify-center overflow-hidden">
            {selectedPlayer.avatar_url ? (
              <img
                src={selectedPlayer.avatar_url}
                alt={selectedPlayer.full_name}
                className="w-full h-full object-cover"
              />
            ) : (
              <User className="w-5 h-5 text-slate-400" />
            )}
          </div>
          <div className="flex-1">
            <p className="text-sm font-medium text-slate-100">
              {selectedPlayer.full_name}
            </p>
            <p className="text-xs text-slate-400">@{selectedPlayer.username}</p>
          </div>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => {
              setSelectedPlayer(null)
              setSearchValue('')
            }}
            className="text-red-400 hover:text-red-300"
          >
            Trocar
          </Button>
        </div>
      ) : (
        <div className="space-y-2">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
            <Input
              type="text"
              placeholder="Buscar jogador..."
              value={searchValue}
              onChange={(e) => setSearchValue(e.target.value)}
              className="pl-10"
            />
          </div>

          {searchValue && (
            <div className="max-h-48 overflow-y-auto space-y-1 bg-slate-700/50 rounded-lg p-2">
              {loadingPlayers ? (
                <div className="text-center py-4 text-sm text-slate-400">
                  Buscando...
                </div>
              ) : options.length > 0 ? (
                options.map((player) => (
                  <button
                    key={player.id}
                    onClick={() => {
                      setSelectedPlayer(player)
                      setSearchValue('')
                    }}
                    className="w-full flex items-center gap-2 p-2 hover:bg-slate-600 rounded transition-colors text-left"
                  >
                    <div className="w-8 h-8 rounded-full bg-slate-600 flex items-center justify-center overflow-hidden">
                      {player.avatar_url ? (
                        <img
                          src={player.avatar_url}
                          alt={player.full_name}
                          className="w-full h-full object-cover"
                        />
                      ) : (
                        <User className="w-4 h-4 text-slate-400" />
                      )}
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-slate-200 truncate">
                        {player.full_name}
                      </p>
                      <p className="text-xs text-slate-400">
                        @{player.username}
                      </p>
                    </div>
                  </button>
                ))
              ) : (
                <div className="text-center py-4 text-sm text-slate-400">
                  Nenhum jogador encontrado
                </div>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  )

  return (
    <PageTransition>
      <div className="min-h-screen bg-slate-900 p-6">
        <div className="max-w-2xl mx-auto space-y-6">
          {/* Header */}
          <div className="flex items-center gap-4">
            <Button
              variant="ghost"
              size="icon"
              onClick={() => navigate(-1)}
              className="text-slate-400 hover:text-slate-100"
            >
              <ArrowLeft className="w-5 h-5" />
            </Button>
            <div>
              <h1 className="text-3xl font-bold text-slate-100">Nova Partida</h1>
              <p className="text-slate-400 mt-1">
                Configure os detalhes da partida
              </p>
            </div>
          </div>

          {/* Progress Steps */}
          <div className="flex items-center gap-2">
            {['players', 'details', 'confirm'].map((s, idx) => (
              <div key={s} className="flex items-center gap-2 flex-1">
                <div
                  className={`h-2 flex-1 rounded-full transition-all ${
                    step === s
                      ? 'bg-court-accent'
                      : idx <
                        ['players', 'details', 'confirm'].indexOf(step)
                      ? 'bg-court-accent/50'
                      : 'bg-slate-700'
                  }`}
                />
              </div>
            ))}
          </div>

          {/* Step 1: Players */}
          {step === 'players' && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="space-y-6"
            >
              <Card>
                <CardHeader>
                  <CardTitle className="text-slate-100 flex items-center gap-2">
                    <User className="w-5 h-5 text-court-accent" />
                    Selecionar Jogadores
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-6">
                  {renderPlayerSelector(
                    1,
                    player1,
                    setPlayer1,
                    player1Search,
                    setPlayer1Search,
                    filteredPlayer1Options
                  )}
                  {renderPlayerSelector(
                    2,
                    player2,
                    setPlayer2,
                    player2Search,
                    setPlayer2Search,
                    filteredPlayer2Options
                  )}
                </CardContent>
              </Card>

              <Button
                variant="filled"
                size="lg"
                className="w-full"
                onClick={() => setStep('details')}
                disabled={!player1 || !player2}
              >
                Continuar
              </Button>
            </motion.div>
          )}

          {/* Step 2: Details */}
          {step === 'details' && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="space-y-6"
            >
              {/* Venue */}
              <Card>
                <CardHeader>
                  <CardTitle className="text-slate-100 flex items-center gap-2">
                    <MapPin className="w-5 h-5 text-court-accent" />
                    Local da Partida
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-2">
                    {venue ? (
                      <div className="flex items-center gap-3 p-3 bg-court-accent/10 border border-court-accent/30 rounded-lg">
                        <MapPin className="w-5 h-5 text-court-accent" />
                        <div className="flex-1">
                          <p className="text-sm font-medium text-slate-100">
                            {venue.name}
                          </p>
                          <p className="text-xs text-slate-400">
                            {venue.city}, {venue.country}
                          </p>
                        </div>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => setVenue(null)}
                          className="text-red-400 hover:text-red-300"
                        >
                          Remover
                        </Button>
                      </div>
                    ) : (
                      <div className="space-y-2">
                        <Input
                          type="text"
                          placeholder="Buscar local..."
                          value={venueSearch}
                          onChange={(e) => setVenueSearch(e.target.value)}
                        />
                        {venueSearch && (
                          <div className="max-h-48 overflow-y-auto space-y-1 bg-slate-700/50 rounded-lg p-2">
                            {loadingVenues ? (
                              <div className="text-center py-4 text-sm text-slate-400">
                                Buscando...
                              </div>
                            ) : venues.length > 0 ? (
                              venues.map((v) => (
                                <button
                                  key={v.id}
                                  onClick={() => {
                                    setVenue(v)
                                    setVenueSearch('')
                                  }}
                                  className="w-full flex items-center gap-2 p-2 hover:bg-slate-600 rounded transition-colors text-left"
                                >
                                  <MapPin className="w-4 h-4 text-court-accent" />
                                  <div>
                                    <p className="text-sm font-medium text-slate-200">
                                      {v.name}
                                    </p>
                                    <p className="text-xs text-slate-400">
                                      {v.city}, {v.country}
                                    </p>
                                  </div>
                                </button>
                              ))
                            ) : (
                              <div className="text-center py-4 text-sm text-slate-400">
                                Nenhum local encontrado
                              </div>
                            )}
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                </CardContent>
              </Card>

              {/* Format */}
              <Card>
                <CardHeader>
                  <CardTitle className="text-slate-100 flex items-center gap-2">
                    <Target className="w-5 h-5 text-court-accent" />
                    Formato da Partida
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="flex gap-3">
                    <button
                      onClick={() => setFormat('best_of_3')}
                      className={`flex-1 p-4 rounded-lg border-2 transition-all ${
                        format === 'best_of_3'
                          ? 'border-court-accent bg-court-accent/10'
                          : 'border-slate-700 bg-slate-800 hover:border-slate-600'
                      }`}
                    >
                      <p className="font-semibold text-slate-100">
                        Melhor de 3
                      </p>
                      <p className="text-xs text-slate-400 mt-1">
                        2 sets para vencer
                      </p>
                    </button>
                    <button
                      onClick={() => setFormat('best_of_5')}
                      className={`flex-1 p-4 rounded-lg border-2 transition-all ${
                        format === 'best_of_5'
                          ? 'border-court-accent bg-court-accent/10'
                          : 'border-slate-700 bg-slate-800 hover:border-slate-600'
                      }`}
                    >
                      <p className="font-semibold text-slate-100">
                        Melhor de 5
                      </p>
                      <p className="text-xs text-slate-400 mt-1">
                        3 sets para vencer
                      </p>
                    </button>
                  </div>
                </CardContent>
              </Card>

              {/* Surface */}
              <Card>
                <CardHeader>
                  <CardTitle className="text-slate-100 flex items-center gap-2">
                    <Calendar className="w-5 h-5 text-court-accent" />
                    Tipo de Superfície
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-2 gap-3">
                    {surfaceOptions.map((option) => (
                      <button
                        key={option.value}
                        onClick={() => setSurface(option.value)}
                        className={`p-4 rounded-lg border-2 transition-all ${
                          surface === option.value
                            ? 'border-court-accent bg-court-accent/10'
                            : 'border-slate-700 bg-slate-800 hover:border-slate-600'
                        }`}
                      >
                        <p className="text-2xl mb-1">{option.icon}</p>
                        <p className="font-semibold text-slate-100 text-sm">
                          {option.label}
                        </p>
                      </button>
                    ))}
                  </div>
                </CardContent>
              </Card>

              <div className="flex gap-3">
                <Button
                  variant="outline"
                  size="lg"
                  className="flex-1"
                  onClick={() => setStep('players')}
                >
                  Voltar
                </Button>
                <Button
                  variant="filled"
                  size="lg"
                  className="flex-1"
                  onClick={() => setStep('confirm')}
                >
                  Continuar
                </Button>
              </div>
            </motion.div>
          )}

          {/* Step 3: Confirm */}
          {step === 'confirm' && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="space-y-6"
            >
              <Card>
                <CardHeader>
                  <CardTitle className="text-slate-100 flex items-center gap-2">
                    <CheckCircle2 className="w-5 h-5 text-court-accent" />
                    Confirmar Detalhes
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  {/* Players */}
                  <div className="p-4 bg-slate-700/50 rounded-lg space-y-3">
                    <p className="text-xs font-medium text-slate-400 uppercase">
                      Jogadores
                    </p>
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <div className="w-8 h-8 rounded-full bg-slate-600 flex items-center justify-center overflow-hidden">
                          {player1?.avatar_url ? (
                            <img
                              src={player1.avatar_url}
                              alt={player1.full_name}
                              className="w-full h-full object-cover"
                            />
                          ) : (
                            <User className="w-4 h-4 text-slate-400" />
                          )}
                        </div>
                        <span className="text-sm font-medium text-slate-100">
                          {player1?.full_name}
                        </span>
                      </div>
                      <span className="text-xs text-slate-500">vs</span>
                      <div className="flex items-center gap-2">
                        <span className="text-sm font-medium text-slate-100">
                          {player2?.full_name}
                        </span>
                        <div className="w-8 h-8 rounded-full bg-slate-600 flex items-center justify-center overflow-hidden">
                          {player2?.avatar_url ? (
                            <img
                              src={player2.avatar_url}
                              alt={player2.full_name}
                              className="w-full h-full object-cover"
                            />
                          ) : (
                            <User className="w-4 h-4 text-slate-400" />
                          )}
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Match Details */}
                  <div className="grid grid-cols-2 gap-3">
                    <div className="p-3 bg-slate-700/50 rounded-lg">
                      <p className="text-xs text-slate-400">Local</p>
                      <p className="text-sm font-medium text-slate-100 mt-1">
                        {venue?.name || 'Não especificado'}
                      </p>
                    </div>
                    <div className="p-3 bg-slate-700/50 rounded-lg">
                      <p className="text-xs text-slate-400">Formato</p>
                      <p className="text-sm font-medium text-slate-100 mt-1">
                        {format === 'best_of_3' ? 'Melhor de 3' : 'Melhor de 5'}
                      </p>
                    </div>
                    <div className="p-3 bg-slate-700/50 rounded-lg">
                      <p className="text-xs text-slate-400">Superfície</p>
                      <p className="text-sm font-medium text-slate-100 mt-1 capitalize">
                        {
                          surfaceOptions.find((s) => s.value === surface)
                            ?.label
                        }
                      </p>
                    </div>
                    <div className="p-3 bg-slate-700/50 rounded-lg">
                      <p className="text-xs text-slate-400">Sacador Inicial</p>
                      <p className="text-sm font-medium text-slate-100 mt-1">
                        {serverPlayer === 'player1'
                          ? player1?.full_name
                          : player2?.full_name}
                      </p>
                    </div>
                  </div>

                  {/* Server Selection */}
                  <div className="space-y-2">
                    <p className="text-sm font-medium text-slate-300">
                      Quem saca primeiro?
                    </p>
                    <div className="flex gap-3">
                      <button
                        onClick={() => setServerPlayer('player1')}
                        className={`flex-1 p-3 rounded-lg border-2 transition-all ${
                          serverPlayer === 'player1'
                            ? 'border-court-accent bg-court-accent/10'
                            : 'border-slate-700 bg-slate-800'
                        }`}
                      >
                        <p className="text-sm font-medium text-slate-100">
                          {player1?.full_name}
                        </p>
                      </button>
                      <button
                        onClick={() => setServerPlayer('player2')}
                        className={`flex-1 p-3 rounded-lg border-2 transition-all ${
                          serverPlayer === 'player2'
                            ? 'border-court-accent bg-court-accent/10'
                            : 'border-slate-700 bg-slate-800'
                        }`}
                      >
                        <p className="text-sm font-medium text-slate-100">
                          {player2?.full_name}
                        </p>
                      </button>
                    </div>
                  </div>

                  {/* Start Options */}
                  <div className="space-y-2">
                    <p className="text-sm font-medium text-slate-300">
                      Opções de Início
                    </p>
                    <div className="flex gap-3">
                      <button
                        onClick={() => setStartImmediately(true)}
                        className={`flex-1 p-3 rounded-lg border-2 transition-all ${
                          startImmediately
                            ? 'border-court-accent bg-court-accent/10'
                            : 'border-slate-700 bg-slate-800'
                        }`}
                      >
                        <Play className="w-4 h-4 mx-auto mb-1 text-court-accent" />
                        <p className="text-sm font-medium text-slate-100">
                          Iniciar Agora
                        </p>
                      </button>
                      <button
                        onClick={() => setStartImmediately(false)}
                        className={`flex-1 p-3 rounded-lg border-2 transition-all ${
                          !startImmediately
                            ? 'border-court-accent bg-court-accent/10'
                            : 'border-slate-700 bg-slate-800'
                        }`}
                      >
                        <Clock className="w-4 h-4 mx-auto mb-1 text-slate-400" />
                        <p className="text-sm font-medium text-slate-100">
                          Agendar
                        </p>
                      </button>
                    </div>
                  </div>
                </CardContent>
              </Card>

              <div className="flex gap-3">
                <Button
                  variant="outline"
                  size="lg"
                  className="flex-1"
                  onClick={() => setStep('details')}
                  disabled={isCreating}
                >
                  Voltar
                </Button>
                <Button
                  variant="filled"
                  size="lg"
                  className="flex-1"
                  onClick={handleCreateMatch}
                  disabled={isCreating}
                >
                  {isCreating ? (
                    <>Criando...</>
                  ) : startImmediately ? (
                    <>
                      <Play className="w-4 h-4 mr-2" />
                      Criar e Iniciar
                    </>
                  ) : (
                    <>Criar Partida</>
                  )}
                </Button>
              </div>
            </motion.div>
          )}
        </div>
      </div>
    </PageTransition>
  )
}

export default NewMatch
