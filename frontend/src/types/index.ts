/**
 * Shared TypeScript interfaces for the Postventa System frontend.
 * Following Audit Expert standards for a clean and typed codebase.
 */

export type UserRole = 
  | 'admin' 
  | 'management' 
  | 'technical_service' 
  | 'quality' 
  | 'supervisor' 
  | 'analyst' 
  | 'customer_service' 
  | 'provider';

export interface User {
  id: number;
  username: string;
  email: string;
  first_name?: string;
  last_name?: string;
  role: UserRole;
  is_active: boolean;
  is_staff: boolean;
  last_login?: string;
}

export interface Incident {
  id: number;
  code: string;
  estado: string;
  cliente: string;
  cliente_rut?: string;
  obra?: string;
  direccion_cliente?: string;
  comuna?: string;
  ciudad?: string;
  salesperson?: string;
  responsable?: string | { id: number; name: string };
  categoria?: string;
  subcategoria?: string;
  created_at: string;
  updated_at: string;
}

export interface VisitReport {
  id: number;
  order_number: string;
  related_incident: number | Incident;
  status: 'created' | 'approved' | 'closed' | 'completed';
  visit_date: string;
  client_name: string;
  project_name: string;
  categoria?: string;
  subcategoria?: string;
  escalated_to_quality: boolean;
  pdf_path?: string;
  download_url?: string;
  has_document: boolean;
  technician_id?: number;
}

export interface ApiResponse<T> {
  results: T[];
  count: number;
  next?: string | null;
  previous?: string | null;
}
