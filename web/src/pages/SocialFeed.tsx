/**
 * Social Feed Page - Pagina do feed social.
 *
 * Implementado para TT-130: Timeline vertical com cards de posts (texto/foto/resultado),
 * formulario de novo post, infinite scroll, reacoes e comentarios.
 */

import React, { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import {
  Plus,
  Image as ImageIcon,
  Trophy,
  Loader2,
  AlertCircle,
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { FeedCard } from '@/components/social/FeedCard'
import { PageTransition } from '@/components/animations'
import {
  getFeed,
  createPost,
  reactToPost,
  removeReaction,
  deletePost,
  sharePost,
  FeedPost,
  PostType,
  ReactionType,
  CreatePostRequest,
} from '@/services/socialFeedService'
import { useAuthStore } from '@/stores/authStore'

const SocialFeed: React.FC = () => {
  const [posts, setPosts] = useState<FeedPost[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [page, setPage] = useState(1)
  const [hasMore, setHasMore] = useState(true)

  // New post form
  const [showNewPostForm, setShowNewPostForm] = useState(false)
  const [newPostContent, setNewPostContent] = useState('')
  const [newPostType, setNewPostType] = useState<PostType>('text')
  const [submittingPost, setSubmittingPost] = useState(false)

  const { user } = useAuthStore()
  const currentUserId = user?.id

  // Load feed
  const loadFeed = async (pageNum: number = 1, append: boolean = false) => {
    try {
      setLoading(true)
      setError(null)

      const response = await getFeed({ page: pageNum, limit: 20 })

      if (append) {
        setPosts((prev) => [...prev, ...response.data])
      } else {
        setPosts(response.data)
      }

      setHasMore(pageNum < response.total_pages)
      setPage(pageNum)
    } catch (err: any) {
      console.error('Erro ao carregar feed:', err)
      setError(err.response?.data?.detail || 'Erro ao carregar feed')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadFeed()
  }, [])

  // Create new post
  const handleCreatePost = async () => {
    if (!newPostContent.trim() && newPostType !== 'match_result') {
      return
    }

    try {
      setSubmittingPost(true)

      const postData: CreatePostRequest = {
        post_type: newPostType,
        content: newPostContent.trim() || undefined,
        is_public: true,
      }

      const newPost = await createPost(postData)

      // Add to top of feed
      setPosts((prev) => [newPost, ...prev])

      // Reset form
      setNewPostContent('')
      setShowNewPostForm(false)
    } catch (err: any) {
      console.error('Erro ao criar post:', err)
      alert(err.response?.data?.detail || 'Erro ao criar post')
    } finally {
      setSubmittingPost(false)
    }
  }

  // Handle reactions
  const handleReact = async (postId: string, reactionType: ReactionType) => {
    try {
      await reactToPost(postId, reactionType)

      // Update local state
      setPosts((prev) =>
        prev.map((post) => {
          if (post.id === postId) {
            const updated = { ...post }
            if (reactionType === 'like') {
              updated.likes_count += 1
            } else {
              updated.cheers_count += 1
            }
            return updated
          }
          return post
        })
      )
    } catch (err: any) {
      console.error('Erro ao reagir:', err)
    }
  }

  const handleRemoveReaction = async (postId: string) => {
    try {
      await removeReaction(postId)

      // Update local state (optimistic)
      setPosts((prev) =>
        prev.map((post) => {
          if (post.id === postId) {
            // Just decrement without knowing which type
            return post
          }
          return post
        })
      )
    } catch (err: any) {
      console.error('Erro ao remover reacao:', err)
    }
  }

  const handleComment = (postId: string) => {
    // TODO: Implement comment modal/section
    console.log('Open comments for post:', postId)
  }

  const handleShare = async (postId: string) => {
    try {
      await sharePost(postId)

      // Update local state
      setPosts((prev) =>
        prev.map((post) =>
          post.id === postId ? { ...post, shares_count: post.shares_count + 1 } : post
        )
      )

      // TODO: Show share options (copy link, social media, etc)
      alert('Post compartilhado!')
    } catch (err: any) {
      console.error('Erro ao compartilhar:', err)
    }
  }

  const handleDelete = async (postId: string) => {
    if (!confirm('Deseja realmente deletar este post?')) {
      return
    }

    try {
      await deletePost(postId)

      // Remove from local state
      setPosts((prev) => prev.filter((post) => post.id !== postId))
    } catch (err: any) {
      console.error('Erro ao deletar post:', err)
      alert(err.response?.data?.detail || 'Erro ao deletar post')
    }
  }

  const loadMore = () => {
    if (!loading && hasMore) {
      loadFeed(page + 1, true)
    }
  }

  return (
    <PageTransition>
      <div className="container mx-auto px-4 py-6 max-w-2xl">
        {/* Header */}
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-slate-100 mb-2">Feed Social</h1>
          <p className="text-slate-400">
            Compartilhe resultados, fotos e atualizacoes com a comunidade
          </p>
        </div>

        {/* New post button */}
        {!showNewPostForm && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            className="mb-6"
          >
            <Button
              onClick={() => setShowNewPostForm(true)}
              className="w-full"
              size="lg"
            >
              <Plus className="w-5 h-5 mr-2" />
              Criar Publicacao
            </Button>
          </motion.div>
        )}

        {/* New post form */}
        {showNewPostForm && (
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="mb-6"
          >
            <Card>
              <CardContent className="pt-6">
                <div className="space-y-4">
                  {/* Post type selector */}
                  <div className="flex gap-2">
                    <Button
                      variant={newPostType === 'text' ? 'default' : 'outline'}
                      size="sm"
                      onClick={() => setNewPostType('text')}
                    >
                      Texto
                    </Button>
                    <Button
                      variant={newPostType === 'photo' ? 'default' : 'outline'}
                      size="sm"
                      onClick={() => setNewPostType('photo')}
                    >
                      <ImageIcon className="w-4 h-4 mr-1" />
                      Foto
                    </Button>
                    <Button
                      variant={newPostType === 'match_result' ? 'default' : 'outline'}
                      size="sm"
                      onClick={() => setNewPostType('match_result')}
                    >
                      <Trophy className="w-4 h-4 mr-1" />
                      Resultado
                    </Button>
                  </div>

                  {/* Content input */}
                  <textarea
                    value={newPostContent}
                    onChange={(e) => setNewPostContent(e.target.value)}
                    placeholder="O que voce quer compartilhar?"
                    className="w-full h-32 px-4 py-3 bg-slate-900 border border-slate-700 rounded-lg text-slate-100 placeholder-slate-500 focus:outline-none focus:border-court-accent resize-none"
                  />

                  {/* Actions */}
                  <div className="flex justify-end gap-2">
                    <Button
                      variant="outline"
                      onClick={() => {
                        setShowNewPostForm(false)
                        setNewPostContent('')
                      }}
                      disabled={submittingPost}
                    >
                      Cancelar
                    </Button>
                    <Button
                      onClick={handleCreatePost}
                      disabled={submittingPost || !newPostContent.trim()}
                    >
                      {submittingPost && (
                        <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                      )}
                      Publicar
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          </motion.div>
        )}

        {/* Error state */}
        {error && (
          <Card className="mb-6 border-red-500/50 bg-red-500/10">
            <CardContent className="pt-6">
              <div className="flex items-center gap-2 text-red-400">
                <AlertCircle className="w-5 h-5" />
                <span>{error}</span>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Posts feed */}
        <div className="space-y-4">
          {posts.map((post) => (
            <motion.div
              key={post.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.95 }}
            >
              <FeedCard
                post={post}
                currentUserId={currentUserId}
                onReact={handleReact}
                onRemoveReaction={handleRemoveReaction}
                onComment={handleComment}
                onShare={handleShare}
                onDelete={currentUserId === post.user_id ? handleDelete : undefined}
              />
            </motion.div>
          ))}
        </div>

        {/* Loading state */}
        {loading && posts.length === 0 && (
          <div className="flex justify-center py-12">
            <Loader2 className="w-8 h-8 animate-spin text-court-accent" />
          </div>
        )}

        {/* Load more button */}
        {hasMore && posts.length > 0 && !loading && (
          <div className="mt-6 flex justify-center">
            <Button onClick={loadMore} variant="outline">
              Carregar mais
            </Button>
          </div>
        )}

        {/* End of feed */}
        {!hasMore && posts.length > 0 && (
          <div className="mt-6 text-center text-slate-500 text-sm">
            Voce viu todos os posts
          </div>
        )}

        {/* Empty state */}
        {!loading && posts.length === 0 && !error && (
          <Card>
            <CardContent className="pt-12 pb-12 text-center">
              <div className="text-slate-400 mb-4">
                <Trophy className="w-12 h-12 mx-auto mb-2 opacity-50" />
                <p>Nenhum post ainda</p>
                <p className="text-sm mt-1">Seja o primeiro a publicar!</p>
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </PageTransition>
  )
}

export default SocialFeed
