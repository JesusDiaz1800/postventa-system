/**
 * Normaliza una cadena de texto para búsquedas inteligentes.
 * - Elimina acentos/tildes.
 * - Convierte a minúsculas.
 * - Elimina espacios al inicio y final.
 * - Colapsa múltiples espacios internos a uno solo.
 * 
 * @param {string} str - La cadena a normalizar.
 * @returns {string} - La cadena normalizada.
 */
export const normalizeText = (str) => {
    if (!str || typeof str !== 'string') return '';

    return str
        .normalize('NFD') // Descompone caracteres con acentos (e.g., 'á' -> 'a' + '´')
        .replace(/[\u0300-\u036f]/g, '') // Elimina los diacríticos (acentos)
        .toLowerCase()
        .trim()
        .replace(/\s+/g, ' '); // Colapsa múltiples espacios en uno
};

/**
 * Compara dos cadenas de texto de forma "inteligente".
 * 
 * @param {string} text - El texto base.
 * @param {string} query - El término de búsqueda.
 * @returns {boolean} - True si hay coincidencia.
 */
export const smartIncludes = (text, query) => {
    const normalizedText = normalizeText(text);
    const normalizedQuery = normalizeText(query);

    return normalizedText.includes(normalizedQuery);
};
