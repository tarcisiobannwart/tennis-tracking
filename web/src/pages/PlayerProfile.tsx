import { useState } from 'react'
import { MessageCircle, Calendar, Trophy, Star, TrendingUp, Users, MapPin, Mail, Phone, Globe, Instagram, Twitter, Facebook } from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'

// Mock data - in real app this would come from API
interface PlayerProfile {
  id: string
  name: string
  country: string
  countryFlag: string
  ranking: number
  age: age
  bio: string
  profileImage: string
  coverImage: string
  stats: {
    yearsPro: number
    careerWins: number
    careerTitles: number
  }
  rating: {
    overall: number
    distribution: {
      5: number
      4: number
      3: number
      2: number
      1: number
    }
  }
  recentMatches: Array<{
    id: string
    tournament: string
    opponent: string
    result: 'win' | 'loss'
    score: string
    date: string
    surface: 'hard' | 'clay' | 'grass'
  }>
  upcomingEvents: Array<{
    id: string
    tournament: string
    location: string
    date: string
    surface: 'hard' | 'clay' | 'grass'
  }>
  contact: {
    email?: string
    phone?: string
    website?: string
  }
  social: {
    instagram?: string
    twitter?: string
    facebook?: string
  }
}

const mockPlayer: PlayerProfile = {
  id: '1',
  name: 'Rafael Nadal',
  country: 'Spain',
  countryFlag: '🇪🇸',
  ranking: 1,
  age: 37,
  bio: '22-time Grand Slam champion, known as the "King of Clay". Holds the record for most French Open titles (14) and is considered one of the greatest tennis players of all time.',
  profileImage: 'https://images.unsplash.com/photo-1599058917212-d750089bc07e?w=400&h=400&fit=crop',
  coverImage: 'https://images.unsplash.com/photo-1622279457486-62dcc4a431d6?w=1200&h=400&fit=crop',
  stats: {
    yearsPro: 20,
    careerWins: 1068,
    careerTitles: 92
  },
  rating: {
    overall: 4.8,
    distribution: {
      5: 856,
      4: 124,
      3: 15,
      2: 3,
      1: 2
    }
  },
  recentMatches: [
    {
      id: '1',
      tournament: 'Australian Open 2024',
      opponent: 'N. Djokovic',
      result: 'loss',
      score: '6-4, 3-6, 4-6',
      date: '2024-01-28',
      surface: 'hard'
    },
    {
      id: '2',
      tournament: 'Roland Garros 2023',
      opponent: 'C. Alcaraz',
      result: 'win',
      score: '6-3, 6-2, 7-5',
      date: '2023-06-11',
      surface: 'clay'
    },
    {
      id: '3',
      tournament: 'Madrid Open 2023',
      opponent: 'D. Medvedev',
      result: 'win',
      score: '6-4, 6-3',
      date: '2023-05-07',
      surface: 'clay'
    }
  ],
  upcomingEvents: [
    {
      id: '1',
      tournament: 'Roland Garros 2024',
      location: 'Paris, France',
      date: '2024-05-26',
      surface: 'clay'
    },
    {
      id: '2',
      tournament: 'Barcelona Open 2024',
      location: 'Barcelona, Spain',
      date: '2024-04-15',
      surface: 'clay'
    }
  ],
  contact: {
    email: 'contact@rafaelnadal.com',
    phone: '+34 xxx xxx xxx',
    website: 'rafaelnadal.com'
  },
  social: {
    instagram: '@rafaelnadal',
    twitter: '@RafaelNadal',
    facebook: 'RafaelNadal'
  }
}

