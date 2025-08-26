import { useState } from 'react';
import { Navigate } from 'react-router-dom';
import { useAuthStore } from '@/stores/authStore';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { AlertCircle } from 'lucide-react';
import CorsHelp from './CorsHelp';
import Logo from './Logo';

const LoginPage = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [showShake, setShowShake] = useState(false);

  const { login, isAuthenticated } = useAuthStore();

  if (isAuthenticated) {
    return <Navigate to="/" replace />;
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');

    console.log('Login form submitted');
    const result = await login(email, password);

    if (result.success) {
      console.log('Login successful, redirecting to dashboard');
      // The navigation will happen automatically due to the Navigate component
    } else {
      console.log('Login failed:', result.error);
      setError(result.error || 'Login failed');
      setShowShake(true);
      setTimeout(() => setShowShake(false), 600);
    }

    setIsLoading(false);
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-background relative overflow-hidden">
      {/* Animated Background */}
      <div className="absolute inset-0 bg-gradient-to-br from-background via-background to-primary/5" />
      
      {/* Floating Orbs */}
      <div className="absolute top-1/4 left-1/4 w-64 h-64 bg-primary/10 rounded-full blur-3xl neura-float" />
      <div className="absolute bottom-1/4 right-1/4 w-48 h-48 bg-accent/10 rounded-full blur-3xl neura-float" style={{ animationDelay: '-3s' }} />

      {/* Login Form */}
      <div className={`neura-panel p-8 w-full max-w-md mx-4 neura-glow transition-neura ${showShake ? 'animate-[shake_0.6s_ease-in-out]' : ''}`}>
        <div className="text-center mb-8">
          <div className="flex justify-center mb-4">
            <Logo size="md" showText={false} />
          </div>
          <h1 className="text-4xl font-extrabold text-center tracking-wide bg-gradient-to-r from-cyan-400 via-blue-500 to-indigo-500 bg-clip-text text-transparent drop-shadow-md">
          NeuraCity
          </h1>
          <p className="text-muted-foreground mt-2">Admin Dashboard</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="space-y-2">
            <Label htmlFor="email" className="text-foreground">Email</Label>
            <Input
              id="email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="neura-glass border-primary/30 focus:border-primary focus:ring-1 focus:ring-primary"
              placeholder="agent@neuracity.ai"
              required
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="password" className="text-foreground">Password</Label>
            <Input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="neura-glass border-primary/30 focus:border-primary focus:ring-1 focus:ring-primary"
              placeholder="••••••••"
              required
            />
          </div>

          {error && (
            <div className="space-y-3">
              <div className="flex items-center gap-2 text-destructive text-sm neura-panel p-3 border-destructive/30">
                <AlertCircle className="h-4 w-4" />
                <span>{error}</span>
              </div>
              
              {error.includes('CORS') && <CorsHelp />}
            </div>
          )}

          <Button
            type="submit"
            disabled={isLoading}
            className="w-full bg-gradient-primary hover:shadow-neura-intense transition-neura text-primary-foreground font-medium"
          >
            {isLoading ? (
              <div className="flex items-center gap-2">
                <div className="w-4 h-4 border-2 border-current border-t-transparent rounded-full animate-spin" />
                Authenticating...
              </div>
            ) : (
              'Access Command Center'
            )}
          </Button>
        </form>

        <div className="mt-6 text-center text-xs text-muted-foreground">
          <p>Authorized Personnel Only</p>
          <p className="mt-1">Classification Level: RESTRICTED</p>
        </div>
      </div>
    </div>
  );
};

export default LoginPage;