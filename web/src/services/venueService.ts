import { apiGet, apiPost, apiPut, apiDelete } from './api'

export interface Venue {
  id: string
  name: string
  slug: string
  description?: string
  avatar_url?: string
  cover_photo_url?: string
  address?: string
  city?: string
  state?: string
  country?: string
  latitude?: number
  longitude?: number
  phone?: string
  email?: string
  website?: string
  sport_types: string[]
  court_count: number
  surface_types: string[]
  amenities: string[]
  followers_count: number
  members_count: number
  is_public: boolean
  owner_id: string
  created_at: string
  updated_at: string
  is_following: boolean
  is_member: boolean
  member_role?: string
}

export interface VenueListResponse {
  venues: Venue[]
  total: number
  skip: number
  limit: number
}

export interface VenueCreate {
  name: string
  description?: string
  avatar_url?: string
  cover_photo_url?: string
  address?: string
  city?: string
  state?: string
  country?: string
  latitude?: number
  longitude?: number
  phone?: string
  email?: string
  website?: string
  sport_types?: string[]
  court_count?: number
  surface_types?: string[]
  amenities?: string[]
  is_public?: boolean
}

export interface VenueUpdate {
  name?: string
  description?: string
  avatar_url?: string
  cover_photo_url?: string
  address?: string
  city?: string
  state?: string
  country?: string
  latitude?: number
  longitude?: number
  phone?: string
  email?: string
  website?: string
  sport_types?: string[]
  court_count?: number
  surface_types?: string[]
  amenities?: string[]
  is_public?: boolean
}

export interface VenueMember {
  user_id: string
  role: string
  joined_at: string
}

export interface VenueFollower {
  user_id: string
  followed_at: string
}

export const venueService = {
  async listVenues(params?: {
    skip?: number
    limit?: number
    city?: string
    country?: string
    sport?: string
    search?: string
  }): Promise<VenueListResponse> {
    return apiGet('/venues', params)
  },

  async getVenueBySlug(slug: string): Promise<Venue> {
    return apiGet(`/venues/${slug}`)
  },

  async createVenue(data: VenueCreate): Promise<Venue> {
    return apiPost('/venues', data)
  },

  async updateVenue(venueId: string, data: VenueUpdate): Promise<Venue> {
    return apiPut(`/venues/${venueId}`, data)
  },

  async deleteVenue(venueId: string): Promise<{ message: string }> {
    return apiDelete(`/venues/${venueId}`)
  },

  async followVenue(venueId: string): Promise<{ message: string }> {
    return apiPost(`/venues/${venueId}/follow`)
  },

  async unfollowVenue(venueId: string): Promise<{ message: string }> {
    return apiPost(`/venues/${venueId}/unfollow`)
  },

  async joinVenue(venueId: string): Promise<{ message: string }> {
    return apiPost(`/venues/${venueId}/join`)
  },

  async leaveVenue(venueId: string): Promise<{ message: string }> {
    return apiPost(`/venues/${venueId}/leave`)
  },

  async getVenueMembers(
    venueId: string,
    params?: { skip?: number; limit?: number }
  ): Promise<{
    members: VenueMember[]
    total: number
    skip: number
    limit: number
  }> {
    return apiGet(`/venues/${venueId}/members`, params)
  },

  async getVenueFollowers(
    venueId: string,
    params?: { skip?: number; limit?: number }
  ): Promise<{
    followers: VenueFollower[]
    total: number
    skip: number
    limit: number
  }> {
    return apiGet(`/venues/${venueId}/followers`, params)
  },
}
