@echo off
rem Double-click to start the Nova agent console for the demo.
cd /d "%~dp0"
start "" "http://localhost:8000"
".venv\Scripts\python.exe" -m uvicorn app.main:app --port 8000
