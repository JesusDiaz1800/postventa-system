export const formatAnalysisResult = (content: string): string => {
    try {
        // Check if it's a JSON string by basic heuristics
        const trimmed = content.trim();
        if ((trimmed.startsWith('{') && trimmed.endsWith('}')) || (trimmed.startsWith('json') && trimmed.includes('{'))) {
            // Remove markdown code blocks if present (e.g. ```json ... ```)
            const jsonString = trimmed.replace(/^```json/, '').replace(/^```/, '').replace(/```$/, '');

            const data = JSON.parse(jsonString);

            // Check if it has the expected analysis fields
            if (data.observations || data.response || data.analysis || data.technical_analysis) {
                let formatted = '';

                if (data.severity_level) formatted += `**NIVEL DE GRAVEDAD:** ${data.severity_level}\n\n`;

                const obs = data.observations || data.description || data.analysis;
                if (obs) formatted += `**OBSERVACIONES:**\n${obs}\n\n`;

                if (data.possible_causes && Array.isArray(data.possible_causes)) {
                    formatted += `**POSIBLES CAUSAS:**\n${data.possible_causes.map((c: string) => `• ${c.replace(/\*\*/g, '')}`).join('\n')}\n\n`;
                }

                if (data.recommendations && Array.isArray(data.recommendations)) {
                    formatted += `**RECOMENDACIONES:**\n${data.recommendations.map((r: string) => `• ${r.replace(/\*\*/g, '')}`).join('\n')}\n\n`;
                }

                if (data.corrective_actions && Array.isArray(data.corrective_actions)) {
                    formatted += `**ACCIONES CORRECTIVAS:**\n${data.corrective_actions.map((r: string) => `• ${r.replace(/\*\*/g, '')}`).join('\n')}\n\n`;
                }

                // Fallback for generic response
                if (!formatted && data.response) return data.response;

                return formatted.trim() || content;
            }
        }
        return content;
    } catch (e) {
        // If parsing fails, return original content
        return content;
    }
};
