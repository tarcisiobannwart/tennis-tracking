import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
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
        // Salvar token no localStorage
        localStorage.setItem('token', data.access_token);
        localStorage.setItem('user', JSON.stringify({ email: credentials.email, name: 'Test User' }));

        toast.success(t('auth.login.loginSuccess'));
        navigate('/');
      } else {
        toast.error(t('auth.login.invalidCredentials'));
      }
    } catch (error) {
      toast.error(t('errors.network'));
    } finally {
      setLoading(false);
    }
  };

  // Auto-login for development
  const handleQuickLogin = async () => {
    // Get test token directly
    try {
      const response = await fetch('http://localhost:8000/api/test-auth/test-token');
      const data = await response.json();

      localStorage.setItem('token', data.token);
      localStorage.setItem('user', JSON.stringify({ email: 'test@tennis.com', name: 'Test User' }));

      toast.success('Login rápido realizado!');
      navigate('/');
    } catch (error) {
      toast.error('Erro no login rápido');
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-background">
      <Card className="w-full max-w-md">
        <CardHeader>
          <CardTitle>{t('auth.login.title')}</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleLogin} className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-2 text-foreground">
                {t('auth.login.email')}
              </label>
              <Input
                type="email"
                value={credentials.email}
                onChange={(e) => setCredentials({ ...credentials, email: e.target.value })}
                placeholder="test@tennis.com"
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-2 text-foreground">
                {t('auth.login.password')}
              </label>
              <Input
                type="password"
                value={credentials.password}
                onChange={(e) => setCredentials({ ...credentials, password: e.target.value })}
                placeholder="test123"
                required
              />
            </div>
            <Button type="submit" className="w-full" disabled={loading}>
              {loading ? t('common.loading') : t('auth.login.submit')}
            </Button>
          </form>

          <div className="mt-6 pt-6 border-t">
            <p className="text-sm text-muted-foreground mb-3">
              Para desenvolvimento rápido:
            </p>
            <Button
              onClick={handleQuickLogin}
              variant="outline"
              className="w-full"
            >
              🚀 Login Rápido (Dev)
            </Button>
            <p className="text-xs text-muted-foreground mt-2">
              Usa: test@tennis.com / test123
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default Login;