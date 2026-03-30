from apps.incidents.models import Responsible
print("Forcing update for Marco...")
# Marco Montenegro -> 4
# Chaned filter to avoid syntax error
cnt = Responsible.objects.filter(name__icontains='Marco').filter(name__icontains='Montenegro').update(sap_technician_id=4)
print(f"Updated {cnt} Marco Montenegro.")
