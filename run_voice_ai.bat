@echo off
setlocal enabledelayedexpansion

:: ------------------------------------------------------------
:: Voice AI System Launch Script
:: ------------------------------------------------------------
:: This script launches:
::   1. KoboldCpp LLM server (port 5001)
::   2. FastAPI backend (port 8001) – includes TTS and STT (faster-whisper)
::   3. Frontend (React dev server)
:: ------------------------------------------------------------

:: ---- 1/3: Start KoboldCpp ------------------------------------------------
echo [1/3] Starting KoboldCpp LLM Server on port 5001...
set "MODEL_NAME=MN-12B-Mag-Mell-R1.Q5_K_M.gguf"
rem You can change MODEL_NAME to another .gguf model if desired
start "KoboldCpp Server" "%~dp0kobolcpp\koboldcpp.exe" --model "%~dp0kobolcpp\koboldcpp_gguf_models\!MODEL_NAME!" --port 5001 --gpulayers 100

:: Give KoboldCpp a moment to spin up
echo Waiting for KoboldCpp to initialize (10 seconds)...
timeout /t 10 /nobreak > nul

:: ---- 2/3: Start FastAPI Backend -------------------------------------------
echo [2/3] Starting FastAPI Backend (port 8001)...
rem The backend script runs uvicorn internally when executed directly
start "Voice AI Backend" "%~dp0venv\Scripts\python.exe" "%~dp0backend\main.py"

:: ---- 3/3: Start Frontend ---------------------------------------------------
echo [3/3] Starting Frontend (React dev server)...
pushd "%~dp0frontend"
start "Voice AI Frontend" cmd /c "npm run dev"
popd

:: ------------------------------------------------------------
:: Summary
:: ------------------------------------------------------------
echo.
echo ======================================================
echo  Voice AI System is launching in separate windows.
echo  - KoboldCpp: http://localhost:5001

echo  - Backend   : http://localhost:8001

echo  - Frontend  : http://localhost:5173 (React dev server)
echo ======================================================
echo.

:: Open the frontend in the default browser after a short delay
timeout /t 5 /nobreak > nul
start http://localhost:5173/

pause
