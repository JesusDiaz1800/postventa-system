/**
 * Configuración de marca para el Sistema de Gestión de Incidencias Postventa
 */

export const brandConfig = {
  // Información de la empresa
  company: {
    name: 'Control de Calidad',
    fullName: 'Sistema de Gestión de Incidencias Postventa',
    description: 'Control de Calidad y Postventa',
    version: '3.0.0',
    year: '2024',
  },

  // Colores de marca
  colors: {
    primary: {
      50: '#eff6ff',
      100: '#dbeafe',
      200: '#bfdbfe',
      300: '#93c5fd',
      400: '#60a5fa',
      500: '#3b82f6',
      600: '#2563eb',
      700: '#1d4ed8',
      800: '#1e40af',
      900: '#1e3a8a',
    },
    secondary: {
      50: '#f0f9ff',
      100: '#e0f2fe',
      200: '#bae6fd',
      300: '#7dd3fc',
      400: '#38bdf8',
      500: '#0ea5e9',
      600: '#0284c7',
      700: '#0369a1',
      800: '#075985',
      900: '#0c4a6e',
    },
    accent: {
      50: '#faf5ff',
      100: '#f3e8ff',
      200: '#e9d5ff',
      300: '#d8b4fe',
      400: '#c084fc',
      500: '#a855f7',
      600: '#9333ea',
      700: '#7c3aed',
      800: '#6b21a8',
      900: '#581c87',
    },
  },

  // Gradientes de marca
  gradients: {
    primary: 'linear-gradient(135deg, #60A5FA 0%, #06B6D4 50%, #8B5CF6 100%)',
    secondary: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
    accent: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)',
  },

  // Configuración del logo
  logo: {
    width: '192px', // 48 * 4
    height: '32px', // 8 * 4
    aspectRatio: '6:1',
    variants: ['default', 'white'],
  },

  // Configuración de la interfaz
  ui: {
    borderRadius: '0.5rem',
    shadow: '0 4px 14px 0 rgba(96, 165, 250, 0.15)',
    transition: 'all 0.2s ease-in-out',
  },

  // Configuración de roles
  roles: {
    administrador: {
      name: 'Administrador',
      color: 'purple',
      permissions: ['all'],
    },
    supervisor: {
      name: 'Supervisor',
      color: 'blue',
      permissions: ['incidents', 'reports', 'users', 'workflows'],
    },
    analyst: {
      name: 'Analista Técnico',
      color: 'green',
      permissions: ['incidents', 'ai_analysis', 'documents'],
    },
    customer_service: {
      name: 'Atención al Cliente',
      color: 'orange',
      permissions: ['incidents', 'documents'],
    },
    provider: {
      name: 'Proveedor',
      color: 'gray',
      permissions: ['incidents_read'],
    },
  },

  // Configuración de estados de incidencias
  incidentStatus: {
    abierto: {
      name: 'Abierto',
      color: 'red',
      icon: 'AlertCircle',
    },
    triage: {
      name: 'Triage',
      color: 'yellow',
      icon: 'Clock',
    },
    inspeccion: {
      name: 'Inspección',
      color: 'blue',
      icon: 'Search',
    },
    laboratorio: {
      name: 'Laboratorio',
      color: 'purple',
      icon: 'FlaskConical',
    },
    propuesta: {
      name: 'Propuesta',
      color: 'indigo',
      icon: 'Lightbulb',
    },
    en_progreso: {
      name: 'En Progreso',
      color: 'orange',
      icon: 'Play',
    },
    resuelto: {
      name: 'Resuelto',
      color: 'green',
      icon: 'CheckCircle',
    },
    cerrado: {
      name: 'Cerrado',
      color: 'gray',
      icon: 'Archive',
    },
  },

  // Configuración de prioridades
  priorities: {
    baja: {
      name: 'Baja',
      color: 'green',
      icon: 'ArrowDown',
    },
    media: {
      name: 'Media',
      color: 'yellow',
      icon: 'Minus',
    },
    alta: {
      name: 'Alta',
      color: 'orange',
      icon: 'ArrowUp',
    },
    critica: {
      name: 'Crítica',
      color: 'red',
      icon: 'AlertTriangle',
    },
  },

  // Configuración de categorías
  categories: {
    defecto_fabricacion: {
      name: 'Defecto de Fabricación',
      color: 'red',
      icon: 'AlertTriangle',
    },
    daño_transporte: {
      name: 'Daño en Transporte',
      color: 'orange',
      icon: 'Truck',
    },
    calidad: {
      name: 'Calidad',
      color: 'blue',
      icon: 'Award',
    },
    embalaje: {
      name: 'Embalaje',
      color: 'purple',
      icon: 'Package',
    },
    etiquetado: {
      name: 'Etiquetado',
      color: 'green',
      icon: 'Tag',
    },
    tuberia_pp_rct: {
      name: 'Tubería PP-RCT',
      color: 'indigo',
      icon: 'Pipe',
    },
    llave_bola: {
      name: 'Llave de Bola',
      color: 'pink',
      icon: 'Wrench',
    },
    accesorio: {
      name: 'Accesorio',
      color: 'teal',
      icon: 'Settings',
    },
  },

  // Configuración de IA
  ai: {
    providers: {
      openai: {
        name: 'OpenAI',
        color: 'green',
        icon: 'Brain',
      },
      anthropic: {
        name: 'Anthropic',
        color: 'orange',
        icon: 'Bot',
      },
      google: {
        name: 'Google',
        color: 'blue',
        icon: 'Search',
      },
      local: {
        name: 'Local',
        color: 'gray',
        icon: 'Cpu',
      },
    },
    quotaMessages: {
      exhausted: 'IA no disponible por límite de créditos. Intente nuevamente después de la hora de reinicio configurada.',
      fallback: 'Usando modelo local (menor precisión)',
      consent: 'Consentimiento requerido para envío a proveedores externos',
    },
  },

  // Configuración de documentos
  documents: {
    templates: {
      cliente_informe: {
        name: 'Informe para Cliente',
        description: 'Informe con tono diplomático y sutil',
        icon: 'FileText',
      },
      proveedor_carta: {
        name: 'Carta Técnica para Proveedor',
        description: 'Carta técnica y directa con petición de acciones',
        icon: 'Mail',
      },
      lab_report: {
        name: 'Reporte de Laboratorio',
        description: 'Reporte técnico con conclusiones científicas',
        icon: 'FlaskConical',
      },
    },
  },

  // Configuración de workflows
  workflows: {
    default: {
      name: 'Workflow por Defecto',
      description: 'Workflow estándar para incidencias',
    },
    defecto_fabricacion: {
      name: 'Workflow Defecto de Fabricación',
      description: 'Workflow específico para defectos de fabricación',
    },
    llave_bola: {
      name: 'Workflow Llave de Bola',
      description: 'Workflow específico para llaves de bola',
    },
  },

  // Configuración de notificaciones
  notifications: {
    types: {
      success: {
        color: 'green',
        icon: 'CheckCircle',
      },
      error: {
        color: 'red',
        icon: 'XCircle',
      },
      warning: {
        color: 'yellow',
        icon: 'AlertTriangle',
      },
      info: {
        color: 'blue',
        icon: 'Info',
      },
    },
  },

  // Configuración de la aplicación
  app: {
    title: 'Sistema de Gestión de Incidencias Postventa',
    description: 'Control de Calidad y Postventa',
    keywords: ['incidencias', 'postventa', 'calidad', 'gestión'],
    author: 'Control de Calidad',
    theme: 'light',
    language: 'es',
    timezone: 'America/Santiago',
  },

  // Configuración de la API
  api: {
    // Use relative base URL by default so Vite dev proxy handles backend calls
    baseUrl: (import.meta as any).env?.VITE_API_URL || '/api',
    timeout: 30000,
    retries: 3,
  },

  // Configuración de almacenamiento
  storage: {
    sharedFolder: '\\\\192.168.1.161\\Y:\\CONTROL DE CALIDAD\\postventa',
    maxFileSize: 10 * 1024 * 1024, // 10MB
    allowedTypes: ['image/jpeg', 'image/png', 'image/gif', 'application/pdf', 'application/msword'],
  },

  // Configuración de la base de datos
  database: {
    host: '192.168.1.161',
    instance: 'SQLEXPRESS',
    name: 'postventa_system',
  },
};

export default brandConfig;
