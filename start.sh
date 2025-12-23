#!/bin/bash

echo "================================"
echo "Murder Mystery Bot - Starting"
echo "================================"
echo ""

# Check if token.txt exists
if [ ! -f "token.txt" ]; then
    echo "ERROR: token.txt not found!"
    echo "Please create token.txt and add your Discord bot token."
    echo ""
    exit 1
fi

echo "Starting bot..."
echo "Press Ctrl+C to stop the bot"
echo ""

python3 bot.py

if [ $? -ne 0 ]; then
    echo ""
    echo "ERROR: Bot crashed or failed to start!"
    exit 1
fi
