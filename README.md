# Murder-Mystery-Bot
A town of salem/mafia-like game inside Discord! This bot brings the classic social deduction game experience to your Discord server.

Invite the bot to your server: https://discord.com/oauth2/authorize?client_id=1452886075621249024&permissions=268823632&integration_type=0&scope=bot

Join our support server: https://discord.gg/kriti

# Running the bot yourself
If you need help, join our Discord server: https://discord.gg/kriti

## Prerequisites
- Python 3.7 or higher (Python 3.13+ recommended)
- pip (Python package manager)

## Quick Setup (Recommended)

### Windows
1. Create your Discord bot and get the token (see below)
2. Paste your bot token into `token.txt`
3. Double-click `setup.bat` to install dependencies
4. Double-click `start.bat` to start the bot

### Linux/macOS
1. Create your Discord bot and get the token (see below)
2. Paste your bot token into `token.txt`
3. Run setup script:
   ```bash
   chmod +x setup.sh start.sh
   ./setup.sh
   ```
4. Start the bot:
   ```bash
   ./start.sh
   ```
5. For production (keeps running in background):
   ```bash
   screen -S discord-bot ./start.sh
   # Press Ctrl+A then D to detach from screen
   # To reattach: screen -r discord-bot
   ```

## Manual Setup Instructions

1. **Install Python** from https://www.python.org/
   - On Windows, make sure to check "Add python to PATH" during installation

2. **Install required libraries**:
   ```bash
   pip install discord.py pymongo dnspython
   ```

3. **Create a Discord Bot**:
   - Go to https://discord.com/developers/applications
   - Click "New Application" and give it a name
   - Go to the "Bot" tab and click "Add Bot"
   - Click "Reset Token" and copy the token
   - Paste the token into `token.txt` in the project directory
   - Under "Privileged Gateway Intents", enable:
     - Presence Intent
     - Server Members Intent
     - Message Content Intent

4. **Run the bot**:
   ```bash
   py bot.py
   ```
   Or on macOS/Linux:
   ```bash
   python3 bot.py
   ```
   
   If successful, you'll see: `Logged in as (bot's username)`

5. **Invite the bot to your server**:
   - Use this invite link (replace CLIENT_ID with your bot's client ID):
   ```
   https://discord.com/oauth2/authorize?client_id=YOUR_CLIENT_ID&permissions=268823632&integration_type=0&scope=bot
   ```


# Database
This bot can either use a json file or MongoDB as a database! By default it uses json, but if you'd like to use mongoDB then paste your mongoDB login key in mongoDBLoginInfo.txt and in bot.py set LocalStorage to false. The bot will use "discord" as the database name and "murder-mystery" as the collection name, but you can change them in datastorage.py on line 25 and 26 if you want.

# Important Notes

⚠️ **This bot uses the discord.py commands library** and does **NOT** support slash commands. It requires the Message Content Intent to be enabled.

⚠️ **All Privileged Intents must be enabled** in the Discord Developer Portal under the Bot settings:
- Presence Intent
- Server Members Intent  
- Message Content Intent

💡 **For production deployment**, consider using:
- `screen` or `tmux` on Linux to keep the bot running
- PM2 for process management
- Docker for containerization

# Contributing

Feel free to fork this bot and make improvements! If you create a public fork, please provide credit and let us know - we'd love to see what you build!

