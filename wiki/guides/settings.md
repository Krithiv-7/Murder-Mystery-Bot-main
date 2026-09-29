# Server settings

Last updated: September 29, 2026

Admins change a server with `!settings` or `/settings`, or with the panel `!settingspanel` / `/settingspanel`. The panel edits timers, the prefix, disabled commands, and live lobbies.

## Numbers

- `minPlayers`: at least 3, and lower than `maxPlayers`
- `maxPlayers`: at least `minPlayers`
- `preGameTimer`, `votingTime`, and `nightTimeTimer`: seconds, at least 5

Examples: `!settings minPlayers 6`, `!settings preGameTimer 120`.

## Toggle

- `kickOfflinePlayers`: remove players who go offline. `!settings kickOfflinePlayers` flips it.

## Prefix

`!prefix <new>` or `/prefix`. A prefix is 1 to 7 characters and cannot contain spaces. Until a server sets one, the default is `BOT_PREFIX` from `.env`.

## Where the game talks

The bot does not create tutorial channels, join channels, voice channels, or a channel per game. Public status stays in the setup channel, or in the channel where the lobby was created. Private actions are DMs.

## Discord permissions the invite requests

Add Reactions, Send Messages, Embed Links, Attach Files, Read Message History, Use External Emojis, and Use External Sounds. The invite does not ask for Manage Channels, Manage Roles, Manage Messages, or Move Members.

The application needs the Message Content and Server Members intents. Slash commands are included because the invite scope contains `applications.commands`.

Command access inside the bot is a separate tree (`member.join`, `admin.*`, and so on). Discord administrators bypass that tree.
