import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { Card } from '@/components/ui/card'
import { Users, CreditCard, Activity, DollarSign, ArrowRight } from 'lucide-react'
import { adminService } from '@/services/adminService'

const AdminDashboard = () => {
  const { t } = useTranslation()
  const [metrics, setMetrics] = useState<any>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    adminService.getMetrics().then(setMetrics).finally(() => setLoading(false))
  }, [])

  if (loading) {
    return (
      <div className="p-6 flex items-center justify-center h-64">
        <div className="w-8 h-8 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />
      </div>
    )
  }

  const statCards = [
    { label: t('admin.totalUsers'), value: metrics?.totalUsers || 0, icon: Users, color: 'text-blue-400' },
    { label: t('admin.newUsersThisMonth'), value: metrics?.newUsersThisMonth || 0, icon: Users, color: 'text-green-400' },
    { label: t('admin.activeSubscriptions'), value: (metrics?.subscriptions?.match_point || 0) + (metrics?.subscriptions?.grand_slam || 0), icon: CreditCard, color: 'text-purple-400' },
    { label: t('admin.mrr'), value: `R$${(metrics?.mrr || 0).toFixed(0)}`, icon: DollarSign, color: 'text-amber-400' },
  ]

  return (
    <div className="p-6 space-y-6">
      <h1 className="text-2xl font-bold text-slate-100">{t('admin.dashboard')}</h1>

      {/* Stat cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {statCards.map((stat, i) => {
          const Icon = stat.icon
          return (
            <Card key={i} className="bg-slate-800 border-slate-700 p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-xs text-slate-400">{stat.label}</p>
                  <p className="text-2xl font-bold text-slate-100 mt-1">{stat.value}</p>
                </div>
                <Icon className={`w-8 h-8 ${stat.color} opacity-50`} />
              </div>
            </Card>
          )
        })}
      </div>

      {/* Subscription breakdown */}
      <Card className="bg-slate-800 border-slate-700 p-6">
        <h2 className="text-lg font-semibold text-slate-100 mb-4">Planos</h2>
        <div className="grid grid-cols-3 gap-4">
          <div className="bg-slate-900 rounded-lg p-4 text-center">
            <p className="text-3xl font-bold text-slate-100">{metrics?.subscriptions?.rally || 0}</p>
            <p className="text-sm text-slate-400">Rally (Gratis)</p>
          </div>
          <div className="bg-slate-900 rounded-lg p-4 text-center">
            <p className="text-3xl font-bold text-blue-400">{metrics?.subscriptions?.match_point || 0}</p>
            <p className="text-sm text-slate-400">Match Point</p>
          </div>
          <div className="bg-slate-900 rounded-lg p-4 text-center">
            <p className="text-3xl font-bold text-amber-400">{metrics?.subscriptions?.grand_slam || 0}</p>
            <p className="text-sm text-slate-400">Grand Slam</p>
          </div>
        </div>
      </Card>

      {/* Quick links */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Link to="/app/admin/users" className="block">
          <Card className="bg-slate-800 border-slate-700 p-6 hover:border-slate-600 transition-colors">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <Users className="w-5 h-5 text-blue-400" />
                <span className="text-slate-100 font-medium">{t('admin.users')}</span>
              </div>
              <ArrowRight className="w-4 h-4 text-slate-400" />
            </div>
          </Card>
        </Link>
        <Link to="/app/admin/subscriptions" className="block">
          <Card className="bg-slate-800 border-slate-700 p-6 hover:border-slate-600 transition-colors">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <CreditCard className="w-5 h-5 text-purple-400" />
                <span className="text-slate-100 font-medium">{t('admin.subscriptions')}</span>
              </div>
              <ArrowRight className="w-4 h-4 text-slate-400" />
            </div>
          </Card>
        </Link>
        <Link to="/app/admin/logs" className="block">
          <Card className="bg-slate-800 border-slate-700 p-6 hover:border-slate-600 transition-colors">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <Activity className="w-5 h-5 text-green-400" />
                <span className="text-slate-100 font-medium">{t('admin.logs')}</span>
              </div>
              <ArrowRight className="w-4 h-4 text-slate-400" />
            </div>
          </Card>
        </Link>
      </div>
    </div>
  )
}

export default AdminDashboard
