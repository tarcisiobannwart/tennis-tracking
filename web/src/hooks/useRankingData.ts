import { useQuery } from '@tanstack/react-query'
import { rankingService, RankingFilters } from '@/services/rankingService'

// Query keys
export const RANKING_QUERY_KEYS = {
  all: ['rankings'] as const,
  lists: () => [...RANKING_QUERY_KEYS.all, 'list'] as const,
  list: (filters: RankingFilters) => [...RANKING_QUERY_KEYS.lists(), filters] as const,
  details: () => [...RANKING_QUERY_KEYS.all, 'detail'] as const,
  detail: (id: string) => [...RANKING_QUERY_KEYS.details(), id] as const,
  standings: (id: string) => [...RANKING_QUERY_KEYS.detail(id), 'standings'] as const,
  rounds: (id: string) => [...RANKING_QUERY_KEYS.detail(id), 'rounds'] as const,
}

// Hook to fetch rankings with filters
export const useRankings = (filters?: RankingFilters) => {
  return useQuery({
    queryKey: RANKING_QUERY_KEYS.list(filters || {}),
    queryFn: () => rankingService.getRankings(filters),
    staleTime: 5 * 60 * 1000, // 5 minutes
  })
}

// Hook to fetch single ranking
export const useRanking = (id: string, enabled = true) => {
  return useQuery({
    queryKey: RANKING_QUERY_KEYS.detail(id),
    queryFn: () => rankingService.getRanking(id),
    enabled: enabled && !!id,
    staleTime: 2 * 60 * 1000, // 2 minutes
  })
}

// Hook to fetch standings
export const useStandings = (rankingId: string, enabled = true) => {
  return useQuery({
    queryKey: RANKING_QUERY_KEYS.standings(rankingId),
    queryFn: () => rankingService.getStandings(rankingId),
    enabled: enabled && !!rankingId,
    staleTime: 1 * 60 * 1000, // 1 minute
  })
}

// Hook to fetch rounds
export const useRounds = (rankingId: string, enabled = true) => {
  return useQuery({
    queryKey: RANKING_QUERY_KEYS.rounds(rankingId),
    queryFn: () => rankingService.getRounds(rankingId),
    enabled: enabled && !!rankingId,
    staleTime: 2 * 60 * 1000, // 2 minutes
  })
}
