import React from 'react';
import UnifiedReportPage from '../components/UnifiedReportPage';
import CreateSupplierReportModal from '../components/CreateSupplierReportModal';
import SupplierResponseModal from '../components/SupplierResponseModal';
import SupplierClosureModal from '../components/SupplierClosureModal';

/**
 * Página unificada para gestión de reportes de proveedores
 * Utiliza el componente UnifiedReportPage para consistencia
 */
const SupplierReportsPageUnified = () => {
  return (
    <UnifiedReportPage
      reportType="supplier-reports"
      reportTitle="Reportes de Proveedores"
      reportDescription="Gestiona reportes de proveedores, adjunta respuestas y cierra incidencias"
      createModal={CreateSupplierReportModal}
      responseModal={SupplierResponseModal}
      closureModal={SupplierClosureModal}
    />
  );
};

export default SupplierReportsPageUnified;
