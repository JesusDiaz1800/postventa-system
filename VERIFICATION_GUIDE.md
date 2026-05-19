# Guía de Verificación Post-Despliegue

## Paso 1: Verificar Backend en Ejecución

### Opción A: Si el servidor NO está corriendo
```powershell
cd C:\Users\jdiaz\Desktop\postventa-system\backend
C:\Users\jdiaz\Desktop\postventa-system\python-portable\python\python.exe manage.py runserver
```

### Opción B: Si el servidor YA está corriendo
1. **Detener el servidor** (Ctrl+C en la terminal donde está corriendo)
2. **Reiniciar**:
```powershell
C:\Users\jdiaz\Desktop\postventa-system\python-portable\python\python.exe manage.py runserver
```
> ⚠️ **IMPORTANTE**: El reinicio es necesario para cargar el nuevo endpoint `/api/ai/generate-text/`

---

## Paso 2: Verificar Frontend en Ejecución

```powershell
cd C:\Users\jdiaz\Desktop\postventa-system\frontend
npm run dev
```

---

## Paso 3: Prueba de Integración Completa

### 3.1 Crear Reporte de Calidad
1. Navegar a: `http://localhost:5173` (o tu puerto de frontend)
2. Ir a **Reportes de Calidad** → **Nuevo Reporte Cliente**
3. Seleccionar una incidencia con escalamiento a calidad

### 3.2 Completar Formulario con Datos Técnicos
**Sección: Especificaciones de Producto**
- Diámetro: `110 mm`
- PN: `10`
- SDR: `11`
- Material: `HDPE PE100`
- Lote: `ABC123456`

**Sección: Condiciones de Instalación**
- Método de Unión: `Termofusión`
- Temperatura Ambiente: `20 °C`
- Estado de Herramientas: `Calibradas`
- ID de Máquina: `TF-001`

**Sección: Protocolo de Pruebas**
- Inspección Visual: `Conforme`
- Prueba de Presión: `Realizada`
- Presión de Prueba: `15 Bar`
- Duración: `30 min`
- Resultado: `Aprobada`

**Sección: Ensayos de Laboratorio** (completar AL MENOS 2):
- Melt Index: `0.3 g/10min`
- Densidad: `0.950 g/cm³`
- TIO: `180 °C`
- DSC: `130 °C`

### 3.3 Adjuntar Imágenes (OPCIONAL pero recomendado)
- **Img. Producto/Lote**: Foto de la tubería con el lote impreso
- **Img. Instalación**: Foto del sitio de instalación
- **Img. Prueba Presión**: Captura del manómetro durante la prueba
- **Img. Ensayos**: Gráfico o foto de los resultados de laboratorio

### 3.4 Guardar y Generar PDF
1. Click en **"Generar Análisis con IA"** (debe responder sin error 404)
2. Click en **"Finalizar y Guardar"**
3. Click en **"Ver PDF Generado"**

---

## Paso 4: Validaciones Esperadas

### ✅ El PDF debe mostrar:
- [ ] Tablas profesionales con las especificaciones del producto
- [ ] Tabla de condiciones de instalación
- [ ] Tabla de protocolo de pruebas con veredictos visuales
- [ ] **Tabla de Ensayos de Laboratorio** con 8 parámetros
- [ ] **Imágenes intercaladas** en las secciones correspondientes
- [ ] Fecha, firmas y metadatos profesionales

### ✅ El endpoint de IA debe:
- [ ] Responder sin error 404
- [ ] Generar análisis de causa raíz
- [ ] Sugerir acciones correctivas
- [ ] Presentar texto profesional y técnico

---

## Paso 5: Verificación de Base de Datos

```powershell
cd C:\Users\jdiaz\Desktop\postventa-system\backend
C:\Users\jdiaz\Desktop\postventa-system\python-portable\python\python.exe verify_db_columns.py
```

**Salida esperada**:
```
Physical columns in documents_documentattachment: [..., 'section']
'section' exists physically.
```

---

## Problemas Comunes y Soluciones

### Problema: Error 404 en `/api/ai/generate-text/`
**Solución**: Reiniciar el servidor backend (ver Paso 1, Opción B)

### Problema: Error de columna `section`
**Solución**: Re-aplicar migración
```powershell
python manage.py migrate documents 0009
python manage.py migrate documents 0010
```

### Problema: PDF no se genera automáticamente
**Solución**: Verificar que el ID del reporte se haya creado correctamente
- Revisar Network Tab en DevTools del navegador
- Confirmar que la respuesta del POST tenga un campo `id`

---

## 📊 Checklist de Aceptación Final

- [ ] Backend reiniciado y corriendo en puerto 8000
- [ ] Frontend corriendo en puerto 5173
- [ ] Reporte de calidad creado con éxito
- [ ] Ensayos de laboratorio guardados correctamente
- [ ] Imágenes asociadas a secciones específicas
- [ ] PDF generado automáticamente
- [ ] PDF descargado y visualizado correctamente
- [ ] Endpoint de IA responde sin errores
- [ ] Análisis de causa raíz generado con éxito

---

**Si todos los checks están completos**: 🎉 **SISTEMA LISTO PARA PRODUCCIÓN**

**Si hay algún error**: Reportar en el chat con el mensaje de error completo y el paso donde ocurrió.
