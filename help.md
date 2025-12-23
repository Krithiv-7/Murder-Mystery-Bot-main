# Murder‑Mystery‑Bot — Help (Basics)

Last updated: December 23, 2025

This guide covers the core commands most players will use. The bot runs via message‑based commands (no slash commands). Enable the Message Content Intent in the Discord Developer Portal for your bot.

## Getting Started
- Install and run: See [README.md](README.md) for setup instructions.
- Prefix: Default prefix is `!`. Change via `!prefix <new>`.
- Join channel: Server admins can configure a dedicated join channel during `!setup`.

## Quick Play
1. Run `!setup` as an admin in a server to initialize.
2. Use `!join` in the allowed channel to join the next game.
3. When enough players join, the game starts automatically after a short countdown.

## Basic Player Commands
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

## Advanced Docs
- Advanced/Admin Commands: [help-advanced.md](help-advanced.md)
- Server Settings Reference: [help-settings.md](help-settings.md)

## Notes
- Admins can change the prefix with `!prefix <new>`.
- If a dedicated join channel is enabled, only `!join` is allowed there; other messages may be deleted.

## Tips
- Games cycle between day and night; items are mostly used at night.
- Broadcaster role affects item availability.
- If a dedicated join channel is enabled, only `!join` is allowed there; other messages may be deleted.

## Support
- Need help or want to report a bug? See the support info in [README.md](README.md) or use `!dc` to get the support invite shown by the bot.
- Discord server: https://discord.gg/kriti
- GitHub: https://github.com/Krithiv-7/Murder-Mystery-Bot-main

See also: [Terms of Service](tos.md), [Privacy Policy](pp.md), and [Code of Conduct](CODE_OF_CONDUCT.md).