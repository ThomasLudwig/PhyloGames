@echo off
setlocal

echo ============================================
echo   Phylo Genie - Installation
echo ============================================
echo.

REM --- Check Python is installed and reachable ---
where python >nul 2>nul
if errorlevel 1 (
    echo [ERROR] Python was not found on your system.
    echo Please install Python 3.10 or newer from:
    echo https://www.python.org/downloads/
    echo IMPORTANT: during install, check "Add Python to PATH"
    pause
    exit /b 1
)

REM --- Check Python version is >= 3.10 ---
for /f "tokens=2" %%v in ('python --version 2^>^&1') do set PYVER=%%v
echo Detected Python %PYVER%

python -c "import sys; exit(0 if sys.version_info >= (3,10) else 1)"
if errorlevel 1 (
    echo [ERROR] Python 3.10+ is required. You have %PYVER%.
    echo Please install a newer version from https://www.python.org/downloads/
    pause
    exit /b 1
)

REM --- Create a virtual environment ---
echo.
echo Creating virtual environment...
python -m venv venv

REM --- Install dependencies inside the venv ---
echo Installing dependencies...
call venv\Scripts\python.exe -m pip install --upgrade pip
call venv\Scripts\python.exe -m pip install -r requirements.txt

echo.
echo ============================================
echo   Installation complete!
echo   Run start.bat to launch the app.
echo ============================================
pause