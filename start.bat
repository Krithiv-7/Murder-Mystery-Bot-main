@echo off
echo ================================
echo Murder Mystery Bot - Starting
echo ================================
echo.

REM Check if token.txt exists
if not exist "token.txt" (
    echo ERROR: token.txt not found!
    echo Please create token.txt and add your Discord bot token.
    echo.
    pause
    exit /b 1
)

echo Starting bot...
echo Press Ctrl+C to stop the bot
echo.

python bot.py

if errorlevel 1 (
    echo.
    echo ERROR: Bot crashed or failed to start!
    pause
)
