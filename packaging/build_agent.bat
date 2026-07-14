@echo off
REM Build GuardianAgent.exe from agent_runner.py.
REM Run this ON WINDOWS, from inside the "packaging" folder, with your venv
REM activated. PyInstaller cannot cross-compile — building on Linux/Mac
REM produces a Linux/Mac binary, not a Windows .exe. If you're doing this from
REM the same machine you've been developing on, you're already on Windows,
REM so this just works.

echo Installing PyInstaller and pywin32 (needed for pynput on Windows)...
pip install pyinstaller pywin32

echo.
echo Building GuardianAgent.exe ...
pyinstaller --clean --noconfirm agent.spec

echo.
echo Done. Find it at: packaging\dist\GuardianAgent.exe
echo.
echo Give that single file to anyone. They double-click it, and:
echo   - if a guardian-pairing.json is sitting in their Downloads folder
echo     (from Settings -^> "Connect this device" on the web app), it links
echo     automatically with zero typing
echo   - otherwise it asks once for username + password in the console window
echo.
echo IMPORTANT: this .exe reads its backend URL from a default baked in at
echo build time, NOT from an environment variable on the other person's PC
echo (they won't have one set, and won't know to set it). Before building,
echo open behavioral_guardian\config\settings.py and change the empty
echo default in API_BASE_URL_OVERRIDE to your real hosted backend URL, e.g.:
echo     API_BASE_URL_OVERRIDE = os.environ.get(
echo         "BEHAVIORAL_GUARDIAN_API_BASE_URL", "https://your-app.onrender.com/api/v1"
echo     )
echo Then rebuild. See ..\DEPLOYMENT.md for getting that URL in the first place.
pause
