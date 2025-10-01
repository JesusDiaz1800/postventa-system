# Módulo de Gestión de Documentos

Sistema completo de generación y gestión de documentos para el sistema de control de calidad, desarrollado con WeasyPrint, Jinja2 y python-docx.

## 🚀 Características Principales

### Tecnologías Utilizadas
- **WeasyPrint**: Generación de PDFs profesionales desde HTML/CSS
- **Jinja2**: Renderizado de plantillas dinámicas
- **python-docx**: Generación y manipulación de documentos Word
- **Pillow**: Procesamiento de imágenes
- **Transformers**: IA para análisis de imágenes y mejora de redacción

### Flujo de Trabajo
1. **Registro de Incidencia**: El usuario registra una incidencia desde la app
2. **Generación Word**: El sistema rellena una plantilla base en Word
3. **Edición**: El usuario puede editar el documento generado
4. **Conversión HTML**: El sistema convierte el documento a HTML internamente
5. **Generación PDF**: Se genera el PDF final con WeasyPrint usando CSS profesional

## 📁 Estructura del Módulo

```
document_manager/
├── __init__.py              # Inicialización del módulo
├── core.py                  # Gestor principal de documentos
├── templates.py             # Gestor de plantillas HTML/Word
├── ai_processor.py          # Procesador de IA para análisis
├── file_manager.py          # Gestor de archivos y biblioteca
├── api.py                   # API REST para integración
├── test_module.py           # Script de pruebas
├── requirements.txt         # Dependencias
└── README.md               # Este archivo
```

## 🛠️ Instalación

### 1. Instalar Dependencias
```bash
pip install -r document_manager/requirements.txt
```

### 2. Configurar Variables de Entorno
```bash
# Para IA (opcional)
export HUGGINGFACE_API_KEY="tu_api_key_aqui"
```

### 3. Integrar con Django
```python
# En settings.py
INSTALLED_APPS = [
    # ... otras apps
    'document_manager',
]

# URLs
from document_manager.api import *
```

## 🎯 Funcionalidades

### Generación de Documentos
- **Documentos Word**: Generación desde plantillas con datos dinámicos
- **PDFs Profesionales**: Conversión con diseño corporativo
- **Plantillas Personalizables**: Sistema de plantillas HTML/CSS
- **Imágenes Integradas**: Inserción automática de imágenes

### Análisis con IA
- **Análisis de Imágenes**: Detección automática de posibles causas
- **Mejora de Redacción**: Reescritura profesional y sutil
- **Clasificación**: Categorización automática de imágenes
- **Resúmenes**: Generación automática de resúmenes técnicos

### Gestión de Archivos
- **Biblioteca de Documentos**: Organización por fecha y tipo
- **Carpeta Compartida**: Sincronización con red empresarial
- **Metadatos**: Trazabilidad completa de documentos
- **Búsqueda**: Sistema de búsqueda avanzada

## 📖 Uso del Módulo

### Ejemplo Básico
```python
from document_manager import DocumentManager

# Inicializar gestor
doc_manager = DocumentManager()

# Contexto de datos
contexto = {
    'incident_code': 'INC-2025-0001',
    'client_name': 'Constructora ABC',
    'description': 'Descripción del problema',
    # ... más datos
}

# Generar documento completo
resultado = doc_manager.generar_documento_completo(contexto)
print(f"Word: {resultado['docx']}")
print(f"PDF: {resultado['pdf']}")
```

### API REST
```python
# Generar documento completo
POST /api/documents/generate/
{
    "contexto": {...},
    "imagenes": [...],
    "tipo_documento": "incident_report"
}

# Obtener biblioteca
GET /api/documents/library/

# Descargar documento
GET /api/documents/download/{tipo}/{filename}
```

## 🎨 Plantillas Disponibles

### 1. Informe de Incidencia
- **Archivo**: `incident_report.html`
- **Uso**: Reportes de incidencias técnicas
- **Campos**: Código, cliente, descripción, acciones, recomendaciones

### 2. Informe de Visita
- **Archivo**: `visit_report.html`
- **Uso**: Reportes de visitas técnicas
- **Campos**: Orden, cliente, observaciones, datos de máquinas

### 3. Informe de Laboratorio
- **Archivo**: `lab_report.html`
- **Uso**: Análisis de laboratorio
- **Campos**: Ensayos, conclusiones, recomendaciones

### 4. Informe de Proveedor
- **Archivo**: `supplier_report.html`
- **Uso**: Comunicación con proveedores
- **Campos**: Análisis técnico, recomendaciones, mejoras

