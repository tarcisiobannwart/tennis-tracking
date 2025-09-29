import { useState } from 'react'
import { Search, Plus, Users, Trophy, TrendingUp, Target } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'

// Mock data - in real app this would come from API
const playersData = [
  {
    id: '1',
    name: 'Rafael Nadal',
    country: 'ESP',
    ranking: 1,
    age: 37,
    height: 185,
    weight: 85,
    playingHand: 'left',
    backhand: 'two-handed',
    profileImage: '/api/players/1/photo',
    statistics: {
      matchesPlayed: 45,
      matchesWon: 39,
      winPercentage: 86.7,
      acesPerMatch: 5.2,
      doubleFaultsPerMatch: 2.1,
      firstServePercentage: 68.5,
      firstServeWonPercentage: 75.8,
      secondServeWonPercentage: 58.3,
      breakPointsSaved: 65.2,
      returnPointsWon: 32.1,
      netPointsWon: 71.4
    }
  },
  {
    id: '2',
    name: 'Novak Djokovic',
    country: 'SRB',
    ranking: 2,
    age: 36,
    height: 188,
    weight: 77,
    playingHand: 'right',
    backhand: 'two-handed',
    profileImage: '/api/players/2/photo',
    statistics: {
      matchesPlayed: 42,
      matchesWon: 37,
      winPercentage: 88.1,
      acesPerMatch: 7.8,
      doubleFaultsPerMatch: 1.9,
      firstServePercentage: 65.2,
      firstServeWonPercentage: 73.1,
      secondServeWonPercentage: 56.8,
      breakPointsSaved: 68.7,
      returnPointsWon: 34.5,
      netPointsWon: 69.2
    }
  },
  {
    id: '3',
    name: 'Carlos Alcaraz',
    country: 'ESP',
    ranking: 3,
    age: 20,
    height: 183,
    weight: 74,
    playingHand: 'right',
    backhand: 'two-handed',
    profileImage: '/api/players/3/photo',
    statistics: {
      matchesPlayed: 38,
      matchesWon: 32,
      winPercentage: 84.2,
      acesPerMatch: 6.5,
      doubleFaultsPerMatch: 2.3,
      firstServePercentage: 62.8,
      firstServeWonPercentage: 71.2,
      secondServeWonPercentage: 54.1,
      breakPointsSaved: 61.3,
      returnPointsWon: 29.8,
      netPointsWon: 73.6
    }
  }
]

