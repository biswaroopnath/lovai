@echo off
setlocal enabledelayedexpansion

:: ------------------------------------------------------------
:: Voice AI System Launch Script
:: ------------------------------------------------------------
:: This script launches KoboldCpp, the Backend, and the Frontend.
:: It also waits for them to be ready and plays a startup greeting.
:: Pressing any key will shut down all associated processes.
:: ------------------------------------------------------------

:: Set window titles for easier management
set BACKEND_TITLE=VoiceAI_Backend
set FRONTEND_TITLE=VoiceAI_Frontend
set KOBOLD_WRAPPER_TITLE=VoiceAI_Kobold_Wrapper

:: ---- 1/3: Start KoboldCpp ------------------------------------------------
echo [1/3] Starting KoboldCpp LLM Server...
:: Using start to keep the wrapper in its own window
:: launch_kobold.py now handles running Kobold in the foreground of this new window
start "%KOBOLD_WRAPPER_TITLE%" "%~dp0venv\Scripts\python.exe" "%~dp0backend\launch_kobold.py"

:: ---- 2/3: Start FastAPI Backend -------------------------------------------
echo [2/3] Starting FastAPI Backend (port 8001)...
start "%BACKEND_TITLE%" "%~dp0venv\Scripts\python.exe" "%~dp0backend\main.py"

:: ---- 3/3: Start Frontend ---------------------------------------------------
echo [3/3] Starting Frontend (React dev server)...
pushd "%~dp0frontend"
start "%FRONTEND_TITLE%" cmd /c "npm run dev"
popd

:: ---- Monitoring and Greeting ----------------------------------------------
echo.
echo [*] System is initializing. Monitoring services for readiness...
echo [*] The character greeting will play automatically once endpoints are live.
echo.

:: Open the frontend in the default browser
echo [*] Launching browser...
start http://localhost:5173/
:: Run the greeting script in this window to show status and wait for readiness
"%~dp0venv\Scripts\python.exe" "%~dp0backend\startup_greeting.py"

:: ------------------------------------------------------------
:: Ready Summary
:: ------------------------------------------------------------
echo.
echo ======================================================
echo  Voice AI System is ACTIVE!
echo  - KoboldCpp: http://localhost:5001
echo  - Backend   : http://localhost:8001
echo  - Frontend  : http://localhost:5173
echo ======================================================
echo.



echo.
echo [!] PRESS ANY KEY TO SHUT DOWN ALL PROCESSES AND EXIT [!]
pause > nul

echo.
echo [*] Shutting down Voice AI System...

:: 1. Kill the Backend and Frontend by title
taskkill /F /FI "WINDOWTITLE eq %BACKEND_TITLE%*" /T > nul 2>&1
taskkill /F /FI "WINDOWTITLE eq %FRONTEND_TITLE%*" /T > nul 2>&1

:: 2. Kill the Kobold wrapper and the actual KoboldCpp executable
taskkill /F /FI "WINDOWTITLE eq %KOBOLD_WRAPPER_TITLE%*" /T > nul 2>&1
taskkill /F /IM koboldcpp.exe /T > nul 2>&1

:: 3. Kill any lingering python processes linked to these windows just in case
taskkill /F /IM python.exe /FI "WINDOWTITLE eq VoiceAI_*" /T > nul 2>&1

echo [+] All processes have been terminated.
echo.
pause
