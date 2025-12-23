# Murder‑Mystery‑Bot — Advanced/Admin Commands

Last updated: December 23, 2025

These commands are intended for server admins or moderators. Many require specific permissions as enforced by the bot.

## Admin & Moderation
- `!setup`: Interactive server setup (creates join channel and configures defaults)
- `!cleanup` (aliases: `!endGames`, `!stopGames`, `!stopAllGames`, `!endAllGames`): End all running games
- `!endGame <ID>` (alias: `!stopGame`): End a specific game
- `!kick <@member>`: Remove a player from their game

## Game Management
- `!createGame [True|False]`: Create an empty game; `True` enables debug mode
- `!startGame <ID>`: Force a game to start (skips countdown if applicable)
- `!skipVotes <ID>`: Skip or cut short voting time
- `!skipNight <ID>`: Skip the current night
- `!setWeather <ID> <int>`: Set weather intensity (game cosmetic)
- `!setMoon <ID> <int>`: Set moon level (game cosmetic)

## Prefix & Permissions
- `!prefix <new>`: Change the command prefix for this server (admin permission required)
- Permissions are controlled via the bot's internal permission system; see your server configuration and `permissions.py` for details.

## Notes
- These commands only work when the bot has the necessary Discord permissions.
- Using admin commands while playing is discouraged (administrator visibility can break game secrecy).

See also: [Basics](help.md), [Server Settings](help-settings.md), [Terms](tos.md), [Privacy](pp.md), [Code of Conduct](CODE_OF_CONDUCT.md).