# NOTA IMPORTANTE

Todos los documentos adjuntos y generados se guardan en la carpeta `documentos/` en la raíz del proyecto. Esta carpeta debe tener permisos de lectura/escritura para todos los usuarios del escritorio remoto.

Para migrar a SQL Server empresarial, revisa los modelos y migraciones para compatibilidad total (evita ArrayField, usa ManyToManyField para listas, revisa tipos de datos).
# 📋 DOCUMENTACIÓN COMPLETA DEL PROYECTO POSTVENTA-SYSTEM

## 🎯 **INFORMACIÓN GENERAL DEL PROYECTO**

### **📌 Descripción del Sistema**
Sistema de gestión de postventa para empresas, enfocado en la gestión de incidencias, reportes de calidad, visitas técnicas, y trazabilidad completa de documentos. El sistema permite la escalación de incidencias entre diferentes departamentos y la generación de reportes profesionales.

### **🏗️ Arquitectura del Sistema**
- **Frontend:** React + TypeScript + Vite + Tailwind CSS
- **Backend:** Django + Django REST Framework + SQL Server
- **Base de Datos:** SQL Server (configuración empresarial)
- **Autenticación:** JWT (JSON Web Tokens)
- **Archivos:** Sistema de carpetas compartidas
- **Deployment:** Docker + Nginx

## 📁 **ESTRUCTURA COMPLETA DEL PROYECTO**

```
postventa-system/
├── backend/                          # Backend Django
│   ├── apps/                         # Aplicaciones Django
│   │   ├── incidents/               # Gestión de incidencias
│   │   ├── documents/               # Gestión de documentos
│   │   ├── users/                   # Gestión de usuarios
│   │   └── reports/                 # Generación de reportes
│   ├── postventa_system/            # Configuración principal
│   │   ├── settings.py             # Configuración desarrollo
│   │   ├── settings-sqlserver.py    # Configuración SQL Server
│   │   ├── urls.py                  # URLs principales
│   │   └── wsgi.py                  # WSGI configuration
│   ├── documents/                   # Carpetas de documentos
│   │   ├── visit_reports/          # Reportes de visita
│   │   ├── quality_reports/        # Reportes de calidad
│   │   ├── supplier_reports/       # Reportes de proveedor
│   │   ├── lab_reports/            # Reportes de laboratorio
│   │   ├── incident_attachments/   # Adjuntos de incidencias
│   │   ├── shared/                 # Documentos compartidos
│   │   └── real_files/             # Archivos reales
│   ├── static/                     # Archivos estáticos
│   ├── templates/                  # Plantillas de documentos
│   └── requirements.txt            # Dependencias Python
├── frontend/                        # Frontend React
│   ├── src/                        # Código fuente
│   │   ├── components/             # Componentes React
│   │   ├── pages/                  # Páginas de la aplicación
│   │   ├── hooks/                  # Custom hooks
│   │   ├── services/               # Servicios API
│   │   ├── contexts/               # Contextos React
│   │   └── utils/                  # Utilidades
│   ├── public/                     # Archivos públicos
│   ├── package.json                # Dependencias Node.js
│   └── vite.config.ts              # Configuración Vite
├── nginx/                          # Configuración Nginx
├── scripts/                        # Scripts de deployment
├── docker-compose.yml              # Configuración Docker
└── shared/                         # Carpeta compartida
```

## 🔧 **CONFIGURACIONES Y ARCHIVOS IMPORTANTES**

### **📋 Archivos de Configuración Backend**

#### **1. settings-sqlserver.py (Configuración SQL Server)**
```python
# Configuración para SQL Server
DATABASES = {
    'default': {
        'ENGINE': 'mssql',
        'NAME': 'postventa_db',
        'USER': 'sa',
        'PASSWORD': 'YourPassword',
        'HOST': 'localhost',
        'PORT': '1433',
        'OPTIONS': {
            'driver': 'ODBC Driver 17 for SQL Server',
        },
    }
}

# Configuración de carpetas compartidas
SHARED_DOCUMENTS_PATH = 'C:/Users/Jesus Diaz/postventa-system/backend/documents'
```

#### **2. urls.py (Rutas de la API)**
```python
# Rutas principales de documentos
urlpatterns = [
    path('api/documents/', include('apps.documents.urls')),
    path('api/incidents/', include('apps.incidents.urls')),
    path('api/users/', include('apps.users.urls')),
    path('api/reports/', include('apps.reports.urls')),
]
```

### **📋 Archivos de Configuración Frontend**

#### **1. package.json**
```json
{
  "name": "postventa-frontend",
  "version": "1.0.0",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.8.0",
    "@tanstack/react-query": "^4.24.0",
    "@heroicons/react": "^2.0.0",
    "tailwindcss": "^3.2.0"
  }
}
```

