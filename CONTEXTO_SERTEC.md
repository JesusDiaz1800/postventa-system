# CONTEXTO ARQUITECTÓNICO: SISTEMA SERTEC (VISITAS RUTINARIAS)

**IMPORTANTE PARA LA IA CREADA EN ESTA VENTANA:** 
Lee este documento exhaustivamente y memorízalo. Contiene el ADN estructural, los patrones de conexión y los errores históricos superados del sistema hermano (Postventa). Tu objetivo es convertir este clon en un sistema ágil enfocado al 100% en **Reportes de Visita**, eliminando las abstracciones innecesarias.

---

## 1. OBJETIVO DEL SISTEMA Y CAMBIO DE PARADIGMA
- **Sistema Anterior (Postventa):** Todo giraba en torno a una `Incidencia`. Un ticket se creaba primero, y de ahí nacían fotos, reportes y cierres.
- **Tu Sistema (Sertec):** **NO EXISTEN INCIDENCIAS COMO TALES.** El personal de terreno usará esta app para llenar *Reportes de Visita Rutinarias* de manera masiva y autónoma (desde 0). 
- **La Entidad Principal:** El `VisitReport` (o como decidas renombrarlo) es ahora el rey. Al crearse un reporte de visita, este debe comunicarse directamente con SAP y abrir/cerrar su propia Llamada de Servicio de manera independiente.
- **Volumen:** Será masivo (centenares al día). Por eso debes aligerar el código, limpiar modelos y asegurar rutas directas.
- **Métricas:** Los dashboards deben reestructurarse (D3/Recharts) para mostrar tipos de visita, eficiencias, técnicos más activos, pero no "estados de incidencia".

---

## 2. ARQUITECTURA DE DATOS (MULTI-TENANT & BASES DE DATOS)
El sistema emplea un patrón de arquitectura *Multi-Tenant* (por país) basado en el dominio de correo electrónico (`@polifusion.cl` -> CL, `@jdiaz.co` -> CO, `@...pe` -> PE). Esto se intercepta en el `TenantMiddleware`.

### 2.1 Bases de Datos de la Aplicación (Django/SQL Server)
Tendrás 3 bases de datos propias, limpias y dedicadas a este masivo volumen:
- `SERTEC_CL` (Chile)
- `SERTEC_PE` (Perú)
- `SERTEC_CO` (Colombia)

### 2.2 Conexión de Lectura (SQL Directo) hacia Servidores SAP
Para sugerir nombres de Clientes, Proyectos o Vendedores, el sistema hace sentencias SQL de *SÓLO LECTURA* hacia las BDs de SAP (`192.168.1.232`).
- **DRIVER OBLIGATORIO:** `ODBC Driver 18 for SQL Server` (No uses el 11 ni el 13, fallarán de forma silente o con errores SSL).
- **USUARIO OBLIGATORIO:** `ccalidad` (Es la llave maestra de lectura para *todas* las empresas). *NOTA: No uses usuarios `jefsertec` aquí, ya experimentamos errores 18456 y 4060 con ellos.*
- **Databases SAP (Lectura):**
  - **CL:** `TESTPOLIFUSION` (o la que se defina para PRD)
  - **PE:** `TSTPOLPERU`
  - **CO:** `TSTPOLCOLOMBIA_2`

---

## 3. INTEGRACIÓN SAP SERVICE LAYER (API DE ESCRITURA)
Para crear la Llamada de Servicio oficial en SAP, se usa la API REST oficial en `https://192.168.1.237:50000/b1s/v1`. 

### 3.1 Credenciales de Service Layer (API)
AQUÍ SÍ se deben utilizar los usuarios por país, para asegurar trazabilidad correcta de auditoría en los metadatos de SAP.
- **CL:** `ccalidad`
- **PE:** `jefsertec_ppe`
- **CO:** `jefsertec_pco`

### 3.2 Peculiaridades de Campos Mapeados (SL)
El archivo `sap_transaction_service.py` tiene la lógica de envío, pero asume que viene de una "Incidencia". Debes re-mapearlo para que nazca puramente de la Visita. Ten en cuenta lo siguiente:
- **Prioridades:** `scp_Low`, `scp_Medium`, `scp_High`.
- **Status de Creación:** 
  - PE -> `1` (Open)
  - CO/CL -> `-3`, `-1`, `-2` (Verificar archivo existente de postventa para confirmaciones previas).
- **Asignación de Técnicos/Responsables:** 
  - Existen campos conflictivos entre el formulario de SAP y el ServiceLayer (`AssigneeCode` vs `TechnicianCode`).
  - PE -> Técnico=1 (Luis Custodio), Asignado=31. UDF Vendedor=`FABRICA`.
  - CO -> Técnico=2.
  - Revisa el bucle de "Resiliencia" (Reparaciones -5002, -6103) dentro de `create_service_call()`. Ya fueron programados escudos antimisiles contra los rechazos de SAP. No los borres, mejóralos y adáptalos al nuevo modelo.
- **UDFs Vitales en Llamada de Servicio:** (Estos son los campos que el vendedor llena en su formulario de visita). Revisa `update_service_call_from_visit_report()`: `U_NX_OBS_MURO`, `U_NX_OBS_MATRIZ`, etc.
- **Subida de Archivos (Attachments2):** Implementa el método de `PATCH` en `sap_transaction_service.py` que permite adicionar fotos sin sobreescribir las que otro vendedor haya agregado. Se programó control de concurrencia `FileLock` que debe mantenerse porque los vendedores subirán fotos al mismo tiempo.

---

## 4. DESPLIEGUE Y RED (CLOUDFLARE)
- **Puerto Asignado:** Esta aplicación correrá en el puerto `8001` local (`127.0.0.1:8001`) para no chocar con la hermana mayor (Postventa en el `8000`).
- **Control de Procesos:** Utiliza `ecosystem.config.js` de PM2 (Asegúrate de cambiar los nombres a `sertec-unificado`).
- **Dominio y Accesos Externos:** Operará tras su propio túnel Zero Trust amarrado a `sertec.sistemati.cl`. 
- **Certificados SSL:** Están configurados en `frontend/ssl`. Para el tráfico en el entorno local (React Vite -> Django), hay túneles asegurados y certificados auto-firmados que deben seguir apuntando y resolviendo correctamente (verifica los CORS si hay problemas).

---

## 5. TAREAS INICIALES OBLIGATORIAS (ROADMAP)
Al leer este documento, tu humano te dará luz verde habiendo ya creado las Bases de Datos SQL `SERTEC_XX`. Tus labores prioritarias son:

1. **Renombrar Entornos:** Asegúrate de que `.env` apunte a las nuevas BDs.
2. **Cambiar Puertos:** Actualiza Django settings (`ALLOWED_HOSTS`), `ecosystem.config.js` a puerto `8001`. Actualiza `vite.config.ts` del frontend a puerto apropiado u offset.
3. **Poda de Código (Backend):** Elimina el modelo `Incident`, la app `incidents` completa y migra todo su peso al modelo o app de `VisitReport`. Si es más fácil, convierte un `VisitReport` en la clase base de todo y refactoriza la base de datos con `makemigrations`.
4. **Poda de Interfaz (Frontend):** Retira la barra lateral y opciones de "Gestión de Incidencias". Deja como foco central un "Crear Visita" gigante, rápido e intuitivo, y los "Dashboard de Visitas", enfocándote ahora en la agilidad de ingreso.

**BIENVENIDO AL PROYECTO SERTEC.**
