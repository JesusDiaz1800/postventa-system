# 🚀 Configuración de Inicio Automático - Sistema Postventa

## 📋 **Archivos Creados para Inicio Automático:**

### **1. `install_autostart.bat`** - Instalar inicio automático
- Crea una tarea programada en Windows
- Se ejecuta automáticamente al iniciar el servidor
- Configura el servicio para ejecutarse como SYSTEM

### **2. `uninstall_autostart.bat`** - Desinstalar inicio automático
- Elimina la tarea programada
- Detiene el inicio automático

### **3. `check_autostart.bat`** - Verificar estado
- Muestra si el inicio automático está activo
- Verifica la configuración de la tarea

### **4. `start_postventa_service.bat`** - Script de inicio
- Script que se ejecuta automáticamente
- Inicia el servidor Django
- Configurado para acceso remoto

## 🔧 **Instrucciones de Instalación:**

### **PASO 1: Instalar Inicio Automático**
```bash
# En el servidor remoto, ejecutar como Administrador:
install_autostart.bat
```

### **PASO 2: Verificar Instalación**
```bash
# Verificar que se instaló correctamente:
check_autostart.bat
```

### **PASO 3: Probar Funcionamiento**
```bash
# Reiniciar el servidor y verificar que:
# 1. El sistema se inicie automáticamente
# 2. La aplicación esté disponible en http://192.168.1.234:8000
```

## 🛠️ **Comandos de Gestión:**

### **Verificar Estado:**
```bash
check_autostart.bat
```

### **Desinstalar:**
```bash
uninstall_autostart.bat
```

### **Reinstalar:**
```bash
uninstall_autostart.bat
install_autostart.bat
```

## 📊 **Ventajas del Inicio Automático:**

- ✅ **Sin intervención manual** - Se inicia automáticamente
- ✅ **Disponible 24/7** - Siempre accesible
- ✅ **Recuperación automática** - Se reinicia si falla
- ✅ **Profesional** - Comportamiento de servidor real

## 🔍 **Verificación Post-Instalación:**

1. **Reiniciar el servidor**
2. **Esperar 2-3 minutos** (tiempo de inicio)
3. **Acceder desde cualquier PC:** `http://192.168.1.234:8000`
4. **Verificar que la aplicación cargue correctamente**

## ⚠️ **Notas Importantes:**

- **Ejecutar como Administrador** para crear la tarea programada
- **El servidor debe estar en la misma ubicación** siempre
- **No mover la carpeta del proyecto** después de la instalación
- **Verificar que Python esté en el PATH** del sistema

## 🆘 **Solución de Problemas:**

### **Si no se inicia automáticamente:**
```bash
# 1. Verificar la tarea:
check_autostart.bat

# 2. Reinstalar:
uninstall_autostart.bat
install_autostart.bat

# 3. Verificar permisos de administrador
```

### **Si hay errores de Python:**
```bash
# Verificar que Python esté instalado y en el PATH
python --version
```

¡Con esta configuración, el sistema estará disponible automáticamente cada vez que se encienda el servidor!
