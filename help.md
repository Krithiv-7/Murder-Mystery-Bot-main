# Murder‑Mystery‑Bot — Help Guide

Last updated: December 23, 2025

This bot runs a murder‑mystery style game inside Discord using message‑based commands (no slash commands). Enable the Message Content Intent in the Discord Developer Portal for your bot.

## Getting Started
- Install and run: See [README.md](README.md) for setup instructions.
- Prefix: Default prefix is `!`. Change via `!prefix <new>`.
- Join channel: Server admins can configure a dedicated join channel during `!setup`.

## Quick Play
1. Run `!setup` as an admin in a server to initialize.
2. Use `!join` in the allowed channel to join the next game.
3. When enough players join, the game starts automatically after a short countdown.

## Player Commands
- `!join [ -overwriteAdminWarning ]`: Join an available game. Admins are warned to play without admin perms for fairness.
- `!list`: Show running games and IDs.
- `!spectate <ID>`: Spectate a running game.
- `!leave`: Leave your current game.
- `!vote <@player>`: Vote to execute a player during day.
- `!whisper <@player>`: Create a temporary private channel with another player (deleted at night).
- `!shop`: View purchasable items during night.
- `!buy <itemId>`: Purchase an item.
- `!use <itemId> [arg]`: Use an item (some need a target).
- `!balance` (aliases: `!money`, `!gold`, `!bal`): Show your gold.

## Admin & Mod Commands
- `!setup`: Interactive server setup (join channel, defaults).
- `!cleanup` (aliases: `!endGames`, `!stopGames`, etc.): End all running games.
- `!endGame <ID>` (alias: `!stopGame`): End a specific game.
- `!createGame [True|False]`: Create a new game (optional debug mode).
- `!startGame <ID>`: Force a game with ID to start.
- `!skipVotes <ID>`: Skip or cut short voting in a game.
- `!skipNight <ID>`: Skip night in a game.
- `!setWeather <ID> <int>`: Set weather intensity.
- `!setMoon <ID> <int>`: Set moon level.
- `!kick <@member>`: Remove a player from their game.

## Server Settings
- `!settings`: Show and change server settings.
  - Numeric settings: `minPlayers`, `maxPlayers`, `preGameTimer`, `votingTime`, `nightTimeTimer`.
  - Toggles: `voiceChannel`, `lockVoiceChannelDuringNight`, `kickOfflinePlayers`.
- `!prefix <newPrefix>`: Set command prefix (admin permission required).
- Permissions are managed via the built‑in permissions system (`permissions.py`).

## Tips
- Games cycle between day and night; items are mostly used at night.
- Broadcaster role affects item availability.
- If a dedicated join channel is enabled, only `!join` is allowed there; other messages may be deleted.

## Support
- Need help or want to report a bug? See the support info in [README.md](README.md) or use `!dc` to get the support invite shown by the bot.
- Discord server: https://discord.gg/kriti
- GitHub: https://github.com/Krithiv-7/Murder-Mystery-Bot-main

See also: [Terms of Service](tos.md), [Privacy Policy](pp.md), and [Code of Conduct](CODE_OF_CONDUCT.md).