import React from 'react';
import UnifiedReportPage from '../components/UnifiedReportPage';
import CreateReportModal from '../components/CreateReportModal';
import EscalateReportModal from '../components/EscalateReportModal';

/**
 * Página unificada para gestión de reportes de calidad interna
 * Utiliza el componente UnifiedReportPage para consistencia
 */
const InternalQualityReportsPageUnified = () => {
  return (
    <UnifiedReportPage
      reportType="quality-reports"
      reportTitle="Reportes de Calidad Interna"
      reportDescription="Gestiona reportes de calidad interna, escala problemas y genera documentos"
      createModal={CreateReportModal}
      escalateModal={EscalateReportModal}
    />
  );
};

export default InternalQualityReportsPageUnified;
