# ✅ DEBUG DE DOCUMENTOS IMPLEMENTADO - DIAGNÓSTICO COMPLETO

## 🎯 **PROBLEMA IDENTIFICADO**

**Problema Principal:**
- Los documentos no aparecen en la página central de documentos
- Existen documentos en las páginas de reportes de visita y reportes de calidad
- Las queries no están funcionando correctamente
- Falta de diagnóstico para identificar el problema

## 🚀 **SOLUCIÓN DE DEBUG IMPLEMENTADA**

### **✅ 1. DEBUG COMPLETO DE QUERIES**

#### **Console.log Detallado para Cada Endpoint:**
```javascript
// ✅ Debug completo de todas las queries
console.log('=== DEBUGGING DOCUMENT QUERIES ===');
console.log('Documents response:', documentsResponse.data); // Debug
console.log('Visit reports response:', visitReportsResponse.data); // Debug
console.log('Supplier reports response:', supplierReportsResponse.data); // Debug
console.log('Quality reports response:', qualityReportsResponse.data); // Debug
console.log('Lab reports response:', labReportsResponse.data); // Debug
console.log('Shared documents response:', sharedDocumentsResponse.data); // Debug
console.log('Real files response:', realFilesResponse.data); // Debug
```

#### **Verificación de Estado de Endpoints:**
```javascript
// ✅ Verificar si hay errores en las respuestas
if (documentsResponse.data && Array.isArray(documentsResponse.data)) {
  console.log('✅ Documents endpoint working, found:', documentsResponse.data.length, 'documents');
} else {
  console.log('❌ Documents endpoint not working or empty');
}

if (visitReportsResponse.data && Array.isArray(visitReportsResponse.data)) {
  console.log('✅ Visit reports endpoint working, found:', visitReportsResponse.data.length, 'reports');
} else {
  console.log('❌ Visit reports endpoint not working or empty');
}

if (qualityReportsResponse.data && Array.isArray(qualityReportsResponse.data)) {
  console.log('✅ Quality reports endpoint working, found:', qualityReportsResponse.data.length, 'reports');
} else {
  console.log('❌ Quality reports endpoint not working or empty');
}
```

### **✅ 2. QUERY DE RESPALDO ALTERNATIVA**

#### **Endpoints Alternativos para Obtener Documentos:**
```javascript
// ✅ Query de respaldo para obtener documentos de manera alternativa
const { 
  data: alternativeDocuments = [], 
  isLoading: alternativeLoading 
} = useQuery({
  queryKey: ['alternative-documents'],
  queryFn: async () => {
    try {
      console.log('=== TRYING ALTERNATIVE ENDPOINTS ===');
      
      // Intentar diferentes endpoints alternativos
      const alternativeEndpoints = [
        '/documents/real-files/',
        '/documents/shared/',
        '/documents/statistics/',
        '/documents/dashboard/'
      ];
      
      const results = [];
      for (const endpoint of alternativeEndpoints) {
        try {
          const response = await api.get(endpoint);
          console.log(`✅ ${endpoint} working:`, response.data);
          if (response.data && Array.isArray(response.data)) {
            results.push(...response.data);
          } else if (response.data && typeof response.data === 'object') {
            // Si es un objeto, intentar extraer documentos
            if (response.data.documents) {
              results.push(...response.data.documents);
            } else if (response.data.results) {
              results.push(...response.data.results);
            }
          }
        } catch (error) {
          console.log(`❌ ${endpoint} failed:`, error.message);
        }
      }
      
      console.log('Alternative documents found:', results);
      return results;
    } catch (error) {
      console.error('Error fetching alternative documents:', error);
      return [];
    }
  },
});
```

### **✅ 3. COMBINACIÓN MEJORADA DE DOCUMENTOS**

#### **Incluir Documentos Alternativos:**
```javascript
// ✅ Combinar todos los documentos incluyendo alternativos
const combinedDocuments = useMemo(() => {
  const baseDocs = Array.isArray(allDocuments) ? allDocuments : [];
  const attachments = Array.isArray(incidentAttachments) ? incidentAttachments : [];
  const alternative = Array.isArray(alternativeDocuments) ? alternativeDocuments : [];
  
  const combined = [...baseDocs, ...attachments, ...alternative];
  console.log('=== FINAL COMBINED DOCUMENTS ===');
  console.log('Base documents:', baseDocs.length);
  console.log('Attachments:', attachments.length);
  console.log('Alternative documents:', alternative.length);
  console.log('Total combined:', combined.length);
  console.log('Combined documents with attachments:', combined); // Debug
  return combined;
}, [allDocuments, incidentAttachments, alternativeDocuments]);
```

### **✅ 4. BOTÓN DE DEBUG MANUAL**

#### **Botón para Probar Endpoints Manualmente:**
```javascript
// ✅ Botón de debug manual para probar endpoints
<button
  onClick={async () => {
    console.log('=== MANUAL DEBUG TEST ===');
    try {
      const testEndpoints = [
        '/documents/',
        '/documents/visit-reports/',
        '/documents/quality-reports/',
        '/documents/real-files/',
        '/documents/shared/'
      ];
      
      for (const endpoint of testEndpoints) {
        try {
          const response = await api.get(endpoint);
          console.log(`✅ ${endpoint}:`, response.data);
        } catch (error) {
          console.log(`❌ ${endpoint}:`, error.message);
        }
      }
    } catch (error) {
      console.error('Manual debug error:', error);
    }
  }}
  className="inline-flex items-center px-6 py-3 text-sm font-semibold text-red-600 bg-red-100 rounded-xl hover:bg-red-200 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2 transition-all duration-200 shadow-lg hover:shadow-xl"
>
  🔍 Debug Endpoints
</button>
```

