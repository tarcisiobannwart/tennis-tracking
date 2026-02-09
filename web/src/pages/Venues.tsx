import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { MapPin, Users, Heart, Search, Plus } from 'lucide-react'
import { Card, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { PageTransition } from '@/components/animations'
import { venueService, Venue } from '@/services/venueService'
import { useAuthStore } from '@/stores/authStore'
import toast from 'react-hot-toast'

const Venues = () => {
  const navigate = useNavigate()
  const { user } = useAuthStore()
  const [loading, setLoading] = useState(true)
  const [venues, setVenues] = useState<Venue[]>([])
  const [total, setTotal] = useState(0)
  const [search, setSearch] = useState('')
  const [city, setCity] = useState('')
  const [country, setCountry] = useState('')
  const [page, setPage] = useState(1)
  const limit = 12

  useEffect(() => {
    loadVenues()
  }, [page, search, city, country])

  const loadVenues = async () => {
    try {
      setLoading(true)
      const response = await venueService.listVenues({
        skip: (page - 1) * limit,
        limit,
        search: search || undefined,
        city: city || undefined,
        country: country || undefined,
      })
      setVenues(response.venues)
      setTotal(response.total)
    } catch (error) {
      console.error('Error loading venues:', error)
      toast.error('Erro ao carregar locais')
    } finally {
      setLoading(false)
    }
  }

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault()
    setPage(1)
    loadVenues()
  }

  const totalPages = Math.ceil(total / limit)

  if (loading && page === 1) {
    return (
      <PageTransition>
        <div className="flex items-center justify-center min-h-screen">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-court-accent"></div>
        </div>
      </PageTransition>
    )
  }

  return (
    <PageTransition>
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h1 className="text-3xl font-bold">Locais e Clubes</h1>
              <p className="text-muted-foreground">
                Encontre quadras e clubes de tênis próximos
              </p>
            </div>
            {user && (
              <Button onClick={() => navigate('/app/venues/create')}>
                <Plus className="w-4 h-4 mr-2" />
                Criar Local
              </Button>
            )}
          </div>

          {/* Search and Filters */}
          <Card>
            <CardContent className="pt-6">
              <form onSubmit={handleSearch} className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                  <div className="md:col-span-2 relative">
                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
                    <Input
                      placeholder="Buscar por nome..."
                      value={search}
                      onChange={(e) => setSearch(e.target.value)}
                      className="pl-10"
                    />
                  </div>
                  <Input
                    placeholder="Cidade"
                    value={city}
                    onChange={(e) => setCity(e.target.value)}
                  />
                  <Input
                    placeholder="País"
                    value={country}
                    onChange={(e) => setCountry(e.target.value)}
                  />
                </div>
                <div className="flex justify-end">
                  <Button type="submit">
                    <Search className="w-4 h-4 mr-2" />
                    Buscar
                  </Button>
                </div>
              </form>
            </CardContent>
          </Card>
        </div>

        {/* Venues Grid */}
        {venues.length === 0 ? (
          <Card>
            <CardContent className="py-12 text-center">
              <MapPin className="w-12 h-12 mx-auto mb-4 text-muted-foreground" />
              <p className="text-muted-foreground">
                Nenhum local encontrado
              </p>
            </CardContent>
          </Card>
        ) : (
          <>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {venues.map((venue) => (
                <Card
                  key={venue.id}
                  className="hover:shadow-lg transition-shadow cursor-pointer"
                  onClick={() => navigate(`/app/venues/${venue.slug}`)}
                >
                  {/* Cover Photo */}
                  <div className="relative h-40 bg-gradient-to-r from-court-primary to-court-accent rounded-t-lg overflow-hidden">
                    {venue.cover_photo_url ? (
                      <img
                        src={venue.cover_photo_url}
                        alt={venue.name}
                        className="w-full h-full object-cover"
                      />
                    ) : (
                      <div className="flex items-center justify-center h-full">
                        <MapPin className="w-12 h-12 text-white opacity-50" />
                      </div>
                    )}
                  </div>

                  <CardContent className="pt-4">
                    {/* Avatar */}
                    <div className="flex items-start gap-3 mb-3">
                      <div className="w-12 h-12 rounded-full bg-court-accent flex items-center justify-center text-white font-bold text-lg shrink-0 -mt-8 border-4 border-background">
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
                      <div className="flex-1 min-w-0">
                        <h3 className="font-semibold text-lg truncate">
                          {venue.name}
                        </h3>
                        <div className="flex items-center text-sm text-muted-foreground">
                          <MapPin className="w-3 h-3 mr-1" />
                          <span className="truncate">
                            {venue.city && venue.country
                              ? `${venue.city}, ${venue.country}`
                              : venue.city || venue.country || 'Localização não informada'}
                          </span>
                        </div>
                      </div>
                    </div>

                    {/* Description */}
                    {venue.description && (
                      <p className="text-sm text-muted-foreground mb-3 line-clamp-2">
                        {venue.description}
                      </p>
                    )}

                    {/* Stats */}
                    <div className="flex items-center gap-4 text-sm">
                      <div className="flex items-center gap-1">
                        <Users className="w-4 h-4 text-court-accent" />
                        <span>{venue.members_count} membros</span>
                      </div>
                      <div className="flex items-center gap-1">
                        <Heart className="w-4 h-4 text-court-accent" />
                        <span>{venue.followers_count} seguidores</span>
                      </div>
                    </div>

                    {/* Court Info */}
                    {venue.court_count > 0 && (
                      <div className="mt-3 text-sm text-muted-foreground">
                        {venue.court_count} {venue.court_count === 1 ? 'quadra' : 'quadras'}
                        {venue.surface_types.length > 0 && (
                          <span> • {venue.surface_types.join(', ')}</span>
                        )}
                      </div>
                    )}
                  </CardContent>
                </Card>
              ))}
            </div>

            {/* Pagination */}
            {totalPages > 1 && (
              <div className="mt-8 flex items-center justify-center gap-2">
                <Button
                  variant="outline"
                  disabled={page === 1}
                  onClick={() => setPage((p) => Math.max(1, p - 1))}
                >
                  Anterior
                </Button>
                <span className="text-sm text-muted-foreground">
                  Página {page} de {totalPages}
                </span>
                <Button
                  variant="outline"
                  disabled={page === totalPages}
                  onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                >
                  Próxima
                </Button>
              </div>
            )}
          </>
        )}
      </div>
    </PageTransition>
  )
}

export default Venues
