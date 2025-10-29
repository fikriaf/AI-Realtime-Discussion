@echo off
echo ========================================
echo AI Voice Assistant - Complete Startup
echo ========================================
echo.

echo Starting Backend Server...
start "Backend Server" cmd /k python backend_realtime.py

timeout /t 3 /nobreak >nul

echo Starting Web Server...
start "Web Server" cmd /k python -m http.server 8080

timeout /t 2 /nobreak >nul

echo Opening Browser...
start http://localhost:8080/BUKA_DUAL.html

echo.
echo ========================================
echo All services started!
echo ========================================
echo.
echo Backend: http://localhost:8000
echo Web UI: http://localhost:8080/BUKA_DUAL.html
echo.
echo Close the terminal windows to stop services
echo.
pause
