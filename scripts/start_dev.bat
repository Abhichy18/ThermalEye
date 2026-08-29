@echo off
TITLE ThermalEye — Unified Startup System (FastAPI + Next.js 15)
echo ======================================================================
echo           THERMALEYE (SIH 2026 / NTRO SIH26162YELLOW)
echo ======================================================================
echo Starting ThermalEye Production FastAPI Backend on http://localhost:8000...
start "ThermalEye FastAPI Backend" cmd /k "cd /d %~dp0\.. && .venv\Scripts\python -m uvicorn app.backend.main:app --host 0.0.0.0 --port 8000 --reload"

timeout /t 2 /nobreak >nul

echo Starting ThermalEye Next.js 15 HUD Frontend on http://localhost:3000...
start "ThermalEye Next.js Frontend" cmd /k "cd /d %~dp0\..\app\frontend && npm run dev"

echo.
echo ======================================================================
echo [SYSTEM ONLINE]
echo  - Command Dashboard:       http://localhost:3000
echo  - Field & Citizen Portal:  http://localhost:3000/citizen
echo  - FastAPI Swagger Docs:    http://localhost:8000/docs
echo ======================================================================
pause
