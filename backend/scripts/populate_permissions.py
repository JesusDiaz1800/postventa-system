from apps.users.models import RolePermission
from apps.users.permissions import ROLE_PERMISSIONS

def calculate_accessible_pages(permissions):
    """
    Simulate get_accessible_pages logic based on a permission dict
    """
    accessible_pages = ['dashboard', 'profile']
    
    if permissions.get('can_manage_users'):
        accessible_pages.append('users')
        
    if permissions.get('can_manage_incidents') or permissions.get('can_view_reports'):
        accessible_pages.extend(['incidents', 'incidents/list'])
        
    if permissions.get('can_manage_workflows'):
        accessible_pages.append('workflows')
        
    if permissions.get('can_manage_documents'):
        accessible_pages.append('documents')
        
    if permissions.get('can_view_audit_logs'):
        accessible_pages.append('audit')
        
    if permissions.get('can_view_reports'):
        accessible_pages.append('reports')
        
    if permissions.get('can_view_supplier_reports'):
        accessible_pages.extend(['reports/supplier', 'documents/supplier-reports'])
        
    return list(set(accessible_pages)) # Remove duplicates

def populate():
    print("Iniciando población de permisos...")
    
    for role, perms in ROLE_PERMISSIONS.items():
        # Enhance permissions for admin
        if role == 'admin':
            perms['can_reopen_incidents'] = True
        else:
            perms['can_reopen_incidents'] = False
            
        print(f"Procesando rol: {role}")
        
        pages = calculate_accessible_pages(perms)
        
        # Use defaults instead of create/update only on role to allow re-running
        obj, created = RolePermission.objects.update_or_create(
            role=role,
            defaults={
                'permissions': perms,
                'accessible_pages': pages
            }
        )
        
        action = "Creado" if created else "Actualizado"
        print(f"- {action}: {role}")
        print(f"  - Permisos: {len(perms)}")
        print(f"  - Páginas: {len(pages)}")

if __name__ == "__main__":
    populate()
