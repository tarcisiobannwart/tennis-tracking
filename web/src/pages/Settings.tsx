import { useState, useEffect } from 'react'
import { useSearchParams } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { Card } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { CreditCard, Zap, Crown, Check, ExternalLink } from 'lucide-react'
import toast from 'react-hot-toast'
import { useAuthStore } from '@/stores/authStore'
import { subscriptionService, Plan } from '@/services/subscriptionService'
import { userService } from '@/services/userService'

const Settings = () => {
  const { t } = useTranslation()
  const { user } = useAuthStore()
  const [searchParams] = useSearchParams()
  const [plans, setPlans] = useState<Plan[]>([])
  const [usage, setUsage] = useState<any>(null)
  const [loading, setLoading] = useState('')

  const currentPlan = user?.subscription?.plan || 'rally'

  useEffect(() => {
    subscriptionService.getPlans().then(setPlans).catch(() => {})
    userService.getUsage().then(setUsage).catch(() => {})

    const status = searchParams.get('status')
    if (status === 'success') {
      toast.success('Assinatura ativada com sucesso!')
    }
  }, [searchParams])

  const handleCheckout = async (planId: string) => {
    setLoading(planId)
    try {
      const url = await subscriptionService.createCheckout(planId)
      window.location.href = url
    } catch {
      toast.error(t('errors.generic'))
    } finally {
      setLoading('')
    }
  }

  const handlePortal = async () => {
    setLoading('portal')
    try {
      const url = await subscriptionService.createPortal()
      window.location.href = url
    } catch {
      toast.error(t('errors.generic'))
    } finally {
      setLoading('')
    }
  }

  const planIcons: Record<string, any> = {
    rally: Zap,
    match_point: CreditCard,
    grand_slam: Crown,
  }

  const planColors: Record<string, string> = {
    rally: 'border-slate-600',
    match_point: 'border-blue-500',
    grand_slam: 'border-amber-500',
  }

  return (
    <div className="p-6 max-w-6xl mx-auto space-y-6">
      <h1 className="text-2xl font-bold text-slate-100">{t('settings.title')}</h1>

      {/* Usage stats */}
      {usage && (
        <Card className="bg-slate-800 border-slate-700 p-6">
          <h2 className="text-lg font-semibold text-slate-100 mb-4">Uso do plano</h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="bg-slate-900 rounded-lg p-4">
              <p className="text-xs text-slate-400">Videos este mes</p>
              <p className="text-2xl font-bold text-slate-100">
                {usage.videos_this_month}
                <span className="text-sm text-slate-400">
                  /{usage.videos_limit === -1 ? 'ilim.' : usage.videos_limit}
                </span>
              </p>
            </div>
            <div className="bg-slate-900 rounded-lg p-4">
              <p className="text-xs text-slate-400">Duracao max</p>
              <p className="text-2xl font-bold text-slate-100">
                {Math.floor(usage.max_video_duration / 60)}min
              </p>
            </div>
            <div className="bg-slate-900 rounded-lg p-4">
              <p className="text-xs text-slate-400">Historico</p>
              <p className="text-2xl font-bold text-slate-100">
                {usage.history_days === -1 ? 'Ilimitado' : `${usage.history_days}d`}
              </p>
            </div>
            <div className="bg-slate-900 rounded-lg p-4">
              <p className="text-xs text-slate-400">Team</p>
              <p className="text-2xl font-bold text-slate-100">{usage.max_team_members}</p>
            </div>
          </div>
        </Card>
      )}

      {/* Plans */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {plans.map((plan) => {
          const Icon = planIcons[plan.id] || Zap
          const isCurrentPlan = currentPlan === plan.id
          const borderColor = planColors[plan.id] || 'border-slate-600'

          return (
            <Card
              key={plan.id}
              className={`bg-slate-800 border-2 ${isCurrentPlan ? borderColor : 'border-slate-700'} p-6 relative`}
            >
              {isCurrentPlan && (
                <div className="absolute -top-3 left-1/2 -translate-x-1/2 bg-blue-500 text-white text-xs px-3 py-1 rounded-full">
                  {t('subscription.currentPlan')}
                </div>
              )}

              <div className="text-center mb-6">
                <Icon className="w-8 h-8 mx-auto mb-2 text-slate-300" />
                <h3 className="text-xl font-bold text-slate-100">{plan.name}</h3>
                <p className="text-3xl font-bold text-slate-100 mt-2">
                  {plan.price === 0 ? 'Gratis' : `R$${(plan.price / 100).toFixed(0)}`}
                  {plan.price > 0 && <span className="text-sm text-slate-400">/mes</span>}
                </p>
              </div>

              <ul className="space-y-2 mb-6">
                <li className="flex items-center gap-2 text-sm text-slate-300">
                  <Check className="w-4 h-4 text-green-400 flex-shrink-0" />
                  {plan.features.videos_per_month === -1 ? 'Videos ilimitados' : `${plan.features.videos_per_month} videos/mes`}
                </li>
                <li className="flex items-center gap-2 text-sm text-slate-300">
                  <Check className="w-4 h-4 text-green-400 flex-shrink-0" />
                  Ate {Math.floor(plan.features.max_video_duration / 60)}min por video
                </li>
                <li className="flex items-center gap-2 text-sm text-slate-300">
                  <Check className="w-4 h-4 text-green-400 flex-shrink-0" />
                  {plan.features.history_days === -1 ? 'Historico ilimitado' : `${plan.features.history_days} dias de historico`}
                </li>
                <li className="flex items-center gap-2 text-sm text-slate-300">
                  <Check className="w-4 h-4 text-green-400 flex-shrink-0" />
                  {plan.features.max_team_members === 1 ? 'Individual' : `Ate ${plan.features.max_team_members} membros`}
                </li>
                {plan.features.api_access && (
                  <li className="flex items-center gap-2 text-sm text-slate-300">
                    <Check className="w-4 h-4 text-green-400 flex-shrink-0" />
                    Acesso API
                  </li>
                )}
              </ul>

              {isCurrentPlan ? (
                <Button
                  variant="outline"
                  className="w-full border-slate-600"
                  onClick={handlePortal}
                  disabled={loading === 'portal' || plan.id === 'rally'}
                >
                  {plan.id === 'rally' ? 'Plano atual' : (
                    <>
                      {t('subscription.manageBilling')}
                      <ExternalLink className="w-3 h-3 ml-2" />
                    </>
                  )}
                </Button>
              ) : (
                <Button
                  className="w-full bg-blue-500 hover:bg-blue-600"
                  onClick={() => handleCheckout(plan.id)}
                  disabled={!!loading || plan.id === 'rally'}
                >
                  {loading === plan.id ? 'Processando...' : (
                    plan.id === 'rally' ? 'Plano gratuito' : t('subscription.upgrade')
                  )}
                </Button>
              )}
            </Card>
          )
        })}
      </div>
    </div>
  )
}

export default Settings
