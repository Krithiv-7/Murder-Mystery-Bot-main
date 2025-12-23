#!/bin/bash

echo "================================"
echo "Murder Mystery Bot - Starting"
echo "================================"
echo ""

# Ensure venv exists
if [ ! -d ".venv" ]; then
    echo "WARNING: .venv not found. Run ./setup.sh first to create the virtual environment."
fi

# Check for token: prefer env var, fallback to token.txt
if [ -z "$DISCORD_TOKEN" ] && [ ! -f "token.txt" ]; then
    echo "ERROR: No bot token found!"
    echo "Set DISCORD_TOKEN in the environment, or create token.txt next to start.sh."
    echo ""
    exit 1
fi

echo "Starting bot..."
echo "Press Ctrl+C to stop the bot"
echo ""

# Activate venv if present
if [ -d ".venv" ]; then
    # shellcheck disable=SC1091
    source .venv/bin/activate
fi

python bot.py

if [ $? -ne 0 ]; then
    echo ""
    echo "ERROR: Bot crashed or failed to start!"
    exit 1
fi
