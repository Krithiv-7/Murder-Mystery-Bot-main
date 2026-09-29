@echo off
echo ================================
echo Murder Mystery Bot - Starting
echo ================================
echo.

if not exist ".env" if "%DISCORD_TOKEN%"=="" if not exist "token.txt" (
    echo ERROR: No bot token found.
    echo Copy .env.example to .env and set DISCORD_TOKEN.
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
