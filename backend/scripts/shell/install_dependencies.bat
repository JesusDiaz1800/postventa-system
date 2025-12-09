@echo off
echo ========================================
echo   INSTALANDO DEPENDENCIAS DE DOCUMENTOS
echo ========================================

echo.
echo [1/3] Activando entorno virtual...
call venv\Scripts\activate.bat

echo.
echo [2/3] Instalando paquetes de documentos...
pip install python-docx==1.1.0
pip install docxtpl==0.16.7
pip install docxcompose==1.4.0

echo.
echo [3/3] Verificando instalación...
python -c "from docx import Document; print('✅ python-docx instalado correctamente')"
python -c "from docxtpl import DocxTemplate; print('✅ docxtpl instalado correctamente')"
python -c "import docxcompose; print('✅ docxcompose instalado correctamente')"

echo.
echo ========================================
echo   INSTALACIÓN COMPLETADA
echo ========================================
echo.
echo Ahora puedes ejecutar: python manage.py runserver 0.0.0.0:8000
echo.
pause