#### **2. vite.config.ts**
```typescript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true
      }
    }
  }
})
```

### **📋 Archivos de Configuración Docker**

#### **1. docker-compose.yml**
```yaml
version: '3.8'
services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    volumes:
      - ./backend:/app
      - ./shared:/app/shared
    environment:
      - DEBUG=1
      - DATABASE_URL=sqlserver://sa:password@sqlserver:1433/postventa_db
  
  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    volumes:
      - ./frontend:/app
    depends_on:
      - backend
  
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf
      - ./nginx/ssl:/etc/nginx/ssl
    depends_on:
      - backend
      - frontend
```

## 🚀 **SCRIPTS DE DEPLOYMENT Y CONFIGURACIÓN**

### **📋 Archivos .bat para Windows**

#### **1. start-system.bat**
```batch
@echo off
echo Iniciando sistema de postventa...
cd /d "C:\Users\Jesus Diaz\postventa-system"
start "Backend" cmd /k "cd backend && python manage.py runserver 0.0.0.0:8000"
timeout /t 5
start "Frontend" cmd /k "cd frontend && npm run dev"
echo Sistema iniciado correctamente
pause
```

#### **2. start_postventa_service.bat**
```batch
@echo off
echo Iniciando servicio de postventa...
cd /d "C:\Users\Jesus Diaz\postventa-system"
python backend/manage.py runserver 0.0.0.0:8000
```

#### **3. install_autostart.bat**
```batch
@echo off
echo Instalando autostart del sistema...
schtasks /create /tn "Postventa System" /tr "C:\Users\Jesus Diaz\postventa-system\start_postventa_service.bat" /sc onstart /ru "SYSTEM"
echo Autostart instalado correctamente
pause
```

#### **4. uninstall_autostart.bat**
```batch
@echo off
echo Desinstalando autostart del sistema...
schtasks /delete /tn "Postventa System" /f
echo Autostart desinstalado correctamente
pause
```

#### **5. check_autostart.bat**
```batch
@echo off
echo Verificando estado del autostart...
schtasks /query /tn "Postventa System"
pause
```

#### **6. update_server.bat**
```batch
@echo off
echo Actualizando servidor...
cd /d "C:\Users\Jesus Diaz\postventa-system"
git pull origin main
cd backend
python manage.py migrate
python manage.py collectstatic --noinput
echo Servidor actualizado correctamente
pause
```

#### **7. push_changes.bat**
```batch
@echo off
echo Subiendo cambios al repositorio...
cd /d "C:\Users\Jesus Diaz\postventa-system"
git add .
git commit -m "Actualización del sistema"
git push origin main
echo Cambios subidos correctamente
pause
```

#### **8. setup_remote_server.bat**
```batch
@echo off
echo Configurando servidor remoto...
cd /d "C:\Users\Jesus Diaz\postventa-system"
scp -r . user@remote-server:/path/to/postventa-system/
ssh user@remote-server "cd /path/to/postventa-system && ./scripts/deploy.sh"
echo Servidor remoto configurado
pause
```

#### **9. start_remote_server.bat**
```batch
@echo off
echo Iniciando servidor remoto...
ssh user@remote-server "cd /path/to/postventa-system && ./scripts/launch-secure.sh"
echo Servidor remoto iniciado
pause
```

### **📋 Scripts de Linux/Unix**

#### **1. scripts/deploy.sh**
```bash
#!/bin/bash
echo "Desplegando sistema de postventa..."
cd /path/to/postventa-system
git pull origin main
cd backend
python manage.py migrate
python manage.py collectstatic --noinput
cd ../frontend
npm install
npm run build
echo "Sistema desplegado correctamente"
```

#### **2. scripts/launch-secure.sh**
```bash
#!/bin/bash
echo "Iniciando sistema de forma segura..."
cd /path/to/postventa-system
nohup python backend/manage.py runserver 0.0.0.0:8000 > backend.log 2>&1 &
nohup npm run dev --prefix frontend > frontend.log 2>&1 &
echo "Sistema iniciado en segundo plano"
```

#### **3. scripts/backup.sh**
```bash
#!/bin/bash
echo "Creando backup del sistema..."
cd /path/to/postventa-system
tar -czf backup_$(date +%Y%m%d_%H%M%S).tar.gz backend/documents/ backend/db.sqlite3
echo "Backup creado correctamente"
```

## 🔧 **FUNCIONALIDADES IMPLEMENTADAS**

### **✅ 1. GESTIÓN DE INCIDENCIAS**

