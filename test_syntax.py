
import sys
import os

# Manual syntax check for the modified files
files_to_check = [
    r'c:\Users\jdiaz\Desktop\postventa-system\backend\apps\documents\services\professional_pdf_generator.py',
    r'c:\Users\jdiaz\Desktop\postventa-system\backend\apps\documents\serializers.py',
    r'c:\Users\jdiaz\Desktop\postventa-system\backend\apps\documents\document_generator_service.py'
]

for f in files_to_check:
    print(f"Checking {f}...")
    try:
        with open(f, 'r', encoding='utf-8') as file:
            compile(file.read(), f, 'exec')
        print("  OK")
    except Exception as e:
        print(f"  FAILED: {e}")
