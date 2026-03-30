---
name: Evolution Tracker
description: Maintains a narrative history of the system's evolution, changes, and versions.
---

# Evolution Tracker

**USE THIS SKILL WHEN:**
*   You complete a significant task or milestone (e.g., "v4.0 Implemented").
*   You need to know what changed in previous versions to avoid regressions.
*   The user asks for a summary of recent changes or the "history" of the project.

**INSTRUCTIONS:**
1.  **READ THE HISTORY:**
    *   Read: `c:\Users\jdiaz\Desktop\postventa-system\.agent\memory\EVOLUTION_LOG.md`
    *   Understand the trajectory of the project.

2.  **LOG NEW MILESTONES:**
    *   **WHEN:** A major feature is completed, verified, and approved by the user.
    *   **ACTION:** Append a new entry to `EVOLUTION_LOG.md`.
    *   **FORMAT:**
        ```markdown
        ## v[Version]: [Title] ([Date])
        **Objetivo:** [One sentence goal]
        *   **[Component]:** [Detail of change]
        ```

3.  **MAINTAIN NARRATIVE:**
    *   Focus on the *impact* and *reasoning*, not just a list of commits.
    *   Example: "Switched to Gemini Flash Lite to save costs" (Good) vs "Changed API model string" (Bad).
