import { useState, useEffect } from 'react'
import { useTranslation } from 'react-i18next'
import { Card } from '@/components/ui/card'
import { adminService } from '@/services/adminService'

const AdminSubscriptions = () => {
  const { t } = useTranslation()
  const [stats, setStats] = useState<any>(null)

  useEffect(() => {
    adminService.getSubscriptionStats().then(setStats)
  }, [])

  return (
    <div className="p-6 space-y-6">
      <h1 className="text-2xl font-bold text-slate-100">{t('admin.subscriptions')}</h1>

      {/* Plan breakdown */}
      <Card className="bg-slate-800 border-slate-700 p-6">
        <h2 className="text-lg font-semibold text-slate-100 mb-4">Distribuicao por plano</h2>
        {stats?.planBreakdown && (
          <div className="grid grid-cols-3 gap-4">
            {Object.entries(stats.planBreakdown).map(([plan, count]) => (
              <div key={plan} className="bg-slate-900 rounded-lg p-4 text-center">
                <p className="text-3xl font-bold text-slate-100">{count as number}</p>
                <p className="text-sm text-slate-400 capitalize">{plan.replace('_', ' ')}</p>
              </div>
            ))}
          </div>
        )}
      </Card>

      {/* Recent events */}
      <Card className="bg-slate-800 border-slate-700 p-6">
        <h2 className="text-lg font-semibold text-slate-100 mb-4">Eventos recentes</h2>
        {stats?.recentEvents?.length ? (
          <div className="space-y-2">
            {stats.recentEvents.map((event: any, i: number) => (
              <div key={i} className="flex items-center justify-between p-3 bg-slate-900 rounded-lg">
                <div>
                  <p className="text-sm text-slate-100">{event.eventType}</p>
                  <p className="text-xs text-slate-400">
                    {new Date(event.createdAt).toLocaleString('pt-BR')}
                  </p>
                </div>
                <span className={`text-xs px-2 py-0.5 rounded-full ${
                  event.processed ? 'bg-green-500/10 text-green-400' : 'bg-yellow-500/10 text-yellow-400'
                }`}>
                  {event.processed ? 'Processado' : 'Pendente'}
                </span>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-slate-400 text-sm">Nenhum evento encontrado</p>
        )}
      </Card>
    </div>
  )
}

export default AdminSubscriptions
