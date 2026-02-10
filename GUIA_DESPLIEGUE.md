
# 🚀 Guía de Despliegue Simplificada - Windows

## 1. Requisitos
- Windows 10/11 o Server.
- SQL Server (SQLEXPRESS) corriendo en 192.168.1.144 o local.
- Python 3.12 (versión portable incluida en `python-portable`).
- Node.js 18+ (instalado en sistema o portable).
- Carpeta compartida para documentos: `C:\Users\jdiaz\Desktop\postventa-system\backend\documents`.

## 2. Iniciar el Sistema (Modo Producción Manual)
Ejecutar el script principal:
`EJECUTAR_PRUEBAS.bat`

Este script:
1.  Detiene procesos anteriores.
2.  Inicia el **Backend** en puerto 8000.
    *   Conecta a BD SQL Server en `192.168.1.144`.
    *   Usa autenticación SQL (`postventa_user`).
3.  Inicia el **Frontend** en puerto 5173 (modo dev por ahora).
4.  Abre el navegador automáticamente.

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
