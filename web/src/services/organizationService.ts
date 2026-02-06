import { apiGet, apiPost, apiDelete } from './api'

export interface OrgMember {
  userId: string
  role: 'owner' | 'admin' | 'member'
  joinedAt: string
}

export interface Organization {
  _id: string
  name: string
  slug: string
  ownerId: string
  plan: string
  maxMembers: number
  members: OrgMember[]
  createdAt: string
  updatedAt: string
}

export interface OrgInvite {
  _id: string
  organizationId: string
  email: string
  role: string
  token: string
  invitedBy: string
  status: string
  expiresAt: string
  createdAt: string
}

export const organizationService = {
  getMyOrg: () => apiGet<Organization | null>('/organizations/me'),

  create: (name: string) => apiPost<Organization>('/organizations/', { name }),

  invite: (email: string, role: string) =>
    apiPost<{ message: string }>('/organizations/invite', { email, role }),

  acceptInvite: (token: string) =>
    apiPost<{ message: string }>(`/organizations/accept-invite?token=${token}`),

  removeMember: (userId: string) =>
    apiDelete<{ message: string }>(`/organizations/members/${userId}`),

  getInvites: () => apiGet<OrgInvite[]>('/organizations/invites'),
}
