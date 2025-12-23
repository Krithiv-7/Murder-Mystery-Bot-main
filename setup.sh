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

echo "Creating virtual environment (venv)..."
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
    if [ $? -ne 0 ]; then
        echo ""
        echo "ERROR: Failed to create venv. On Debian/Ubuntu, install venv support:"
        echo "  sudo apt update && sudo apt install -y python3-venv"
        echo "Then re-run: ./setup.sh"
        exit 1
    fi
fi

echo "Activating venv and installing dependencies..."
source .venv/bin/activate
python -m pip install --upgrade pip
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
else
    pip install discord.py pymongo dnspython
fi

if [ $? -ne 0 ]; then
    echo ""
    echo "ERROR: Failed to install dependencies!"
    echo "If you saw an externally-managed-environment (PEP 668) error, ensure you are inside the venv above."
    deactivate 2>/dev/null
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
echo "Or manually run inside venv: source .venv/bin/activate && python bot.py"
echo ""
echo "For production (keeps running in background):"
echo "  screen -S discord-bot ./start.sh"
echo "  (Press Ctrl+A then D to detach)"
echo ""