#### **Funcionalidades Principales:**
- ✅ **Crear incidencias** - Formulario completo con validación
- ✅ **Listar incidencias** - Tabla con filtros y búsqueda
- ✅ **Editar incidencias** - Modificación de datos existentes
- ✅ **Eliminar incidencias** - Eliminación con confirmación
- ✅ **Estados de incidencias** - Abierto, En Proceso, Cerrado
- ✅ **Escalación** - Escalar a calidad, proveedor, laboratorio
- ✅ **Adjuntos** - Subir archivos a incidencias
- ✅ **Historial** - Seguimiento de cambios

#### **Campos de Incidencia:**
```javascript
const incidentFields = {
  id: 'ID único',
  code: 'Código de incidencia (INC-2025-XXXX)',
  title: 'Título de la incidencia',
  description: 'Descripción detallada',
  category: 'Categoría (Técnica, Calidad, etc.)',
  subcategory: 'Subcategoría (texto libre)',
  priority: 'Prioridad (Alta, Media, Baja)',
  status: 'Estado (Abierto, En Proceso, Cerrado)',
  assigned_to: 'Usuario asignado',
  created_by: 'Usuario creador',
  created_at: 'Fecha de creación',
  updated_at: 'Fecha de actualización',
  escalation_status: 'Estado de escalación',
  resolution: 'Resolución final'
};
```

### **✅ 2. GESTIÓN DE DOCUMENTOS**

#### **Funcionalidades Principales:**
- ✅ **Subir documentos** - Múltiples formatos (PDF, DOC, XLS, etc.)
- ✅ **Organizar por incidencia** - Documentos agrupados por incidencia
- ✅ **Tipos de documentos** - Reportes de visita, calidad, proveedor, etc.
- ✅ **Apertura directa** - Desde carpeta compartida del sistema
- ✅ **Búsqueda y filtros** - Por tipo, fecha, usuario, incidencia
- ✅ **Estadísticas** - Conteo de documentos por tipo
- ✅ **Trazabilidad completa** - Historial de todos los documentos

#### **Tipos de Documentos:**
```javascript
const documentTypes = {
  'visit_reports': 'Reportes de Visita',
  'quality_reports': 'Reportes de Calidad',
  'supplier_reports': 'Reportes de Proveedor',
  'lab_reports': 'Reportes de Laboratorio',
  'incident_attachments': 'Adjuntos de Incidencia',
  'shared': 'Documentos Compartidos',
  'real_files': 'Archivos Reales'
};
```

### **✅ 3. REPORTES DE VISITA**

#### **Funcionalidades Principales:**
- ✅ **Crear reportes** - Formulario completo con datos de la incidencia
- ✅ **Adjuntar documentos** - Subir archivos relacionados
- ✅ **Generar PDF** - Reportes profesionales en PDF
- ✅ **Listar reportes** - Tabla con filtros y búsqueda
- ✅ **Editar reportes** - Modificación de datos existentes
- ✅ **Eliminar reportes** - Eliminación con confirmación
- ✅ **Abrir documentos** - Visualización directa desde carpeta compartida

#### **Campos del Reporte de Visita:**
```javascript
const visitReportFields = {
  id: 'ID único',
  incident: 'Incidencia relacionada',
  visit_date: 'Fecha de la visita',
  technician: 'Técnico que realizó la visita',
  customer: 'Cliente visitado',
  address: 'Dirección de la visita',
  objective: 'Objetivo de la visita',
  activities: 'Actividades realizadas',
  findings: 'Hallazgos encontrados',
  recommendations: 'Recomendaciones',
  next_actions: 'Próximas acciones',
  status: 'Estado del reporte',
  created_by: 'Usuario creador',
  created_at: 'Fecha de creación'
};
```

### **✅ 4. REPORTES DE CALIDAD**

#### **Funcionalidades Principales:**
- ✅ **Crear reportes** - Formulario completo con datos de la incidencia
- ✅ **Adjuntar documentos** - Subir archivos relacionados
- ✅ **Generar PDF** - Reportes profesionales en PDF
- ✅ **Listar reportes** - Tabla con filtros y búsqueda
- ✅ **Editar reportes** - Modificación de datos existentes
- ✅ **Eliminar reportes** - Eliminación con confirmación
- ✅ **Abrir documentos** - Visualización directa desde carpeta compartida

#### **Campos del Reporte de Calidad:**
```javascript
const qualityReportFields = {
  id: 'ID único',
  incident: 'Incidencia relacionada',
  report_date: 'Fecha del reporte',
  quality_manager: 'Gerente de calidad',
  department: 'Departamento',
  issue_description: 'Descripción del problema',
  root_cause: 'Causa raíz',
  corrective_actions: 'Acciones correctivas',
  preventive_actions: 'Acciones preventivas',
  responsible_person: 'Persona responsable',
  due_date: 'Fecha límite',
  status: 'Estado del reporte',
  created_by: 'Usuario creador',
  created_at: 'Fecha de creación'
};
```

