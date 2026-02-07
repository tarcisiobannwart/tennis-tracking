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

  const renderContent = () => {
    // Match result card
    if (post.post_type === 'match_result' && post.match_id) {
      // TODO: Fetch match details from match_id
      // For now, show placeholder
      return (
        <div className="mb-4">
          <MatchResultCard
            matchResult={{
              match_id: post.match_id,
              player1: {
                id: '1',
                name: 'Jogador 1',
                ranking: 10,
              },
              player2: {
                id: '2',
                name: 'Jogador 2',
                ranking: 15,
              },
              score: '6-4, 7-5',
              winner_id: '1',
              tournament: 'Torneio Demo',
              court: 'Quadra Central',
              duration: '1h 45min',
              date: post.created_at,
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
