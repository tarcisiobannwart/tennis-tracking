import { useState, useEffect } from 'react'
import { useTranslation } from 'react-i18next'
import { Card } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Search, ChevronLeft, ChevronRight } from 'lucide-react'
import toast from 'react-hot-toast'
import { adminService } from '@/services/adminService'

const AdminUsers = () => {
  const { t } = useTranslation()
  const [users, setUsers] = useState<any[]>([])
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(0)
  const [search, setSearch] = useState('')
  const [roleFilter, setRoleFilter] = useState('')
  const [planFilter, setPlanFilter] = useState('')
  const limit = 20

  const loadUsers = async () => {
    try {
      const data = await adminService.getUsers({
        skip: page * limit,
        limit,
        role: roleFilter || undefined,
        plan: planFilter || undefined,
        search: search || undefined,
      })
      setUsers(data.users)
      setTotal(data.total)
    } catch {
      toast.error(t('errors.generic'))
    }
  }

  useEffect(() => { loadUsers() }, [page, roleFilter, planFilter])

  const handleSearch = () => {
    setPage(0)
    loadUsers()
  }

  const handleRoleChange = async (userId: string, role: string) => {
    try {
      await adminService.updateUserRole(userId, role)
      toast.success('Role atualizado')
      loadUsers()
    } catch {
      toast.error(t('errors.generic'))
    }
  }

  const handlePlanChange = async (userId: string, plan: string) => {
    try {
      await adminService.updateUserPlan(userId, plan)
      toast.success('Plano atualizado')
      loadUsers()
    } catch {
      toast.error(t('errors.generic'))
    }
  }

  const handleToggleActive = async (userId: string, isActive: boolean) => {
    try {
      await adminService.toggleUserActive(userId, !isActive)
      toast.success('Status atualizado')
      loadUsers()
    } catch {
      toast.error(t('errors.generic'))
    }
  }

  const totalPages = Math.ceil(total / limit)

  return (
    <div className="p-6 space-y-6">
      <h1 className="text-2xl font-bold text-slate-100">{t('admin.users')}</h1>

      {/* Filters */}
      <div className="flex flex-wrap gap-3">
        <div className="relative flex-1 min-w-[200px]">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
          <Input
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
            placeholder="Buscar por nome, email, username..."
            className="pl-10 bg-slate-800 border-slate-700 text-slate-100"
          />
        </div>
        <select
          value={roleFilter}
          onChange={(e) => setRoleFilter(e.target.value)}
          className="bg-slate-800 border border-slate-700 text-slate-100 rounded-md px-3 py-2 text-sm"
        >
          <option value="">Todos os roles</option>
          <option value="admin">Admin</option>
          <option value="coach">Coach</option>
          <option value="player">Player</option>
          <option value="analyst">Analyst</option>
          <option value="viewer">Viewer</option>
        </select>
        <select
          value={planFilter}
          onChange={(e) => setPlanFilter(e.target.value)}
          className="bg-slate-800 border border-slate-700 text-slate-100 rounded-md px-3 py-2 text-sm"
        >
          <option value="">Todos os planos</option>
          <option value="rally">Rally</option>
          <option value="match_point">Match Point</option>
          <option value="grand_slam">Grand Slam</option>
        </select>
      </div>

      {/* Table */}
      <Card className="bg-slate-800 border-slate-700 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead className="bg-slate-900">
              <tr>
                <th className="text-left p-3 text-slate-400 font-medium">Usuario</th>
                <th className="text-left p-3 text-slate-400 font-medium">Email</th>
                <th className="text-left p-3 text-slate-400 font-medium">{t('admin.role')}</th>
                <th className="text-left p-3 text-slate-400 font-medium">{t('admin.plan')}</th>
                <th className="text-left p-3 text-slate-400 font-medium">{t('admin.status')}</th>
                <th className="text-left p-3 text-slate-400 font-medium">{t('admin.actions')}</th>
              </tr>
            </thead>
            <tbody>
              {users.map((user) => (
                <tr key={user._id} className="border-t border-slate-700 hover:bg-slate-700/50">
                  <td className="p-3">
                    <div>
                      <p className="text-slate-100 font-medium">{user.fullName}</p>
                      <p className="text-xs text-slate-400">{user.username}</p>
                    </div>
                  </td>
                  <td className="p-3 text-slate-300">{user.email}</td>
                  <td className="p-3">
                    <select
                      value={user.role}
                      onChange={(e) => handleRoleChange(user._id, e.target.value)}
                      className="bg-slate-900 border border-slate-600 text-slate-100 rounded px-2 py-1 text-xs"
                    >
                      <option value="admin">Admin</option>
                      <option value="coach">Coach</option>
                      <option value="player">Player</option>
                      <option value="analyst">Analyst</option>
                      <option value="viewer">Viewer</option>
                    </select>
                  </td>
                  <td className="p-3">
                    <select
                      value={user.subscription?.plan || 'rally'}
                      onChange={(e) => handlePlanChange(user._id, e.target.value)}
                      className="bg-slate-900 border border-slate-600 text-slate-100 rounded px-2 py-1 text-xs"
                    >
                      <option value="rally">Rally</option>
                      <option value="match_point">Match Point</option>
                      <option value="grand_slam">Grand Slam</option>
                    </select>
                  </td>
                  <td className="p-3">
                    <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium ${
                      user.isActive ? 'bg-green-500/10 text-green-400' : 'bg-red-500/10 text-red-400'
                    }`}>
                      <span className={`w-1.5 h-1.5 rounded-full ${user.isActive ? 'bg-green-400' : 'bg-red-400'}`} />
                      {user.isActive ? 'Ativo' : 'Inativo'}
                    </span>
                  </td>
                  <td className="p-3">
                    <Button
                      size="sm"
                      variant="ghost"
                      onClick={() => handleToggleActive(user._id, user.isActive)}
                      className="text-xs"
                    >
                      {user.isActive ? 'Desativar' : 'Ativar'}
                    </Button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Pagination */}
        <div className="flex items-center justify-between p-3 border-t border-slate-700">
          <p className="text-sm text-slate-400">
            {total} usuarios total
          </p>
          <div className="flex items-center gap-2">
            <Button
              size="sm"
              variant="ghost"
              disabled={page === 0}
              onClick={() => setPage(p => p - 1)}
            >
              <ChevronLeft className="w-4 h-4" />
            </Button>
            <span className="text-sm text-slate-300">
              {page + 1} / {Math.max(totalPages, 1)}
            </span>
            <Button
              size="sm"
              variant="ghost"
              disabled={page + 1 >= totalPages}
              onClick={() => setPage(p => p + 1)}
            >
              <ChevronRight className="w-4 h-4" />
            </Button>
          </div>
        </div>
      </Card>
    </div>
  )
}

export default AdminUsers
