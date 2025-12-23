# Murder‑Mystery‑Bot — Advanced/Admin Commands

Last updated: December 23, 2025

These commands are intended for server admins or moderators. Many require specific permissions as enforced by the bot.

## Game (Advanced Help)
- Arguments in <> are required; [] are optional.
- These commands have no extra permission settings because they are only usable in-game, which itself requires the `member.join` permission.

- `!vote <player>`: Vote on the specified player to be executed during the game.
- `!shop`: View all shop items (night only).
- `!buy <item>`: Buy an item from the shop (night only).
- `!use <item> [argument]`: Use an item; whether an argument is required depends on the item.
- `!whisper <player>`: Create a private channel between you and the specified player (day only).
- `!leave`: Leave the game.

## Member (Advanced Help)
- Arguments in <> are required; [] are optional.

- `!help` — permission: `member.help`
	- Views a list of all simple commands.

- `!advancedHelp [category]` — permission: `member.help`
	- Views a list of all commands. Optionally filter by category.

- `!join` — permission: `member.join`
	- Joins a game. Depending on server configuration, this command may only be usable in the join channel.

- `!spectate [id]` — permission: `member.spectate`
	- Spectates a game. If only one game is running, no ID is required.

- `!list` — permission: `member.list`
	- Shows all currently running games and their IDs.

- `!level [player]` — permission: `member.levels.level`
	- Shows the player's level.

- `!objective` — permission: `member.levels.objective`
	- Shows your current objective progress or gives you a new one.

- `!stats [player]` — permission: `member.levels.stats`
	- Shows your or the specified player's stats.

- `!prefix` — permission: none required
	- Shows the bot's prefix for this server.

## Admin & Moderation
- `!setup`: Interactive server setup (creates join channel and configures defaults)
- `!cleanup` (aliases: `!endGames`, `!stopGames`, `!stopAllGames`, `!endAllGames`): End all running games
- `!endGame <ID>` (alias: `!stopGame`): End a specific game
- `!kick <@member>`: Remove a player from their game
- `!purge <number>` — permission: `admin.purge`
	- Deletes the last `<number>` messages in the current channel.
- `!purgeInfoChannels` — permission: `admin.purge`
	- Cleans up bot info channels created during games.
- `!giveGold <player> <amount>` — permission: `admin.game.giveGold`
	- Gives the specified player extra gold during a game.

## Game Management
- `!createGame [True|False]`: Create an empty game; `True` enables debug mode
- `!startGame <ID>`: Force a game to start (skips countdown if applicable)
- `!skipVotes <ID>`: Skip or cut short voting time
- `!skipNight <ID>`: Skip the current night
- `!setWeather <ID> <int>`: Set weather intensity (game cosmetic)
- `!setMoon <ID> <int>`: Set moon level (game cosmetic)
 - `!settings [setting] [value]` — permission: `admin.settings`
	 - Configure game behavior: minimum/maximum players, timers, toggles, etc.

## Prefix & Permissions
 - `!prefix [new]` — permission: `admin.prefix`
	 - Show the current prefix or set a new one. Members can view the prefix but cannot change it without `admin.prefix`.
- Permissions are controlled via the bot's internal permission system; see your server configuration and `permissions.py` for details.
 - `!addPermission <member/role> <permission>` — permission: `admin.permissions.addPermission`
	 - Adds a permission to a role or member.
 - `!removePermission <member/role> <permission>` — permission: `admin.permissions.removePermissions`
	 - Removes a permission from a role or member.
 - `!permissions [member/role]` — permission: `admin.permissions`
	 - View permissions for a member/role, or all possible permissions when no argument is provided.

## Notes
- These commands only work when the bot has the necessary Discord permissions.
- Using admin commands while playing is discouraged (administrator visibility can break game secrecy).

See also: [Basics](help.md), [Server Settings](help-settings.md), [Terms](tos.md), [Privacy](pp.md), [Code of Conduct](CODE_OF_CONDUCT.md).