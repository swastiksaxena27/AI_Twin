@echo off
title AI Behavioral Guardian Launcher v3.0
color 0A
mode con: cols=90 lines=35

:: ======================================================
:: AI Behavioral Guardian Launcher
:: Fixed: correct backend entry point + npm run dev
:: ======================================================

set "ROOT=%~dp0"
set "VENV=%ROOT%venv\Scripts\activate"

:MENU
cls

echo.
echo  ========================================================================
echo                     AI BEHAVIORAL GUARDIAN
echo  ========================================================================
echo.
echo      Team : CodeudersZ
echo      Role : Machine Learning Engineer
echo.
echo  ========================================================================
echo.
echo      [1] Start Complete Project  (Backend + Frontend)
echo      [2] Start Backend API only
echo      [3] Start Monitoring Agent only
echo      [4] Start Frontend only
echo      [5] Train ML Model
echo      [6] Run Tests
echo      [7] Project Information
echo      [8] Stop All Services
echo      [9] Exit
echo.
echo  ========================================================================
echo.

set /p choice=Enter your choice: 

if "%choice%"=="1" goto STARTALL
if "%choice%"=="2" goto BACKEND
if "%choice%"=="3" goto AGENT
if "%choice%"=="4" goto FRONTEND
if "%choice%"=="5" goto TRAIN
if "%choice%"=="6" goto TEST
if "%choice%"=="7" goto INFO
if "%choice%"=="8" goto STOP
if "%choice%"=="9" exit

goto MENU

:: ======================================================
:: START EVERYTHING
:: ======================================================

:STARTALL
cls
echo  Starting Complete Project...
echo.

:: Initialize DB silently first
call "%VENV%" && python -m behavioral_guardian.database.connection >nul 2>&1

:: Backend in its own terminal
start "AG - Backend API" cmd /k "cd /d "%ROOT%" && call venv\Scripts\activate && uvicorn behavioral_guardian.backend.main:app --reload --port 8080"

:: Wait 3 seconds for backend to boot before starting frontend
timeout /t 3 /nobreak >nul

:: Frontend in its own terminal
start "AG - Frontend" cmd /k "cd /d "%ROOT%frontend" && npm run dev"

echo.
echo  [OK] Backend  -> http://localhost:8080/docs
echo  [OK] Frontend -> http://localhost:5173
echo.
timeout /t 4 /nobreak >nul

:: Open browser
start "" "http://localhost:5173"

pause
goto MENU

:: ======================================================
:: BACKEND ONLY
:: ======================================================

:BACKEND
cls
echo  Starting Backend API...
echo.

call "%VENV%" && python -m behavioral_guardian.database.connection >nul 2>&1
start "AG - Backend API" cmd /k "cd /d "%ROOT%" && call venv\Scripts\activate && uvicorn behavioral_guardian.backend.main:app --reload --port 8080"

echo.
echo  [OK] Backend -> http://localhost:8080/docs
echo.
pause
goto MENU

:: ======================================================
:: AGENT ONLY
:: ======================================================

:AGENT
cls
echo  Starting Monitoring Agent...
echo.

start "AG - Monitoring Agent" cmd /k "cd /d "%ROOT%" && call venv\Scripts\activate && python -m behavioral_guardian.agent.agent_runner"

echo.
echo  [OK] Agent started.
echo.
pause
goto MENU

:: ======================================================
:: FRONTEND ONLY
:: ======================================================

:FRONTEND
cls
echo  Starting Frontend...
echo.

start "AG - Frontend" cmd /k "cd /d "%ROOT%frontend" && npm run dev"

echo.
echo  [OK] Frontend -> http://localhost:5173
echo.
pause
goto MENU

:: ======================================================
:: TRAIN MODEL
:: ======================================================

:TRAIN
cls
echo  Training Isolation Forest Model...
echo.

if exist "%ROOT%train_from_csv.py" (
    start "AG - Training" cmd /k "cd /d "%ROOT%" && call venv\Scripts\activate && python train_from_csv.py && pause"
) else (
    echo  [ERROR] train_from_csv.py not found.
)

pause
goto MENU

:: ======================================================
:: RUN TESTS
:: ======================================================

:TEST
cls
echo  Running Tests...
echo.

start "AG - Tests" cmd /k "cd /d "%ROOT%" && call venv\Scripts\activate && pytest behavioral_guardian/tests -v && pause"

pause
goto MENU

:: ======================================================
:: PROJECT INFO
:: ======================================================

:INFO
cls

echo  ============================================================
echo                  AI BEHAVIORAL GUARDIAN
echo  ============================================================
echo.
echo  Team Name      : CodeudersZ
echo  Role           : Machine Learning Engineer
echo  ML Algorithm   : Isolation Forest (Digital Twin)
echo  Library        : Scikit-learn
echo  Dataset        : User Behaviour CSV
echo  Language       : Python
echo  IDE            : VS Code
echo  Backend        : FastAPI (port 8080)
echo  Frontend       : React 19 + Vite + Tailwind (port 5173)
echo.
echo  Purpose:
echo  Continuous behavioral authentication — trust scored at
echo  every moment, not just at login. Anomalies trigger alerts
echo  and optional re-authentication.
echo.
echo  URLs (when running):
echo    API Docs   -> http://localhost:8080/docs
echo    Dashboard  -> http://localhost:5173
echo.
echo  ============================================================

pause
goto MENU

:: ======================================================
:: STOP ALL SERVICES
:: ======================================================

:STOP
cls

echo  Stopping all services...
echo.

taskkill /F /IM python.exe  >nul 2>&1
taskkill /F /IM pythonw.exe >nul 2>&1
taskkill /F /IM node.exe    >nul 2>&1
taskkill /F /IM uvicorn.exe >nul 2>&1

echo  [OK] All services stopped.
echo.
pause
goto MENU