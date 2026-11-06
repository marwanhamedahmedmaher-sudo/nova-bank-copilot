@echo off
rem Double-click to start the Nova agent console for the demo.
cd /d "%~dp0"
rem Stop an older console still holding port 8000, so the latest code is what runs.
for /f "tokens=5" %%p in ('netstat -ano ^| findstr /r /c:":8000 .*LISTENING"') do taskkill /f /pid %%p >nul 2>&1
start "" "http://localhost:8000"
".venv\Scripts\python.exe" -m uvicorn app.main:app --port 8000
