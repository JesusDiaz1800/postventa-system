# CONTEXTO MAESTRO DEL PRODUCTO: SISTEMA DE POSTVENTA

## 1. Identidad y Misión
**Nombre:** Sistema de Gestión de Postventa y Calidad (Postventa System).
**Empresa:** Polifusion (Chile, Perú, Colombia).
**Misión:** Centralizar, gestionar y dar trazabilidad a los reclamos de clientes, reportes de calidad interna/externa y visitas técnicas, integrándose nativamente con el ERP SAP Business One.
**Visión:** Ser una plataforma "Premium", rápida y estéticamente impactante (Dark Mode, Glassmorphism) que opere como una sola unidad lógica servida a múltiples países.

## 2. Arquitectura de Alto Nivel
*   **Tipo:** Monolito Modular con Frontend Desacoplado.
*   **Modelo de Despliegue:** On-Premise (Windows Server).
*   **Modelo de Datos:** Multi-Tenant Dinámico con Aislamiento de Base de Datos (Database-per-Tenant).

### Tech Stack
*   **Frontend:** React 18 + Vite.
    *   **Estilo:** TailwindCSS (Diseño Industrial/Premium, Dark Mode forzado).
    *   **Estado:** Context API (Auth, PWA).
    *   **Librerías Clave:** Axios (HTTP), Framer Motion (Animaciones), Heroicons.
*   **Backend:** Python 3.x + Django REST Framework (DRF).
    *   **Motor:** Django 5.x.
    *   **Async:** Celery + Redis (Tareas en segundo plano, e.g., correos).
    *   **AI:** Google Gemini (2.0 Flash Lite) + ChromaDB (RAG).
*   **Base de Datos:** SQL Server (MSSQL).
    *   **Driver:** ODBC Driver 13/17 for SQL Server.
    *   **Estrategia:**
        *   `postventa_system` (Legacy/Default -> Chile).
        *   `POSTVENTA_PE` (Tenant Perú).
        *   `POSTVENTA_CO` (Tenant Colombia).
*   **Integración SAP:**
    *   Lectura directa de vistas/tablas de SAP (`PRDPOLIFUSION`, `PRDPOLPERU`, etc.) vía `SapRouter` y `SAPQueryService`.

## 3. Módulos Principales
1.  **Gestión de Incidencias (Reclamos):** Flujo de creación, aprobación y cierre de reclamos de clientes.
2.  **Reportes de Calidad:**
    *   **Cliente:** Problemas reportados externamente.
    *   **Interno:** Problemas detectados en planta/producción.
    *   **Proveedores:** Reclamos a proveedores de materia prima.
3.  **Gestión de Visitas:** Reportes técnicos de terreno con geolocalización y firma digital.
4.  **Inteligencia Artificial (Asistente):**
    *   Chatbot contextual (RAG) capaz de leer manuales PDF y datos del sistema.
    *   Análisis de imágenes de fallas.

## 4. Reglas de Negocio Críticas
*   **Aislamiento:** Un usuario de Perú SOLO ve datos de Perú.
*   **Seguridad:** Autenticación JWT. Passwords encriptados.
*   **Inmutabilidad SAP:** Nunca escribir en tablas nativas de SAP sin validación extrema. Preferir lectura.
*   **UX Premium:** La interfaz debe "sorprender" (Wow factor). No se aceptan diseños planos o aburridos.

## 5. Estado Actual (v4.0)
*   **Multi-País:** Implementado selector de país en Login.
*   **Infraestructura:** Bases de datos separadas creadas.
*   **Pendiente:** Migración completa de datos históricos y despliegue final en IIS.
