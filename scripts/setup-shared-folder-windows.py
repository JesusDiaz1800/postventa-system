#!/usr/bin/env python3
"""
Script to setup shared folder structure for Postventa System on Windows
Specific configuration for \\192.168.1.161\Y:\postventa
"""

import os
import sys
import subprocess
from pathlib import Path

def create_shared_folder_structure(shared_path):
    """Create the folder structure in the shared location"""
    
    folders = [
        'documents',
        'images', 
        'incidents',
        'templates',
        'temp',
        'backups',
        'lab_reports'
    ]
    
    print(f"Creating folder structure in: {shared_path}")
    
    try:
        # Create main folder
        os.makedirs(shared_path, exist_ok=True)
        print(f"✅ Created main folder: {shared_path}")
        
        # Create subfolders
        for folder in folders:
            folder_path = os.path.join(shared_path, folder)
            os.makedirs(folder_path, exist_ok=True)
            print(f"✅ Created folder: {folder_path}")
            
            # Create incident subfolders
            if folder == 'incidents':
                for subfolder in ['images', 'documents', 'reports']:
                    subfolder_path = os.path.join(folder_path, subfolder)
                    os.makedirs(subfolder_path, exist_ok=True)
                    print(f"  ✅ Created subfolder: {subfolder_path}")
        
        # Create sample templates
        templates_path = os.path.join(shared_path, 'templates')
        sample_templates = [
            'cliente_informe.docx',
            'proveedor_carta.docx', 
            'lab_report.docx'
        ]
        
        for template in sample_templates:
            template_path = os.path.join(templates_path, template)
            if not os.path.exists(template_path):
                with open(template_path, 'w', encoding='utf-8') as f:
                    f.write(f"# {template}\n# This is a placeholder for the {template} template\n")
                print(f"✅ Created template placeholder: {template_path}")
        
        print(f"\n🎉 Shared folder structure created successfully!")
        print(f"📁 Main folder: {shared_path}")
        print(f"📋 Folders created: {len(folders)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating folder structure: {e}")
        return False

def test_network_access(shared_path):
    """Test network access to the shared folder"""
    try:
        # Test if we can access the shared folder
        test_file = os.path.join(shared_path, 'test_access.txt')
        with open(test_file, 'w') as f:
            f.write("Test access")
        
        if os.path.exists(test_file):
            os.remove(test_file)
            print(f"✅ Network access to {shared_path} is working")
            return True
        else:
            print(f"❌ Cannot write to {shared_path}")
            return False
            
    except Exception as e:
        print(f"❌ Network access test failed: {e}")
        return False

def map_network_drive(shared_path, drive_letter='Z'):
    """Map network drive (optional)"""
    try:
        # Extract server and share from UNC path
        # \\192.168.1.161\Y:\postventa -> \\192.168.1.161\Y
        parts = shared_path.split('\\')
        if len(parts) >= 4:
            server_share = f"\\\\{parts[2]}\\{parts[3]}"
            
            # Map network drive
            cmd = f'net use {drive_letter}: "{server_share}" /persistent:yes'
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"✅ Mapped network drive {drive_letter}: to {server_share}")
                return True
            else:
                print(f"⚠️  Could not map network drive: {result.stderr}")
                return False
        else:
            print(f"⚠️  Invalid UNC path format: {shared_path}")
            return False
            
    except Exception as e:
        print(f"⚠️  Error mapping network drive: {e}")
        return False

def set_permissions(shared_path):
    """Set appropriate permissions for the shared folder"""
    try:
        print(f"📝 Setting permissions for: {shared_path}")
        
        # Use icacls to set permissions (Windows)
        cmd = f'icacls "{shared_path}" /grant Everyone:(OI)(CI)F /T'
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ Permissions set successfully")
            return True
        else:
            print(f"⚠️  Warning: Could not set permissions: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"⚠️  Warning: Could not set permissions: {e}")
        return False

def main():
    # Fixed configuration for your setup
    shared_path = r"\\192.168.1.161\Y:\CONTROL DE CALIDAD\postventa"
    
    print("🚀 Setting up shared folder for Postventa System")
    print(f"📁 Target path: {shared_path}")
    print(f"🖥️  SQL Server: NB-JDIAZ25\\SQLEXPRESS")
    print()
    
    # Test network access first
    print("🔍 Testing network access...")
    if not test_network_access(shared_path):
        print("\n❌ Cannot access shared folder. Please check:")
        print("   1. Network connectivity to 192.168.1.161")
        print("   2. Share permissions on the server")
        print("   3. Windows credentials for network access")
        print("   4. Firewall settings")
        return False
    
    # Create folder structure
    if create_shared_folder_structure(shared_path):
        # Set permissions
        set_permissions(shared_path)
        
        print("\n📋 Configuration Summary:")
        print(f"   📁 Shared Folder: {shared_path}")
        print(f"   🗄️  SQL Server: NB-JDIAZ25\\SQLEXPRESS")
        print(f"   🗄️  Database: postventa_system")
        print(f"   🌐 Server IP: 192.168.1.161")
        print(f"   🚀 Frontend: http://192.168.1.161:3000")
        print(f"   🔧 Backend: http://192.168.1.161:8000")
        print(f"   📂 Control de Calidad: Y:\\CONTROL DE CALIDAD\\postventa")
        
        print("\n📋 Next steps:")
        print("1. ✅ Shared folder is ready")
        print("2. ✅ SQL Server database exists")
        print("3. 🚀 Run: docker-compose -f docker-compose-production.yml up -d")
        print("4. 👤 Login with: admin / admin123")
        print("5. 🔧 Configure AI providers in admin panel")
        
        return True
    else:
        print("\n❌ Failed to create shared folder structure")
        return False

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)
