import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { motion } from 'framer-motion';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { LogIn } from 'lucide-react';
import toast from 'react-hot-toast';

const Login = () => {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [credentials, setCredentials] = useState({
    email: 'test@tennis.com',
    password: 'test123'
  });

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    try {
      const response = await fetch('http://localhost:8000/api/test-auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(credentials),
      });

      if (response.ok) {
        const data = await response.json();
        localStorage.setItem('token', data.access_token);
        localStorage.setItem('user', JSON.stringify({ email: credentials.email, name: 'Test User' }));

        toast.success(t('auth.login.loginSuccess'));

        // Verificar se já completou onboarding
        const onboardingCompleted = localStorage.getItem('onboardingCompleted');
        if (!onboardingCompleted) {
          navigate('/onboarding');
        } else {
          navigate('/');
        }
      } else {
        toast.error(t('auth.login.invalidCredentials'));
      }
    } catch (error) {
      toast.error(t('errors.network'));
    } finally {
      setLoading(false);
    }
  };

  const handleQuickLogin = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/test-auth/test-token');
      const data = await response.json();

      localStorage.setItem('token', data.token);
      localStorage.setItem('user', JSON.stringify({ email: 'test@tennis.com', name: 'Test User' }));

      toast.success('Login rápido realizado!');

      // Verificar se já completou onboarding
      const onboardingCompleted = localStorage.getItem('onboardingCompleted');
      if (!onboardingCompleted) {
        navigate('/onboarding');
      } else {
        navigate('/');
      }
    } catch (error) {
      toast.error('Erro no login rápido');
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-900 relative overflow-hidden">
      {/* Background decorativo */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute -top-1/2 -left-1/2 w-full h-full bg-gradient-to-br from-blue-500/10 to-transparent rounded-full blur-3xl" />
        <div className="absolute -bottom-1/2 -right-1/2 w-full h-full bg-gradient-to-tl from-blue-500/10 to-transparent rounded-full blur-3xl" />
      </div>

      {/* Card de login */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="relative z-10 w-full max-w-md px-4"
      >
        <Card className="bg-slate-800 border-slate-700 overflow-hidden">
          {/* Header com gradiente */}
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
              Análise profissional de partidas
            </p>
          </div>

          {/* Formulário */}
          <div className="p-8">
            <form onSubmit={handleLogin} className="space-y-5">
              <div>
                <label className="block text-sm font-medium mb-2 text-slate-100">
                  {t('auth.login.email')}
                </label>
                <Input
                  type="email"
                  value={credentials.email}
                  onChange={(e) => setCredentials({ ...credentials, email: e.target.value })}
                  placeholder="seu@email.com"
                  className="bg-slate-900 border-slate-700 text-slate-100 focus:border-blue-500"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-2 text-slate-100">
                  {t('auth.login.password')}
                </label>
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
                  >
                    ⏳
                  </motion.div>
                ) : (
                  t('auth.login.submit')
                )}
              </Button>
            </form>

            {/* Divisor */}
            <div className="relative my-6">
              <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t border-slate-700" />
              </div>
              <div className="relative flex justify-center text-xs uppercase">
                <span className="bg-slate-800 px-2 text-slate-400">
                  Desenvolvimento
                </span>
              </div>
            </div>

            {/* Login rápido */}
            <Button
              onClick={handleQuickLogin}
              variant="outline"
              className="w-full border-slate-700 text-slate-400 hover:bg-slate-900 hover:text-slate-100"
            >
              🚀 Login Rápido (Dev)
            </Button>
            <p className="text-xs text-center text-slate-500 mt-3">
              Credenciais: test@tennis.com / test123
            </p>
          </div>
        </Card>

        {/* Footer */}
        <motion.p
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.8 }}
          className="text-center text-xs text-slate-500 mt-6"
        >
          © 2024 Tennis Tracking. Todos os direitos reservados.
        </motion.p>
      </motion.div>
    </div>
  );
};

export default Login;