### **✅ 5. ENDPOINTS ADICIONALES PROBADOS**

#### **Nuevos Endpoints Incluidos:**
```javascript
// ✅ Endpoints adicionales para obtener documentos
const [
  documentsResponse,
  visitReportsResponse,
  supplierReportsResponse,
  qualityReportsResponse,
  labReportsResponse,
  sharedDocumentsResponse,
  realFilesResponse  // ✅ Nuevo endpoint
] = await Promise.all([
  api.get('/documents/').catch(() => ({ data: [] })),
  api.get('/documents/visit-reports/').catch(() => ({ data: [] })),
  api.get('/documents/supplier-reports/').catch(() => ({ data: [] })),
  api.get('/documents/quality-reports/').catch(() => ({ data: [] })),
  api.get('/documents/lab-reports/').catch(() => ({ data: [] })),
  api.get('/documents/shared/').catch(() => ({ data: [] })),
  api.get('/documents/real-files/').catch(() => ({ data: [] }))  // ✅ Nuevo endpoint
]);
```

## 📊 **FUNCIONALIDADES DE DEBUG IMPLEMENTADAS**

### **✅ Diagnóstico Completo:**
1. **Console.log detallado** - Para cada endpoint y respuesta
2. **Verificación de estado** - Si los endpoints funcionan o fallan
3. **Conteo de documentos** - Cuántos documentos se encuentran
4. **Mensajes de estado** - ✅ para éxito, ❌ para fallo

### **✅ Endpoints Alternativos:**
1. **Query de respaldo** - Endpoints alternativos si los principales fallan
2. **Múltiples fuentes** - Diferentes formas de obtener documentos
3. **Extracción inteligente** - De objetos y arrays de respuesta
4. **Manejo de errores** - Fallbacks automáticos

### **✅ Debug Manual:**
1. **Botón de debug** - Para probar endpoints manualmente
2. **Prueba de endpoints** - Todos los endpoints importantes
3. **Console.log detallado** - Resultados de cada prueba
4. **Identificación de problemas** - Qué endpoints funcionan y cuáles no

### **✅ Combinación Mejorada:**
1. **Documentos base** - De queries principales
2. **Adjuntos** - De incidencias
3. **Documentos alternativos** - De endpoints de respaldo
4. **Debug de combinación** - Conteo detallado de cada fuente

## 🎯 **INSTRUCCIONES DE USO**

### **✅ Para Diagnosticar el Problema:**

1. **Abrir la consola del navegador** (F12)
2. **Ir a la página de documentos**
3. **Hacer clic en "🔍 Debug Endpoints"**
4. **Revisar los mensajes de console.log**
5. **Identificar qué endpoints funcionan y cuáles fallan**

### **✅ Mensajes a Buscar:**

- **✅ [endpoint] working:** - Endpoint funciona correctamente
- **❌ [endpoint] failed:** - Endpoint no funciona
- **Base documents: X** - Documentos encontrados en query principal
- **Attachments: X** - Adjuntos encontrados
- **Alternative documents: X** - Documentos alternativos encontrados
- **Total combined: X** - Total de documentos combinados

### **✅ Pasos de Diagnóstico:**

1. **Verificar endpoints principales** - Si `/documents/` funciona
2. **Verificar endpoints de reportes** - Si `/documents/visit-reports/` funciona
3. **Verificar endpoints alternativos** - Si `/documents/real-files/` funciona
4. **Revisar combinación final** - Si se combinan correctamente
5. **Identificar el problema** - Qué endpoint específico falla

## 🎯 **RESULTADO ESPERADO**

**✅ DIAGNÓSTICO COMPLETO IMPLEMENTADO**

### **✅ Funcionalidades de Debug:**
- ✅ **Console.log detallado** - Para cada endpoint y respuesta
- ✅ **Verificación de estado** - Si los endpoints funcionan
- ✅ **Query de respaldo** - Endpoints alternativos
- ✅ **Botón de debug manual** - Para probar endpoints
- ✅ **Combinación mejorada** - Incluye todas las fuentes
- ✅ **Debug de combinación** - Conteo detallado

### **✅ Diagnóstico Disponible:**
- ✅ **Endpoints principales** - `/documents/`, `/documents/visit-reports/`, etc.
- ✅ **Endpoints alternativos** - `/documents/real-files/`, `/documents/shared/`
- ✅ **Adjuntos de incidencias** - `/documents/incident-attachments/`
- ✅ **Combinación final** - Todos los documentos unidos
- ✅ **Debug manual** - Botón para probar todos los endpoints

**Estado: ✅ DEBUG DE DOCUMENTOS COMPLETAMENTE IMPLEMENTADO**

El sistema ahora tiene debug completo implementado para diagnosticar por qué no aparecen los documentos. Usa el botón "🔍 Debug Endpoints" y revisa la consola para identificar qué endpoints funcionan y cuáles fallan.
