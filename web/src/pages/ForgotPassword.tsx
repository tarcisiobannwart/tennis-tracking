import { useState } from 'react'
import { Link } from 'react-router-dom'
import { useTranslation } from 'react-i18next'
import { motion } from 'framer-motion'
import { Card } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Mail, ArrowLeft } from 'lucide-react'
import toast from 'react-hot-toast'
import { authService } from '@/services/authService'

const ForgotPassword = () => {
  const { t } = useTranslation()
  const [loading, setLoading] = useState(false)
  const [sent, setSent] = useState(false)
  const [email, setEmail] = useState('')

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)

    try {
      await authService.forgotPassword(email)
      setSent(true)
      toast.success(t('auth.forgotPassword.emailSent'))
    } catch {
      toast.success(t('auth.forgotPassword.emailSent'))
      setSent(true)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-900 relative overflow-hidden">
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute -top-1/2 -left-1/2 w-full h-full bg-gradient-to-br from-amber-500/10 to-transparent rounded-full blur-3xl" />
      </div>

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="relative z-10 w-full max-w-md px-4"
      >
        <Card className="bg-slate-800 border-slate-700 overflow-hidden">
          <div className="relative bg-gradient-to-r from-amber-500/20 to-amber-600/20 p-8 text-center border-b border-slate-700">
            <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-amber-500/20 mb-4">
              <Mail className="w-8 h-8 text-amber-400" />
            </div>
            <h1 className="text-2xl font-bold text-slate-100 mb-2">
              {t('auth.forgotPassword.title')}
            </h1>
            <p className="text-sm text-slate-400">
              {t('auth.forgotPassword.description')}
            </p>
          </div>

          <div className="p-8">
            {sent ? (
              <div className="text-center">
                <p className="text-slate-300 mb-4">
                  {t('auth.forgotPassword.checkEmail')}
                </p>
                <Link to="/login">
                  <Button variant="outline" className="border-slate-700 text-slate-300">
                    <ArrowLeft className="w-4 h-4 mr-2" />
                    {t('auth.forgotPassword.backToLogin')}
                  </Button>
                </Link>
              </div>
            ) : (
              <form onSubmit={handleSubmit} className="space-y-5">
                <div>
                  <label className="block text-sm font-medium mb-2 text-slate-100">
                    {t('auth.login.email')}
                  </label>
                  <Input
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="seu@email.com"
                    className="bg-slate-900 border-slate-700 text-slate-100"
                    required
                  />
                </div>

                <Button
                  type="submit"
                  className="w-full bg-amber-500 hover:bg-amber-600 text-white font-medium h-11"
                  disabled={loading}
                >
                  {loading ? (
                    <motion.div
                      animate={{ rotate: 360 }}
                      transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
                      className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full"
                    />
                  ) : (
                    t('auth.forgotPassword.submit')
                  )}
                </Button>

                <div className="text-center">
                  <Link to="/login" className="text-sm text-slate-400 hover:text-slate-300">
                    <ArrowLeft className="w-3 h-3 inline mr-1" />
                    {t('auth.forgotPassword.backToLogin')}
                  </Link>
                </div>
              </form>
            )}
          </div>
        </Card>
      </motion.div>
    </div>
  )
}

export default ForgotPassword
