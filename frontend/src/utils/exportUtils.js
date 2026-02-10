/**
 * Export utilities for data export functionality
 * Supports CSV and Excel-like export
 */

/**
 * Export data to CSV file
 * @param {Array} data - Array of objects to export
 * @param {string} filename - Name of the file (without extension)
 * @param {Array} columns - Column configuration [{key: 'field', label: 'Header'}]
 */
export const exportToCSV = (data, filename, columns) => {
    if (!data || data.length === 0) {
        console.warn('No data to export');
        return;
    }

    // Build header row
    const headers = columns.map(col => `"${col.label}"`).join(',');

    // Build data rows
    const rows = data.map(item => {
        return columns.map(col => {
            let value = item[col.key];

            // Handle nested properties (e.g., 'related_incident.code')
            if (col.key.includes('.')) {
                const keys = col.key.split('.');
                value = keys.reduce((obj, key) => obj?.[key], item);
            }

            // Format value
            if (value === null || value === undefined) {
                value = '';
            } else if (typeof value === 'object') {
                value = JSON.stringify(value);
            } else if (typeof value === 'string') {
                // Escape quotes and wrap in quotes
                value = `"${value.replace(/"/g, '""')}"`;
            }

            return value;
        }).join(',');
    });

    // Combine and create blob
    const csvContent = [headers, ...rows].join('\n');
    const blob = new Blob(['\ufeff' + csvContent], { type: 'text/csv;charset=utf-8;' });

    // Download
    downloadBlob(blob, `${filename}.csv`);
};

/**
 * Export data to Excel XML format (compatible with Excel)
 * @param {Array} data - Array of objects to export
 * @param {string} filename - Name of the file (without extension)
 * @param {Array} columns - Column configuration [{key: 'field', label: 'Header', width: 100}]
 * @param {string} sheetName - Name of the Excel sheet
 */
export const exportToExcel = (data, filename, columns, sheetName = 'Datos') => {
    if (!data || data.length === 0) {
        console.warn('No data to export');
        return;
    }

    // Create XML spreadsheet
    let xml = `<?xml version="1.0" encoding="UTF-8"?>
<?mso-application progid="Excel.Sheet"?>
<Workbook xmlns="urn:schemas-microsoft-com:office:spreadsheet"
    xmlns:ss="urn:schemas-microsoft-com:office:spreadsheet">
  <Styles>
    <Style ss:ID="Header">
      <Font ss:Bold="1" ss:Color="#FFFFFF"/>
      <Interior ss:Color="#2563EB" ss:Pattern="Solid"/>
      <Alignment ss:Horizontal="Center"/>
    </Style>
    <Style ss:ID="Date">
      <NumberFormat ss:Format="yyyy-mm-dd"/>
    </Style>
    <Style ss:ID="Number">
      <NumberFormat ss:Format="#,##0"/>
    </Style>
  </Styles>
  <Worksheet ss:Name="${sheetName}">
    <Table>`;

    // Column widths
    columns.forEach(col => {
        xml += `<Column ss:Width="${col.width || 100}"/>`;
    });

    // Header row
    xml += '<Row>';
    columns.forEach(col => {
        xml += `<Cell ss:StyleID="Header"><Data ss:Type="String">${escapeXml(col.label)}</Data></Cell>`;
    });
    xml += '</Row>';

    // Data rows
    data.forEach(item => {
        xml += '<Row>';
        columns.forEach(col => {
            let value = item[col.key];

            // Handle nested properties
            if (col.key.includes('.')) {
                const keys = col.key.split('.');
                value = keys.reduce((obj, key) => obj?.[key], item);
            }

            // Determine type and format
            let type = 'String';
            let styleId = '';

            if (value === null || value === undefined) {
                value = '';
            } else if (typeof value === 'number') {
                type = 'Number';
                styleId = ' ss:StyleID="Number"';
            } else if (value instanceof Date || (typeof value === 'string' && isDateString(value))) {
                type = 'String';
                value = formatDate(value);
            } else if (typeof value === 'object') {
                value = JSON.stringify(value);
            }

            xml += `<Cell${styleId}><Data ss:Type="${type}">${escapeXml(String(value))}</Data></Cell>`;
        });
        xml += '</Row>';
    });

    xml += '</Table></Worksheet></Workbook>';

    // Download
    const blob = new Blob([xml], { type: 'application/vnd.ms-excel' });
    downloadBlob(blob, `${filename}.xls`);
};

/**
 * Export incidents data
 */
export const exportIncidents = (incidents, filename = 'incidencias') => {
    const columns = [
        { key: 'code', label: 'Código', width: 80 },
        { key: 'fecha_reporte', label: 'Fecha', width: 100 },
        { key: 'cliente', label: 'Cliente', width: 150 },
        { key: 'obra', label: 'Obra', width: 150 },
        { key: 'provider', label: 'Proveedor', width: 120 },
        { key: 'sku', label: 'SKU', width: 100 },
        { key: 'lote', label: 'Lote', width: 80 },
        { key: 'estado', label: 'Estado', width: 80 },
        { key: 'prioridad', label: 'Prioridad', width: 80 },
        { key: 'descripcion', label: 'Descripción', width: 250 },
    ];

    exportToExcel(incidents, filename, columns, 'Incidencias');
};

/**
 * Export reports statistics
 */
export const exportReportStats = (stats, filename = 'estadisticas') => {
    const summaryData = [
        { metrica: 'Total Incidencias', valor: stats.total },
        { metrica: 'Abiertos', valor: stats.abiertos },
        { metrica: 'En Laboratorio', valor: stats.laboratorio },
        { metrica: 'En Proveedor', valor: stats.proveedor },
        { metrica: 'Cerrados', valor: stats.cerrados },
        { metrica: 'Tasa de Resolución', valor: `${stats.resolutionRate}%` },
        { metrica: 'Tiempo Promedio (días)', valor: stats.avgResolutionDays },
    ];

    const columns = [
        { key: 'metrica', label: 'Métrica', width: 150 },
        { key: 'valor', label: 'Valor', width: 100 },
    ];

    exportToExcel(summaryData, filename, columns, 'Estadísticas');
};

// Helper functions
const downloadBlob = (blob, filename) => {
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(link.href);
};

const escapeXml = (str) => {
    if (!str) return '';
    return str
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&apos;');
};

const isDateString = (str) => {
    if (typeof str !== 'string') return false;
    return /^\d{4}-\d{2}-\d{2}/.test(str);
};

const formatDate = (value) => {
    try {
        const date = new Date(value);
        return date.toLocaleDateString('es-ES');
    } catch {
        return value;
    }
};
