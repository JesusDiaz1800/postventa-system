// Configuración de endpoints para alternar entre producción y prueba
const USE_TEST_ENDPOINTS = false; // Cambiar a false para usar endpoints normales

const ENDPOINTS = {
  // Endpoints normales (con autenticación)
  normal: {
    generatePolifusionIncidentReport: '/api/documents/generate-polifusion-incident-report/',
    generatePolifusionVisitReport: '/api/documents/generate-polifusion-visit-report/',
    generatePolifusionIncidentReportPDF: '/api/documents/generate-polifusion-incident-report-pdf/',
    generatePolifusionVisitReportPDF: '/api/documents/generate-polifusion-visit-report-pdf/',
  },

  // Endpoints de prueba (sin autenticación)
  test: {
    generatePolifusionIncidentReport: '/api/documents/test/generate-polifusion-incident-report/',
    generatePolifusionVisitReport: '/api/documents/test/generate-polifusion-visit-report/',
    generatePolifusionIncidentReportPDF: '/api/documents/generate-polifusion-incident-report-pdf/',
    generatePolifusionVisitReportPDF: '/api/documents/generate-polifusion-visit-report-pdf/',
  }
};

// Función para obtener el endpoint correcto
export const getEndpoint = (endpointName) => {
  const endpointGroup = USE_TEST_ENDPOINTS ? 'test' : 'normal';
  return ENDPOINTS[endpointGroup][endpointName];
};

// Función para obtener headers (con o sin autenticación)
export const getHeaders = () => {
  const headers = {
    'Content-Type': 'application/json',
  };

  // Solo agregar autenticación si no estamos usando endpoints de prueba
  if (!USE_TEST_ENDPOINTS) {
    const token = localStorage.getItem('access_token');
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }
  }

  return headers;
};

export default ENDPOINTS;
