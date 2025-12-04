@echo off
echo ====================================
echo Agent-Driven TODO Executor
echo ====================================
echo.

REM Check if venv exists
if not exist "venv\Scripts\activate.bat" (
    echo Creating virtual environment...
    python -m venv venv
    echo.
)

REM Activate venv
call venv\Scripts\activate.bat

REM Check if requirements installed
pip show openai >nul 2>&1
if errorlevel 1 (
    echo Installing dependencies...
    pip install -r requirements.txt
    echo.
)

REM Run the agent
echo Starting agent...
echo.
python main.py

REM Keep window open if there's an error
if errorlevel 1 pause

