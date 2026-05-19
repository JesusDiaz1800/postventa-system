@echo off
echo =======================================================
echo          LIMPIANDO BASES DE DATOS SQLITE RESIDUALES
echo =======================================================
echo.
echo Eliminando archivos *.sqlite3 en %~dp0...
del /S /Q *.sqlite3
echo.
echo =======================================================
echo                 LIMPIEZA FINALIZADA
echo =======================================================
pause
