import myLogo from '/logo.svg';

interface LogoProps {
  size?: 'sm' | 'md' | 'lg';
  showText?: boolean;
  className?: string;
}

const Logo = ({ size = 'md', showText = true, className = '' }: LogoProps) => {
  const sizeClasses = {
    sm: 'h-12 w-12',
    md: 'h-40 w-40',
    lg: 'h-40 w-40',
  };

  const textSizeClasses = {
    sm: 'text-2xl',
    md: 'text-4xl',
    lg: 'text-5xl',
  };

  return (
    <div className={`flex items-center gap-3 ${className}`}>
      <img
        src={myLogo}
        alt="Logo"
        className={`${sizeClasses[size]} object-contain`}
      />
      {showText && (
        <span
          className={`${textSizeClasses[size]} font-bold text-transparent bg-clip-text`}
          style={{ backgroundImage: 'var(--gradient-primary)' }}
        >
          NeuraCity
        </span>
      )}
    </div>
  );
};

export default Logo;