@echo off
echo ====================================
echo UBA PASANTIAS MONITOR - INICIO
echo ====================================
cd /d "%~dp0"
echo Cambiando al directorio del proyecto...
echo.
echo Iniciando monitor automatico...
echo Presiona Ctrl+C para detener
echo.
".venv\Scripts\python.exe" scheduler.py
pause