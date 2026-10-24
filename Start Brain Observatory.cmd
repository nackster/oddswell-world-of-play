@echo off
title OddsWell Admin Console
cd /d "%~dp0"

where py >nul 2>nul
if not errorlevel 1 (
  py -3 brain_admin\server.py
  exit /b
)

where python >nul 2>nul
if not errorlevel 1 (
  python brain_admin\server.py
  exit /b
)

set "CODEX_PYTHON=%USERPROFILE%\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
if exist "%CODEX_PYTHON%" (
  "%CODEX_PYTHON%" brain_admin\server.py
  exit /b
)

echo Python 3 was not found. Install Python 3 or open this project through Codex once.
pause
