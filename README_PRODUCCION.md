# 🚀 Sistema PostVenta - Producción

## 📋 **INSTRUCCIONES DE USO**

### 🚀 **INICIO RÁPIDO**

1. **Instalar dependencias** (solo la primera vez):
   ```bash
   INSTALAR_DEPENDENCIAS.bat
   ```

2. **Iniciar el sistema**:
   ```bash
   INICIAR_SISTEMA_PRODUCCION.bat
   ```

3. **Verificar funcionamiento**:
   ```bash
   VERIFICAR_SISTEMA.bat
   ```

4. **Detener el sistema**:
   ```bash
   DETENER_SISTEMA.bat
   ```

---

## 🌐 **ACCESO AL SISTEMA**

- **URL**: `http://192.168.1.234:5173`
- **Backend API**: `http://192.168.1.234:8000`
- **Base de datos**: SQL Server Express en `192.168.1.124:1433`

### 👤 **CREDENCIALES**

| Usuario | Contraseña | Rol |
|---------|------------|-----|
| `jdiaz` | `adminJDR` | Administrador |
| `pestay` | `Pestay2025!` | Gerencia |
| `pmorales` | `Patricio2025!` | Servicio Técnico |
| `mmontenegro` | `Marco2025!` | Servicio Técnico |

---

## 📁 **ARCHIVOS PRINCIPALES**

### 🚀 **Scripts de Producción**
- `INICIAR_SISTEMA_PRODUCCION.bat` - **Script principal para iniciar**
- `VERIFICAR_SISTEMA.bat` - Verificar funcionamiento
- `DETENER_SISTEMA.bat` - Detener el sistema
- `INSTALAR_DEPENDENCIAS.bat` - Instalar dependencias

### 🔍 **Scripts de Diagnóstico**
- `test-sql-connection.py` - Verificación completa
- `VERIFICAR_SISTEMA_SIMPLE.py` - Verificación básica

---

## ⚙️ **CONFIGURACIÓN TÉCNICA**

### 🖥️ **Backend (Django)**
- **Puerto**: 8000
- **Base de datos**: SQL Server Express
- **Autenticación**: JWT
- **API**: REST completa

### 🎨 **Frontend (React)**
- **Puerto**: 5173
- **Framework**: React + Vite
- **UI**: Tailwind CSS
- **Estado**: React Query

### 🗄️ **Base de Datos**
- **Servidor**: 192.168.1.124:1433
- **Base de datos**: postventa_system
- **Usuario**: postventa_user
- **Motor**: SQL Server Express

---

## 🛠️ **SOLUCIÓN DE PROBLEMAS**

### ❌ **Sistema no inicia**
1. Ejecutar `INSTALAR_DEPENDENCIAS.bat`
2. Verificar que Python portable esté instalado
3. Verificar que Node.js esté instalado
4. Verificar conexión a SQL Server

### ❌ **Error de base de datos**
1. Verificar que SQL Server esté ejecutándose en `192.168.1.124:1433`
2. Verificar credenciales en `backend/apps/core/settings.py`
3. Verificar conexión de red

### ❌ **Frontend no carga**
1. Verificar que Node.js esté instalado
2. Ejecutar `cd frontend && npm install`
3. Verificar puerto 5173 disponible

---

## 📊 **FUNCIONALIDADES**

### ✅ **Sistema de Autenticación**
- Login/logout seguro
- Roles y permisos
- Sesiones con timeout
- JWT tokens

### ✅ **Gestión de Usuarios**
- CRUD completo
- Asignación de roles
- Gestión de departamentos
- Historial de actividades

### ✅ **Gestión de Incidentes**
- Creación y edición
- Estados y prioridades
- Asignación de responsables
- Adjuntos de documentos

### ✅ **Sistema de Reportes**
- Dashboard interactivo
- Reportes de calidad
- Reportes para proveedores
- Exportación a PDF/Excel

---

## 🎯 **COMANDOS ÚTILES**

### 🔍 **Verificación Manual**
```bash
# Verificar backend
python-portable\python\python.exe -c "import requests; r = requests.get('http://192.168.1.234:8000/'); print(r.status_code)"

# Verificar frontend
python-portable\python\python.exe -c "import requests; r = requests.get('http://192.168.1.234:5173/'); print(r.status_code)"

# Verificar login
python-portable\python\python.exe -c "import requests; r = requests.post('http://192.168.1.234:8000/api/auth/login/', json={'username': 'jdiaz', 'password': 'adminJDR'}); print(r.status_code)"
```

### 🛠️ **Mantenimiento**
```bash
# Detener todos los procesos
taskkill /f /im python.exe
taskkill /f /im node.exe

# Verificar procesos
tasklist | findstr python
tasklist | findstr node
```

---

## 📞 **SOPORTE**

### 🔍 **Logs del Sistema**
- **Backend**: Consola de Django
- **Frontend**: Consola de Vite
- **Base de datos**: SQL Server logs

### 🆘 **Contacto**
- **Sistema**: PostVenta v1.0.0
- **Fecha**: 2025-01-10
- **Estado**: Producción

---

**¡Sistema listo para producción!** 🚀
