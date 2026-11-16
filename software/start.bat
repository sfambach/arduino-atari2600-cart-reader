@echo off
rem Starts the PC program from its folder; creates the venv and installs the requirements on the first run.
cd /d "%~dp0"
if not exist .venv\Scripts\python.exe (
    py -m venv .venv || exit /b 1
    .venv\Scripts\pip install -r requirements.txt || exit /b 1
)
.venv\Scripts\python -m acr %*