### **✅ 5. REPORTES DE PROVEEDOR**

#### **Funcionalidades Principales:**
- ✅ **Crear reportes** - Formulario completo con datos de la incidencia
- ✅ **Adjuntar documentos** - Subir archivos relacionados
- ✅ **Generar PDF** - Reportes profesionales en PDF
- ✅ **Listar reportes** - Tabla con filtros y búsqueda
- ✅ **Editar reportes** - Modificación de datos existentes
- ✅ **Eliminar reportes** - Eliminación con confirmación
- ✅ **Abrir documentos** - Visualización directa desde carpeta compartida

#### **Campos del Reporte de Proveedor:**
```javascript
const supplierReportFields = {
  id: 'ID único',
  incident: 'Incidencia relacionada',
  report_date: 'Fecha del reporte',
  supplier: 'Proveedor',
  contact_person: 'Persona de contacto',
  issue_description: 'Descripción del problema',
  supplier_response: 'Respuesta del proveedor',
  corrective_actions: 'Acciones correctivas',
  timeline: 'Cronograma',
  status: 'Estado del reporte',
  created_by: 'Usuario creador',
  created_at: 'Fecha de creación'
};
```

### **✅ 6. REPORTES DE LABORATORIO**

#### **Funcionalidades Principales:**
- ✅ **Crear reportes** - Formulario completo con datos de la incidencia
- ✅ **Adjuntar documentos** - Subir archivos relacionados
- ✅ **Generar PDF** - Reportes profesionales en PDF
- ✅ **Listar reportes** - Tabla con filtros y búsqueda
- ✅ **Editar reportes** - Modificación de datos existentes
- ✅ **Eliminar reportes** - Eliminación con confirmación
- ✅ **Abrir documentos** - Visualización directa desde carpeta compartida

#### **Campos del Reporte de Laboratorio:**
```javascript
const labReportFields = {
  id: 'ID único',
  incident: 'Incidencia relacionada',
  report_date: 'Fecha del reporte',
  lab_technician: 'Técnico de laboratorio',
  test_type: 'Tipo de prueba',
  sample_info: 'Información de la muestra',
  test_results: 'Resultados de la prueba',
  analysis: 'Análisis',
  conclusions: 'Conclusiones',
  recommendations: 'Recomendaciones',
  status: 'Estado del reporte',
  created_by: 'Usuario creador',
  created_at: 'Fecha de creación'
};
```

### **✅ 7. GESTIÓN DE USUARIOS**

#### **Funcionalidades Principales:**
- ✅ **Crear usuarios** - Formulario completo con validación
- ✅ **Listar usuarios** - Tabla con filtros y búsqueda
- ✅ **Editar usuarios** - Modificación de datos existentes
- ✅ **Eliminar usuarios** - Eliminación con confirmación
- ✅ **Permisos** - Sistema de permisos granular
- ✅ **Roles** - Administrador, Usuario, Técnico, etc.
- ✅ **Autenticación** - Login con JWT
- ✅ **Cambio de contraseña** - Formulario seguro

#### **Campos de Usuario:**
```javascript
const userFields = {
  id: 'ID único',
  username: 'Nombre de usuario',
  email: 'Correo electrónico',
  first_name: 'Nombre',
  last_name: 'Apellido',
  role: 'Rol del usuario',
  permissions: 'Permisos específicos',
  is_active: 'Usuario activo',
  created_at: 'Fecha de creación',
  last_login: 'Último acceso'
};
```

### **✅ 8. DASHBOARD Y ESTADÍSTICAS**

#### **Funcionalidades Principales:**
- ✅ **Dashboard principal** - Vista general del sistema
- ✅ **Estadísticas de incidencias** - Conteo por estado, prioridad, etc.
- ✅ **Estadísticas de documentos** - Conteo por tipo, fecha, etc.
- ✅ **Gráficos** - Visualización de datos
- ✅ **Filtros** - Por fecha, usuario, departamento, etc.
- ✅ **Exportar datos** - Exportación a Excel/PDF
- ✅ **Reportes automáticos** - Generación automática de reportes

## 🚧 **FUNCIONALIDADES FALTANTES POR IMPLEMENTAR**

### **❌ 1. NOTIFICACIONES EN TIEMPO REAL**

#### **Funcionalidades Pendientes:**
- ❌ **WebSocket** - Notificaciones en tiempo real
- ❌ **Email automático** - Notificaciones por correo
- ❌ **SMS** - Notificaciones por mensaje de texto
- ❌ **Push notifications** - Notificaciones push del navegador
- ❌ **Sistema de alertas** - Alertas por incidencias críticas

