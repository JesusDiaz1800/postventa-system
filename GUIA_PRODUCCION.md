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

## 🔄 Script de Inicio Principal

| Script | Función |
|--------|---------|
| `INICIAR_PM2.bat` | Inicia Backend + Frontend con PM2 |
| `INICIAR_PM2.bat stop` | Detiene todos los servicios |
| `INICIAR_PM2.bat restart` | Reinicia servicios |
| `INICIAR_PM2.bat status` | Ver estado de los procesos |
| `INICIAR_PM2.bat logs` | Ver logs en tiempo real |
| `INICIAR_PM2.bat monit` | Dashboard de monitoreo PM2 |

**Requisito:** PM2 instalado (`npm install -g pm2`)

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
# Iniciar con PM2
cd C:\Users\jdiaz\Desktop\postventa-system
INICIAR_PM2.bat start

# Detener
INICIAR_PM2.bat stop

# Ver estado
INICIAR_PM2.bat status

# Logs en tiempo real
INICIAR_PM2.bat logs
```

---

**Última actualización:** 2025-12-11
