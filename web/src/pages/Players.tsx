import { useState } from 'react'
import { Search, Plus, Users, Trophy, TrendingUp, Target, Loader2, AlertCircle, UserX } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Skeleton } from '@/components/ui/skeleton'
import { PageTransition, StaggerContainer, StaggerItem } from '@/components/animations'
import { usePlayers } from '@/hooks/usePlayerData'
import { PlayerProfile } from '@/services/playerService'

const Players = () => {
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedPlayerId, setSelectedPlayerId] = useState<string | null>(null)

  const { data: players, isLoading, isError, refetch } = usePlayers(
    searchTerm ? { search: searchTerm } : undefined
  )

  const filteredPlayers = players || []
  const selectedPlayer = filteredPlayers.find(p => p.id === selectedPlayerId) || filteredPlayers[0] || null

  const getCountryFlag = (country?: string) => {
    if (!country) return '🏳️'
    const flags: Record<string, string> = {
      'BR': '🇧🇷',
      'BRA': '🇧🇷',
      'ESP': '🇪🇸',
      'SRB': '🇷🇸',
      'USA': '🇺🇸',
      'GER': '🇩🇪',
      'FRA': '🇫🇷',
      'ITA': '🇮🇹',
      'GBR': '🇬🇧',
      'ARG': '🇦🇷',
    }
    return flags[country.toUpperCase()] || '🏳️'
  }

  const getWinPercentage = (player: PlayerProfile) => {
    if (!player.stats || player.stats.total_matches === 0) return 0
    return player.stats.win_percentage || 0
  }

  // Loading state
  if (isLoading) {
    return (
      <PageTransition>
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold tracking-tight">Players</h1>
              <p className="text-muted-foreground">Manage player profiles and performance statistics</p>
            </div>
          </div>
          <Card>
            <CardContent className="p-6">
              <Skeleton className="h-10 w-full" />
            </CardContent>
          </Card>
          <div className="grid gap-6 lg:grid-cols-4">
            <div className="lg:col-span-1">
              <Card>
                <CardHeader><Skeleton className="h-6 w-32" /></CardHeader>
                <CardContent className="space-y-2">
                  {[1, 2, 3].map(i => (
                    <Skeleton key={i} className="h-16 w-full" />
                  ))}
                </CardContent>
              </Card>
            </div>
            <div className="lg:col-span-3 space-y-6">
              <Card><CardContent className="p-6"><Skeleton className="h-32 w-full" /></CardContent></Card>
              <div className="grid gap-6 md:grid-cols-3">
                {[1, 2, 3].map(i => (
                  <Card key={i}><CardContent className="p-6"><Skeleton className="h-24 w-full" /></CardContent></Card>
                ))}
              </div>
            </div>
          </div>
        </div>
      </PageTransition>
    )
  }

  // Error state
  if (isError) {
    return (
      <PageTransition>
        <div className="space-y-6">
          <div>
            <h1 className="text-3xl font-bold tracking-tight">Players</h1>
            <p className="text-muted-foreground">Manage player profiles and performance statistics</p>
          </div>
          <Card>
            <CardContent className="p-12 text-center">
              <AlertCircle className="w-12 h-12 mx-auto mb-4 text-destructive" />
              <h3 className="text-lg font-semibold mb-2">Error loading players</h3>
              <p className="text-muted-foreground mb-4">Could not load the player list. Please try again.</p>
              <Button onClick={() => refetch()} variant="outline">
                <Loader2 className="w-4 h-4 mr-2" />
                Retry
              </Button>
            </CardContent>
          </Card>
        </div>
      </PageTransition>
    )
  }

  return (
    <PageTransition>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Players</h1>
          <p className="text-muted-foreground">
            Manage player profiles and performance statistics
          </p>
        </div>
        <Button>
          <Plus className="w-4 h-4 mr-2" />
          Add Player
        </Button>
      </div>

      {/* Search */}
      <Card>
        <CardContent className="p-6">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-muted-foreground" />
            <input
              type="text"
              placeholder="Search players..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10 pr-4 py-2 w-full bg-background border border-input rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-ring"
            />
          </div>
        </CardContent>
      </Card>

      {/* Empty state */}
      {filteredPlayers.length === 0 ? (
        <Card>
          <CardContent className="p-12 text-center">
            <UserX className="w-12 h-12 mx-auto mb-4 text-muted-foreground" />
            <h3 className="text-lg font-semibold mb-2">No players found</h3>
            <p className="text-muted-foreground">
              {searchTerm ? `No players match "${searchTerm}". Try a different search.` : 'No players registered yet.'}
            </p>
          </CardContent>
        </Card>
      ) : (
      <div className="grid gap-6 lg:grid-cols-4">
        {/* Players List */}
        <div className="lg:col-span-1">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <Users className="w-5 h-5 mr-2" />
                Players ({filteredPlayers.length})
              </CardTitle>
            </CardHeader>
            <CardContent>
              <StaggerContainer className="space-y-2">
                {filteredPlayers.map((player) => (
                  <StaggerItem key={player.id}>
                    <div
                    onClick={() => setSelectedPlayerId(player.id)}
                    className={`p-3 rounded-lg cursor-pointer transition-colors ${
                      selectedPlayer?.id === player.id
                        ? 'bg-primary text-primary-foreground'
                        : 'hover:bg-accent'
                    }`}
                  >
                    <div className="flex items-center space-x-3">
                      <div className="w-10 h-10 bg-muted rounded-full flex items-center justify-center overflow-hidden">
                        {player.avatar_url ? (
                          <img src={player.avatar_url} alt={player.full_name} className="w-full h-full object-cover" />
                        ) : (
                          <span className="text-lg">{getCountryFlag(player.country)}</span>
                        )}
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="font-medium truncate">{player.full_name}</p>
                        <p className="text-sm opacity-75">@{player.username}</p>
                      </div>
                    </div>
                  </div>
                  </StaggerItem>
                ))}
              </StaggerContainer>
            </CardContent>
          </Card>
        </div>

        {/* Player Details */}
        {selectedPlayer && (
        <div className="lg:col-span-3 space-y-6">
          {/* Player Info */}
          <Card>
            <CardContent className="p-6">
              <div className="flex items-start space-x-6">
                <div className="w-24 h-24 bg-muted rounded-full flex items-center justify-center text-4xl overflow-hidden">
                  {selectedPlayer.avatar_url ? (
                    <img src={selectedPlayer.avatar_url} alt={selectedPlayer.full_name} className="w-full h-full object-cover" />
                  ) : (
                    getCountryFlag(selectedPlayer.country)
                  )}
                </div>
                <div className="flex-1">
                  <h2 className="text-2xl font-bold mb-2">{selectedPlayer.full_name}</h2>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                    <div>
                      <span className="text-muted-foreground">Username</span>
                      <p className="font-medium">@{selectedPlayer.username}</p>
                    </div>
                    <div>
                      <span className="text-muted-foreground">Country</span>
                      <p className="font-medium">{getCountryFlag(selectedPlayer.country)} {selectedPlayer.country || 'N/A'}</p>
                    </div>
                    {selectedPlayer.height_cm && (
                    <div>
                      <span className="text-muted-foreground">Height</span>
                      <p className="font-medium">{selectedPlayer.height_cm} cm</p>
                    </div>
                    )}
                    {selectedPlayer.laterality && (
                    <div>
                      <span className="text-muted-foreground">Playing Hand</span>
                      <p className="font-medium capitalize">{selectedPlayer.laterality}</p>
                    </div>
                    )}
                  </div>
                  {(selectedPlayer.backhand_type || selectedPlayer.gender) && (
                  <div className="grid grid-cols-2 md:grid-cols-3 gap-4 text-sm mt-4">
                    {selectedPlayer.backhand_type && (
                    <div>
                      <span className="text-muted-foreground">Backhand</span>
                      <p className="font-medium capitalize">{selectedPlayer.backhand_type}</p>
                    </div>
                    )}
                    {selectedPlayer.gender && (
                    <div>
                      <span className="text-muted-foreground">Gender</span>
                      <p className="font-medium capitalize">{selectedPlayer.gender}</p>
                    </div>
                    )}
                  </div>
                  )}
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Statistics Overview */}
          {selectedPlayer.stats && (
          <div className="grid gap-6 md:grid-cols-3">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <Trophy className="w-5 h-5 mr-2 text-court-accent" />
                  Match Record
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-center">
                  <div className="text-3xl font-bold mb-2">
                    {selectedPlayer.stats.wins}-{selectedPlayer.stats.losses}
                  </div>
                  <div className="text-sm text-muted-foreground mb-4">
                    {getWinPercentage(selectedPlayer).toFixed(1)}% Win Rate
                  </div>
                  <div className="w-full bg-secondary rounded-full h-2">
                    <div
                      className="bg-court-accent h-2 rounded-full"
                      style={{ width: `${getWinPercentage(selectedPlayer)}%` }}
                    />
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <Target className="w-5 h-5 mr-2 text-court-accent" />
                  Serving
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <div className="flex justify-between">
                    <span className="text-sm">Aces</span>
                    <span className="font-medium">{selectedPlayer.stats.aces}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm">Double Faults</span>
                    <span className="font-medium">{selectedPlayer.stats.double_faults}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm">1st Serve %</span>
                    <span className="font-medium">{selectedPlayer.stats.first_serve_percentage?.toFixed(1)}%</span>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <TrendingUp className="w-5 h-5 mr-2 text-court-accent" />
                  Performance
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <div className="flex justify-between">
                    <span className="text-sm">Winners</span>
                    <span className="font-medium">{selectedPlayer.stats.winners}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm">Unforced Errors</span>
                    <span className="font-medium">{selectedPlayer.stats.unforced_errors}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm">Total Matches</span>
                    <span className="font-medium">{selectedPlayer.stats.total_matches}</span>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
          )}

          {/* Detailed Statistics */}
          {selectedPlayer.stats && (
          <Card>
            <CardHeader>
              <CardTitle>Detailed Statistics</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid gap-6 md:grid-cols-2">
                <div>
                  <h4 className="font-medium mb-4">Serving Performance</h4>
                  <div className="space-y-3">
                    {[
                      { label: 'First Serve Percentage', value: selectedPlayer.stats.first_serve_percentage || 0 },
                      { label: 'Win Percentage', value: getWinPercentage(selectedPlayer) },
                    ].map((stat) => (
                      <div key={stat.label}>
                        <div className="flex justify-between text-sm mb-1">
                          <span>{stat.label}</span>
                          <span>{stat.value.toFixed(1)}%</span>
                        </div>
                        <div className="w-full bg-secondary rounded-full h-2">
                          <div
                            className="bg-court-accent h-2 rounded-full"
                            style={{ width: `${Math.min(stat.value, 100)}%` }}
                          />
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                <div>
                  <h4 className="font-medium mb-4">Shot Statistics</h4>
                  <div className="space-y-3">
                    <div className="flex justify-between">
                      <span className="text-sm">Aces</span>
                      <span className="font-medium">{selectedPlayer.stats.aces}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-sm">Double Faults</span>
                      <span className="font-medium">{selectedPlayer.stats.double_faults}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-sm">Winners</span>
                      <span className="font-medium">{selectedPlayer.stats.winners}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-sm">Unforced Errors</span>
                      <span className="font-medium">{selectedPlayer.stats.unforced_errors}</span>
                    </div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
          )}

          {/* Bio */}
          {selectedPlayer.bio && (
          <Card>
            <CardHeader>
              <CardTitle>Bio</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-muted-foreground">{selectedPlayer.bio}</p>
            </CardContent>
          </Card>
          )}
        </div>
        )}
      </div>
      )}
      </div>
    </PageTransition>
  )
}

export default Players
