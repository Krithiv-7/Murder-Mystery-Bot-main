#!/bin/bash

echo "================================"
echo "Murder Mystery Bot - Setup"
echo "================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python3 is not installed!"
    echo "Please install Python3 using your package manager:"
    echo "  Ubuntu/Debian: sudo apt install python3 python3-pip"
    echo "  CentOS/RHEL: sudo yum install python3 python3-pip"
    echo "  Arch: sudo pacman -S python python-pip"
    exit 1
fi

echo "Python found!"
python3 --version
echo ""

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "ERROR: pip3 is not installed!"
    echo "Please install pip3 using your package manager"
    exit 1
fi

# Check if token.txt exists
if [ ! -f "token.txt" ]; then
    echo "WARNING: token.txt not found!"
    echo "Please create token.txt and add your Discord bot token."
    echo ""
    read -p "Press enter to continue..."
fi

echo "Installing dependencies..."
python3 -m pip install --upgrade pip
pip3 install discord.py pymongo dnspython

if [ $? -ne 0 ]; then
    echo ""
    echo "ERROR: Failed to install dependencies!"
    exit 1
fi

# Make start.sh executable
chmod +x start.sh

echo ""
echo "================================"
echo "Setup completed successfully!"
echo "================================"
echo ""
echo "To start the bot, run: ./start.sh"
echo "Or manually run: python3 bot.py"
echo ""
echo "For production (keeps running in background):"
echo "  screen -S discord-bot ./start.sh"
echo "  (Press Ctrl+A then D to detach)"
echo ""
