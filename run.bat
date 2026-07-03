@echo off
cd /d "%~dp0"
set PYTHONPATH=%~dp0
.\venv311\Scripts\python.exe app.py
pause
