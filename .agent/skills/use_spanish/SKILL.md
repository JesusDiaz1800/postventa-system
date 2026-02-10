---
name: Siempre Español
description: Obliga al agente a generar todo el contenido, planes, artefactos y respuestas en Español.
---

# Reglas de Idioma Español

Esta skill define la política de idioma para todas las interacciones.

## Instrucciones Obligatorias

1.  **Idioma Principal**: Todo el contenido generado para el usuario debe ser en **Español**.
2.  **Artefactos**:
    *   **Planes (`implementation_plan.md`)**: Títulos, descripciones y contenido en español.
    *   **Tareas (`task.md`)**: Descripciones de tareas en español.
    *   **Guías (`walkthrough.md`)**: Explicaciones paso a paso en español.
3.  **Comunicación**:
    *   Resúmenes de estado (`task_boundary`): En español.
    *   Mensajes directos (`notify_user`): En español.
    *   Comentarios en código: Se permite inglés si es el estándar del proyecto, pero la documentación explicativa debe ser en español.

## Excepciones
*   Código fuente (nombres de variables, funciones, palabras clave).
*   Mensajes de error técnicos literales.
