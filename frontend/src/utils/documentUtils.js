/**
 * Utilidades unificadas para manejo de documentos
 * Centraliza la lógica de apertura, descarga y gestión de documentos
 */
import { API_ORIGIN } from '../services/api';

/**
 * Abre un documento en el navegador
 * @param {Object} report - Objeto del reporte
 * @param {string} documentType - Tipo de documento (visit-report, quality-report, etc.)
 * @param {Function} showSuccess - Función para mostrar mensaje de éxito
 * @param {Function} showError - Función para mostrar mensaje de error
 */
export const openDocument = (report, documentType, showSuccess, showError) => {
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

    // Construir URL del documento
    let url;
    // Si el reporte ya tiene una URL de descarga pre-calculada, la usamos
    if (report.download_url) {
      // Aseguramos que tenga el origen correcto (si es relativa)
      url = report.download_url.startsWith('http')
        ? report.download_url
        : `${API_ORIGIN}${report.download_url}`;
    } else {
      // Fallback: construir URL manualmente
      const filename = report.pdf_filename || report.filename || report.title || 'documento.pdf';
      if (!filename || filename === 'undefined') {
        throw new Error('Nombre de archivo no válido');
      }
      const encodedFilename = encodeURIComponent(filename);
      url = `${API_ORIGIN}/api/documents/open/${documentType}/${incidentId}/${encodedFilename}`;
    }

    // Abrir documento en nueva pestaña
    const newWindow = window.open(url, '_blank');

    if (!newWindow) {
      throw new Error('No se pudo abrir la ventana. Verifica que los pop-ups estén permitidos.');
    }

    if (showSuccess) showSuccess('Documento abierto exitosamente');

  } catch (error) {
    console.error('Error opening document:', error);
    if (showError) showError(`Error al abrir el documento: ${error.message}`);
  }
};

/**
 * Descarga un documento
 * @param {Object} report - Objeto del reporte
 * @param {string} documentType - Tipo de documento
 * @param {Function} showSuccess - Función para mostrar mensaje de éxito
 * @param {Function} showError - Función para mostrar mensaje de error
 */
export const downloadDocument = (report, documentType, showSuccess, showError) => {
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

    // Construir URL del documento
    let url;
    let filename = report.pdf_filename || report.filename || report.title || 'documento.pdf';

    // Si el reporte ya tiene una URL de descarga pre-calculada y válida, la usamos
    if (report.download_url) {
      // Aseguramos que tenga el origen correcto (si es relativa)
      url = report.download_url.startsWith('http')
        ? report.download_url
        : `${API_ORIGIN}${report.download_url}`;

      // Intentamos extraer filename de la URL si no tenemos uno mejor
      if (!report.filename && !report.pdf_filename) {
        const parts = report.download_url.split('/');
        filename = decodeURIComponent(parts[parts.length - 1] || 'documento.pdf');
      }
    } else {
      // Fallback: construir URL manualmente
      if (!filename || filename === 'undefined') {
        throw new Error('Nombre de archivo no válido');
      }
      const encodedFilename = encodeURIComponent(filename);
      url = `${API_ORIGIN}/api/documents/open/${documentType}/${incidentId}/${encodedFilename}`;
    }

    // Crear enlace de descarga
    const link = document.createElement('a');
    link.href = url;
    link.download = filename;
    link.target = '_blank';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);

    if (showSuccess) showSuccess('Documento descargado exitosamente');

  } catch (error) {
    console.error('Error downloading document:', error);
    if (showError) showError(`Error al descargar el documento: ${error.message}`);
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

    if (showSuccess) showSuccess('Documento generado exitosamente');

  } catch (error) {
    console.error('Error generating document:', error);
    if (showError) showError(`Error al generar el documento: ${error.message}`);
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
