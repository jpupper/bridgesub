@echo off
echo Installing SubBridge - Subtitle Generator
echo ======================================

:: Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Python is not installed! Please install Python 3.10 or higher.
    echo You can download it from: https://www.python.org/downloads/
    pause
    exit /b 1
)

:: Check if pip is installed
pip --version >nul 2>&1
if errorlevel 1 (
    echo pip is not installed! Please install pip.
    pause
    exit /b 1
)

:: Create virtual environment if it doesn't exist
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

:: Activate virtual environment and install dependencies
echo Activating virtual environment and installing dependencies...
call venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt

:: Check if installation was successful
if errorlevel 1 (
    echo Error during installation! Please check the error messages above.
    pause
    exit /b 1
)

echo.
echo Installation completed successfully!
echo.
echo To run SubBridge:
echo 1. Double click on 'run.bat'
echo.
echo Note: Make sure you have ImageMagick installed.
echo You can download it from: https://imagemagick.org/script/download.php#windows
echo.
pause
