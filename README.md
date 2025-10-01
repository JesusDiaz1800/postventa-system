# Sistema de Gestión de Incidencias Postventa

## 🎯 Descripción

Sistema completo de gestión de incidencias postventa para control de calidad, desarrollado con tecnologías modernas y open-source. Permite el registro, seguimiento y resolución de incidencias con integración de IA, generación automática de documentos y gestión de workflows.

## ✨ Características Principales

### 🔐 Autenticación y Seguridad
- **Sistema de roles**: Admin, Supervisor, Analista, Atención al Cliente, Proveedor
- **Autenticación JWT** con refresh tokens
- **Auditoría completa** de todas las acciones
- **Encriptación** de datos sensibles
- **Políticas de contraseñas** configurables

### 📋 Gestión de Incidencias
- **Registro completo** con campos específicos del negocio
- **Códigos únicos** automáticos (INC-YYYYMMDD-XXX)
- **Estados configurables**: Abierto, Triage, Inspección, Laboratorio, Propuesta, En Progreso, Resuelto, Cerrado
- **Prioridades**: Crítica, Alta, Media, Baja
- **Categorías específicas**: Defecto de Fabricación, Daño en Transporte, Calidad, etc.

### 🤖 Inteligencia Artificial
- **Análisis de imágenes** con múltiples proveedores (OpenAI, Anthropic, Google)
- **Fallback automático** a modelos locales
- **Gestión de cuotas** y límites de uso
- **Sugerencias de causas** y recomendaciones
- **Generación de texto** con tono configurable

### 📄 Generación de Documentos
- **Plantillas personalizables** para cliente y proveedor
- **Editor WYSIWYG** integrado
- **Conversión automática** DOCX → PDF
- **Versionado** de documentos
- **Búsqueda full-text** en documentos

### 🔄 Workflows Configurables
- **Estados y transiciones** personalizables por tipo de incidencia
- **Acciones requeridas** en cada estado
- **Validaciones** automáticas
- **Notificaciones** por email e in-app

### 📊 Reportes y Analytics
- **Dashboard** con KPIs en tiempo real
- **Métricas** de rendimiento y tiempos de resolución
- **Gráficos** interactivos
- **Exportación** a PDF y Excel
- **Filtros avanzados** por fecha, proveedor, estado

## 🏗️ Arquitectura Técnica

### Frontend
- **React 18** con TypeScript
- **Vite** para build y desarrollo
- **Tailwind CSS** para estilos
- **React Query** para gestión de estado
- **React Router** para navegación
- **Lucide React** para iconos

### Backend
- **Django 4.2** con Django REST Framework
- **SQL Server Express** como base de datos
- **Celery** para tareas en background
- **Redis** para cache y broker
- **JWT** para autenticación

### IA y Procesamiento
- **AI Orchestrator** para gestión de proveedores
- **Múltiples adapters** (OpenAI, Anthropic, Google, Local)
- **LibreOffice** para conversión de documentos
- **python-docx** para manipulación de Word

### Infraestructura
- **Docker** y **Docker Compose** para contenerización
- **Nginx** como reverse proxy
- **Carpeta compartida** para almacenamiento de archivos
- **SSL/TLS** para seguridad

## 🚀 Instalación y Configuración

### Prerrequisitos
- Docker y Docker Compose
- Acceso a carpeta compartida `\\192.168.1.161\Y:\CONTROL DE CALIDAD\postventa`
- SQL Server Express en `192.168.1.161\SQLEXPRESS`

### Instalación Rápida

1. **Clonar el repositorio**
```bash
git clone <repository-url>
cd postventa-system
```

2. **Configurar variables de entorno**
```bash
cp .env.example .env
# Editar .env con tus configuraciones
```

3. **Levantar el sistema**
```bash
# Para desarrollo
docker-compose -f docker-compose.dev.yml up -d

# Para producción
docker-compose -f docker-compose.prod.yml up -d
```

4. **Inicializar la base de datos**
```bash
docker-compose exec backend python manage.py migrate
docker-compose exec backend python manage.py createsuperuser
```

5. **Acceder al sistema**
- Frontend: http://localhost:3000 (dev) o http://localhost (prod)
- Backend API: http://localhost:8000/api
- Admin: http://localhost:8000/admin

