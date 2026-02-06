import { useAuthStore } from '@/stores/authStore'
import { useTranslation } from 'react-i18next'
import { Lock } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { useNavigate } from 'react-router-dom'

interface PlanGateProps {
  children: React.ReactNode
  requiredPlans: string[]
  featureName?: string
}

const PlanGate = ({ children, requiredPlans, featureName }: PlanGateProps) => {
  const { user } = useAuthStore()
  const { t } = useTranslation()
  const navigate = useNavigate()

  const userPlan = user?.subscription?.plan || 'rally'

  if (requiredPlans.includes(userPlan)) {
    return <>{children}</>
  }

  return (
    <div className="flex flex-col items-center justify-center p-8 text-center">
      <div className="w-16 h-16 rounded-full bg-slate-700 flex items-center justify-center mb-4">
        <Lock className="w-8 h-8 text-slate-400" />
      </div>
      <h3 className="text-lg font-semibold text-slate-100 mb-2">
        {featureName || t('subscription.featureLocked')}
      </h3>
      <p className="text-sm text-slate-400 mb-4 max-w-md">
        {t('subscription.upgradeMessage', {
          plan: requiredPlans.includes('match_point') ? 'Match Point' : 'Grand Slam'
        })}
      </p>
      <Button
        onClick={() => navigate('/app/settings?tab=subscription')}
        className="bg-blue-500 hover:bg-blue-600"
      >
        {t('subscription.upgrade')}
      </Button>
    </div>
  )
}

export default PlanGate
