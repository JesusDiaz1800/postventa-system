# 🚀 Guía de Despliegue Remoto - Sistema Postventa

## 📋 Configuración Completada

### ✅ **Cambios Implementados:**

1. **Documentos dentro del proyecto** - Todos los documentos ahora se almacenan en `backend/documents/`
2. **Acceso universal** - Sin dependencias de carpetas compartidas externas
3. **Configuración remota** - Servidor configurado para IP `192.168.1.234:8000`
4. **URLs directas** - Los documentos se sirven directamente desde Django

### 🗂️ **Estructura de Documentos:**
```
backend/documents/
├── visit_reports/
│   ├── incident_78/
│   ├── incident_80/
│   ├── incident_83/
│   ├── incident_84/
│   ├── incident_85/
│   └── incident_86/
├── lab_reports/
├── supplier_reports/
│   └── incident_81/
├── quality_reports/
│   └── incident_81/
└── incident_attachments/
    ├── 83/
    └── 85/
```

## 🖥️ **Instrucciones para el Servidor Remoto**

### **1. Copiar el Proyecto al Servidor**
```bash
# En el servidor (192.168.1.234)
# Copiar toda la carpeta postventa-system al escritorio remoto
```

### **2. Configurar el Servidor**
```bash
# Ejecutar en el servidor:
setup_remote_server.bat
```

### **3. Acceso desde Cualquier PC**
- **URL:** `http://192.168.1.234:8000`
- **Usuarios:** Todos los usuarios de la red pueden acceder
- **Documentos:** Acceso directo sin dependencias externas

## 🔧 **Configuración Técnica**

### **Backend (Django):**
- ✅ Documentos servidos como archivos estáticos
- ✅ URLs directas: `/documents/visit_reports/incident_X/archivo.pdf`
- ✅ Configuración para acceso remoto
- ✅ Base de datos SQL Server Express

### **Frontend (React):**
- ✅ URLs directas para documentos
- ✅ Fallback a API si es necesario
- ✅ Interfaz optimizada para acceso remoto

## 📁 **Ventajas de la Nueva Configuración:**

1. **🌐 Acceso Universal** - Cualquier usuario puede acceder desde cualquier PC
2. **📂 Sin Dependencias** - No requiere carpetas compartidas externas
3. **🔒 Seguro** - Documentos dentro del proyecto, controlados por Django
4. **⚡ Rápido** - Servido directamente por Django
5. **🔄 Sincronizado** - Todos los usuarios ven los mismos documentos

## 🚀 **Comandos de Despliegue:**

### **Iniciar Servidor:**
```bash
start_remote_server.bat
```

### **Configurar Todo:**
```bash
setup_remote_server.bat
```

### **Verificar Estado:**
```bash
# Verificar que el servidor esté corriendo
# Acceder a: http://192.168.1.234:8000
```

## 📞 **Soporte:**
- **IP del Servidor:** 192.168.1.234
- **Puerto:** 8000
- **Acceso:** http://192.168.1.234:8000
- **Documentos:** Automáticamente disponibles para todos los usuarios
