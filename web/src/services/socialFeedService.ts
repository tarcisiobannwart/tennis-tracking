/**
 * Social Feed Service - API client para feed social.
 *
 * Implementado para TT-130: Feed tipo timeline com publicacoes texto+foto,
 * cards de resultado de partida, reacoes (like/torcer), comentarios e compartilhamento.
 */

import { apiGet, apiPost, apiDelete } from './api'

export type PostType = 'text' | 'match_result' | 'photo' | 'text_photo'
export type ReactionType = 'like' | 'cheer'

export interface FeedPost {
  id: string
  user_id: string
  post_type: PostType
  content?: string
  image_url?: string
  match_id?: string
  likes_count: number
  cheers_count: number
  comments_count: number
  shares_count: number
  is_public: boolean
  created_at: string
  updated_at: string
}

export interface FeedReaction {
  id: string
  post_id: string
  user_id: string
  reaction_type: ReactionType
  created_at: string
}

export interface FeedComment {
  id: string
  post_id: string
  user_id: string
  content: string
  created_at: string
  updated_at: string
}

export interface FeedResponse {
  data: FeedPost[]
  total: number
  page: number
  limit: number
  total_pages: number
}

export interface CreatePostRequest {
  post_type: PostType
  content?: string
  image_url?: string
  match_id?: string
  is_public?: boolean
}

export interface ReactToPostRequest {
  reaction_type: ReactionType
}

export interface AddCommentRequest {
  content: string
}

/**
 * Obtem o feed social com paginacao.
 */
export const getFeed = async (params?: {
  page?: number
  limit?: number
  user_id?: string
  post_type?: PostType
}): Promise<FeedResponse> => {
  return apiGet<FeedResponse>('/feed', params)
}

/**
 * Obtem um post especifico por ID.
 */
export const getPost = async (postId: string): Promise<FeedPost> => {
  return apiGet<FeedPost>(`/feed/${postId}`)
}

/**
 * Cria um novo post no feed.
 */
export const createPost = async (data: CreatePostRequest): Promise<FeedPost> => {
  return apiPost<FeedPost>('/feed', data)
}

/**
 * Deleta um post (apenas o proprio usuario pode deletar).
 */
export const deletePost = async (postId: string): Promise<{ message: string }> => {
  return apiDelete<{ message: string }>(`/feed/${postId}`)
}

/**
 * Adiciona ou atualiza uma reacao (like/torcer) a um post.
 */
export const reactToPost = async (
  postId: string,
  reactionType: ReactionType
): Promise<FeedReaction> => {
  return apiPost<FeedReaction>(`/feed/${postId}/react`, {
    reaction_type: reactionType,
  })
}

/**
 * Remove a reacao do usuario a um post.
 */
export const removeReaction = async (postId: string): Promise<{ message: string }> => {
  return apiDelete<{ message: string }>(`/feed/${postId}/react`)
}

/**
 * Adiciona um comentario a um post.
 */
export const addComment = async (
  postId: string,
  content: string
): Promise<FeedComment> => {
  return apiPost<FeedComment>(`/feed/${postId}/comment`, { content })
}

/**
 * Obtem comentarios de um post com paginacao.
 */
export const getPostComments = async (
  postId: string,
  params?: { page?: number; limit?: number }
): Promise<{ data: FeedComment[] }> => {
  return apiGet<{ data: FeedComment[] }>(`/feed/${postId}/comments`, params)
}

/**
 * Deleta um comentario (apenas o proprio usuario pode deletar).
 */
export const deleteComment = async (
  postId: string,
  commentId: string
): Promise<{ message: string }> => {
  return apiDelete<{ message: string }>(`/feed/${postId}/comment/${commentId}`)
}

/**
 * Incrementa o contador de compartilhamentos de um post.
 */
export const sharePost = async (postId: string): Promise<{ message: string }> => {
  return apiPost<{ message: string }>(`/feed/${postId}/share`)
}