## 🤖 Funciones de IA

### Análisis de Imágenes
```python
# Analizar imágenes
analisis = ai_processor.analizar_imagenes(['imagen1.jpg', 'imagen2.jpg'])
print(analisis)
```

### Mejora de Redacción
```python
# Mejorar redacción
contexto_mejorado = ai_processor.maquillar_redaccion(contexto)
```

### Generación de Resúmenes
```python
# Generar resumen
resumen = ai_processor.generar_resumen_ia(contexto, imagenes)
```

## 📊 Características del Diseño

### PDFs Profesionales
- **Logo Corporativo**: Integración del logo de Polifusión
- **Colores Corporativos**: #126FCC (azul), #10B981 (verde)
- **Tipografía**: Helvetica para máxima legibilidad
- **Tablas**: Diseño profesional con filas alternadas
- **Imágenes**: Integración automática con descripciones

### CSS Profesional
```css
/* Colores corporativos */
.primary-color { color: #126FCC; }
.secondary-color { color: #10B981; }

/* Tablas profesionales */
.professional-table {
    border-collapse: collapse;
    width: 100%;
}

/* Headers con logo */
.header {
    background-color: #126FCC;
    color: white;
    padding: 20px;
}
```

## 🔧 Configuración Avanzada

### Personalizar Plantillas
```python
# Crear plantilla personalizada
template_manager.create_custom_template(
    'mi_plantilla',
    '<html>...</html>',
    'html'
)
```

### Configurar IA
```python
# Configurar modelos de IA
ai_processor.models = {
    'image_caption': 'mi-modelo-personalizado',
    'text_generation': 'mi-modelo-texto'
}
```

### Gestión de Archivos
```python
# Configurar rutas
file_manager.base_path = '/ruta/personalizada'
file_manager.shared_path = '\\\\servidor\\compartido'
```

## 🧪 Pruebas

### Ejecutar Pruebas Completas
```bash
python document_manager/test_module.py
```

### Pruebas Individuales
```python
# Probar gestor de documentos
from document_manager.test_module import test_document_manager
test_document_manager()

# Probar plantillas
from document_manager.test_module import test_templates
test_templates()
```

## 📈 Rendimiento

### Optimizaciones
- **Caché de Plantillas**: Plantillas compiladas en memoria
- **Procesamiento Asíncrono**: IA en segundo plano
- **Compresión de Imágenes**: Optimización automática
- **Limpieza Automática**: Archivos temporales

### Métricas
- **Tiempo de Generación**: < 5 segundos por documento
- **Tamaño de PDF**: < 2MB promedio
- **Calidad de Imagen**: 85% JPEG para balance calidad/tamaño

## 🔒 Seguridad

### Control de Acceso
- **Autenticación**: Integración con sistema de usuarios
- **Permisos**: Control granular por tipo de documento
- **Auditoría**: Registro completo de acciones

### Protección de Datos
- **Encriptación**: Archivos sensibles encriptados
- **Backup**: Copias de seguridad automáticas
- **Retención**: Políticas de retención de documentos

## 🚀 Despliegue

### Requisitos del Sistema
- **Python**: 3.10+
- **Memoria**: 4GB RAM mínimo
- **Almacenamiento**: 10GB para biblioteca
- **Red**: Acceso a Hugging Face API (opcional)

### Variables de Entorno
```bash
# Configuración base
DOCUMENT_BASE_PATH=/ruta/documentos
SHARED_NETWORK_PATH=\\\\servidor\\compartido

# IA (opcional)
HUGGINGFACE_API_KEY=tu_api_key
AI_ENABLED=true
```

## 📞 Soporte

### Logs y Debugging
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Monitoreo
- **Logs**: Registro detallado de operaciones
- **Métricas**: Estadísticas de uso
- **Alertas**: Notificaciones de errores

## 🎯 Roadmap

### Próximas Funcionalidades
- [ ] Integración con Microsoft Office 365
- [ ] Análisis de sentimientos en texto
- [ ] Traducción automática
- [ ] OCR para documentos escaneados
- [ ] Firma digital avanzada

### Mejoras Planificadas
- [ ] Interfaz web para gestión
- [ ] API GraphQL
- [ ] Integración con SharePoint
- [ ] Análisis predictivo
- [ ] Automatización de workflows

---

**Desarrollado para Polifusión S.A. - Sistema de Control de Calidad**  
*Versión 1.0.0 - 2025*