#### **Implementación Requerida:**
```javascript
// WebSocket para notificaciones en tiempo real
const useWebSocket = () => {
  const [socket, setSocket] = useState(null);
  const [notifications, setNotifications] = useState([]);
  
  useEffect(() => {
    const ws = new WebSocket('ws://localhost:8000/ws/notifications/');
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      setNotifications(prev => [...prev, data]);
    };
    setSocket(ws);
    return () => ws.close();
  }, []);
  
  return { socket, notifications };
};
```

### **❌ 2. SISTEMA DE WORKFLOW**

#### **Funcionalidades Pendientes:**
- ❌ **Flujo de aprobación** - Aprobación de documentos
- ❌ **Estados automáticos** - Cambio automático de estados
- ❌ **Reglas de negocio** - Reglas automáticas del sistema
- ❌ **Escalación automática** - Escalación automática por tiempo
- ❌ **Notificaciones de workflow** - Notificaciones de cambios de estado

#### **Implementación Requerida:**
```python
# Modelo de Workflow en Django
class WorkflowStep(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    order = models.IntegerField()
    required_approval = models.BooleanField(default=False)
    auto_advance = models.BooleanField(default=False)
    time_limit = models.DurationField(null=True, blank=True)

class WorkflowInstance(models.Model):
    incident = models.ForeignKey(Incident, on_delete=models.CASCADE)
    current_step = models.ForeignKey(WorkflowStep, on_delete=models.CASCADE)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
```

### **❌ 3. INTEGRACIÓN CON SISTEMAS EXTERNOS**

#### **Funcionalidades Pendientes:**
- ❌ **API REST** - API pública para integración
- ❌ **Webhooks** - Notificaciones a sistemas externos
- ❌ **Sincronización** - Sincronización con sistemas ERP
- ❌ **Importación masiva** - Importación de datos desde Excel
- ❌ **Exportación** - Exportación a sistemas externos

#### **Implementación Requerida:**
```python
# API REST para integración externa
class ExternalAPIView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        # Procesar datos externos
        data = request.data
        # Validar y procesar
        return Response({'status': 'success'})
```

### **❌ 4. SISTEMA DE AUDITORÍA**

#### **Funcionalidades Pendientes:**
- ❌ **Log de auditoría** - Registro de todas las acciones
- ❌ **Trazabilidad** - Seguimiento completo de cambios
- ❌ **Reportes de auditoría** - Reportes de actividad
- ❌ **Compliance** - Cumplimiento de regulaciones
- ❌ **Backup automático** - Respaldo automático de datos

#### **Implementación Requerida:**
```python
# Modelo de Auditoría
class AuditLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    action = models.CharField(max_length=100)
    model = models.CharField(max_length=100)
    object_id = models.CharField(max_length=100)
    old_values = models.JSONField()
    new_values = models.JSONField()
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
```

### **❌ 5. SISTEMA DE REPORTES AVANZADOS**

#### **Funcionalidades Pendientes:**
- ❌ **Reportes personalizados** - Creación de reportes personalizados
- ❌ **Dashboards personalizados** - Dashboards configurables
- ❌ **Scheduled reports** - Reportes programados
- ❌ **Data visualization** - Visualización avanzada de datos
- ❌ **Exportación múltiple** - Exportación a múltiples formatos

#### **Implementación Requerida:**
```javascript
// Sistema de reportes personalizados
const useCustomReports = () => {
  const [reports, setReports] = useState([]);
  const [templates, setTemplates] = useState([]);
  
  const createReport = (config) => {
    // Crear reporte personalizado
  };
  
  const scheduleReport = (reportId, schedule) => {
    // Programar reporte
  };
  
  return { reports, templates, createReport, scheduleReport };
};
```

### **❌ 6. SISTEMA DE MÓVIL**

#### **Funcionalidades Pendientes:**
- ❌ **App móvil** - Aplicación móvil nativa
- ❌ **PWA** - Progressive Web App
- ❌ **Offline mode** - Funcionamiento sin conexión
- ❌ **Sincronización** - Sincronización de datos
- ❌ **Notificaciones push** - Notificaciones móviles

#### **Implementación Requerida:**
```javascript
// PWA Configuration
const pwaConfig = {
  name: 'Postventa System',
  short_name: 'Postventa',
  description: 'Sistema de gestión de postventa',
  start_url: '/',
  display: 'standalone',
  background_color: '#ffffff',
  theme_color: '#000000',
  icons: [
    {
      src: '/icons/icon-192x192.png',
      sizes: '192x192',
      type: 'image/png'
    }
  ]
};
```

