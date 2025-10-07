/**
 * Utilidades unificadas para manejo de documentos
 * Centraliza la lógica de apertura, descarga y gestión de documentos
 */

/**
 * Abre un documento en el navegador
 * @param {Object} report - Objeto del reporte
 * @param {string} documentType - Tipo de documento (visit-report, quality-report, etc.)
 * @param {Function} showSuccess - Función para mostrar mensaje de éxito
 * @param {Function} showError - Función para mostrar mensaje de error
 */
export const openDocument = async (report, documentType, showSuccess, showError) => {
  try {
    // Validar parámetros requeridos
    if (!report) {
      throw new Error('Reporte no especificado');
    }
    
    if (!documentType) {
      throw new Error('Tipo de documento no especificado');
    }
    
    // Obtener ID de la incidencia
    const incidentId = report.related_incident?.id || report.incident_id;
    if (!incidentId) {
      throw new Error('ID de incidencia no encontrado');
    }
    
    // Obtener nombre del archivo
    const filename = report.pdf_filename || report.filename || report.title || 'documento.pdf';
    if (!filename || filename === 'undefined') {
      throw new Error('Nombre de archivo no válido');
    }
    
    // Codificar el nombre del archivo para manejar caracteres especiales
    const encodedFilename = encodeURIComponent(filename);
    
    // Construir URL del documento
    const { API_ORIGIN } = await import('../services/api');
    const url = `${API_ORIGIN}/api/documents/open/${documentType}/${incidentId}/${encodedFilename}`;
    
    // Abrir documento en nueva pestaña
    const newWindow = window.open(url, '_blank', 'noopener,noreferrer');
    
    if (!newWindow) {
      throw new Error('No se pudo abrir la ventana. Verifica que los pop-ups estén permitidos.');
    }
    
    showSuccess('Documento abierto exitosamente');
    
  } catch (error) {
    console.error('Error opening document:', error);
    showError(`Error al abrir el documento: ${error.message}`);
  }
};

/**
 * Descarga un documento
 * @param {Object} report - Objeto del reporte
 * @param {string} documentType - Tipo de documento
 * @param {Function} showSuccess - Función para mostrar mensaje de éxito
 * @param {Function} showError - Función para mostrar mensaje de error
 */
export const downloadDocument = async (report, documentType, showSuccess, showError) => {
  try {
    // Validar parámetros requeridos
    if (!report) {
      throw new Error('Reporte no especificado');
    }
    
    if (!documentType) {
      throw new Error('Tipo de documento no especificado');
    }
    
    // Obtener ID de la incidencia
    const incidentId = report.related_incident?.id || report.incident_id;
    if (!incidentId) {
      throw new Error('ID de incidencia no encontrado');
    }
    
    // Obtener nombre del archivo
    const filename = report.pdf_filename || report.filename || report.title || 'documento.pdf';
    if (!filename || filename === 'undefined') {
      throw new Error('Nombre de archivo no válido');
    }
    
    // Codificar el nombre del archivo
    const encodedFilename = encodeURIComponent(filename);
    
    // Construir URL del documento
    const { API_ORIGIN } = await import('../services/api');
    const url = `${API_ORIGIN}/api/documents/open/${documentType}/${incidentId}/${encodedFilename}`;
    
    // Crear enlace de descarga
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    link.target = '_blank';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    
    showSuccess('Documento descargado exitosamente');
    
  } catch (error) {
    console.error('Error downloading document:', error);
    showError(`Error al descargar el documento: ${error.message}`);
  }
};

/**
 * Genera un documento PDF
 * @param {Object} report - Objeto del reporte
 * @param {string} documentType - Tipo de documento
 * @param {Function} showSuccess - Función para mostrar mensaje de éxito
 * @param {Function} showError - Función para mostrar mensaje de error
 */
export const generateDocument = async (report, documentType, showSuccess, showError) => {
  try {
    if (!report || !report.id) {
      throw new Error('Reporte no válido');
    }
    
    if (!documentType) {
      throw new Error('Tipo de documento no especificado');
    }
    
    // Construir URL de generación
  const { API_ORIGIN } = await import('../services/api');
    const url = `${API_ORIGIN}/api/documents/generate/${documentType}/${report.id}/`;
    
    // Hacer petición para generar documento
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
        'Content-Type': 'application/json',
      },
    });
    
    if (!response.ok) {
      throw new Error('Error al generar el documento');
    }
    
    showSuccess('Documento generado exitosamente');
    
  } catch (error) {
    console.error('Error generating document:', error);
    showError(`Error al generar el documento: ${error.message}`);
  }
};

/**
 * Obtiene el tipo de documento basado en la ruta
 * @param {string} pathname - Ruta actual
 * @returns {string} Tipo de documento
 */
export const getDocumentTypeFromPath = (pathname) => {
  if (pathname.includes('visit-reports')) return 'visit-report';
  if (pathname.includes('quality-reports')) return 'quality-report';
  if (pathname.includes('supplier-reports')) return 'supplier-report';
  if (pathname.includes('lab-reports')) return 'lab-report';
  return 'document';
};

/**
 * Valida si un reporte tiene los datos necesarios para abrir documentos
 * @param {Object} report - Objeto del reporte
 * @returns {boolean} True si es válido
 */
export const isValidReportForDocument = (report) => {
  if (!report) return false;
  
  const incidentId = report.related_incident?.id || report.incident_id;
  const filename = report.pdf_filename || report.filename || report.title;
  
  return !!(incidentId && filename && filename !== 'undefined');
};

/**
 * Obtiene información del documento para debugging
 * @param {Object} report - Objeto del reporte
 * @returns {Object} Información del documento
 */
export const getDocumentInfo = (report) => {
  return {
    reportId: report?.id,
    incidentId: report?.related_incident?.id || report?.incident_id,
    filename: report?.pdf_filename || report?.filename || report?.title,
    documentType: report?.document_type,
    hasValidData: isValidReportForDocument(report)
  };
};
