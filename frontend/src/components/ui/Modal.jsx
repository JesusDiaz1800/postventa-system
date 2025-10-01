import React, { useEffect } from 'react';
import { cn } from '../../utils/cn';

const Modal = ({
  isOpen,
  onClose,
  children,
  size = 'md',
  className = '',
  closeOnOverlayClick = true,
  closeOnEscape = true
}) => {
  useEffect(() => {
    if (!isOpen) return;
    
    const handleEscape = (e) => {
      if (e.key === 'Escape' && closeOnEscape) {
        onClose();
      }
    };
    
    document.addEventListener('keydown', handleEscape);
    document.body.style.overflow = 'hidden';
    
    return () => {
      document.removeEventListener('keydown', handleEscape);
      document.body.style.overflow = 'unset';
    };
  }, [isOpen, onClose, closeOnEscape]);
  
  if (!isOpen) return null;
  
  const sizes = {
    sm: 'max-w-md',
    md: 'max-w-lg',
    lg: 'max-w-2xl',
    xl: 'max-w-4xl',
    full: 'max-w-full mx-4'
  };
  
  return (
    <div className="modal-overlay" onClick={closeOnOverlayClick ? onClose : undefined}>
      <div
        className={cn(
          'modal',
          sizes[size],
          className
        )}
        onClick={(e) => e.stopPropagation()}
      >
        {children}
      </div>
    </div>
  );
};

const ModalHeader = React.forwardRef(({
  children,
  className = '',
  ...props
}, ref) => {
  return (
    <div
      ref={ref}
      className={cn('flex items-center justify-between p-6 border-b border-gray-200', className)}
      {...props}
    >
      {children}
    </div>
  );
});

ModalHeader.displayName = 'ModalHeader';

const ModalBody = React.forwardRef(({
  children,
  className = '',
  ...props
}, ref) => {
  return (
    <div
      ref={ref}
      className={cn('p-6', className)}
      {...props}
    >
      {children}
    </div>
  );
});

ModalBody.displayName = 'ModalBody';

const ModalFooter = React.forwardRef(({
  children,
  className = '',
  ...props
}, ref) => {
  return (
    <div
      ref={ref}
      className={cn('flex items-center justify-end gap-3 p-6 border-t border-gray-200', className)}
      {...props}
    >
      {children}
    </div>
  );
});

ModalFooter.displayName = 'ModalFooter';

const ModalTitle = React.forwardRef(({
  children,
  className = '',
  ...props
}, ref) => {
  return (
    <h3
      ref={ref}
      className={cn('text-lg font-semibold text-gray-900', className)}
      {...props}
    >
      {children}
    </h3>
  );
});

ModalTitle.displayName = 'ModalTitle';

const ModalCloseButton = React.forwardRef(({
  onClick,
  className = '',
  ...props
}, ref) => {
  return (
    <button
      ref={ref}
      onClick={onClick}
      className={cn(
        'text-gray-400 hover:text-gray-600 transition-colors',
        className
      )}
      {...props}
    >
      <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
      </svg>
    </button>
  );
});

ModalCloseButton.displayName = 'ModalCloseButton';

export { Modal, ModalHeader, ModalBody, ModalFooter, ModalTitle, ModalCloseButton };
export default Modal;