## 📁 Estructura del Proyecto

```
postventa-system/
├── frontend/                 # Aplicación React
│   ├── src/
│   │   ├── components/      # Componentes reutilizables
│   │   ├── pages/          # Páginas principales
│   │   ├── hooks/          # Hooks personalizados
│   │   ├── config/         # Configuración
│   │   └── lib/            # Utilidades
│   ├── public/             # Archivos estáticos
│   └── package.json        # Dependencias frontend
├── backend/                # Aplicación Django
│   ├── apps/              # Aplicaciones Django
│   │   ├── incidents/     # Gestión de incidencias
│   │   ├── users/         # Gestión de usuarios
│   │   ├── documents/     # Gestión de documentos
│   │   ├── ai_orchestrator/ # Orquestador de IA
│   │   ├── workflows/     # Gestión de workflows
│   │   └── audit/         # Sistema de auditoría
│   ├── postventa_system/  # Configuración Django
│   └── requirements.txt   # Dependencias Python
├── docker-compose.yml     # Configuración Docker
├── docker-compose.prod.yml # Configuración producción
└── README.md             # Este archivo
```

## 🔧 Configuración Avanzada

### Base de Datos
- **Host**: 192.168.1.161
- **Instancia**: SQLEXPRESS
- **Base de datos**: postventa_system
- **Usuario**: sa
- **Contraseña**: Configurable en .env

### Almacenamiento
- **Carpeta compartida**: `\\192.168.1.161\Y:\CONTROL DE CALIDAD\postventa`
- **Estructura**: `incidencias/{id}/docs` y `incidencias/{id}/images`
- **Tipos permitidos**: JPG, PNG, PDF, DOCX, XLSX

### IA y Proveedores
- **OpenAI**: GPT-4 para análisis de imágenes y texto
- **Anthropic**: Claude para análisis avanzado
- **Google**: Gemini para análisis multimodal
- **Local**: Fallback con modelos locales

## 📊 Monitoreo y Logs

### Logs de Aplicación
- **Backend**: `/var/log/django/`
- **Frontend**: Console del navegador
- **Nginx**: `/var/log/nginx/`

### Métricas
- **Incidencias por día/semana/mes**
- **Tiempo promedio de resolución**
- **Uso de IA y costos**
- **Actividad de usuarios**

## 🔒 Seguridad

### Autenticación
- **JWT tokens** con expiración configurable
- **Refresh tokens** para renovación automática
- **Límite de intentos** de login
- **Bloqueo de cuentas** por seguridad

### Autorización
- **Roles granulares** con permisos específicos
- **Middleware** de autenticación
- **Validación** de permisos en cada endpoint

### Auditoría
- **Registro completo** de acciones
- **IP y User-Agent** de cada acción
- **Retención** configurable de logs
- **Exportación** de auditoría

## 🚀 Despliegue en Producción

### Requisitos del Servidor
- **CPU**: 4 cores mínimo
- **RAM**: 8GB mínimo
- **Disco**: 100GB mínimo
- **Red**: Acceso a carpeta compartida

### Pasos de Despliegue
1. **Preparar servidor** con Docker
2. **Configurar red** y firewall
3. **Montar carpeta compartida**
4. **Configurar SSL** (opcional)
5. **Levantar servicios** con docker-compose
6. **Configurar backup** automático
7. **Monitoreo** y alertas

## 📞 Soporte y Contacto

### Documentación
- **API**: http://localhost:8000/api/docs (Swagger)
- **Admin**: http://localhost:8000/admin
- **Logs**: Docker logs de cada servicio

### Contacto
- **Desarrollador**: [Tu información de contacto]
- **Empresa**: [Información de la empresa]
- **Versión**: 1.0.0

## 📄 Licencia

Este proyecto está bajo la licencia MIT. Ver el archivo `LICENSE` para más detalles.

## 🙏 Agradecimientos

- **Django** por el framework web
- **React** por la interfaz de usuario
- **Tailwind CSS** por el sistema de estilos
- **Lucide** por los iconos
- **OpenAI, Anthropic, Google** por los servicios de IA

---

**¡Sistema listo para producción y presentación a gerencia!** 🎉