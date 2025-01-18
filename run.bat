@echo off
echo Starting SubBridge - Subtitle Generator
echo =====================================

:: Check if virtual environment exists
if not exist "venv" (
    echo Virtual environment not found!
    echo Please run install.bat first.
    pause
    exit /b 1
)

:: Activate virtual environment and run the application
call venv\Scripts\activate.bat
python subtitle_generator.py

:: If there was an error, show it
if errorlevel 1 (
    echo.
    echo An error occurred while running the application.
    echo Please check the error message above.
)

pause
