import os
import sys
# Ensure backend folder is on sys.path so 'apps' package (backend/apps) can be imported
THIS_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(THIS_DIR, '..'))
BACKEND_DIR = os.path.join(REPO_ROOT, 'backend')
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

os.environ.setdefault('DJANGO_SETTINGS_MODULE','apps.core.settings')
import django
django.setup()
from django.db import connection

with connection.cursor() as cur:
    print('--- INFORMATION_SCHEMA COLUMNS for incidents (categoria / categoria_id) ---')
    cur.execute("SELECT COLUMN_NAME, DATA_TYPE, CHARACTER_MAXIMUM_LENGTH, IS_NULLABLE FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME='incidents' AND COLUMN_NAME IN ('categoria','categoria_id')")
    rows = cur.fetchall()
    if not rows:
        print('No rows found (columns may not exist yet)')
    else:
        for r in rows:
            print(r)

    print('\n--- SAMPLE DISTINCT categoria values (top 50) ---')
    try:
        cur.execute("SELECT DISTINCT TOP 50 categoria FROM incidents WHERE categoria IS NOT NULL ORDER BY categoria")
        for r in cur.fetchall():
            print(r)
    except Exception as e:
        print('Error selecting categoria:', e)

    print('\n--- SAMPLE categoria_id values (top 50) ---')
    try:
        cur.execute("SELECT TOP 50 categoria_id FROM incidents")
        for r in cur.fetchall():
            print(r)
    except Exception as e:
        print('Error selecting categoria_id:', e)

    print('\n--- COUNT of incidents and NULL categoria_id ---')
    try:
        cur.execute("SELECT COUNT(*) FROM incidents")
        total = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM incidents WHERE categoria_id IS NULL")
        nulls = cur.fetchone()[0]
        print(f'Total incidents: {total}, categoria_id NULLs: {nulls}')
    except Exception as e:
        print('Error counting incidents:', e)
