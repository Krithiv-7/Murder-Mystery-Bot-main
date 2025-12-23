@echo off
echo ================================
echo Murder Mystery Bot - Setup
echo ================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH!
    echo Please install Python from https://www.python.org/
    pause
    exit /b 1
)

echo Python found!
python --version
echo.

REM Check if token.txt exists
if not exist "token.txt" (
    echo WARNING: token.txt not found!
    echo Please create token.txt and add your Discord bot token.
    echo.
    pause
)

echo Installing dependencies...
python -m pip install --upgrade pip
pip install discord.py pymongo dnspython

if errorlevel 1 (
    echo.
    echo ERROR: Failed to install dependencies!
    pause
    exit /b 1
)

echo.
echo ================================
echo Setup completed successfully!
echo ================================
echo.
echo To start the bot, run: start.bat
echo Or manually run: python bot.py
echo.
pause
