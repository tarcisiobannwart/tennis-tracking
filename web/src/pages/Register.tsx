import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { motion } from 'framer-motion'
import { Card } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { UserPlus } from 'lucide-react'
import toast from 'react-hot-toast'
import { authService } from '@/services/authService'
import { useAuthStore } from '@/stores/authStore'

const Register = () => {
  const { t } = useTranslation()
  const navigate = useNavigate()
  const { setAuth } = useAuthStore()
  const [loading, setLoading] = useState(false)
  const [form, setForm] = useState({
    fullName: '',
    email: '',
    username: '',
    password: '',
    confirmPassword: '',
  })

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault()

    if (form.password !== form.confirmPassword) {
      toast.error(t('auth.register.passwordMismatch'))
      return
    }

    if (form.password.length < 6) {
      toast.error(t('auth.register.passwordTooShort'))
      return
    }

    setLoading(true)

    try {
      const data = await authService.register({
        email: form.email,
        username: form.username,
        fullName: form.fullName,
        password: form.password,
      })

      setAuth(data.user, data.access_token, data.refresh_token)
      toast.success(t('auth.register.registerSuccess'))
      navigate('/app')
    } catch (error: any) {
      const msg = error.response?.data?.detail || t('errors.generic')
      toast.error(msg)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-900 relative overflow-hidden">
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute -top-1/2 -left-1/2 w-full h-full bg-gradient-to-br from-green-500/10 to-transparent rounded-full blur-3xl" />
        <div className="absolute -bottom-1/2 -right-1/2 w-full h-full bg-gradient-to-tl from-green-500/10 to-transparent rounded-full blur-3xl" />
      </div>

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="relative z-10 w-full max-w-md px-4"
      >
        <Card className="bg-slate-800 border-slate-700 overflow-hidden">
          <div className="relative bg-gradient-to-r from-green-500/20 to-green-600/20 p-8 text-center border-b border-slate-700">
            <motion.div
              initial={{ scale: 0.8, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              transition={{ delay: 0.2 }}
              className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-green-500/20 mb-4"
            >
              <UserPlus className="w-8 h-8 text-green-400" />
            </motion.div>
            <h1 className="text-3xl font-bold text-slate-100 mb-2">
              Tennis Tracking
            </h1>
            <p className="text-sm text-slate-400">
              {t('auth.register.title')}
            </p>
          </div>

          <div className="p-8">
            <form onSubmit={handleRegister} className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-2 text-slate-100">
                  {t('auth.register.name')}
                </label>
                <Input
                  type="text"
                  value={form.fullName}
                  onChange={(e) => setForm({ ...form, fullName: e.target.value })}
                  className="bg-slate-900 border-slate-700 text-slate-100 focus:border-green-500"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-2 text-slate-100">
                  Username
                </label>
                <Input
                  type="text"
                  value={form.username}
                  onChange={(e) => setForm({ ...form, username: e.target.value })}
                  className="bg-slate-900 border-slate-700 text-slate-100 focus:border-green-500"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-2 text-slate-100">
                  {t('auth.register.email')}
                </label>
                <Input
                  type="email"
                  value={form.email}
                  onChange={(e) => setForm({ ...form, email: e.target.value })}
                  className="bg-slate-900 border-slate-700 text-slate-100 focus:border-green-500"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-2 text-slate-100">
                  {t('auth.register.password')}
                </label>
                <Input
                  type="password"
                  value={form.password}
                  onChange={(e) => setForm({ ...form, password: e.target.value })}
                  className="bg-slate-900 border-slate-700 text-slate-100 focus:border-green-500"
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
                  value={form.confirmPassword}
                  onChange={(e) => setForm({ ...form, confirmPassword: e.target.value })}
                  className="bg-slate-900 border-slate-700 text-slate-100 focus:border-green-500"
                  required
                />
              </div>

              <Button
                type="submit"
                className="w-full bg-green-500 hover:bg-green-600 text-white font-medium h-11"
                disabled={loading}
              >
                {loading ? (
                  <motion.div
                    animate={{ rotate: 360 }}
                    transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
                    className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full"
                  />
                ) : (
                  t('auth.register.submit')
                )}
              </Button>
            </form>

            <p className="text-sm text-center text-slate-400 mt-6">
              {t('auth.register.haveAccount')}{' '}
              <Link to="/login" className="text-green-400 hover:text-green-300 font-medium">
                {t('auth.register.signIn')}
              </Link>
            </p>
          </div>
        </Card>
      </motion.div>
    </div>
  )
}

export default Register
