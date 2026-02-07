import { Camera, Trophy, TrendingUp, Calendar } from 'lucide-react'
import { Button } from '@/components/ui/button'

interface ProfileHeaderProps {
  username: string
  fullName: string
  avatarUrl?: string
  coverPhotoUrl?: string
  gamesCount: number
  rankingsCount: number
  tournamentsCount: number
  onEditCover?: () => void
  onEditAvatar?: () => void
  isOwnProfile?: boolean
}

export const ProfileHeader = ({
  username,
  fullName,
  avatarUrl,
  coverPhotoUrl,
  gamesCount,
  rankingsCount,
  tournamentsCount,
  onEditCover,
  onEditAvatar,
  isOwnProfile = false
}: ProfileHeaderProps) => {
  return (
    <div className="relative">
      {/* Cover Photo */}
      <div className="relative h-64 bg-gradient-to-r from-court-accent/20 to-court-accent/10 rounded-t-lg overflow-hidden">
        {coverPhotoUrl ? (
          <img src={coverPhotoUrl} alt="Cover" className="w-full h-full object-cover" />
        ) : (
          <div className="w-full h-full flex items-center justify-center">
            <Camera className="w-16 h-16 text-muted-foreground opacity-20" />
          </div>
        )}
        {isOwnProfile && (
          <Button
            variant="secondary"
            size="sm"
            className="absolute top-4 right-4"
            onClick={onEditCover}
          >
            <Camera className="w-4 h-4 mr-2" />
            Editar Capa
          </Button>
        )}
      </div>

      {/* Profile Info */}
      <div className="relative px-6 pb-6">
        <div className="flex items-end justify-between -mt-16">
          {/* Avatar */}
          <div className="relative">
            <div className="w-32 h-32 rounded-full border-4 border-background bg-muted overflow-hidden">
              {avatarUrl ? (
                <img src={avatarUrl} alt={fullName} className="w-full h-full object-cover" />
              ) : (
                <div className="w-full h-full flex items-center justify-center bg-gradient-to-br from-court-accent/30 to-court-accent/10">
                  <span className="text-4xl font-bold text-court-accent">
                    {fullName.charAt(0).toUpperCase()}
                  </span>
                </div>
              )}
            </div>
            {isOwnProfile && (
              <Button
                variant="secondary"
                size="icon"
                className="absolute bottom-0 right-0 rounded-full w-8 h-8"
                onClick={onEditAvatar}
              >
                <Camera className="w-4 h-4" />
              </Button>
            )}
          </div>

          {/* Stats Counters */}
          <div className="flex gap-6 mb-4">
            <div className="text-center">
              <div className="flex items-center justify-center w-12 h-12 rounded-full bg-court-accent/10 mb-2">
                <Trophy className="w-6 h-6 text-court-accent" />
              </div>
              <p className="text-2xl font-bold">{gamesCount}</p>
              <p className="text-sm text-muted-foreground">Jogos</p>
            </div>
            <div className="text-center">
              <div className="flex items-center justify-center w-12 h-12 rounded-full bg-court-accent/10 mb-2">
                <TrendingUp className="w-6 h-6 text-court-accent" />
              </div>
              <p className="text-2xl font-bold">{rankingsCount}</p>
              <p className="text-sm text-muted-foreground">Rankings</p>
            </div>
            <div className="text-center">
              <div className="flex items-center justify-center w-12 h-12 rounded-full bg-court-accent/10 mb-2">
                <Calendar className="w-6 h-6 text-court-accent" />
              </div>
              <p className="text-2xl font-bold">{tournamentsCount}</p>
              <p className="text-sm text-muted-foreground">Torneios</p>
            </div>
          </div>
        </div>

        {/* Name and Username */}
        <div className="mt-4">
          <h1 className="text-3xl font-bold">{fullName}</h1>
          <p className="text-muted-foreground">@{username}</p>
        </div>
      </div>
    </div>
  )
}
