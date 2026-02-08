/**
 * Search Service - API client para busca global.
 *
 * Implementado para TT-138: Busca global de jogadores, locais, rankings e torneios.
 */

import { apiGet } from './api'

export interface PlayerSearchResult {
  id: string
  name: string
  avatar_url?: string
  username: string
}

export interface VenueSearchResult {
  id: string
  name: string
  city?: string
  type: string
}

export interface RankingSearchResult {
  id: string
  name: string
  category?: string
}

export interface TournamentSearchResult {
  id: string
  name: string
  date?: string
  status: string
}

export interface SearchResponse {
  players: PlayerSearchResult[]
  venues: VenueSearchResult[]
  rankings: RankingSearchResult[]
  tournaments: TournamentSearchResult[]
}

/**
 * Realiza busca global unificada.
 */
export const searchGlobal = async (params: {
  q: string
  limit?: number
}): Promise<SearchResponse> => {
  return apiGet<SearchResponse>('/search', params)
}
