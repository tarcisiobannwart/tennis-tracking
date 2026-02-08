import { useState } from 'react'
import { useNavigate, Navigate, Link, useLocation } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { motion } from 'framer-motion'
import { Card } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { LogIn } from 'lucide-react'
import toast from 'react-hot-toast'
import { authService } from '@/services/authService'
import { useAuthStore } from '@/stores/authStore'

const Login = () => {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const location = useLocation()
  const { setAuth, isAuthenticated } = useAuthStore()
  const [loading, setLoading] = useState(false)
  const [credentials, setCredentials] = useState({
    username: '',
    password: '',
  })

  // Redirect if already authenticated
  if (isAuthenticated) {
    const from = (location.state as any)?.from?.pathname || '/app'
    return <Navigate to={from} replace />
  }

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)

    try {
      const data = await authService.login(credentials.username, credentials.password)
      setAuth(data.user, data.access_token, data.refresh_token)
      toast.success(t('auth.login.loginSuccess'))

      const from = (location.state as any)?.from?.pathname || '/app'
      navigate(from, { replace: true })
    } catch (error: any) {
      const msg = error.response?.data?.detail || t('auth.login.invalidCredentials')
      toast.error(msg)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-900 relative overflow-hidden">
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute -top-1/2 -left-1/2 w-full h-full bg-gradient-to-br from-blue-500/10 to-transparent rounded-full blur-3xl" />
        <div className="absolute -bottom-1/2 -right-1/2 w-full h-full bg-gradient-to-tl from-blue-500/10 to-transparent rounded-full blur-3xl" />
      </div>

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="relative z-10 w-full max-w-md px-4"
      >
        <Card className="bg-slate-800 border-slate-700 overflow-hidden">
          <div className="relative bg-gradient-to-r from-blue-500/20 to-blue-600/20 p-8 text-center border-b border-slate-700">
            <motion.div
              initial={{ scale: 0.8, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              transition={{ delay: 0.2 }}
              className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-blue-500/20 mb-4"
            >
              <LogIn className="w-8 h-8 text-blue-400" />
            </motion.div>
            <h1 className="text-3xl font-bold text-slate-100 mb-2">
              Tennis Tracking
            </h1>
            <p className="text-sm text-slate-400">
              {t('auth.login.title')}
            </p>
          </div>

          <div className="p-8">
            <form onSubmit={handleLogin} className="space-y-5">
              <div>
                <label className="block text-sm font-medium mb-2 text-slate-100">
                  {t('auth.login.email')}
                </label>
                <Input
                  type="text"
                  value={credentials.username}
                  onChange={(e) => setCredentials({ ...credentials, username: e.target.value })}
                  placeholder="usuario ou email"
                  className="bg-slate-900 border-slate-700 text-slate-100 focus:border-blue-500"
                  required
                />
              </div>

              <div>
                <div className="flex items-center justify-between mb-2">
                  <label className="block text-sm font-medium text-slate-100">
                    {t('auth.login.password')}
                  </label>
                  <Link to="/forgot-password" className="text-xs text-blue-400 hover:text-blue-300">
                    {t('auth.login.forgotPassword')}
                  </Link>
                </div>
                <Input
                  type="password"
                  value={credentials.password}
                  onChange={(e) => setCredentials({ ...credentials, password: e.target.value })}
                  placeholder="••••••••"
                  className="bg-slate-900 border-slate-700 text-slate-100 focus:border-blue-500"
                  required
                />
              </div>

              <Button
                type="submit"
                className="w-full bg-blue-500 hover:bg-blue-600 text-white font-medium h-11"
                disabled={loading}
              >
                {loading ? (
                  <motion.div
                    animate={{ rotate: 360 }}
                    transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
                    className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full"
                  />
                ) : (
                  t('auth.login.submit')
                )}
              </Button>
            </form>

            <p className="text-sm text-center text-slate-400 mt-6">
              {t('auth.login.noAccount')}{' '}
              <Link to="/register" className="text-blue-400 hover:text-blue-300 font-medium">
                {t('auth.login.signUp')}
              </Link>
            </p>
          </div>
        </Card>

        <motion.p
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.8 }}
          className="text-center text-xs text-slate-500 mt-6"
        >
          {t('footer.copyright')}
        </motion.p>
      </motion.div>
    </div>
  )
}

export default Login
