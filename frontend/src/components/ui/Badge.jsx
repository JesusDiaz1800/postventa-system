import React from 'react';
import { cn } from '../../utils/cn';

const Badge = React.forwardRef(({
  children,
  variant = 'gray',
  size = 'md',
  className = '',
  ...props
}, ref) => {
  const variants = {
    primary: 'badge-primary',
    success: 'badge-success',
    warning: 'badge-warning',
    danger: 'badge-danger',
    gray: 'badge-gray'
  };
  
  const sizes = {
    sm: 'text-xs px-2 py-1',
    md: 'text-xs px-3 py-1',
    lg: 'text-sm px-4 py-2'
  };
  
  return (
    <span
      ref={ref}
      className={cn(
        'badge',
        variants[variant],
        sizes[size],
        className
      )}
      {...props}
    >
      {children}
    </span>
  );
});

Badge.displayName = 'Badge';

export { Badge };
export default Badge;
