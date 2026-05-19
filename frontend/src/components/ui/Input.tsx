import React from 'react';
import { cn } from '../../utils/cn';

export interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  error?: boolean;
}

const Input = React.forwardRef<HTMLInputElement, InputProps>(({
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

export interface TextareaProps extends React.TextareaHTMLAttributes<HTMLTextAreaElement> {
  error?: boolean;
}

const Textarea = React.forwardRef<HTMLTextAreaElement, TextareaProps>(({
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

export interface SelectProps extends React.SelectHTMLAttributes<HTMLSelectElement> {
  error?: boolean;
}

const Select = React.forwardRef<HTMLSelectElement, SelectProps>(({
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

export interface FormGroupProps extends React.HTMLAttributes<HTMLDivElement> {
  children?: React.ReactNode;
}

const FormGroup = React.forwardRef<HTMLDivElement, FormGroupProps>(({
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

export interface LabelProps extends React.LabelHTMLAttributes<HTMLLabelElement> {
  required?: boolean;
}

const Label = React.forwardRef<HTMLLabelElement, LabelProps>(({
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

export interface ErrorMessageProps extends React.HTMLAttributes<HTMLParagraphElement> {
  children?: React.ReactNode;
}

const ErrorMessage = React.forwardRef<HTMLParagraphElement, ErrorMessageProps>(({
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
