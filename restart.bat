@echo off
cd "C:\portafolio miguel leon\SIGIREC"
timeout /t 2 /nobreak >nul
taskkill /F /IM python.exe 2>nul
timeout /t 1 /nobreak >nul
start "SIGIREC" "C:\portafolio miguel leon\SIGIREC\venv\Scripts\python.exe" app.py
timeout /t 5 /nobreak >nul
echo Servidor iniciando en http://127.0.0.1:5000