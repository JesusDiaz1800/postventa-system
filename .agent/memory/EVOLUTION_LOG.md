# HISTORIAL EVOLUTIVO DEL SISTEMA

Este documento registra la evolución narrativa del sistema, capturando las decisiones clave, mejoras y hitos alcanzados por el equipo de desarrollo (Usuario + Agente).

## v4.0: La Era Multi-País (Febrero 2026)
**Objetivo:** Escalar la aplicación para soportar operaciones en Perú y Colombia sin duplicar el código base.
*   **Arquitectura Tenant Dinámica:** Se descartó la idea de múltiples servicios (Docker/PM2) en favor de un "Router Dinámico" en Django.
    *   *Por qué:* Menor consumo de RAM en el servidor Windows y mantenimiento centralizado.
*   **Frontend Adaptativo:**
    *   **Login:** Se añadió un selector de país premium con banderas (Glassmorphism).
    *   **Header:** Indicador visual persistente del país activo.
    *   **Middleware:** Inyección automática del header `X-Country-Code` en todas las peticiones API.
*   **Backend Core:**
    *   Creación de `TenantMiddleware` y `DynamicTenantRouter`.
    *   Aprovisionamiento de bases de datos `POSTVENTA_PE` y `POSTVENTA_CO` en SQL Server.

## v3.6: Optimización de IA (Febrero 2026)
**Objetivo:** Restaurar y potenciar el módulo de IA tras fallos de cuota y disponibilidad.
*   **Modelo:** Migración exitosa a `gemini-2.0-flash-lite-001`.
    *   *Resultado:* Respuestas más rápidas y económicas.
*   **Eficiencia:** Implementación de redimensionamiento de imágenes (max 1024px) antes de enviarlas a la IA para ahorrar tokens.
*   **Estabilidad:** Refactorización de `test_gemini_direct.py` para diagnósticos precisos.

## v3.5: Estabilización y Seguridad
**Objetivo:** Resolver problemas de autenticación "401 Unauthorized" persistentes.
*   **Auth Flow:** Mejora en la lógica de `refreshToken` en el frontend (`api.jsx`) y manejo de sesiones en el backend.
*   **Limpieza:** Eliminación de endpoints muertos y dependencias cíclicas en `urls.py`.

## v3.0: Rediseño Visual "Premium"
**Objetivo:** Transformar una aplicación funcional en una experiencia visual moderna.
*   **UI Kit:** Adopción total de TailwindCSS con diseño "Dark Industrial".
*   **Efectos:** Uso intensivo de Glassmorphism (fondos borrosos), gradientes sutiles y animaciones con Framer Motion.
*   **Dashboards:** Gráficos integrados con Recharts y métricas en tiempo real.

## v2.0 - v1.0: Fundaciones (Legacy)
*   Creación del monolito Django.
*   Integración inicial con SAP (lectura básica).
*   Digitalización de formularios de papel (Incidencias).
