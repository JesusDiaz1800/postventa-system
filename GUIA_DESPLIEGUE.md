
# 🚀 Guía de Despliegue Simplificada - Windows

## 1. Requisitos
- Windows 10/11 o Server.
- SQL Server (SQLEXPRESS) corriendo en 192.168.1.144 o local.
- Python 3.12 (versión portable incluida en `python-portable`).
- Node.js 18+ (instalado en sistema o portable).
- Carpeta compartida para documentos: `C:\Users\jdiaz\Desktop\postventa-system\backend\documents`.

## 2. Iniciar el Sistema (Modo Producción)
Ejecutar el script principal:
`INICIAR_PM2.bat`

O con parámetros: `INICIAR_PM2.bat start` | `stop` | `restart` | `status` | `logs` | `monit`

Este script (usa PM2 como gestor de procesos):
1.  Verifica/renueva certificados SSL automáticamente.
2.  Inicia el **Backend** (Django + Daphne) en puerto 8000.
3.  Inicia el **Frontend** (Vite) en puerto 5173 (HTTPS).
4.  Requiere: Node.js con PM2 instalado (`npm install -g pm2`).

## 3. Credenciales
- **Usuario:** `jdiaz`
- **Contraseña:** `adminJDR`

## 4. Mantenimiento
- **Respaldos:** SQL Server debe tener su propio plan de mantenimiento.
- **Logs:** Revisar carpeta `backend/logs/`.
- **Archivos:** Los documentos adjuntos se guardan en la carpeta `backend/documents`.

## 5. Solución de Problemas
- Si falla la conexión a BD: Verificar IP `192.168.1.144` y que SQLEXPRESS acepte conexiones TCP/IP puerto 1433.
- Si falla login: Ejecutar `verify_login.py` (si existe) o revisar logs de Django.
