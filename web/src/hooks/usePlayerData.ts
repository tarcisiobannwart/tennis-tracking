import { useQuery } from '@tanstack/react-query'
import { playerService, PlayerListFilters } from '@/services/playerService'

// Query keys
export const PLAYER_QUERY_KEYS = {
  all: ['players'] as const,
  lists: () => [...PLAYER_QUERY_KEYS.all, 'list'] as const,
  list: (filters: PlayerListFilters, skip: number, limit: number) =>
    [...PLAYER_QUERY_KEYS.lists(), filters, skip, limit] as const,
  details: () => [...PLAYER_QUERY_KEYS.all, 'detail'] as const,
  detail: (username: string) => [...PLAYER_QUERY_KEYS.details(), username] as const,
  activity: (playerId: string, months: number) =>
    [...PLAYER_QUERY_KEYS.detail(playerId), 'activity', months] as const,
  winLoss: (playerId: string) =>
    [...PLAYER_QUERY_KEYS.detail(playerId), 'win-loss'] as const,
  recentForm: (playerId: string, matches: number) =>
    [...PLAYER_QUERY_KEYS.detail(playerId), 'recent-form', matches] as const,
}

// Hook to fetch players with filters
export const usePlayers = (filters?: PlayerListFilters, skip: number = 0, limit: number = 100) => {
  return useQuery({
    queryKey: PLAYER_QUERY_KEYS.list(filters || {}, skip, limit),
    queryFn: () => playerService.getPlayers(filters, skip, limit),
    staleTime: 5 * 60 * 1000, // 5 minutes
  })
}

// Hook to fetch single player by username
export const usePlayer = (username: string, enabled = true) => {
  return useQuery({
    queryKey: PLAYER_QUERY_KEYS.detail(username),
    queryFn: () => playerService.getPlayerByUsername(username),
    enabled: enabled && !!username,
    staleTime: 2 * 60 * 1000, // 2 minutes
  })
}

// Hook to fetch player activity
export const usePlayerActivity = (playerId: string, months: number = 12, enabled = true) => {
  return useQuery({
    queryKey: PLAYER_QUERY_KEYS.activity(playerId, months),
    queryFn: () => playerService.getPlayerActivity(playerId, months),
    enabled: enabled && !!playerId,
    staleTime: 5 * 60 * 1000, // 5 minutes
  })
}

// Hook to fetch player win/loss by type
export const usePlayerWinLoss = (playerId: string, enabled = true) => {
  return useQuery({
    queryKey: PLAYER_QUERY_KEYS.winLoss(playerId),
    queryFn: () => playerService.getWinLossByType(playerId),
    enabled: enabled && !!playerId,
    staleTime: 5 * 60 * 1000, // 5 minutes
  })
}

// Hook to fetch player recent form
export const usePlayerRecentForm = (playerId: string, matches: number = 20, enabled = true) => {
  return useQuery({
    queryKey: PLAYER_QUERY_KEYS.recentForm(playerId, matches),
    queryFn: () => playerService.getRecentForm(playerId, matches),
    enabled: enabled && !!playerId,
    staleTime: 2 * 60 * 1000, // 2 minutes
  })
}
