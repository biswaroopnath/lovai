@echo off
:: This script was generated to run the installation steps provided.
:: Since the commands provided are PowerShell-based, we use PowerShell to execute them.

powershell -NoProfile -ExecutionPolicy Bypass -Command ^
"Set-ExecutionPolicy Unrestricted -Scope Process; ^
python -m venv venv; ^
. .\venv\Scripts\Activate.ps1; ^
pip install -r requirements.txt; ^
curl -L -o kobolcpp/koboldcpp.exe https://github.com/LostRuins/koboldcpp/releases/download/v1.108.2/koboldcpp.exe; ^
cd frontend; ^
npm install"

echo.
echo Installation process completed.
pause
