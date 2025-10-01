# 🏢 CONFIGURACIÓN EMPRESARIAL - SISTEMA POSTVENTA

## 📋 **OPCIONES DE DEPLOYMENT**

### 🥇 **OPCIÓN 1: SERVIDOR EMPRESARIAL (RECOMENDADA)**

#### **Configuración del Servidor:**
```
Servidor Windows Server 2019/2022
├── IIS (Internet Information Services)
├── SQL Server Express/Standard
├── Python 3.11+
├── Node.js 18+
└── Carpeta Compartida: \\servidor\documentos\
```

#### **Estructura de Carpetas:**
```
\\servidor\documentos\
├── visit_report\
│   ├── incident_1\
│   ├── incident_2\
│   └── incident_N\
├── lab_report\
├── supplier_report\
└── quality_report\
```

#### **Configuración en settings.py:**
```python
# Carpeta compartida de red
SHARED_DOCUMENTS_PATH = r'\\servidor\documentos'

# O si es unidad mapeada
SHARED_DOCUMENTS_PATH = r'Z:\documentos'
```

### 🥈 **OPCIÓN 2: ESCRITORIO REMOTO**

#### **Configuración:**
```
Escritorio Windows 10/11 Pro
├── Aplicación Web (Puerto 80/443)
├── SQL Server Express
└── Carpeta Compartida: C:\Documentos\
```

#### **Configuración en settings.py:**
```python
SHARED_DOCUMENTS_PATH = r'C:\Documentos'
```

## 🔧 **CONFIGURACIÓN PASO A PASO**

### **1. Preparar el Servidor/Escritorio:**

```bash
# Instalar dependencias
pip install -r requirements.txt
npm install

# Configurar base de datos
python manage.py migrate
python manage.py createsuperuser
```

### **2. Configurar Carpeta Compartida:**

#### **En Windows Server:**
1. Crear carpeta `C:\Documentos`
2. Compartir carpeta con nombre `documentos`
3. Configurar permisos para usuarios del dominio
4. Mapear como `Z:` en el servidor

#### **Configuración en settings.py:**
```python
# Para servidor con carpeta compartida
SHARED_DOCUMENTS_PATH = r'\\servidor\documentos'

# Para escritorio local
SHARED_DOCUMENTS_PATH = r'C:\Documentos'
```

### **3. Configurar IIS (Servidor):**

```xml
<!-- web.config -->
<?xml version="1.0" encoding="utf-8"?>
<configuration>
  <system.webServer>
    <handlers>
      <add name="PythonHandler" path="*" verb="*" modules="FastCgiModule" scriptProcessor="C:\Python311\python.exe|C:\ruta\a\tu\app\wsgi.py" resourceType="Unspecified" />
    </handlers>
  </system.webServer>
</configuration>
```

### **4. Configurar Acceso de Red:**

#### **Para Personal Interno:**
```
URL: http://servidor-empresa/
Usuario: dominio\usuario
Contraseña: [contraseña del dominio]
```

#### **Para Acceso Remoto:**
```
URL: https://servidor-empresa.com/
VPN: [Configurar VPN empresarial]
```

## 🔐 **SEGURIDAD EMPRESARIAL**

### **1. Autenticación con Active Directory:**
```python
# settings.py
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'django_auth_ldap.backend.LDAPBackend',
]

import ldap
from django_auth_ldap.config import LDAPSearch, GroupOfNamesType

AUTH_LDAP_SERVER_URI = "ldap://servidor-dominio.local"
AUTH_LDAP_BIND_DN = "CN=usuario,CN=Users,DC=empresa,DC=local"
AUTH_LDAP_BIND_PASSWORD = "contraseña"
AUTH_LDAP_USER_SEARCH = LDAPSearch(
    "CN=Users,DC=empresa,DC=local",
    ldap.SCOPE_SUBTREE,
    "(sAMAccountName=%(user)s)"
)
```

### **2. Permisos por Roles:**
```python
# roles.py
ROLES_PERMISSIONS = {
    'admin': ['view_all', 'edit_all', 'delete_all'],
    'supervisor': ['view_all', 'edit_assigned'],
    'tecnico': ['view_assigned', 'upload_documents'],
    'cliente': ['view_own', 'upload_own']
}
```

## 📊 **BACKUP Y MANTENIMIENTO**

### **1. Backup Automático:**
```batch
@echo off
REM backup_daily.bat
set FECHA=%date:~-4,4%%date:~-10,2%%date:~-7,2%
xcopy "C:\Documentos" "\\backup\documentos\%FECHA%\" /E /I /Y
```

### **2. Monitoreo:**
```python
# monitoring.py
import psutil
import os

def check_system_health():
    # Verificar espacio en disco
    disk_usage = psutil.disk_usage('/')
    if disk_usage.percent > 90:
        send_alert("Espacio en disco bajo")
    
    # Verificar carpeta compartida
    if not os.path.exists(SHARED_DOCUMENTS_PATH):
        send_alert("Carpeta compartida no accesible")
```

## 🚀 **DEPLOYMENT RECOMENDADO**

### **Para Empresa Pequeña (1-10 usuarios):**
- **Escritorio Windows Pro** con carpeta compartida
- **Costo**: ~$500-1000
- **Mantenimiento**: Mínimo

### **Para Empresa Mediana (10-50 usuarios):**
- **Servidor Windows Server** con IIS
- **Costo**: ~$2000-5000
- **Mantenimiento**: Medio

### **Para Empresa Grande (50+ usuarios):**
- **Servidor dedicado** con alta disponibilidad
- **Costo**: ~$5000-15000
- **Mantenimiento**: Profesional

## 📞 **SOPORTE TÉCNICO**

### **Configuración Inicial:**
1. **Instalación**: 2-4 horas
2. **Configuración de red**: 1-2 horas
3. **Capacitación**: 2-3 horas
4. **Total**: 1 día laboral

### **Mantenimiento Mensual:**
- **Backup**: Automático
- **Actualizaciones**: 1-2 horas/mes
- **Monitoreo**: Continuo

---

## ✅ **RECOMENDACIÓN FINAL**

**Para tu empresa, recomiendo:**

1. **Servidor Windows Server** (si tienes 10+ usuarios)
2. **Carpeta compartida de red** para documentos
3. **Backup automático** diario
4. **Acceso VPN** para trabajo remoto

**¿Te ayudo a configurar alguna de estas opciones?**
