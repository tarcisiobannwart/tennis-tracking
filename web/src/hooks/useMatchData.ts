import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { matchService, MatchFilters, CreateMatchData } from '@/services/matchService'
import { Match } from '@/types'
import { useUIStore } from '@/stores/uiStore'

// Query keys
export const MATCH_QUERY_KEYS = {
  all: ['matches'] as const,
  lists: () => [...MATCH_QUERY_KEYS.all, 'list'] as const,
  list: (filters: MatchFilters) => [...MATCH_QUERY_KEYS.lists(), filters] as const,
  details: () => [...MATCH_QUERY_KEYS.all, 'detail'] as const,
  detail: (id: string) => [...MATCH_QUERY_KEYS.details(), id] as const,
  statistics: (id: string) => [...MATCH_QUERY_KEYS.detail(id), 'statistics'] as const,
  live: () => [...MATCH_QUERY_KEYS.all, 'live'] as const,
  recent: () => [...MATCH_QUERY_KEYS.all, 'recent'] as const,
  highlights: (id: string) => [...MATCH_QUERY_KEYS.detail(id), 'highlights'] as const,
}

// Hook to fetch matches with filters
export const useMatches = (filters?: MatchFilters) => {
  return useQuery({
    queryKey: MATCH_QUERY_KEYS.list(filters || {}),
    queryFn: () => matchService.getMatches(filters),
    staleTime: 5 * 60 * 1000, // 5 minutes
  })
}

// Hook to fetch single match
export const useMatch = (id: string, enabled = true) => {
  return useQuery({
    queryKey: MATCH_QUERY_KEYS.detail(id),
    queryFn: () => matchService.getMatch(id),
    enabled: enabled && !!id,
    staleTime: 2 * 60 * 1000, // 2 minutes
  })
}

// Hook to fetch match statistics
export const useMatchStatistics = (id: string, enabled = true) => {
  return useQuery({
    queryKey: MATCH_QUERY_KEYS.statistics(id),
    queryFn: () => matchService.getMatchStatistics(id),
    enabled: enabled && !!id,
    staleTime: 1 * 60 * 1000, // 1 minute
  })
}

// Hook to fetch live matches
export const useLiveMatches = () => {
  return useQuery({
    queryKey: MATCH_QUERY_KEYS.live(),
    queryFn: () => matchService.getLiveMatches(),
    refetchInterval: 30 * 1000, // Refetch every 30 seconds
    staleTime: 10 * 1000, // 10 seconds
  })
}

// Hook to fetch recent matches
export const useRecentMatches = (limit = 10) => {
  return useQuery({
    queryKey: MATCH_QUERY_KEYS.recent(),
    queryFn: () => matchService.getRecentMatches(limit),
    staleTime: 5 * 60 * 1000, // 5 minutes
  })
}

// Hook to fetch match highlights
export const useMatchHighlights = (id: string, enabled = true) => {
  return useQuery({
    queryKey: MATCH_QUERY_KEYS.highlights(id),
    queryFn: () => matchService.getMatchHighlights(id),
    enabled: enabled && !!id,
    staleTime: 10 * 60 * 1000, // 10 minutes
  })
}

// Hook to create match
export const useCreateMatch = () => {
  const queryClient = useQueryClient()
  const { addNotification } = useUIStore()

  return useMutation({
    mutationFn: (data: CreateMatchData) => matchService.createMatch(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: MATCH_QUERY_KEYS.lists() })
      addNotification({
        type: 'success',
        title: 'Match Created',
        message: 'New match has been created successfully',
      })
    },
    onError: (error: any) => {
      addNotification({
        type: 'error',
        title: 'Error',
        message: error.response?.data?.message || 'Failed to create match',
      })
    },
  })
}

// Hook to update match
export const useUpdateMatch = () => {
  const queryClient = useQueryClient()
  const { addNotification } = useUIStore()

  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<Match> }) =>
      matchService.updateMatch(id, data),
    onSuccess: (_, { id }) => {
      queryClient.invalidateQueries({ queryKey: MATCH_QUERY_KEYS.detail(id) })
      queryClient.invalidateQueries({ queryKey: MATCH_QUERY_KEYS.lists() })
      addNotification({
        type: 'success',
        title: 'Match Updated',
        message: 'Match has been updated successfully',
      })
    },
    onError: (error: any) => {
      addNotification({
        type: 'error',
        title: 'Error',
        message: error.response?.data?.message || 'Failed to update match',
      })
    },
  })
}

// Hook to delete match
export const useDeleteMatch = () => {
  const queryClient = useQueryClient()
  const { addNotification } = useUIStore()

  return useMutation({
    mutationFn: (id: string) => matchService.deleteMatch(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: MATCH_QUERY_KEYS.lists() })
      addNotification({
        type: 'success',
        title: 'Match Deleted',
        message: 'Match has been deleted successfully',
      })
    },
    onError: (error: any) => {
      addNotification({
        type: 'error',
        title: 'Error',
        message: error.response?.data?.message || 'Failed to delete match',
      })
    },
  })
}

// Hook to upload video
export const useUploadVideo = () => {
  const queryClient = useQueryClient()
  const { addNotification, setLoading } = useUIStore()

  return useMutation({
    mutationFn: ({ matchId, file }: { matchId: string; file: File }) =>
      matchService.uploadVideo(matchId, file, (progress) => {
        setLoading(true, `Uploading video... ${Math.round(progress)}%`)
      }),
    onSuccess: (_, { matchId }) => {
      setLoading(false)
      queryClient.invalidateQueries({ queryKey: MATCH_QUERY_KEYS.detail(matchId) })
      addNotification({
        type: 'success',
        title: 'Video Uploaded',
        message: 'Video has been uploaded successfully',
      })
    },
    onError: (error: any) => {
      setLoading(false)
      addNotification({
        type: 'error',
        title: 'Upload Failed',
        message: error.response?.data?.message || 'Failed to upload video',
      })
    },
  })
}

// Hook to start live analysis
export const useStartLiveAnalysis = () => {
  const { addNotification } = useUIStore()

  return useMutation({
    mutationFn: (matchId: string) => matchService.startLiveAnalysis(matchId),
    onSuccess: () => {
      addNotification({
        type: 'success',
        title: 'Analysis Started',
        message: 'Live analysis has been started',
      })
    },
    onError: (error: any) => {
      addNotification({
        type: 'error',
        title: 'Error',
        message: error.response?.data?.message || 'Failed to start analysis',
      })
    },
  })
}

// Hook to stop live analysis
export const useStopLiveAnalysis = () => {
  const { addNotification } = useUIStore()

  return useMutation({
    mutationFn: (matchId: string) => matchService.stopLiveAnalysis(matchId),
    onSuccess: () => {
      addNotification({
        type: 'success',
        title: 'Analysis Stopped',
        message: 'Live analysis has been stopped',
      })
    },
    onError: (error: any) => {
      addNotification({
        type: 'error',
        title: 'Error',
        message: error.response?.data?.message || 'Failed to stop analysis',
      })
    },
  })
}