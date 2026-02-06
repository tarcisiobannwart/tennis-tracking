import { useState, useEffect } from 'react'
import { useTranslation } from 'react-i18next'
import { useSearchParams, useNavigate } from 'react-router-dom'
import { Card } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { organizationService } from '@/services/organizationService'
import { CheckCircle, XCircle, Loader2 } from 'lucide-react'

const AcceptInvite = () => {
  const { t } = useTranslation()
  const [searchParams] = useSearchParams()
  const navigate = useNavigate()
  const token = searchParams.get('token')

  const [status, setStatus] = useState<'loading' | 'success' | 'error'>('loading')
  const [errorMsg, setErrorMsg] = useState('')

  useEffect(() => {
    if (!token) {
      setStatus('error')
      setErrorMsg(t('organization.inviteExpired'))
      return
    }

    organizationService.acceptInvite(token)
      .then(() => {
        setStatus('success')
      })
      .catch((err) => {
        setStatus('error')
        setErrorMsg(err.response?.data?.detail || t('organization.inviteExpired'))
      })
  }, [token, t])

  return (
    <div className="flex items-center justify-center min-h-[60vh]">
      <Card className="bg-slate-800 border-slate-700 p-8 max-w-md w-full text-center">
        {status === 'loading' && (
          <div className="space-y-4">
            <Loader2 className="w-12 h-12 text-blue-400 animate-spin mx-auto" />
            <p className="text-slate-300">{t('organization.acceptInvite')}...</p>
          </div>
        )}

        {status === 'success' && (
          <div className="space-y-4">
            <CheckCircle className="w-12 h-12 text-green-400 mx-auto" />
            <h2 className="text-lg font-semibold text-slate-100">{t('organization.inviteAccepted')}</h2>
            <Button
              onClick={() => navigate('/app/organization')}
              className="bg-blue-500 hover:bg-blue-600"
            >
              {t('organization.title')}
            </Button>
          </div>
        )}

        {status === 'error' && (
          <div className="space-y-4">
            <XCircle className="w-12 h-12 text-red-400 mx-auto" />
            <h2 className="text-lg font-semibold text-slate-100">{errorMsg}</h2>
            <Button
              onClick={() => navigate('/app')}
              variant="ghost"
              className="text-slate-300"
            >
              Voltar ao dashboard
            </Button>
          </div>
        )}
      </Card>
    </div>
  )
}

export default AcceptInvite
