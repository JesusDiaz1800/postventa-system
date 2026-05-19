import os
import shutil

BASE_DIR = r"c:\Users\jdiaz\Desktop\sertec-system"

FILES_TO_DELETE = [
    # Pages
    r"frontend\src\pages\CreateIncident.tsx",
    r"frontend\src\pages\IncidentDetailView.tsx",
    r"frontend\src\pages\IncidentsControl.tsx",
    r"frontend\src\pages\ClientQualityReportsPage.tsx",
    r"frontend\src\pages\InternalQualityReportsPage.tsx",
    r"frontend\src\pages\QualityReportForm.tsx",
    r"frontend\src\pages\SupplierReportsPage.tsx",
    r"frontend\src\pages\SupplierReportForm.tsx",
    # Components
    r"frontend\src\components\IncidentAttachments.tsx",
    r"frontend\src\components\IncidentClosureForm.tsx",
    r"frontend\src\components\IncidentDocuments.tsx",
    r"frontend\src\components\IncidentImages.tsx",
    r"frontend\src\components\IncidentImagesViewer.tsx",
    r"frontend\src\components\IncidentSearchSelect.tsx",
    r"frontend\src\components\IncidentTimeline.tsx",
    r"frontend\src\components\DocumentsByIncident.tsx",
    r"frontend\src\components\SupplierReportAttachments.tsx",
]

DIRS_TO_DELETE = [
    r"backend\apps\incidents",
]

print("Iniciando PODA EXTREMA (Scorched Earth)...")

for f in FILES_TO_DELETE:
    path = os.path.join(BASE_DIR, f)
    if os.path.exists(path):
        os.remove(path)
        print(f"Borrando archivo: {f}")
    else:
        print(f"Archivo ya no existe: {f}")

for d in DIRS_TO_DELETE:
    path = os.path.join(BASE_DIR, d)
    if os.path.exists(path):
        shutil.rmtree(path, ignore_errors=True)
        print(f"Borrando directorio: {d}")
    else:
        print(f"Directorio ya no existe: {d}")

print("PODA EXTREMA COMPLETADA Exitósamente.")
