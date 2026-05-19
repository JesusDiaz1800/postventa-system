
# 🚀 Resumen Técnico del Sistema Postventa (Optimizado)

## 📊 Estado Actual
El sistema se encuentra en un estado **100% funcional y optimizado**, con conectividad estable a SQL Server y una arquitectura limpia.

## 🛠️ Stack Tecnológico
- **Backend:** Django 5.x + Django REST Framework.
- **Frontend:** React 18 + Vite + TailwindCSS.
- **Base de Datos:** SQL Server 2019/2022 (Conectado a `192.168.1.144`).
- **Autenticación:** JWT (SimpleJWT) con roles personalizados.

## ⚡ Optimizaciones Implementadas
1.  **Base de Datos:**
    *   Índices (`db_index=True`) agregados a campos críticos: `email`, `role`, `status`, `priority`, `created_at`.
    *   Eliminación de tablas obsoletas y corrección de migraciones.
2.  **Seguridad:**
    *   Configuración de producción (`DEBUG=False`) segura.
    *   Gestión de secretos mediante variables de entorno.
    *   Protección contra N+1 queries en vistas principales usando `select_related` y `prefetch_related`.
3.  **Frontend:**
    *   Cargas paralelas (`Promise.all`) para documentos y reportes.
    *   Interfaz unificada de trazabilidad documental.
    *   Filtros avanzados y búsqueda optimizada.
4.  **Despliegue:**
    *   Script unificado `EJECUTAR_PRUEBAS.bat` para inicio rápido.
    *   Guía simplificada `GUIA_DESPLIEGUE.md`.

## 📁 Estructura de Carpetas Clave
- `backend/apps/`: Módulos de la aplicación (incidents, documents, users, etc.).
- `backend/documents/`: Almacenamiento centralizado de archivos (PDFs, adjuntos).
- `frontend/src/pages/`: Vistas principales React.
- `scripts/`: Utilidades de mantenimiento.

## 🔑 Credenciales
- **Admin:** `jdiaz` / `adminJDR`

## 📝 Notas de Mantenimiento
- Para limpiar archivos temporales, usar `Remove-Item` en PowerShell.
- Los logs de Django se encuentran en `backend/logs/`.
