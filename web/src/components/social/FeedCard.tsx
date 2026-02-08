/**
 * Feed Card - Componente de card para feed social.
 *
 * Implementado para TT-130: Card de post com texto/foto, reacoes (like/torcer),
 * comentarios expandiveis e compartilhamento.
 */

import React, { useState } from 'react'
import {
  Heart,
  MessageCircle,
  Share2,
  Sparkles,
  MoreVertical,
  Trash2,
  Loader2,
} from 'lucide-react'
import { Card, CardContent, CardHeader } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { MatchResultCard } from './MatchResultCard'
import { FeedPost, ReactionType } from '@/services/socialFeedService'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import { useMatch } from '@/hooks/useMatchData'

interface FeedCardProps {
  post: FeedPost
  currentUserId?: string
  onReact: (postId: string, reactionType: ReactionType) => void
  onRemoveReaction: (postId: string) => void
  onComment: (postId: string) => void
  onShare: (postId: string) => void
  onDelete?: (postId: string) => void
}

export const FeedCard: React.FC<FeedCardProps> = ({
  post,
  currentUserId,
  onReact,
  onRemoveReaction,
  onComment,
  onShare,
  onDelete,
}) => {
  const [showComments, setShowComments] = useState(false)
  const [hasLiked, setHasLiked] = useState(false)
  const [hasCheered, setHasCheered] = useState(false)

  const isOwnPost = currentUserId === post.user_id

  const handleReaction = (reactionType: ReactionType) => {
    const currentReaction = hasLiked ? 'like' : hasCheered ? 'cheer' : null

    if (currentReaction === reactionType) {
      // Remove reaction if clicking same button
      onRemoveReaction(post.id)
      if (reactionType === 'like') setHasLiked(false)
      if (reactionType === 'cheer') setHasCheered(false)
    } else {
      // Add/update reaction
      onReact(post.id, reactionType)
      if (reactionType === 'like') {
        setHasLiked(true)
        setHasCheered(false)
      }
      if (reactionType === 'cheer') {
        setHasCheered(true)
        setHasLiked(false)
      }
    }
  }

  // Fetch match details when post has match_id
  const {
    data: match,
    isLoading: isLoadingMatch,
    isError: isMatchError,
  } = useMatch(post.match_id || '', !!post.match_id && post.post_type === 'match_result')

  const renderContent = () => {
    // Match result card
    if (post.post_type === 'match_result' && post.match_id) {
      // Loading state
      if (isLoadingMatch) {
        return (
          <div className="mb-4 flex items-center justify-center py-8">
            <Loader2 className="w-6 h-6 animate-spin text-slate-400" />
            <span className="ml-2 text-sm text-slate-400">Carregando detalhes da partida...</span>
          </div>
        )
      }

      // Error or no match data
      if (isMatchError || !match) {
        return (
          <div className="mb-4 p-4 bg-slate-800 rounded-lg border border-slate-700">
            <p className="text-sm text-slate-400 text-center">
              Não foi possível carregar os detalhes da partida
            </p>
          </div>
        )
      }

      // Format score from match data
      const formatScore = (): string => {
        if (!match.score?.sets || match.score.sets.length === 0) {
          return '0-0'
        }
        return match.score.sets
          .map((set) => `${set.player1Games}-${set.player2Games}`)
          .join(', ')
      }

      // Determine winner
      const getWinnerId = (): string => {
        if (match.status !== 'completed' || !match.score?.sets) {
          return match.player1.id
        }
        const player1Sets = match.score.sets.filter(
          (set) => set.player1Games > set.player2Games
        ).length
        const player2Sets = match.score.sets.filter(
          (set) => set.player2Games > set.player1Games
        ).length
        return player1Sets > player2Sets ? match.player1.id : match.player2.id
      }

      // Format duration
      const formatDuration = (): string | undefined => {
        if (!match.duration) return undefined
        const hours = Math.floor(match.duration / 60)
        const minutes = match.duration % 60
        return hours > 0 ? `${hours}h ${minutes}min` : `${minutes}min`
      }

      return (
        <div className="mb-4">
          <MatchResultCard
            matchResult={{
              match_id: post.match_id,
              player1: {
                id: match.player1.id,
                name: match.player1.name,
                avatar: match.player1.avatar,
                ranking: match.player1.ranking,
              },
              player2: {
                id: match.player2.id,
                name: match.player2.name,
                avatar: match.player2.avatar,
                ranking: match.player2.ranking,
              },
              score: formatScore(),
              winner_id: getWinnerId(),
              tournament: match.tournament,
              court: match.round,
              duration: formatDuration(),
              date: match.date,
            }}
          />
        </div>
      )
    }

    // Text/photo post
    return (
      <div className="space-y-3">
        {post.content && (
          <p className="text-slate-200 whitespace-pre-wrap">{post.content}</p>
        )}
        {post.image_url && (
          <div className="rounded-lg overflow-hidden">
            <img
              src={post.image_url}
              alt="Post"
              className="w-full h-auto object-cover"
            />
          </div>
        )}
      </div>
    )
  }

  return (
    <Card>
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            {/* User avatar */}
            <div className="w-10 h-10 rounded-full bg-slate-700 flex items-center justify-center text-sm font-semibold text-slate-300">
              U
            </div>
            <div>
              <div className="font-semibold text-slate-100">Usuario</div>
              <div className="text-xs text-slate-400">
                {new Date(post.created_at).toLocaleDateString('pt-BR', {
                  day: '2-digit',
                  month: 'short',
                  hour: '2-digit',
                  minute: '2-digit',
                })}
              </div>
            </div>
          </div>

          {/* Actions menu */}
          {isOwnPost && onDelete && (
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="ghost" size="sm" className="h-8 w-8 p-0">
                  <MoreVertical className="h-4 w-4" />
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end">
                <DropdownMenuItem
                  onClick={() => onDelete(post.id)}
                  className="text-red-500"
                >
                  <Trash2 className="mr-2 h-4 w-4" />
                  Deletar
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          )}
        </div>
      </CardHeader>

      <CardContent className="pt-0">
        {/* Post content */}
        {renderContent()}

        {/* Reactions bar */}
        <div className="flex items-center justify-between pt-4 mt-4 border-t border-slate-700">
          <div className="flex items-center gap-1">
            {/* Like button */}
            <Button
              variant="ghost"
              size="sm"
              onClick={() => handleReaction('like')}
              className={hasLiked ? 'text-red-500' : 'text-slate-400'}
            >
              <Heart
                className={`w-4 h-4 mr-1 ${hasLiked ? 'fill-current' : ''}`}
              />
              <span className="text-sm">{post.likes_count}</span>
            </Button>

            {/* Cheer button */}
            <Button
              variant="ghost"
              size="sm"
              onClick={() => handleReaction('cheer')}
              className={hasCheered ? 'text-yellow-500' : 'text-slate-400'}
            >
              <Sparkles
                className={`w-4 h-4 mr-1 ${hasCheered ? 'fill-current' : ''}`}
              />
              <span className="text-sm">{post.cheers_count}</span>
            </Button>

            {/* Comment button */}
            <Button
              variant="ghost"
              size="sm"
              onClick={() => {
                setShowComments(!showComments)
                if (!showComments) onComment(post.id)
              }}
              className="text-slate-400"
            >
              <MessageCircle className="w-4 h-4 mr-1" />
              <span className="text-sm">{post.comments_count}</span>
            </Button>
          </div>

          {/* Share button */}
          <Button
            variant="ghost"
            size="sm"
            onClick={() => onShare(post.id)}
            className="text-slate-400"
          >
            <Share2 className="w-4 h-4 mr-1" />
            <span className="text-sm">{post.shares_count}</span>
          </Button>
        </div>

        {/* Comments section (expandable) */}
        {showComments && (
          <div className="mt-4 pt-4 border-t border-slate-700">
            <div className="text-sm text-slate-400">
              Comentarios aparecerao aqui
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  )
}
