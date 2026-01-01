@echo off
setlocal

:: Start Backend
echo Starting Backend...
start "WebUI Tester Backend" cmd /k "python backend/server.py"

:: Start Frontend
echo Starting Frontend...
cd frontend
start "WebUI Tester Frontend" cmd /k "npm run dev"

echo WebUI Tester started.
endlocal
