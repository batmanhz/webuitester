@echo off
setlocal

echo Stopping WebUI Tester...

:: Kill Backend (Port 19000)
echo Killing Backend on port 19000...
for /f "tokens=5" %%a in ('netstat -aon ^| find ":19000" ^| find "LISTENING"') do (
    echo Killing PID %%a
    taskkill /f /pid %%a
)

:: Kill Frontend (Port 5173)
echo Killing Frontend on port 5173...
for /f "tokens=5" %%a in ('netstat -aon ^| find ":5173" ^| find "LISTENING"') do (
    echo Killing PID %%a
    taskkill /f /pid %%a
)

echo Done.
endlocal