### **❌ 7. SISTEMA DE BACKUP Y RECUPERACIÓN**

#### **Funcionalidades Pendientes:**
- ❌ **Backup automático** - Respaldo automático de datos
- ❌ **Recuperación** - Recuperación de datos
- ❌ **Versionado** - Control de versiones de documentos
- ❌ **Disaster recovery** - Recuperación ante desastres
- ❌ **Monitoring** - Monitoreo del sistema

#### **Implementación Requerida:**
```bash
#!/bin/bash
# Script de backup automático
BACKUP_DIR="/backup/postventa"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="postventa_backup_$DATE.tar.gz"

# Crear backup de la base de datos
pg_dump postventa_db > $BACKUP_DIR/db_$DATE.sql

# Crear backup de documentos
tar -czf $BACKUP_DIR/$BACKUP_FILE backend/documents/

# Limpiar backups antiguos
find $BACKUP_DIR -name "*.tar.gz" -mtime +30 -delete
```

## 🔧 **CONFIGURACIONES TÉCNICAS DETALLADAS**

### **📋 Configuración de Base de Datos SQL Server**

#### **1. Configuración de Conexión:**
```python
# settings-sqlserver.py
DATABASES = {
    'default': {
        'ENGINE': 'mssql',
        'NAME': 'postventa_db',
        'USER': 'sa',
        'PASSWORD': 'YourPassword',
        'HOST': 'localhost',
        'PORT': '1433',
        'OPTIONS': {
            'driver': 'ODBC Driver 17 for SQL Server',
            'extra_params': 'TrustServerCertificate=yes'
        },
    }
}
```

#### **2. Configuración de Carpetas Compartidas:**
```python
# Configuración de rutas de documentos
SHARED_DOCUMENTS_PATH = 'C:/Users/Jesus Diaz/postventa-system/backend/documents'
VISIT_REPORTS_PATH = os.path.join(SHARED_DOCUMENTS_PATH, 'visit_reports')
QUALITY_REPORTS_PATH = os.path.join(SHARED_DOCUMENTS_PATH, 'quality_reports')
SUPPLIER_REPORTS_PATH = os.path.join(SHARED_DOCUMENTS_PATH, 'supplier_reports')
LAB_REPORTS_PATH = os.path.join(SHARED_DOCUMENTS_PATH, 'lab_reports')
INCIDENT_ATTACHMENTS_PATH = os.path.join(SHARED_DOCUMENTS_PATH, 'incident_attachments')
SHARED_FILES_PATH = os.path.join(SHARED_DOCUMENTS_PATH, 'shared')
REAL_FILES_PATH = os.path.join(SHARED_DOCUMENTS_PATH, 'real_files')
```

### **📋 Configuración de Autenticación JWT**

#### **1. Configuración de JWT:**
```python
# settings.py
JWT_AUTH = {
    'JWT_SECRET_KEY': 'your-secret-key',
    'JWT_ALGORITHM': 'HS256',
    'JWT_EXPIRATION_DELTA': timedelta(days=7),
    'JWT_REFRESH_EXPIRATION_DELTA': timedelta(days=30),
}
```

#### **2. Middleware de Autenticación:**
```python
# middleware.py
class JWTAuthenticationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        token = request.META.get('HTTP_AUTHORIZATION')
        if token:
            try:
                payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=['HS256'])
                request.user = User.objects.get(id=payload['user_id'])
            except:
                pass
        return self.get_response(request)
```

### **📋 Configuración de Nginx**

#### **1. nginx.conf:**
```nginx
server {
    listen 80;
    server_name localhost;
    
    location / {
        proxy_pass http://frontend:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    location /api/ {
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    location /static/ {
        alias /app/static/;
    }
    
    location /media/ {
        alias /app/media/;
    }
}
```

### **📋 Configuración de Docker**

#### **1. Dockerfile Backend:**
```dockerfile
FROM python:3.9
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
```

#### **2. Dockerfile Frontend:**
```dockerfile
FROM node:16
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
CMD ["npm", "run", "dev"]
```

## 🚀 **INSTRUCCIONES DE DEPLOYMENT**

### **📋 Deployment Local**

#### **1. Configuración Inicial:**
```bash
# Clonar repositorio
git clone <repository-url>
cd postventa-system

# Configurar backend
cd backend
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver 0.0.0.0:8000

# Configurar frontend
cd ../frontend
npm install
npm run dev
```

#### **2. Configuración de Base de Datos:**
```bash
# Crear base de datos SQL Server
sqlcmd -S localhost -U sa -P YourPassword
CREATE DATABASE postventa_db;
GO
```

### **📋 Deployment con Docker**

