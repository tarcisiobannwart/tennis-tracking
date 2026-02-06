import { useState } from 'react'
import { useNavigate, useSearchParams, Link } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { motion } from 'framer-motion'
import { Card } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { KeyRound } from 'lucide-react'
import toast from 'react-hot-toast'
import { authService } from '@/services/authService'

const ResetPassword = () => {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const token = searchParams.get('token') || ''
  const [loading, setLoading] = useState(false)
  const [password, setPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (password !== confirmPassword) {
      toast.error(t('auth.register.passwordMismatch'))
      return
    }

    setLoading(true)

    try {
      await authService.resetPassword(token, password)
      toast.success(t('auth.resetPassword.success'))
      navigate('/login')
    } catch (error: any) {
      const msg = error.response?.data?.detail || t('errors.generic')
      toast.error(msg)
    } finally {
      setLoading(false)
    }
  }

  if (!token) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-900">
        <Card className="bg-slate-800 border-slate-700 p-8 text-center">
          <p className="text-slate-300 mb-4">{t('auth.resetPassword.invalidToken')}</p>
          <Link to="/forgot-password">
            <Button className="bg-blue-500 hover:bg-blue-600">
              {t('auth.resetPassword.requestNew')}
            </Button>
          </Link>
        </Card>
      </div>
    )
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-900 relative overflow-hidden">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="relative z-10 w-full max-w-md px-4"
      >
        <Card className="bg-slate-800 border-slate-700 overflow-hidden">
          <div className="relative bg-gradient-to-r from-purple-500/20 to-purple-600/20 p-8 text-center border-b border-slate-700">
            <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-purple-500/20 mb-4">
              <KeyRound className="w-8 h-8 text-purple-400" />
            </div>
            <h1 className="text-2xl font-bold text-slate-100 mb-2">
              {t('auth.resetPassword.title')}
            </h1>
          </div>

          <div className="p-8">
            <form onSubmit={handleSubmit} className="space-y-5">
              <div>
                <label className="block text-sm font-medium mb-2 text-slate-100">
                  {t('auth.resetPassword.newPassword')}
                </label>
                <Input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="bg-slate-900 border-slate-700 text-slate-100"
                  required
                  minLength={6}
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-2 text-slate-100">
                  {t('auth.register.confirmPassword')}
                </label>
                <Input
                  type="password"
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  className="bg-slate-900 border-slate-700 text-slate-100"
                  required
                />
              </div>

              <Button
                type="submit"
                className="w-full bg-purple-500 hover:bg-purple-600 text-white font-medium h-11"
                disabled={loading}
              >
                {loading ? (
                  <motion.div
                    animate={{ rotate: 360 }}
                    transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
                    className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full"
                  />
                ) : (
                  t('auth.resetPassword.submit')
                )}
              </Button>
            </form>
          </div>
        </Card>
      </motion.div>
    </div>
  )
}

export default ResetPassword
