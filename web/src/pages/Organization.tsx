import { useState, useEffect } from 'react'
import { useTranslation } from 'react-i18next'
import { Card } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { useAuthStore } from '@/stores/authStore'
import { organizationService, Organization as Org, OrgInvite } from '@/services/organizationService'
import { Users, Crown, Shield, User, Trash2, Mail, Plus } from 'lucide-react'
import PlanGate from '@/components/auth/PlanGate'

const Organization = () => {
  const { t } = useTranslation()
  const { user } = useAuthStore()
  const [org, setOrg] = useState<Org | null>(null)
  const [invites, setInvites] = useState<OrgInvite[]>([])
  const [loading, setLoading] = useState(true)
  const [creating, setCreating] = useState(false)
  const [inviting, setInviting] = useState(false)
  const [newOrgName, setNewOrgName] = useState('')
  const [inviteEmail, setInviteEmail] = useState('')
  const [inviteRole, setInviteRole] = useState('member')
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')

  const loadData = async () => {
    try {
      const data = await organizationService.getMyOrg()
      setOrg(data)
      if (data) {
        const inv = await organizationService.getInvites()
        setInvites(inv)
      }
    } catch {
      // User has no org
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadData()
  }, [])

  const handleCreate = async () => {
    if (!newOrgName.trim()) return
    setCreating(true)
    setError('')
    try {
      const created = await organizationService.create(newOrgName.trim())
      setOrg(created)
      setNewOrgName('')
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Erro ao criar organizacao')
    } finally {
      setCreating(false)
    }
  }

  const handleInvite = async () => {
    if (!inviteEmail.trim()) return
    setInviting(true)
    setError('')
    setMessage('')
    try {
      await organizationService.invite(inviteEmail.trim(), inviteRole)
      setMessage(t('organization.inviteSent'))
      setInviteEmail('')
      setInviteRole('member')
      const inv = await organizationService.getInvites()
      setInvites(inv)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Erro ao enviar convite')
    } finally {
      setInviting(false)
    }
  }

  const handleRemove = async (userId: string) => {
    try {
      await organizationService.removeMember(userId)
      await loadData()
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Erro ao remover membro')
    }
  }

  const getRoleIcon = (role: string) => {
    switch (role) {
      case 'owner': return <Crown className="w-4 h-4 text-amber-400" />
      case 'admin': return <Shield className="w-4 h-4 text-blue-400" />
      default: return <User className="w-4 h-4 text-slate-400" />
    }
  }

  const getRoleBadge = (role: string) => {
    const colors: Record<string, string> = {
      owner: 'bg-amber-500/10 text-amber-400',
      admin: 'bg-blue-500/10 text-blue-400',
      member: 'bg-slate-500/10 text-slate-400',
    }
    return colors[role] || colors.member
  }

  const currentMember = org?.members.find(m => m.userId === user?.id)
  const canManage = currentMember?.role === 'owner' || currentMember?.role === 'admin'

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="w-8 h-8 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />
      </div>
    )
  }

  return (
    <PlanGate requiredPlans={['grand_slam']} featureName={t('organization.title')}>
      <div className="p-6 space-y-6">
        <div className="flex items-center gap-3">
          <Users className="w-6 h-6 text-blue-400" />
          <h1 className="text-2xl font-bold text-slate-100">{t('organization.title')}</h1>
        </div>

        {error && (
          <div className="bg-red-500/10 border border-red-500/20 rounded-lg p-3 text-red-400 text-sm">
            {error}
          </div>
        )}
        {message && (
          <div className="bg-green-500/10 border border-green-500/20 rounded-lg p-3 text-green-400 text-sm">
            {message}
          </div>
        )}

        {!org ? (
          <Card className="bg-slate-800 border-slate-700 p-6">
            <h2 className="text-lg font-semibold text-slate-100 mb-4">{t('organization.createOrg')}</h2>
            <div className="flex gap-3">
              <input
                type="text"
                value={newOrgName}
                onChange={(e) => setNewOrgName(e.target.value)}
                placeholder={t('organization.orgName')}
                className="flex-1 bg-slate-900 border border-slate-700 rounded-md px-3 py-2 text-slate-100 text-sm placeholder:text-slate-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
              />
              <Button
                onClick={handleCreate}
                disabled={creating || !newOrgName.trim()}
                className="bg-blue-500 hover:bg-blue-600"
              >
                {creating ? '...' : t('organization.createOrg')}
              </Button>
            </div>
          </Card>
        ) : (
          <>
            {/* Org Info */}
            <Card className="bg-slate-800 border-slate-700 p-6">
              <div className="flex items-center justify-between mb-4">
                <div>
                  <h2 className="text-lg font-semibold text-slate-100">{org.name}</h2>
                  <p className="text-sm text-slate-400">/{org.slug}</p>
                </div>
                <span className="text-sm text-slate-400">
                  {org.members.length}/{org.maxMembers} {t('organization.members').toLowerCase()}
                </span>
              </div>
            </Card>

            {/* Members */}
            <Card className="bg-slate-800 border-slate-700 overflow-hidden">
              <div className="p-4 border-b border-slate-700">
                <h3 className="text-md font-semibold text-slate-100">{t('organization.members')}</h3>
              </div>
              <div className="divide-y divide-slate-700">
                {org.members.map((member) => (
                  <div key={member.userId} className="flex items-center justify-between p-4">
                    <div className="flex items-center gap-3">
                      {getRoleIcon(member.role)}
                      <div>
                        <p className="text-sm text-slate-100">{member.userId}</p>
                        <span className={`text-xs px-2 py-0.5 rounded-full ${getRoleBadge(member.role)}`}>
                          {t(`organization.${member.role}`)}
                        </span>
                      </div>
                    </div>
                    {canManage && member.role !== 'owner' && member.userId !== user?.id && (
                      <Button
                        size="sm"
                        variant="ghost"
                        onClick={() => handleRemove(member.userId)}
                        className="text-red-400 hover:text-red-300 hover:bg-red-500/10"
                      >
                        <Trash2 className="w-4 h-4" />
                      </Button>
                    )}
                  </div>
                ))}
              </div>
            </Card>

            {/* Invite Section */}
            {canManage && (
              <Card className="bg-slate-800 border-slate-700 p-6">
                <h3 className="text-md font-semibold text-slate-100 mb-4">
                  <div className="flex items-center gap-2">
                    <Plus className="w-4 h-4" />
                    {t('organization.inviteMembers')}
                  </div>
                </h3>
                <div className="flex gap-3 items-end">
                  <div className="flex-1">
                    <label className="text-xs text-slate-400 mb-1 block">{t('organization.inviteEmail')}</label>
                    <input
                      type="email"
                      value={inviteEmail}
                      onChange={(e) => setInviteEmail(e.target.value)}
                      placeholder="email@example.com"
                      className="w-full bg-slate-900 border border-slate-700 rounded-md px-3 py-2 text-slate-100 text-sm placeholder:text-slate-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
                    />
                  </div>
                  <div className="w-32">
                    <label className="text-xs text-slate-400 mb-1 block">{t('organization.inviteRole')}</label>
                    <select
                      value={inviteRole}
                      onChange={(e) => setInviteRole(e.target.value)}
                      className="w-full bg-slate-900 border border-slate-700 rounded-md px-3 py-2 text-slate-100 text-sm"
                    >
                      <option value="member">{t('organization.member')}</option>
                      <option value="admin">{t('organization.admin')}</option>
                    </select>
                  </div>
                  <Button
                    onClick={handleInvite}
                    disabled={inviting || !inviteEmail.trim()}
                    className="bg-blue-500 hover:bg-blue-600"
                  >
                    {inviting ? '...' : t('organization.sendInvite')}
                  </Button>
                </div>
              </Card>
            )}

            {/* Pending Invites */}
            {invites.length > 0 && (
              <Card className="bg-slate-800 border-slate-700 overflow-hidden">
                <div className="p-4 border-b border-slate-700">
                  <h3 className="text-md font-semibold text-slate-100 flex items-center gap-2">
                    <Mail className="w-4 h-4" />
                    Convites pendentes
                  </h3>
                </div>
                <div className="divide-y divide-slate-700">
                  {invites.map((invite) => (
                    <div key={invite._id} className="flex items-center justify-between p-4">
                      <div>
                        <p className="text-sm text-slate-100">{invite.email}</p>
                        <p className="text-xs text-slate-400">
                          {t(`organization.${invite.role}`)} — expira {new Date(invite.expiresAt).toLocaleDateString('pt-BR')}
                        </p>
                      </div>
                      <span className="text-xs px-2 py-0.5 rounded-full bg-yellow-500/10 text-yellow-400">
                        Pendente
                      </span>
                    </div>
                  ))}
                </div>
              </Card>
            )}
          </>
        )}
      </div>
    </PlanGate>
  )
}

export default Organization