#### **1. Construir y Ejecutar:**
```bash
# Construir imágenes
docker-compose build

# Ejecutar servicios
docker-compose up -d

# Verificar servicios
docker-compose ps
```

#### **2. Configuración de Volúmenes:**
```yaml
# docker-compose.yml
volumes:
  - ./backend:/app
  - ./frontend:/app
  - ./shared:/app/shared
  - ./nginx/ssl:/etc/nginx/ssl
```

### **📋 Deployment en Producción**

#### **1. Configuración de Servidor:**
```bash
# Instalar dependencias del sistema
sudo apt update
sudo apt install nginx postgresql python3-pip nodejs npm

# Configurar Nginx
sudo cp nginx/nginx.conf /etc/nginx/sites-available/postventa
sudo ln -s /etc/nginx/sites-available/postventa /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

#### **2. Configuración de SSL:**
```bash
# Generar certificados SSL
sudo certbot --nginx -d yourdomain.com
```

## 🔍 **ANÁLISIS DE FUNCIONALIDADES FALTANTES**

### **❌ 1. FUNCIONALIDADES CRÍTICAS FALTANTES**

#### **A. Sistema de Notificaciones:**
- **Prioridad:** ALTA
- **Descripción:** Sistema completo de notificaciones en tiempo real
- **Implementación:** WebSocket + Email + SMS
- **Tiempo estimado:** 2-3 semanas

#### **B. Sistema de Workflow:**
- **Prioridad:** ALTA
- **Descripción:** Flujo de aprobación y estados automáticos
- **Implementación:** Django + Celery + Redis
- **Tiempo estimado:** 3-4 semanas

#### **C. Sistema de Auditoría:**
- **Prioridad:** MEDIA
- **Descripción:** Log completo de auditoría y trazabilidad
- **Implementación:** Django + PostgreSQL + Logging
- **Tiempo estimado:** 2-3 semanas

### **❌ 2. FUNCIONALIDADES IMPORTANTES FALTANTES**

#### **A. Integración con Sistemas Externos:**
- **Prioridad:** MEDIA
- **Descripción:** API REST + Webhooks + Sincronización
- **Implementación:** Django REST Framework + Celery
- **Tiempo estimado:** 4-5 semanas

#### **B. Sistema de Reportes Avanzados:**
- **Prioridad:** MEDIA
- **Descripción:** Reportes personalizados + Dashboards + Programación
- **Implementación:** React + Chart.js + Django
- **Tiempo estimado:** 3-4 semanas

#### **C. Sistema Móvil:**
- **Prioridad:** MEDIA
- **Descripción:** PWA + App móvil + Offline mode
- **Implementación:** React Native + PWA + Service Workers
- **Tiempo estimado:** 6-8 semanas

### **❌ 3. FUNCIONALIDADES OPCIONALES FALTANTES**

#### **A. Sistema de Backup:**
- **Prioridad:** BAJA
- **Descripción:** Backup automático + Recuperación + Versionado
- **Implementación:** Scripts + Cron + Cloud Storage
- **Tiempo estimado:** 1-2 semanas

#### **B. Sistema de Monitoreo:**
- **Prioridad:** BAJA
- **Descripción:** Monitoreo del sistema + Alertas + Métricas
- **Implementación:** Prometheus + Grafana + AlertManager
- **Tiempo estimado:** 2-3 semanas

## 📊 **ESTADO ACTUAL DEL PROYECTO**

### **✅ FUNCIONALIDADES COMPLETADAS (80%)**

#### **Backend (90% completo):**
- ✅ Gestión de incidencias
- ✅ Gestión de documentos
- ✅ Gestión de usuarios
- ✅ API REST completa
- ✅ Autenticación JWT
- ✅ Configuración SQL Server
- ✅ Sistema de archivos

#### **Frontend (85% completo):**
- ✅ Páginas principales
- ✅ Componentes React
- ✅ Hooks personalizados
- ✅ Contextos de autenticación
- ✅ Servicios API
- ✅ Optimizaciones de rendimiento

#### **Deployment (70% completo):**
- ✅ Scripts de Windows
- ✅ Scripts de Linux
- ✅ Configuración Docker
- ✅ Configuración Nginx
- ✅ Autostart del sistema

### **❌ FUNCIONALIDADES FALTANTES (20%)**

#### **Funcionalidades Críticas:**
- ❌ Sistema de notificaciones
- ❌ Sistema de workflow
- ❌ Sistema de auditoría

#### **Funcionalidades Importantes:**
- ❌ Integración externa
- ❌ Reportes avanzados
- ❌ Sistema móvil

#### **Funcionalidades Opcionales:**
- ❌ Sistema de backup
- ❌ Sistema de monitoreo

## 🎯 **PLAN DE IMPLEMENTACIÓN RECOMENDADO**

### **📋 Fase 1: Funcionalidades Críticas (6-8 semanas)**

#### **Semana 1-2: Sistema de Notificaciones**
- Implementar WebSocket
- Configurar notificaciones por email
- Implementar notificaciones push

#### **Semana 3-4: Sistema de Workflow**
- Crear modelos de workflow
- Implementar flujo de aprobación
- Configurar estados automáticos

#### **Semana 5-6: Sistema de Auditoría**
- Implementar log de auditoría
- Configurar trazabilidad
- Crear reportes de auditoría

#### **Semana 7-8: Testing y Optimización**
- Pruebas completas del sistema
- Optimización de rendimiento
- Documentación actualizada

### **📋 Fase 2: Funcionalidades Importantes (8-10 semanas)**

#### **Semana 9-12: Integración Externa**
- Implementar API REST pública
- Configurar webhooks
- Implementar sincronización

#### **Semana 13-16: Reportes Avanzados**
- Crear sistema de reportes personalizados
- Implementar dashboards configurables
- Configurar reportes programados

#### **Semana 17-18: Sistema Móvil**
- Implementar PWA
- Configurar offline mode
- Implementar notificaciones móviles

### **📋 Fase 3: Funcionalidades Opcionales (4-6 semanas)**

#### **Semana 19-20: Sistema de Backup**
- Implementar backup automático
- Configurar recuperación
- Implementar versionado

#### **Semana 21-22: Sistema de Monitoreo**
- Configurar monitoreo del sistema
- Implementar alertas
- Configurar métricas

#### **Semana 23-24: Finalización**
- Pruebas finales
- Documentación completa
- Deployment en producción

## 🔧 **INSTRUCCIONES PARA NUEVA IA**

### **📋 Información Esencial para Continuar el Proyecto**

#### **1. Estructura del Proyecto:**
- **Backend:** Django + SQL Server + JWT
- **Frontend:** React + TypeScript + Vite + Tailwind
- **Deployment:** Docker + Nginx + Scripts .bat
- **Archivos:** Sistema de carpetas compartidas

#### **2. Configuraciones Importantes:**
- **Base de datos:** SQL Server en localhost:1433
- **Backend:** Puerto 8000
- **Frontend:** Puerto 3000
- **Carpetas:** C:/Users/Jesus Diaz/postventa-system/backend/documents/

#### **3. Scripts de Deployment:**
- **start-system.bat:** Iniciar sistema completo
- **install_autostart.bat:** Instalar autostart
- **update_server.bat:** Actualizar servidor
- **push_changes.bat:** Subir cambios

#### **4. Funcionalidades Implementadas:**
- ✅ Gestión de incidencias
- ✅ Gestión de documentos
- ✅ Reportes de visita, calidad, proveedor, laboratorio
- ✅ Gestión de usuarios
- ✅ Dashboard y estadísticas
- ✅ Apertura directa de archivos

#### **5. Funcionalidades Faltantes:**
- ❌ Sistema de notificaciones
- ❌ Sistema de workflow
- ❌ Sistema de auditoría
- ❌ Integración externa
- ❌ Reportes avanzados
- ❌ Sistema móvil

#### **6. Archivos Críticos:**
- **backend/apps/documents/views.py:** Lógica de documentos
- **frontend/src/pages/Documents.jsx:** Página central de documentos
- **backend/postventa_system/settings-sqlserver.py:** Configuración SQL Server
- **docker-compose.yml:** Configuración Docker

#### **7. Comandos Importantes:**
```bash
# Iniciar backend
cd backend && python manage.py runserver 0.0.0.0:8000

# Iniciar frontend
cd frontend && npm run dev

# Iniciar con Docker
docker-compose up -d

# Migrar base de datos
python manage.py migrate

# Crear superusuario
python manage.py createsuperuser
```

#### **8. Problemas Conocidos:**
- **Apertura de documentos:** Usar rutas directas del sistema de archivos
- **Autenticación:** JWT tokens en headers
- **Carpetas compartidas:** Configurar permisos de Windows
- **SQL Server:** Configurar ODBC Driver 17

#### **9. Próximos Pasos Recomendados:**
1. Implementar sistema de notificaciones
2. Crear sistema de workflow
3. Implementar sistema de auditoría
4. Configurar integración externa
5. Desarrollar reportes avanzados

#### **10. Contacto y Soporte:**
- **Usuario:** Jesus Diaz
- **Proyecto:** postventa-system
- **Ubicación:** C:\Users\Jesus Diaz\postventa-system
- **Estado:** 80% completo, listo para funcionalidades avanzadas

**¡El proyecto está en excelente estado y listo para continuar con las funcionalidades avanzadas!**

