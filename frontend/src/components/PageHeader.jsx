import React from 'react';
import { Logo } from './Logo';

const PageHeader = ({ 
  title, 
  subtitle, 
  icon: Icon, 
  children, 
  showLogo = true,
  className = "" 
}) => {
  return (
    <div className={`relative ${className}`}>
      {/* Background gradient */}
      <div className="absolute inset-0 bg-gradient-to-r from-blue-600/10 via-purple-600/10 to-indigo-600/10 rounded-3xl blur-3xl"></div>
      
      {/* Main content */}
      <div className="relative bg-white/90 backdrop-blur-sm rounded-2xl p-8 border border-white/20 shadow-xl">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-6">
            {/* Logo */}
            {showLogo && (
              <div className="flex-shrink-0">
                <div className="h-16 w-64">
                  <Logo className="h-full w-full" />
                </div>
              </div>
            )}
            
            {/* Title section */}
            <div className="flex items-center space-x-4">
              {Icon && (
                <div className="p-3 bg-gradient-to-r from-blue-500 to-purple-600 rounded-xl shadow-lg">
                  <Icon className="h-8 w-8 text-white" />
                </div>
              )}
              <div>
                <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-600 via-purple-600 to-indigo-600 bg-clip-text text-transparent">
                  {title}
                </h1>
                {subtitle && (
                  <p className="mt-2 text-lg text-gray-600">
                    {subtitle}
                  </p>
                )}
              </div>
            </div>
          </div>
          
          {/* Right side content */}
          {children && (
            <div className="flex items-center space-x-4">
              {children}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default PageHeader;
