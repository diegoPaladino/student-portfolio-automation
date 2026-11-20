@echo off
setlocal
cd /d "%~dp0"
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\ambiente.ps1" iniciar
if errorlevel 1 pause
exit /b %errorlevel%