const PlayerProfile = () => {
  const [player] = useState<PlayerProfile>(mockPlayer)

  const getSurfaceColor = (surface: string) => {
    switch (surface) {
      case 'hard':
        return 'bg-blue-500'
      case 'clay':
        return 'bg-orange-500'
      case 'grass':
        return 'bg-green-500'
      default:
        return 'bg-gray-500'
    }
  }

  const totalReviews = Object.values(player.rating.distribution).reduce((a, b) => a + b, 0)

  return (
    <div className="space-y-6 pb-8">
      {/* Hero Section with Cover Image */}
      <div className="relative h-[300px] rounded-lg overflow-hidden">
        <img
          src={player.coverImage}
          alt={player.name}
          className="w-full h-full object-cover"
        />
        <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-black/40 to-transparent" />

        {/* Profile Content Overlay */}
        <div className="absolute bottom-0 left-0 right-0 p-6">
          <div className="flex items-end justify-between">
            <div className="flex items-end space-x-6">
              {/* Profile Image */}
              <div className="w-32 h-32 rounded-full overflow-hidden border-4 border-background shadow-xl">
                <img
                  src={player.profileImage}
                  alt={player.name}
                  className="w-full h-full object-cover"
                />
              </div>

              {/* Basic Info */}
              <div className="pb-2">
                <div className="flex items-center space-x-3 mb-2">
                  <h1 className="text-3xl font-bold text-white">{player.name}</h1>
                  <span className="text-3xl">{player.countryFlag}</span>
                </div>
                <div className="flex items-center space-x-4 text-white/90">
                  <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-[var(--accent)]/20 text-[var(--accent)] border border-[var(--accent)]/30">
                    ATP Ranking #{player.ranking}
                  </span>
                  <span className="text-sm">{player.age} years old</span>
                  <span className="text-sm">{player.country}</span>
                </div>
              </div>
            </div>

            {/* Contact Button */}
            <Button className="bg-[var(--accent)] hover:bg-[var(--accent-hover)] text-white">
              <MessageCircle className="w-4 h-4 mr-2" />
              Contact
            </Button>
          </div>
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        {/* Left Column */}
        <div className="lg:col-span-2 space-y-6">
          {/* About Section */}
          <Card>
            <CardHeader>
              <CardTitle>About</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-muted-foreground leading-relaxed">{player.bio}</p>
            </CardContent>
          </Card>

          {/* Career Stats */}
          <div className="grid gap-4 md:grid-cols-3">
            <Card>
              <CardContent className="p-6">
                <div className="flex items-center space-x-4">
                  <div className="p-3 rounded-lg bg-blue-500/10">
                    <Calendar className="w-6 h-6 text-blue-500" />
                  </div>
                  <div>
                    <p className="text-2xl font-bold">{player.stats.yearsPro}</p>
                    <p className="text-sm text-muted-foreground">Years Pro</p>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-6">
                <div className="flex items-center space-x-4">
                  <div className="p-3 rounded-lg bg-green-500/10">
                    <TrendingUp className="w-6 h-6 text-green-500" />
                  </div>
                  <div>
                    <p className="text-2xl font-bold">{player.stats.careerWins}</p>
                    <p className="text-sm text-muted-foreground">Career Wins</p>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-6">
                <div className="flex items-center space-x-4">
                  <div className="p-3 rounded-lg bg-yellow-500/10">
                    <Trophy className="w-6 h-6 text-yellow-500" />
                  </div>
                  <div>
                    <p className="text-2xl font-bold">{player.stats.careerTitles}</p>
                    <p className="text-sm text-muted-foreground">Career Titles</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Rating Section */}
          <Card>
            <CardHeader>
              <CardTitle>Performance Rating</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex items-start space-x-8">
                {/* Overall Rating */}
                <div className="text-center">
                  <div className="text-5xl font-bold text-[var(--accent)] mb-2">
                    {player.rating.overall}
                  </div>
                  <div className="flex items-center justify-center mb-1">
                    {[...Array(5)].map((_, i) => (
                      <Star
                        key={i}
                        className={`w-5 h-5 ${
                          i < Math.floor(player.rating.overall)
                            ? 'fill-[var(--accent)] text-[var(--accent)]'
                            : 'text-muted-foreground'
                        }`}
                      />
                    ))}
                  </div>
                  <p className="text-sm text-muted-foreground">{totalReviews} reviews</p>
                </div>

                {/* Rating Distribution */}
                <div className="flex-1 space-y-2">
                  {[5, 4, 3, 2, 1].map((stars) => {
                    const count = player.rating.distribution[stars as keyof typeof player.rating.distribution]
                    const percentage = (count / totalReviews) * 100
                    return (
                      <div key={stars} className="flex items-center space-x-3">
                        <span className="text-sm w-8">{stars}</span>
                        <Star className="w-4 h-4 fill-[var(--accent)] text-[var(--accent)]" />
                        <div className="flex-1 h-2 bg-secondary rounded-full overflow-hidden">
                          <div
                            className="h-full bg-[var(--accent)] transition-all"
                            style={{ width: `${percentage}%` }}
                          />
                        </div>
                        <span className="text-sm text-muted-foreground w-12 text-right">
                          {count}
                        </span>
                      </div>
                    )
                  })}
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Recent Matches */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <Trophy className="w-5 h-5 mr-2" />
                Recent Matches
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {player.recentMatches.map((match) => (
                  <div
                    key={match.id}
                    className="flex items-center justify-between p-4 rounded-lg border border-border hover:bg-accent/50 transition-colors"
                  >
                    <div className="flex items-center space-x-4">
                      <div
                        className={`w-2 h-2 rounded-full ${
                          match.result === 'win' ? 'bg-green-500' : 'bg-red-500'
                        }`}
                      />
                      <div>
                        <p className="font-medium">{match.tournament}</p>
                        <p className="text-sm text-muted-foreground">vs {match.opponent}</p>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className="font-medium">{match.score}</p>
                      <div className="flex items-center justify-end space-x-2">
                        <span
                          className={`inline-block w-2 h-2 rounded-full ${getSurfaceColor(
                            match.surface
                          )}`}
                        />
                        <span className="text-sm text-muted-foreground capitalize">
                          {match.surface}
                        </span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Upcoming Events */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <Calendar className="w-5 h-5 mr-2" />
                Upcoming Tournaments
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {player.upcomingEvents.map((event) => (
                  <div
                    key={event.id}
                    className="flex items-center justify-between p-4 rounded-lg border border-border hover:bg-accent/50 transition-colors"
                  >
                    <div className="flex items-center space-x-4">
                      <div className="p-2 rounded-lg bg-[var(--accent)]/10">
                        <Calendar className="w-5 h-5 text-[var(--accent)]" />
                      </div>
                      <div>
                        <p className="font-medium">{event.tournament}</p>
                        <div className="flex items-center space-x-2 text-sm text-muted-foreground">
                          <MapPin className="w-3 h-3" />
                          <span>{event.location}</span>
                        </div>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className="text-sm font-medium">
                        {new Date(event.date).toLocaleDateString('pt-BR', {
                          day: '2-digit',
                          month: 'short'
                        })}
                      </p>
                      <div className="flex items-center justify-end space-x-2">
                        <span
                          className={`inline-block w-2 h-2 rounded-full ${getSurfaceColor(
                            event.surface
                          )}`}
                        />
                        <span className="text-sm text-muted-foreground capitalize">
                          {event.surface}
                        </span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Right Column - Contact & Social */}
        <div className="space-y-6">
          {/* Contact Information */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <Users className="w-5 h-5 mr-2" />
                Contact Information
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {player.contact.email && (
                  <div className="flex items-center space-x-3 p-3 rounded-lg hover:bg-accent/50 transition-colors">
                    <Mail className="w-4 h-4 text-muted-foreground" />
                    <span className="text-sm">{player.contact.email}</span>
                  </div>
                )}
                {player.contact.phone && (
                  <div className="flex items-center space-x-3 p-3 rounded-lg hover:bg-accent/50 transition-colors">
                    <Phone className="w-4 h-4 text-muted-foreground" />
                    <span className="text-sm">{player.contact.phone}</span>
                  </div>
                )}
                {player.contact.website && (
                  <div className="flex items-center space-x-3 p-3 rounded-lg hover:bg-accent/50 transition-colors">
                    <Globe className="w-4 h-4 text-muted-foreground" />
                    <span className="text-sm">{player.contact.website}</span>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>

          {/* Social Media */}
          <Card>
            <CardHeader>
              <CardTitle>Social Media</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                {player.social.instagram && (
                  <Button variant="outline" className="w-full justify-start">
                    <Instagram className="w-4 h-4 mr-2" />
                    {player.social.instagram}
                  </Button>
                )}
                {player.social.twitter && (
                  <Button variant="outline" className="w-full justify-start">
                    <Twitter className="w-4 h-4 mr-2" />
                    {player.social.twitter}
                  </Button>
                )}
                {player.social.facebook && (
                  <Button variant="outline" className="w-full justify-start">
                    <Facebook className="w-4 h-4 mr-2" />
                    {player.social.facebook}
                  </Button>
                )}
              </div>
            </CardContent>
          </Card>

          {/* Quick Actions */}
          <Card>
            <CardHeader>
              <CardTitle>Quick Actions</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              <Button className="w-full bg-[var(--accent)] hover:bg-[var(--accent-hover)]">
                <MessageCircle className="w-4 h-4 mr-2" />
                Send Message
              </Button>
              <Button variant="outline" className="w-full">
                <Calendar className="w-4 h-4 mr-2" />
                Schedule Training
              </Button>
              <Button variant="outline" className="w-full">
                <TrendingUp className="w-4 h-4 mr-2" />
                View Full Stats
              </Button>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}

export default PlayerProfile
