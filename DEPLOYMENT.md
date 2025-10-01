# 🚀 Guía de Despliegue - Sistema Postventa

## 📋 Requisitos del Sistema

### Hardware Mínimo
- **CPU:** 4 cores
- **RAM:** 8 GB
- **Almacenamiento:** 50 GB SSD
- **Red:** Conexión estable a internet

### Software Requerido
- **Docker Desktop** 4.0+
- **Docker Compose** 2.0+
- **Git** 2.30+

## 🔧 Instalación y Configuración

### 1. Clonar el Repositorio
```bash
git clone <repository-url>
cd postventa-system
```

### 2. Configurar Variables de Entorno
```bash
# Copiar archivo de ejemplo
cp backend/env.example backend/.env

# Editar variables según tu entorno
nano backend/.env
```

### 3. Generar Certificados SSL (Opcional)
```bash
# Para desarrollo
scripts/generate-ssl.bat

# Para producción, usar certificados de CA confiable
```

## 🚀 Opciones de Despliegue

### Opción 1: Despliegue con Docker (Recomendado)
```bash
# Iniciar todos los servicios
scripts/start-production.bat

# O manualmente
docker-compose -f docker-compose-production.yml up -d
```

### Opción 2: Despliegue Local (Desarrollo)
```bash
# Iniciar servicios localmente
scripts/start-local.bat
```

## 🌐 URLs de Acceso

### Producción
- **Frontend:** https://192.168.1.161
- **Backend API:** https://192.168.1.161/api/
- **Admin Panel:** https://192.168.1.161/admin/

### Desarrollo
- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8000/api/
- **Admin Panel:** http://localhost:8000/admin/

## 👤 Credenciales por Defecto

### Administrador
- **Usuario:** admin
- **Contraseña:** admin123

⚠️ **IMPORTANTE:** Cambiar estas credenciales en producción.

## 📊 Monitoreo y Logs

### Ver Logs en Tiempo Real
```bash
# Todos los servicios
docker-compose -f docker-compose-production.yml logs -f

# Servicio específico
docker-compose -f docker-compose-production.yml logs -f backend
```

### Verificar Estado de Servicios
```bash
docker-compose -f docker-compose-production.yml ps
```

## 🔧 Comandos de Mantenimiento

### Backup de Base de Datos
```bash
# Backup automático (configurado en cron)
scripts/backup-automatic.sh

# Backup manual
docker-compose -f docker-compose-production.yml exec sqlserver /opt/mssql-tools/bin/sqlcmd -S localhost -U sa -P ikBZos7lEYVyGd_oNKkdkQ -Q "BACKUP DATABASE postventa_system TO DISK = '/var/opt/mssql/backup/postventa_backup.bak'"
```

### Actualizar Sistema
```bash
# Detener servicios
docker-compose -f docker-compose-production.yml down

# Actualizar código
git pull origin main

# Reconstruir imágenes
docker-compose -f docker-compose-production.yml build --no-cache

# Iniciar servicios
docker-compose -f docker-compose-production.yml up -d
```

### Limpiar Sistema
```bash
# Limpiar contenedores e imágenes no utilizadas
docker system prune -a

# Limpiar volúmenes (¡CUIDADO! Esto elimina datos)
docker volume prune
```

## 🛡️ Configuración de Seguridad

### 1. Cambiar Credenciales por Defecto
```bash
# Cambiar contraseña de base de datos
# Editar backend/.env
DB_PASSWORD=nueva_contraseña_segura

# Cambiar contraseña de admin
# Acceder a /admin/ y cambiar desde la interfaz
```

### 2. Configurar Firewall
```bash
# Permitir solo puertos necesarios
# 80 (HTTP)
# 443 (HTTPS)
# 22 (SSH) - solo si es necesario
```

### 3. Configurar SSL/TLS
```bash
# Para producción, reemplazar certificados autofirmados
# con certificados de una CA confiable (Let's Encrypt, etc.)
```

## 📈 Optimización de Rendimiento

### 1. Configuración de Base de Datos
- **Connection Pooling:** Configurado automáticamente
- **Índices:** Optimizados para consultas frecuentes
- **Backup:** Automático cada 24 horas

### 2. Configuración de Caché
- **Redis:** Configurado para sesiones y caché
- **TTL:** 1 hora para sesiones, 10 minutos para caché

### 3. Configuración de Nginx
- **Gzip:** Habilitado para compresión
- **Rate Limiting:** 10 req/s para API, 5 req/m para login
- **Caching:** Headers optimizados para archivos estáticos

## 🚨 Solución de Problemas

### Problema: Servicios no inician
```bash
# Verificar logs
docker-compose -f docker-compose-production.yml logs

# Verificar estado de Docker
docker info

# Reiniciar Docker Desktop
```

### Problema: Base de datos no conecta
```bash
# Verificar conectividad
docker-compose -f docker-compose-production.yml exec backend python test_db_connection.py

# Verificar configuración
docker-compose -f docker-compose-production.yml exec backend cat .env
```

### Problema: Frontend no carga
```bash
# Verificar logs del frontend
docker-compose -f docker-compose-production.yml logs frontend

# Verificar conectividad con backend
curl http://localhost:8000/api/
```

## 📞 Soporte

### Logs Importantes
- **Backend:** `/app/logs/django.log`
- **Nginx:** `/var/log/nginx/`
- **Docker:** `docker-compose logs`

### Información del Sistema
```bash
# Versión de Docker
docker --version

# Información del sistema
docker system info

# Uso de recursos
docker stats
```

## 🔄 Actualizaciones

### Proceso de Actualización
1. **Backup** de base de datos
2. **Detener** servicios
3. **Actualizar** código
4. **Reconstruir** imágenes
5. **Iniciar** servicios
6. **Verificar** funcionamiento

### Rollback
```bash
# Volver a versión anterior
git checkout <commit-hash>
docker-compose -f docker-compose-production.yml up -d
```

---

## 📝 Notas Adicionales

- **Backup automático:** Configurado para ejecutarse diariamente a las 2:00 AM
- **Logs rotativos:** Configurados para mantener 30 días de historial
- **Monitoreo:** Considerar implementar herramientas como Prometheus/Grafana para producción
- **Escalabilidad:** El sistema está preparado para escalado horizontal con load balancer
