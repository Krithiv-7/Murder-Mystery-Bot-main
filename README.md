# Murder-Mystery-Bot
A town of salem/mafia-like game inside Discord! This bot brings the classic social deduction game experience to your Discord server.

Invite the bot to your server: https://discord.com/oauth2/authorize?client_id=1452886075621249024&permissions=268823632&integration_type=0&scope=bot%20applications.commands

Top.gg Listing: https://top.gg/bot/1452886075621249024

Join our support server: https://discord.gg/kriti
GitHub repository: https://github.com/Krithiv-7/Murder-Mystery-Bot-main

# Running the bot yourself
If you need help, join our Discord server: https://discord.gg/kriti

## Support & Maintenance
- Actively maintained: Issues and improvements are addressed regularly.
- Found a bug? Please open an issue on the repository or join the support server for help.
- Suggestions welcome: create an issue or drop by the server to discuss.

## Prerequisites
- Python 3.10 or higher (Python 3.13+ recommended)
- pip (Python package manager)
- A Discord application with the required privileged intents enabled

## Quick Setup (Recommended)

### Windows
1. Create your Discord bot and get the token (see below)
2. Set `DISCORD_TOKEN` in the process environment, or put a single-line token in `token.txt` for local development
3. Double-click `setup.bat` to install dependencies
4. Double-click `start.bat` to start the bot

### Linux/macOS
1. Create your Discord bot and get the token (see below)
2. Set `DISCORD_TOKEN` in the process environment, or put a single-line token in `token.txt` for local development
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

3. **Install required libraries**:
   ```bash
   python -m pip install -r requirements.txt
   ```

3. **Create a Discord Bot**:
   - Go to https://discord.com/developers/applications
   - Click "New Application" and give it a name
   - Go to the "Bot" tab and click "Add Bot"
   - Click "Reset Token" and copy the token
   - Store the token in `DISCORD_TOKEN` for deployments. Never commit it or paste it into issues, chat, or documentation.
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
The default configuration uses local JSON storage. MongoDB can be enabled through the configuration and requires a valid `mongoDBLoginInfo.txt`. Local mode writes runtime data and rotating backups; keep those files private and back them up according to your retention needs.

# Important Notes

ℹ️ **Gameplay uses prefix commands**, with a small slash-command set: `/ping`, `/help`, `/create`, `/list`, `/join`, and `/spectate`. The invite scope must include `applications.commands`.

## In-Discord Setup

Run `!setup` as an administrator. The setup panel uses buttons and does not create tutorial or join channels. Choose whether the current channel should receive game summaries, then mention the admin roles in one message. Player-private instructions and role abilities are delivered by DM where possible.

Use `!list` to open a lobby dropdown with Join and Spectate buttons. The game still creates a public game channel and may create temporary channels for specific abilities such as whispering or jail. Text commands remain available as a fallback.

The bot needs permission to view and send messages, manage channels, manage roles, manage permissions, and optionally connect/speak/move members when voice settings are enabled.

⚠️ **All Privileged Intents must be enabled** in the Discord Developer Portal under the Bot settings:
- Presence Intent
- Server Members Intent  
- Message Content Intent

⚠️ **Admin join warning:** Discord administrators can see hidden channels. To join a lobby with admin permissions, run `!join <ID> -overwriteAdminWarning`.

🔒 **Starting lobbies:** `!startGame <ID>` can only be used by the lobby owner or an admin. `!forceStart` (`!ownerstart` / `!fs`) remains an owner/admin shortcut for the active lobby.

💡 **For production deployment**, consider using:
- `screen` or `tmux` on Linux to keep the bot running
- PM2 for process management
- Docker for containerization

# Contributing

Feel free to fork this bot and make improvements! If you create a public fork, please provide credit and let us know - we'd love to see what you build!


# Credits
- Original Creator: **Ikbenmathijs**
- Current Fork Maintainer: **Krithiv-7**

# License
This project is licensed under the **MIT License**. See [LICENSE](LICENSE) for details.

# Code of Conduct
We follow a community-friendly code of conduct. Please read and adhere to our [Code of Conduct](CODE_OF_CONDUCT.md).

