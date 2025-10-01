import React from 'react';
import { cn } from '../../utils/cn';

const Input = React.forwardRef(({
  type = 'text',
  className = '',
  error = false,
  disabled = false,
  ...props
}, ref) => {
  return (
    <input
      type={type}
      ref={ref}
      className={cn(
        'form-input',
        {
          'border-red-300 focus:border-red-500 focus:ring-red-500': error,
          'bg-gray-100 cursor-not-allowed': disabled
        },
        className
      )}
      disabled={disabled}
      {...props}
    />
  );
});

Input.displayName = 'Input';

const Textarea = React.forwardRef(({
  className = '',
  error = false,
  disabled = false,
  ...props
}, ref) => {
  return (
    <textarea
      ref={ref}
      className={cn(
        'form-input form-textarea',
        {
          'border-red-300 focus:border-red-500 focus:ring-red-500': error,
          'bg-gray-100 cursor-not-allowed': disabled
        },
        className
      )}
      disabled={disabled}
      {...props}
    />
  );
});

Textarea.displayName = 'Textarea';

const Select = React.forwardRef(({
  children,
  className = '',
  error = false,
  disabled = false,
  ...props
}, ref) => {
  return (
    <select
      ref={ref}
      className={cn(
        'form-input form-select',
        {
          'border-red-300 focus:border-red-500 focus:ring-red-500': error,
          'bg-gray-100 cursor-not-allowed': disabled
        },
        className
      )}
      disabled={disabled}
      {...props}
    >
      {children}
    </select>
  );
});

Select.displayName = 'Select';

const FormGroup = React.forwardRef(({
  children,
  className = '',
  ...props
}, ref) => {
  return (
    <div
      ref={ref}
      className={cn('form-group', className)}
      {...props}
    >
      {children}
    </div>
  );
});

FormGroup.displayName = 'FormGroup';

const Label = React.forwardRef(({
  children,
  className = '',
  required = false,
  ...props
}, ref) => {
  return (
    <label
      ref={ref}
      className={cn('form-label', className)}
      {...props}
    >
      {children}
      {required && <span className="text-red-500 ml-1">*</span>}
    </label>
  );
});

Label.displayName = 'Label';

const ErrorMessage = React.forwardRef(({
  children,
  className = '',
  ...props
}, ref) => {
  if (!children) return null;
  
  return (
    <p
      ref={ref}
      className={cn('text-red-600 text-sm mt-1', className)}
      {...props}
    >
      {children}
    </p>
  );
});

ErrorMessage.displayName = 'ErrorMessage';

export { Input, Textarea, Select, FormGroup, Label, ErrorMessage };
export default Input;
