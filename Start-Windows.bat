@echo off
setlocal
chcp 65001 >nul
cd /d "%~dp0"

set "PS_SCRIPT=%~dp0start_windows.ps1"
if not exist "%PS_SCRIPT%" (
  echo ERROR: start_windows.ps1 not found.
  pause
  exit /b 1
)

powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%PS_SCRIPT%"
set "EXIT_CODE=%ERRORLEVEL%"

if not "%EXIT_CODE%"=="0" (
  echo.
  echo Exit code: %EXIT_CODE%
  pause
  exit /b %EXIT_CODE%
)

echo.
echo Startup finished.
pause
exit /b 0