const Players = () => {
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedPlayer, setSelectedPlayer] = useState(playersData[0])

  const filteredPlayers = playersData.filter(player =>
    player.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    player.country.toLowerCase().includes(searchTerm.toLowerCase())
  )

  const getCountryFlag = (country: string) => {
    const flags: Record<string, string> = {
      'ESP': '🇪🇸',
      'SRB': '🇷🇸',
      'USA': '🇺🇸',
      'GER': '🇩🇪',
      'FRA': '🇫🇷',
      'ITA': '🇮🇹'
    }
    return flags[country] || '🏳️'
  }

  return (
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
              <div className="space-y-2">
                {filteredPlayers.map((player) => (
                  <div
                    key={player.id}
                    onClick={() => setSelectedPlayer(player)}
                    className={`p-3 rounded-lg cursor-pointer transition-colors ${
                      selectedPlayer.id === player.id
                        ? 'bg-primary text-primary-foreground'
                        : 'hover:bg-accent'
                    }`}
                  >
                    <div className="flex items-center space-x-3">
                      <div className="w-10 h-10 bg-muted rounded-full flex items-center justify-center">
                        <span className="text-lg">
                          {getCountryFlag(player.country)}
                        </span>
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="font-medium truncate">{player.name}</p>
                        <p className="text-sm opacity-75">#{player.ranking}</p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Player Details */}
        <div className="lg:col-span-3 space-y-6">
          {/* Player Info */}
          <Card>
            <CardContent className="p-6">
              <div className="flex items-start space-x-6">
                <div className="w-24 h-24 bg-muted rounded-full flex items-center justify-center text-4xl">
                  {getCountryFlag(selectedPlayer.country)}
                </div>
                <div className="flex-1">
                  <h2 className="text-2xl font-bold mb-2">{selectedPlayer.name}</h2>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                    <div>
                      <span className="text-muted-foreground">Ranking</span>
                      <p className="font-medium">#{selectedPlayer.ranking}</p>
                    </div>
                    <div>
                      <span className="text-muted-foreground">Country</span>
                      <p className="font-medium">{selectedPlayer.country}</p>
                    </div>
                    <div>
                      <span className="text-muted-foreground">Age</span>
                      <p className="font-medium">{selectedPlayer.age}</p>
                    </div>
                    <div>
                      <span className="text-muted-foreground">Playing Hand</span>
                      <p className="font-medium capitalize">{selectedPlayer.playingHand}</p>
                    </div>
                  </div>
                  <div className="grid grid-cols-2 md:grid-cols-3 gap-4 text-sm mt-4">
                    <div>
                      <span className="text-muted-foreground">Height</span>
                      <p className="font-medium">{selectedPlayer.height} cm</p>
                    </div>
                    <div>
                      <span className="text-muted-foreground">Weight</span>
                      <p className="font-medium">{selectedPlayer.weight} kg</p>
                    </div>
                    <div>
                      <span className="text-muted-foreground">Backhand</span>
                      <p className="font-medium capitalize">{selectedPlayer.backhand}</p>
                    </div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Statistics Overview */}
          <div className="grid gap-6 md:grid-cols-3">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <Trophy className="w-5 h-5 mr-2 text-yellow-500" />
                  Match Record
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-center">
                  <div className="text-3xl font-bold mb-2">
                    {selectedPlayer.statistics.matchesWon}-
                    {selectedPlayer.statistics.matchesPlayed - selectedPlayer.statistics.matchesWon}
                  </div>
                  <div className="text-sm text-muted-foreground mb-4">
                    {selectedPlayer.statistics.winPercentage}% Win Rate
                  </div>
                  <div className="w-full bg-secondary rounded-full h-2">
                    <div
                      className="bg-green-500 h-2 rounded-full"
                      style={{ width: `${selectedPlayer.statistics.winPercentage}%` }}
                    />
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <Target className="w-5 h-5 mr-2 text-blue-500" />
                  Serving
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <div className="flex justify-between">
                    <span className="text-sm">Aces/Match</span>
                    <span className="font-medium">{selectedPlayer.statistics.acesPerMatch}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm">1st Serve %</span>
                    <span className="font-medium">{selectedPlayer.statistics.firstServePercentage}%</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm">1st Serve Won</span>
                    <span className="font-medium">{selectedPlayer.statistics.firstServeWonPercentage}%</span>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <TrendingUp className="w-5 h-5 mr-2 text-green-500" />
                  Return & Defense
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <div className="flex justify-between">
                    <span className="text-sm">Return Points Won</span>
                    <span className="font-medium">{selectedPlayer.statistics.returnPointsWon}%</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm">Break Points Saved</span>
                    <span className="font-medium">{selectedPlayer.statistics.breakPointsSaved}%</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm">Net Points Won</span>
                    <span className="font-medium">{selectedPlayer.statistics.netPointsWon}%</span>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Detailed Statistics */}
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
                      { label: 'First Serve Percentage', value: selectedPlayer.statistics.firstServePercentage },
                      { label: 'First Serve Won', value: selectedPlayer.statistics.firstServeWonPercentage },
                      { label: 'Second Serve Won', value: selectedPlayer.statistics.secondServeWonPercentage },
                      { label: 'Break Points Saved', value: selectedPlayer.statistics.breakPointsSaved }
                    ].map((stat) => (
                      <div key={stat.label}>
                        <div className="flex justify-between text-sm mb-1">
                          <span>{stat.label}</span>
                          <span>{stat.value}%</span>
                        </div>
                        <div className="w-full bg-secondary rounded-full h-2">
                          <div
                            className="bg-blue-500 h-2 rounded-full"
                            style={{ width: `${stat.value}%` }}
                          />
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                <div>
                  <h4 className="font-medium mb-4">Return & Court Coverage</h4>
                  <div className="space-y-3">
                    {[
                      { label: 'Return Points Won', value: selectedPlayer.statistics.returnPointsWon },
                      { label: 'Net Points Won', value: selectedPlayer.statistics.netPointsWon },
                      { label: 'Win Percentage', value: selectedPlayer.statistics.winPercentage }
                    ].map((stat) => (
                      <div key={stat.label}>
                        <div className="flex justify-between text-sm mb-1">
                          <span>{stat.label}</span>
                          <span>{stat.value}%</span>
                        </div>
                        <div className="w-full bg-secondary rounded-full h-2">
                          <div
                            className="bg-green-500 h-2 rounded-full"
                            style={{ width: `${stat.value}%` }}
                          />
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}

export default Players