# 🚀 POSTVENTA SYSTEM - Guía de Despliegue a Producción

## 📋 Información del Sistema

| Elemento | Valor |
|----------|-------|
| **IP del Servidor** | `192.168.1.234` |
| **Puerto Backend** | `8000` |
| **Puerto Frontend** | `5173` (dev) / `80` (prod) |
| **URL para Usuarios** | `http://192.168.1.234:5173` |
| **Base de Datos** | SQL Server Express (`localhost\SQLEXPRESS`) |
| **DB Name** | `postventa_system` |

---

## 📧 Configuración de Correos

**Método:** Outlook COM Automation (win32com)

| Destino | Correos |
|---------|---------|
| **TO:** | `vlutz@polifusion.cl`, `cmunizaga@polifusion.cl` |
| **CC:** | `jdiaz@polifusion.cl`, `mmiranda@polifusion.cl`, `rcruz@polifusion.cl`, `pestay@polifusion.cl` |

**Archivo:** `backend/apps/incidents/services/email_service.py` (líneas 26-27, 65-66)

---

## 📁 Almacenamiento de Archivos

```
C:\Users\jdiaz\Desktop\postventa-system\backend\documentos\
├── visit_reports/           # PDFs de reportes de visita
├── shared_documents/        # Documentos subidos
└── ...
```

---

## 🔄 Scripts de Auto-Inicio (PENDIENTE EJECUTAR)

| Script | Ruta | Función |
|--------|------|---------|
| `start_postventa.bat` | `C:\Users\jdiaz\Desktop\postventa-system\` | Inicia Backend + Frontend |
| `stop_postventa.bat` | `C:\Users\jdiaz\Desktop\postventa-system\` | Detiene servicios |
| `configurar_inicio_automatico.bat` | `C:\Users\jdiaz\Desktop\postventa-system\` | Crea tarea programada |

### Pasos para Activar Auto-Inicio:
1. Clic derecho en `configurar_inicio_automatico.bat`
2. "Ejecutar como administrador"
3. Verificar que se creó la tarea en `taskschd.msc`

---

## 🔒 Firewall (EJECUTAR ANTES DE PRODUCCIÓN)

```cmd
netsh advfirewall firewall add rule name="Postventa Frontend" dir=in action=allow protocol=tcp localport=5173
netsh advfirewall firewall add rule name="Postventa Backend" dir=in action=allow protocol=tcp localport=8000
```

---

## ✅ Checklist Pre-Producción

- [ ] SQL Server Express instalado en escritorio remoto
- [ ] Base de datos migrada desde laptop
- [ ] SQL Server configurado como servicio automático
- [ ] Variables de entorno configuradas en `.env`
- [ ] Build de producción del frontend (`npm run build`)
- [ ] Firewall configurado (puertos 5173, 8000)
- [ ] Scripts de auto-inicio ejecutados
- [ ] Outlook configurado para envío de correos
- [ ] Prueba de acceso desde otro PC en la red

---

## 🔧 Comandos Útiles

```bash
# Iniciar manualmente
cd C:\Users\jdiaz\Desktop\postventa-system
start_postventa.bat

# Detener
stop_postventa.bat

# Ver tareas programadas
taskschd.msc

# Ver servicios
services.msc
```

---

**Última actualización:** 2025-12-11
