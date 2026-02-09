import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { User, Heart } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { PageTransition } from '@/components/animations'
import { ProfileHeader } from '@/components/player/ProfileHeader'
import { ProfileTabs } from '@/components/player/ProfileTabs'
import { WinLossBar } from '@/components/player/WinLossBar'
import { ActivityChart } from '@/components/player/ActivityChart'
import { playerService, PlayerProfile as PlayerProfileType, PlayerActivity, WinLossStats, RecentMatch } from '@/services/playerService'
import { useAuthStore } from '@/stores/authStore'
import toast from 'react-hot-toast'

const PlayerProfile = () => {
  const { username } = useParams<{ username: string }>()
  const navigate = useNavigate()
  const { user: currentUser } = useAuthStore()
  const [loading, setLoading] = useState(true)
  const [player, setPlayer] = useState<PlayerProfileType | null>(null)
  const [activity, setActivity] = useState<PlayerActivity[]>([])
  const [winLossStats, setWinLossStats] = useState<WinLossStats | null>(null)
  const [recentMatches, setRecentMatches] = useState<RecentMatch[]>([])

  const isOwnProfile = currentUser?.username === username

  useEffect(() => {
    if (!username) {
      navigate('/app/players')
      return
    }

    loadPlayerProfile()
  }, [username])

  const loadPlayerProfile = async () => {
    if (!username) return

    try {
      setLoading(true)

      // Load player profile
      const profileData = await playerService.getPlayerByUsername(username)
      setPlayer(profileData)

      // Load additional data in parallel
      const [activityData, statsData, matchesData] = await Promise.all([
        playerService.getPlayerActivity(profileData.id, 12),
        playerService.getWinLossByType(profileData.id),
        playerService.getRecentForm(profileData.id, 20)
      ])

      setActivity(activityData)
      setWinLossStats(statsData)
      setRecentMatches(matchesData)
    } catch (error) {
      console.error('Error loading player profile:', error)
      toast.error('Erro ao carregar perfil do jogador')
      navigate('/app/players')
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <PageTransition>
        <div className="flex items-center justify-center min-h-screen">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-court-accent"></div>
        </div>
      </PageTransition>
    )
  }

  if (!player) {
    return (
      <PageTransition>
        <div className="text-center py-12">
          <p className="text-muted-foreground">Jogador não encontrado</p>
        </div>
      </PageTransition>
    )
  }

  const mainContent = (
    <div className="space-y-6">
      {/* Player Info Card */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <User className="w-5 h-5 mr-2" />
            Informações do Jogador
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {player.gender && (
              <div>
                <p className="text-sm text-muted-foreground">Gênero</p>
                <p className="font-medium capitalize">{player.gender === 'male' ? 'Masculino' : player.gender === 'female' ? 'Feminino' : 'Outro'}</p>
              </div>
            )}
            {player.height_cm && (
              <div>
                <p className="text-sm text-muted-foreground">Altura</p>
                <p className="font-medium">{player.height_cm} cm</p>
              </div>
            )}
            {player.laterality && (
              <div>
                <p className="text-sm text-muted-foreground">Lateralidade</p>
                <p className="font-medium capitalize">{player.laterality === 'right' ? 'Destro' : 'Canhoto'}</p>
              </div>
            )}
            {player.backhand_type && (
              <div>
                <p className="text-sm text-muted-foreground">Backhand</p>
                <p className="font-medium capitalize">{player.backhand_type === 'one-handed' ? 'Uma mão' : 'Duas mãos'}</p>
              </div>
            )}
          </div>
          {player.bio && (
            <div className="mt-4">
              <p className="text-sm text-muted-foreground mb-1">Bio</p>
              <p className="text-muted-foreground leading-relaxed">{player.bio}</p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Win/Loss by Type */}
      {winLossStats && (
        <Card>
          <CardHeader>
            <CardTitle>Vitórias e Derrotas por Tipo</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <WinLossBar wins={winLossStats.singles.wins} losses={winLossStats.singles.losses} label="Simples" />
            <WinLossBar wins={winLossStats.doubles.wins} losses={winLossStats.doubles.losses} label="Duplas" />
            <WinLossBar wins={winLossStats.ranking.wins} losses={winLossStats.ranking.losses} label="Rankings" />
            <WinLossBar wins={winLossStats.tournaments.wins} losses={winLossStats.tournaments.losses} label="Torneios" />
            <WinLossBar wins={winLossStats.friendly.wins} losses={winLossStats.friendly.losses} label="Amistosos" />
          </CardContent>
        </Card>
      )}

      {/* Recent Matches */}
      {recentMatches.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Resultados dos Últimos 20 Jogos</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex flex-wrap gap-2 mb-4">
              {recentMatches.slice(0, 20).map((match, index) => (
                <div
                  key={index}
                  className={`w-10 h-10 rounded-full flex items-center justify-center font-bold text-sm ${
                    match.result === 'W' ? 'bg-green-500 text-white' : 'bg-red-500 text-white'
                  }`}
                  title={`${match.result === 'W' ? 'Vitória' : 'Derrota'} vs ${match.opponent_name} (${match.score})`}
                >
                  {match.result}
                </div>
              ))}
            </div>
            <div className="space-y-2 max-h-96 overflow-y-auto">
              {recentMatches.map((match, index) => (
                <div
                  key={index}
                  className="flex items-center justify-between p-3 rounded-lg border border-border hover:bg-accent/50 transition-colors"
                >
                  <div className="flex items-center gap-3">
                    <div
                      className={`w-2 h-2 rounded-full ${
                        match.result === 'W' ? 'bg-green-500' : 'bg-red-500'
                      }`}
                    />
                    <div>
                      <p className="font-medium">vs {match.opponent_name}</p>
                      <p className="text-sm text-muted-foreground">
                        {match.tournament || 'Amistoso'} • {match.surface}
                      </p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="font-medium">{match.score}</p>
                    <p className="text-sm text-muted-foreground">
                      {new Date(match.date).toLocaleDateString('pt-BR')}
                    </p>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Activity Chart */}
      {activity.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Gráfico de Atividade</CardTitle>
          </CardHeader>
          <CardContent>
            <ActivityChart activity={activity} />
          </CardContent>
        </Card>
      )}

      {/* Player Stats */}
      {player.stats && (
        <Card>
          <CardHeader>
            <CardTitle>Estatísticas</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div>
                <p className="text-sm text-muted-foreground">Win Rate</p>
                <p className="text-2xl font-bold">{player.stats.win_percentage.toFixed(1)}%</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Partidas</p>
                <p className="text-2xl font-bold">{player.stats.total_matches}</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Aces</p>
                <p className="text-2xl font-bold">{player.stats.aces}</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">1º Saque</p>
                <p className="text-2xl font-bold">{player.stats.first_serve_percentage.toFixed(0)}%</p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* H2H Link (placeholder) */}
      <Card>
        <CardContent className="p-4">
          <Button variant="outline" className="w-full">
            <Heart className="w-4 h-4 mr-2" />
            Ver Head-to-Head
          </Button>
        </CardContent>
      </Card>
    </div>
  )

  return (
    <PageTransition>
      <div className="space-y-6 pb-8">
        <ProfileHeader
          username={player.username}
          fullName={player.full_name}
          avatarUrl={player.avatar_url}
          coverPhotoUrl={player.cover_photo_url}
          gamesCount={player.stats?.total_matches || 0}
          rankingsCount={winLossStats?.ranking.wins || 0}
          tournamentsCount={winLossStats?.tournaments.wins || 0}
          isOwnProfile={isOwnProfile}
        />

        <ProfileTabs mainContent={mainContent} />
      </div>
    </PageTransition>
  )
}

export default PlayerProfile
