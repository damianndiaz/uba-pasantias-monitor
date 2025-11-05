@echo off
echo ====================================
echo UBA PASANTIAS MONITOR - REVISION MANUAL
echo ====================================
cd /d "%~dp0"
echo Ejecutando revision manual...
echo.
".venv\Scripts\python.exe" scheduler.py --check
echo.
pause