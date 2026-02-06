import { useState } from 'react'
import { useTranslation } from 'react-i18next'
import { Card } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { User, Mail, Phone, Globe, Save } from 'lucide-react'
import toast from 'react-hot-toast'
import { useAuthStore } from '@/stores/authStore'
import { userService } from '@/services/userService'

const Profile = () => {
  const { t } = useTranslation()
  const { user, setUser } = useAuthStore()
  const [loading, setLoading] = useState(false)
  const [form, setForm] = useState({
    fullName: user?.fullName || '',
    phone: user?.phone || '',
    country: user?.country || '',
    language: user?.language || 'pt-BR',
  })

  const [passwordForm, setPasswordForm] = useState({
    currentPassword: '',
    newPassword: '',
    confirmPassword: '',
  })
  const [passwordLoading, setPasswordLoading] = useState(false)

  const handleUpdateProfile = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    try {
      const updated = await userService.updateMe(form)
      setUser(updated)
      toast.success(t('profile.profileUpdated'))
    } catch {
      toast.error(t('errors.generic'))
    } finally {
      setLoading(false)
    }
  }

  const handleChangePassword = async (e: React.FormEvent) => {
    e.preventDefault()
    if (passwordForm.newPassword !== passwordForm.confirmPassword) {
      toast.error(t('auth.register.passwordMismatch'))
      return
    }
    setPasswordLoading(true)
    try {
      await userService.changePassword(passwordForm.currentPassword, passwordForm.newPassword)
      toast.success(t('profile.passwordChanged'))
      setPasswordForm({ currentPassword: '', newPassword: '', confirmPassword: '' })
    } catch (error: any) {
      toast.error(error.response?.data?.detail || t('errors.generic'))
    } finally {
      setPasswordLoading(false)
    }
  }

  return (
    <div className="p-6 max-w-4xl mx-auto space-y-6">
      <h1 className="text-2xl font-bold text-slate-100">{t('profile.title')}</h1>

      {/* Profile Info */}
      <Card className="bg-slate-800 border-slate-700 p-6">
        <h2 className="text-lg font-semibold text-slate-100 mb-4 flex items-center gap-2">
          <User className="w-5 h-5" />
          {t('profile.personalInfo')}
        </h2>
        <form onSubmit={handleUpdateProfile} className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium mb-1 text-slate-300">
                {t('auth.register.name')}
              </label>
              <Input
                value={form.fullName}
                onChange={(e) => setForm({ ...form, fullName: e.target.value })}
                className="bg-slate-900 border-slate-700 text-slate-100"
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1 text-slate-300">
                <Mail className="w-3 h-3 inline mr-1" />
                {t('auth.register.email')}
              </label>
              <Input value={user?.email || ''} disabled className="bg-slate-900/50 border-slate-700 text-slate-500" />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1 text-slate-300">
                <Phone className="w-3 h-3 inline mr-1" />
                Telefone
              </label>
              <Input
                value={form.phone}
                onChange={(e) => setForm({ ...form, phone: e.target.value })}
                className="bg-slate-900 border-slate-700 text-slate-100"
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1 text-slate-300">
                <Globe className="w-3 h-3 inline mr-1" />
                Pais
              </label>
              <Input
                value={form.country}
                onChange={(e) => setForm({ ...form, country: e.target.value })}
                className="bg-slate-900 border-slate-700 text-slate-100"
              />
            </div>
          </div>
          <Button type="submit" disabled={loading} className="bg-blue-500 hover:bg-blue-600">
            <Save className="w-4 h-4 mr-2" />
            {t('profile.updateProfile')}
          </Button>
        </form>
      </Card>

      {/* Change Password */}
      <Card className="bg-slate-800 border-slate-700 p-6">
        <h2 className="text-lg font-semibold text-slate-100 mb-4">
          {t('profile.changePassword')}
        </h2>
        <form onSubmit={handleChangePassword} className="space-y-4 max-w-md">
          <div>
            <label className="block text-sm font-medium mb-1 text-slate-300">
              {t('profile.currentPassword')}
            </label>
            <Input
              type="password"
              value={passwordForm.currentPassword}
              onChange={(e) => setPasswordForm({ ...passwordForm, currentPassword: e.target.value })}
              className="bg-slate-900 border-slate-700 text-slate-100"
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1 text-slate-300">
              {t('profile.newPassword')}
            </label>
            <Input
              type="password"
              value={passwordForm.newPassword}
              onChange={(e) => setPasswordForm({ ...passwordForm, newPassword: e.target.value })}
              className="bg-slate-900 border-slate-700 text-slate-100"
              required
              minLength={6}
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1 text-slate-300">
              {t('profile.confirmNewPassword')}
            </label>
            <Input
              type="password"
              value={passwordForm.confirmPassword}
              onChange={(e) => setPasswordForm({ ...passwordForm, confirmPassword: e.target.value })}
              className="bg-slate-900 border-slate-700 text-slate-100"
              required
            />
          </div>
          <Button type="submit" disabled={passwordLoading} variant="outline" className="border-slate-600">
            {t('profile.changePassword')}
          </Button>
        </form>
      </Card>
    </div>
  )
}

export default Profile
