/**
 * Feed Card - Componente de card para feed social.
 *
 * Implementado para TT-130: Card de post com texto/foto, reacoes (like/torcer),
 * comentarios expandiveis e compartilhamento.
 */

import React, { useState, useEffect } from 'react'
import {
  Heart,
  MessageCircle,
  Share2,
  Sparkles,
  MoreVertical,
  Trash2,
  Loader2,
  Send,
} from 'lucide-react'
import { Card, CardContent, CardHeader } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { MatchResultCard } from './MatchResultCard'
import { FeedPost, ReactionType, FeedComment, getPostComments, addComment } from '@/services/socialFeedService'
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
  const [comments, setComments] = useState<FeedComment[]>([])
  const [isLoadingComments, setIsLoadingComments] = useState(false)
  const [newCommentText, setNewCommentText] = useState('')
  const [isSubmittingComment, setIsSubmittingComment] = useState(false)
  const [commentsPage, setCommentsPage] = useState(1)
  const [hasMoreComments, setHasMoreComments] = useState(false)

  const isOwnPost = currentUserId === post.user_id

  // Load comments when comments section is opened
  useEffect(() => {
    if (showComments && comments.length === 0) {
      loadComments()
    }
  }, [showComments])

  const loadComments = async (page = 1) => {
    setIsLoadingComments(true)
    try {
      const response = await getPostComments(post.id, { page, limit: 10 })
      if (page === 1) {
        setComments(response.data)
      } else {
        setComments((prev) => [...prev, ...response.data])
      }
      setCommentsPage(page)
      // Check if there are more comments (assuming API returns less than limit when no more)
      setHasMoreComments(response.data.length === 10)
    } catch (error) {
      console.error('Failed to load comments:', error)
    } finally {
      setIsLoadingComments(false)
    }
  }

  const handleAddComment = async () => {
    if (!newCommentText.trim() || isSubmittingComment) return

    setIsSubmittingComment(true)
    try {
      const newComment = await addComment(post.id, newCommentText.trim())
      setComments((prev) => [newComment, ...prev])
      setNewCommentText('')
      // Update the comments count in the post
      post.comments_count += 1
    } catch (error) {
      console.error('Failed to add comment:', error)
    } finally {
      setIsSubmittingComment(false)
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleAddComment()
    }
  }

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
                avatar: match.player1.profileImage,
                ranking: match.player1.ranking,
              },
              player2: {
                id: match.player2.id,
                name: match.player2.name,
                avatar: match.player2.profileImage,
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
          <div className="mt-4 pt-4 border-t border-slate-700 space-y-4">
            {/* Add comment input */}
            <div className="flex gap-2">
              <div className="w-8 h-8 rounded-full bg-slate-700 flex items-center justify-center text-xs font-semibold text-slate-300 flex-shrink-0">
                U
              </div>
              <div className="flex-1 flex gap-2">
                <Input
                  placeholder="Adicionar um comentário..."
                  value={newCommentText}
                  onChange={(e) => setNewCommentText(e.target.value)}
                  onKeyPress={handleKeyPress}
                  disabled={isSubmittingComment}
                  className="flex-1"
                />
                <Button
                  size="sm"
                  onClick={handleAddComment}
                  disabled={!newCommentText.trim() || isSubmittingComment}
                  className="px-3"
                >
                  {isSubmittingComment ? (
                    <Loader2 className="w-4 h-4 animate-spin" />
                  ) : (
                    <Send className="w-4 h-4" />
                  )}
                </Button>
              </div>
            </div>

            {/* Comments list */}
            {isLoadingComments && comments.length === 0 ? (
              <div className="flex items-center justify-center py-4">
                <Loader2 className="w-5 h-5 animate-spin text-slate-400" />
                <span className="ml-2 text-sm text-slate-400">Carregando comentários...</span>
              </div>
            ) : comments.length === 0 ? (
              <div className="text-center py-4">
                <p className="text-sm text-slate-400">
                  Nenhum comentário ainda. Seja o primeiro a comentar!
                </p>
              </div>
            ) : (
              <div className="space-y-3">
                {comments.map((comment) => (
                  <div key={comment.id} className="flex gap-2">
                    <div className="w-8 h-8 rounded-full bg-slate-700 flex items-center justify-center text-xs font-semibold text-slate-300 flex-shrink-0">
                      U
                    </div>
                    <div className="flex-1 bg-slate-800/50 rounded-lg p-3">
                      <div className="flex items-center justify-between mb-1">
                        <span className="text-sm font-semibold text-slate-200">
                          Usuário
                        </span>
                        <span className="text-xs text-slate-500">
                          {new Date(comment.created_at).toLocaleDateString('pt-BR', {
                            day: '2-digit',
                            month: 'short',
                            hour: '2-digit',
                            minute: '2-digit',
                          })}
                        </span>
                      </div>
                      <p className="text-sm text-slate-300">{comment.content}</p>
                    </div>
                  </div>
                ))}

                {/* Load more button */}
                {hasMoreComments && (
                  <div className="text-center pt-2">
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => loadComments(commentsPage + 1)}
                      disabled={isLoadingComments}
                      className="text-slate-400 hover:text-slate-200"
                    >
                      {isLoadingComments ? (
                        <>
                          <Loader2 className="w-4 h-4 animate-spin mr-2" />
                          Carregando...
                        </>
                      ) : (
                        'Carregar mais comentários'
                      )}
                    </Button>
                  </div>
                )}
              </div>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  )
}
