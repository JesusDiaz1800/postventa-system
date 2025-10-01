#!/usr/bin/env python3
"""
Script to setup shared folder structure for Postventa System
"""

import os
import sys
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

def set_permissions(shared_path):
    """Set appropriate permissions for the shared folder"""
    try:
        # This is a placeholder - actual permission setting depends on OS
        print(f"📝 Note: Set appropriate permissions for: {shared_path}")
        print("   - Read/Write access for application users")
        print("   - Network access if using UNC path")
        return True
    except Exception as e:
        print(f"⚠️  Warning: Could not set permissions: {e}")
        return False

def main():
    if len(sys.argv) != 2:
        print("Usage: python setup-shared-folder.py <shared_folder_path>")
        print("Examples:")
        print("  python setup-shared-folder.py \\\\servidor\\compartido\\postventa")
        print("  python setup-shared-folder.py C:\\shared\\postventa")
        print("  python setup-shared-folder.py /shared/postventa")
        sys.exit(1)
    
    shared_path = sys.argv[1]
    
    print("🚀 Setting up shared folder for Postventa System")
    print(f"📁 Target path: {shared_path}")
    print()
    
    # Create folder structure
    if create_shared_folder_structure(shared_path):
        # Set permissions
        set_permissions(shared_path)
        
        print("\n📋 Next steps:")
        print("1. Update your .env file with:")
        print(f"   SHARED_FOLDER_PATH={shared_path}")
        print("2. Ensure the application has read/write access to this folder")
        print("3. If using UNC path, ensure network access is configured")
        print("4. Start the application with SQL Server configuration")
        
    else:
        print("\n❌ Failed to create shared folder structure")
        sys.exit(1)

if __name__ == "__main__":
    main()
