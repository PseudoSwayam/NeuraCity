import { Shield, Zap } from 'lucide-react';

interface LogoProps {
  size?: 'sm' | 'md' | 'lg';
  showText?: boolean;
  className?: string;
}

const Logo = ({ size = 'md', showText = true, className = '' }: LogoProps) => {
  const sizeClasses = {
    sm: 'h-6 w-6',
    md: 'h-12 w-12', 
    lg: 'h-16 w-16'
  };

  const zapSizeClasses = {
    sm: 'h-3 w-3',
    md: 'h-6 w-6',
    lg: 'h-8 w-8'
  };

  const textSizeClasses = {
    sm: 'text-lg',
    md: 'text-3xl',
    lg: 'text-4xl'
  };

  return (
    <div className={`flex items-center gap-3 ${className}`}>
      <div className="relative">
        {/* Replace this SVG with your custom logo */}
        <Shield className={`${sizeClasses[size]} text-primary neura-pulse`} />
        <Zap className={`${zapSizeClasses[size]} text-accent absolute -top-1 -right-1`} />
      </div>
      {showText && (
        <span className={`${textSizeClasses[size]} font-bold text-transparent bg-clip-text`} 
              style={{ backgroundImage: 'var(--gradient-primary)' }}>
          NeuraCity
        </span>
      )}
    </div>
  );
};

export default Logo;