import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import {
  MapPin,
  Users,
  Heart,
  Phone,
  Mail,
  Globe,
  Calendar,
  Trophy,
  Image as ImageIcon,
  Info,
  UserPlus,
  UserMinus,
  Edit,
} from 'lucide-react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { PageTransition } from '@/components/animations'
import { venueService, Venue, VenueMember, VenueFollower } from '@/services/venueService'
import { useAuthStore } from '@/stores/authStore'
import toast from 'react-hot-toast'

const VenueProfile = () => {
  const { slug } = useParams<{ slug: string }>()
  const navigate = useNavigate()
  const { user } = useAuthStore()
  const [loading, setLoading] = useState(true)
  const [venue, setVenue] = useState<Venue | null>(null)
  const [members, setMembers] = useState<VenueMember[]>([])
  const [followers, setFollowers] = useState<VenueFollower[]>([])
  const [activeTab, setActiveTab] = useState('principal')

  useEffect(() => {
    if (!slug) {
      navigate('/app/venues')
      return
    }

    loadVenueProfile()
  }, [slug])

  const loadVenueProfile = async () => {
    if (!slug) return

    try {
      setLoading(true)
      const venueData = await venueService.getVenueBySlug(slug)
      setVenue(venueData)

      // Load members and followers
      const [membersData, followersData] = await Promise.all([
        venueService.getVenueMembers(venueData.id, { limit: 20 }),
        venueService.getVenueFollowers(venueData.id, { limit: 20 }),
      ])

      setMembers(membersData.members)
      setFollowers(followersData.followers)
    } catch (error) {
      console.error('Error loading venue profile:', error)
      toast.error('Erro ao carregar perfil do local')
      navigate('/app/venues')
    } finally {
      setLoading(false)
    }
  }

  const handleFollow = async () => {
    if (!venue || !user) return

    try {
      if (venue.is_following) {
        await venueService.unfollowVenue(venue.id)
        toast.success('Você deixou de seguir este local')
        setVenue({ ...venue, is_following: false, followers_count: venue.followers_count - 1 })
      } else {
        await venueService.followVenue(venue.id)
        toast.success('Você agora segue este local')
        setVenue({ ...venue, is_following: true, followers_count: venue.followers_count + 1 })
      }
    } catch (error) {
      console.error('Error following/unfollowing venue:', error)
      toast.error('Erro ao processar ação')
    }
  }

  const handleJoin = async () => {
    if (!venue || !user) return

    try {
      if (venue.is_member) {
        await venueService.leaveVenue(venue.id)
        toast.success('Você saiu deste local')
        setVenue({ ...venue, is_member: false, members_count: venue.members_count - 1 })
      } else {
        await venueService.joinVenue(venue.id)
        toast.success('Você agora é membro deste local')
        setVenue({ ...venue, is_member: true, members_count: venue.members_count + 1 })
      }
    } catch (error) {
      console.error('Error joining/leaving venue:', error)
      toast.error('Erro ao processar ação')
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

  if (!venue) {
    return (
      <PageTransition>
        <div className="text-center py-12">
          <p className="text-muted-foreground">Local não encontrado</p>
        </div>
      </PageTransition>
    )
  }

  const canEdit = user && (venue.member_role === 'owner' || venue.member_role === 'admin')

  return (
    <PageTransition>
      <div className="container mx-auto px-4 py-8">
        {/* Cover Photo */}
        <div className="relative h-64 bg-gradient-to-r from-court-primary to-court-accent rounded-lg overflow-hidden mb-8">
          {venue.cover_photo_url ? (
            <img
              src={venue.cover_photo_url}
              alt={venue.name}
              className="w-full h-full object-cover"
            />
          ) : (
            <div className="flex items-center justify-center h-full">
              <MapPin className="w-24 h-24 text-white opacity-50" />
            </div>
          )}
        </div>

        {/* Profile Header */}
        <div className="mb-8">
          <div className="flex items-start gap-6">
            {/* Avatar */}
            <div className="w-32 h-32 rounded-full bg-court-accent flex items-center justify-center text-white font-bold text-4xl shrink-0 -mt-16 border-4 border-background">
              {venue.avatar_url ? (
                <img
                  src={venue.avatar_url}
                  alt={venue.name}
                  className="w-full h-full rounded-full object-cover"
                />
              ) : (
                venue.name.charAt(0).toUpperCase()
              )}
            </div>

            {/* Info */}
            <div className="flex-1 pt-4">
              <div className="flex items-center justify-between mb-2">
                <h1 className="text-3xl font-bold">{venue.name}</h1>
                {canEdit && (
                  <Button
                    variant="outline"
                    onClick={() => navigate(`/app/venues/${venue.slug}/edit`)}
                  >
                    <Edit className="w-4 h-4 mr-2" />
                    Editar
                  </Button>
                )}
              </div>

              <div className="flex items-center gap-4 text-muted-foreground mb-4">
                {(venue.city || venue.country) && (
                  <div className="flex items-center gap-1">
                    <MapPin className="w-4 h-4" />
                    <span>
                      {venue.city && venue.country
                        ? `${venue.city}, ${venue.country}`
                        : venue.city || venue.country}
                    </span>
                  </div>
                )}
                {venue.phone && (
                  <div className="flex items-center gap-1">
                    <Phone className="w-4 h-4" />
                    <span>{venue.phone}</span>
                  </div>
                )}
                {venue.email && (
                  <div className="flex items-center gap-1">
                    <Mail className="w-4 h-4" />
                    <span>{venue.email}</span>
                  </div>
                )}
                {venue.website && (
                  <a
                    href={venue.website}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex items-center gap-1 hover:text-court-accent"
                  >
                    <Globe className="w-4 h-4" />
                    <span>Website</span>
                  </a>
                )}
              </div>

              {/* Stats */}
              <div className="flex items-center gap-6 mb-4">
                <div className="text-center">
                  <div className="text-2xl font-bold">{venue.members_count}</div>
                  <div className="text-sm text-muted-foreground">Membros</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold">{venue.followers_count}</div>
                  <div className="text-sm text-muted-foreground">Seguidores</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold">{venue.court_count}</div>
                  <div className="text-sm text-muted-foreground">Quadras</div>
                </div>
              </div>

              {/* Action Buttons */}
              {user && (
                <div className="flex items-center gap-3">
                  <Button onClick={handleJoin} disabled={venue.member_role === 'owner'}>
                    {venue.is_member ? (
                      <>
                        <UserMinus className="w-4 h-4 mr-2" />
                        Sair do Local
                      </>
                    ) : (
                      <>
                        <UserPlus className="w-4 h-4 mr-2" />
                        Associar-se
                      </>
                    )}
                  </Button>
                  <Button variant="outline" onClick={handleFollow}>
                    <Heart
                      className={`w-4 h-4 mr-2 ${venue.is_following ? 'fill-current' : ''}`}
                    />
                    {venue.is_following ? 'Seguindo' : 'Seguir'}
                  </Button>
                  <Button variant="outline">
                    <Trophy className="w-4 h-4 mr-2" />
                    Participar Ranking
                  </Button>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Main Content */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Main Column */}
          <div className="lg:col-span-2">
            <Tabs value={activeTab} onValueChange={setActiveTab}>
              <TabsList className="grid w-full grid-cols-5">
                <TabsTrigger value="principal">Principal</TabsTrigger>
                <TabsTrigger value="agenda">Agenda</TabsTrigger>
                <TabsTrigger value="jogos">Jogos</TabsTrigger>
                <TabsTrigger value="seguidores">Seguidores</TabsTrigger>
                <TabsTrigger value="fotos">Fotos</TabsTrigger>
              </TabsList>

              <TabsContent value="principal" className="space-y-6">
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center">
                      <Info className="w-5 h-5 mr-2" />
                      Sobre
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    {venue.description ? (
                      <p className="text-muted-foreground">{venue.description}</p>
                    ) : (
                      <p className="text-muted-foreground italic">Sem descrição</p>
                    )}

                    {venue.amenities.length > 0 && (
                      <div className="mt-4">
                        <h4 className="font-semibold mb-2">Comodidades</h4>
                        <div className="flex flex-wrap gap-2">
                          {venue.amenities.map((amenity) => (
                            <span
                              key={amenity}
                              className="px-3 py-1 bg-court-accent/10 text-court-accent rounded-full text-sm"
                            >
                              {amenity}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}

                    {venue.surface_types.length > 0 && (
                      <div className="mt-4">
                        <h4 className="font-semibold mb-2">Tipos de Superfície</h4>
                        <div className="flex flex-wrap gap-2">
                          {venue.surface_types.map((surface) => (
                            <span
                              key={surface}
                              className="px-3 py-1 bg-primary/10 text-primary rounded-full text-sm"
                            >
                              {surface}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}

                    {venue.address && (
                      <div className="mt-4">
                        <h4 className="font-semibold mb-2">Endereço</h4>
                        <p className="text-muted-foreground">{venue.address}</p>
                      </div>
                    )}
                  </CardContent>
                </Card>
              </TabsContent>

              <TabsContent value="agenda">
                <Card>
                  <CardContent className="py-12 text-center">
                    <Calendar className="w-12 h-12 mx-auto mb-4 text-muted-foreground" />
                    <p className="text-muted-foreground">Agenda em breve</p>
                  </CardContent>
                </Card>
              </TabsContent>

              <TabsContent value="jogos">
                <Card>
                  <CardContent className="py-12 text-center">
                    <Trophy className="w-12 h-12 mx-auto mb-4 text-muted-foreground" />
                    <p className="text-muted-foreground">Jogos em breve</p>
                  </CardContent>
                </Card>
              </TabsContent>

              <TabsContent value="seguidores">
                <Card>
                  <CardHeader>
                    <CardTitle>Seguidores ({followers.length})</CardTitle>
                  </CardHeader>
                  <CardContent>
                    {followers.length > 0 ? (
                      <div className="space-y-2">
                        {followers.map((follower) => (
                          <div
                            key={follower.user_id}
                            className="flex items-center justify-between p-3 rounded-lg hover:bg-accent"
                          >
                            <span>{follower.user_id}</span>
                            <span className="text-sm text-muted-foreground">
                              {new Date(follower.followed_at).toLocaleDateString()}
                            </span>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <p className="text-center text-muted-foreground py-8">
                        Nenhum seguidor ainda
                      </p>
                    )}
                  </CardContent>
                </Card>
              </TabsContent>

              <TabsContent value="fotos">
                <Card>
                  <CardContent className="py-12 text-center">
                    <ImageIcon className="w-12 h-12 mx-auto mb-4 text-muted-foreground" />
                    <p className="text-muted-foreground">Galeria de fotos em breve</p>
                  </CardContent>
                </Card>
              </TabsContent>
            </Tabs>
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <Trophy className="w-5 h-5 mr-2" />
                  Rankings Ativos
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-muted-foreground text-center py-4">
                  Nenhum ranking ativo
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <Trophy className="w-5 h-5 mr-2" />
                  Próximos Torneios
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-muted-foreground text-center py-4">
                  Nenhum torneio agendado
                </p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <Calendar className="w-5 h-5 mr-2" />
                  Reservas
                </CardTitle>
              </CardHeader>
              <CardContent>
                <Button className="w-full">Ver Horários Disponíveis</Button>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center">
                  <Users className="w-5 h-5 mr-2" />
                  Membros ({members.length})
                </CardTitle>
              </CardHeader>
              <CardContent>
                {members.length > 0 ? (
                  <div className="space-y-2">
                    {members.slice(0, 5).map((member) => (
                      <div
                        key={member.user_id}
                        className="flex items-center justify-between text-sm"
                      >
                        <span>{member.user_id}</span>
                        <span className="text-xs text-muted-foreground capitalize">
                          {member.role}
                        </span>
                      </div>
                    ))}
                    {members.length > 5 && (
                      <button
                        className="text-sm text-court-accent hover:underline w-full text-center"
                        onClick={() => setActiveTab('seguidores')}
                      >
                        Ver todos
                      </button>
                    )}
                  </div>
                ) : (
                  <p className="text-sm text-muted-foreground text-center py-4">
                    Nenhum membro ainda
                  </p>
                )}
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </PageTransition>
  )
}

export default VenueProfile
