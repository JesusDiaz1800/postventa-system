---
name: Project Context Keeper
description: Mantiene el contexto crítico e inmutable del entorno de despliegue y arquitectura del sistema. Evita desviaciones de la infraestructura real.
---

# 🌍 Contexto del Proyecto (Inmutable)

Esta skill asegura que NUNCA olvides dónde y cómo está desplegado el sistema.

## 🏢 Infraestructura
1.  **Entorno Host**: Escritorio Remoto (Windows Server/Windows 10/11) en la red corporativa.
2.  **Acceso de Usuarios**: Los usuarios acceden a la aplicación web a través de la **IP Local** de este escritorio remoto.
    *   *Implicación*: `localhost` solo sirve para ti/dev. Los usuarios usan `http://<IP-SERVER>:PUERTO`.
    *   *Configuración*: Vite/Django deben permitir conexiones externas (`--host 0.0.0.0`).

## 🗄️ Datos Corporativos
1.  **Base de Datos Principal**: SQL Server Corporativo (`PRDPOLIFUSION`).
    *   **Acceso**: Estrictamente controlado. Generalmente LECTURA (SELECT) para reportes.
    *   **Escritura**: Solo en tablas específicas o bases de datos satélites permitidas.
    *   **Regla de Oro**: NUNCA intentes migraciones destructivas en el SQL Server corporativo sin autorización explícita y backup.
2.  **Base de Datos Local**: SQLite/Postgres (si aplica para la app satélite) para gestión de sesiones, caché o datos transitorios de la IA.

## 🧩 Stack Tecnológico
*   **Frontend**: React + Vite + TailwindCSS.
*   **Backend**: Python + Django Rest Framework.
*   **IA**:
    *   Modelos: Gemini Pro / Flash.
    *   RAG: NotebookLM (Arquitectura/PDFs) + SQL (Datos Vivos).
    *   Agentes: LangGraph (Orquestación).

## 🚨 Restricciones
*   No reiniciar servicios en horas pico (si el usuario indica que hay usuarios activos).
*   No cambiar puertos bruscamente (afecta a usuarios remotos).
*   Respetar las rutas de archivos de Windows (`C:\...`).
