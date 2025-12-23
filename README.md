# Murder-Mystery-Bot
Archival of my old project Murder Mystery, a town of salem/mafia-like game inside discord! I still try to keep this bot up, but it's not getting updated anymore unless necessary to keep it online. If you'd like to play it and not host the bot yourself you can invite the main bot here: https://discord.com/api/oauth2/authorize?client_id=590980247801954304&permissions=2434133072&scope=bot

This bot also has a support server/server to play the game with other people: https://discord.gg/kriti

# Inviting to your own server
Click this link: https://discord.com/api/oauth2/authorize?client_id=590980247801954304&permissions=2434133072&scope=bot

The bot also has a page on top.gg: https://top.gg/bot/590980247801954304

# Running the bot yourself
I'm gonna assume you already know the basics of discord bots, if you need help you can use google or message me on discord (https://discord.gg/kriti)

Fist you need to install python from https://www.python.org/. I'm pretty sure it should work with 3.7 or above but I'm using 3.10, you should probably just use the newest version. Make sure to check "Add python to PATH" in the installer if you're on windows

Now you have to install the libaries used by this bot. Open command prompt or your terminal and execute the command "pip install discord pymongo dnspython"

Then create a bot on the discord developer portal by going to https://discord.com/developers/applications > new application. Then on the bot tab click add bot and then click reset token. Then copy the token and paste it into token.txt. In "privileged gateway intent" check everything (presence, server members and message content)

Then you can run the bot by opening cmd and using the command "py bot.py" (I'm pretty sure it's "python3 bot.py" on macOS or linux). If you did it correctly it should say "Logged in as (bot's username)"

Now you can invite the bot by clicking on the oauth2 tab and then URL generator. Then under scopes check bot and the easiest is to just give it the "administrator" permission but you can also check manage roles, manage channels, view channels, send messages, manage messages, embed links, attach files, read message history, use external emojis and add reactions instead if you want.

Now copy the invite link under "generate link" and invite the bot to your server!


# Database
This bot can either use a json file or MongoDB as a database! By default it uses json, but if you'd like to use mongoDB then paste your mongoDB login key in mongoDBLoginInfo.txt and in bot.py set LocalStorage to false. The bot will use "discord" as the database name and "murder-mystery" as the collection name, but you can change them in datastorage.py on line 25 and 26 if you want.

# Notes
**This bot was made with the old discord.py commands library**, which means this bot does **NOT** support slash commands. It requires the message content intent

This bot **REQUIRES ALL PRIVELAGED INTENTS TO BE ENABLED**. This means that if you fork this bot and don't make any major changes to it and it reaches over 100 servers, you will have to apply for all of the privelaged intents. The main bot is approved for all intents. If the bot is under 100 servers you just have to turn on everything under "Privileged Gateway Intents" in the bot tab and you sould be fine

This code is a bit messy, I wrote it a while ago (and was 14 at the time)

Please credit me if you make a public fork of this bot! Also let me know I'm curious what you'd do with it

