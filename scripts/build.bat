@echo off
REM Build the Restaurant POS executable. Run from anywhere; paths are resolved
REM relative to this script.
echo Building Restaurant POS System...
echo.

python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python not found. Please install Python first.
    pause
    exit /b 1
)

python "%~dp0build.py"

echo.
echo Build process finished. Check the dist folder for the executable.
pause
