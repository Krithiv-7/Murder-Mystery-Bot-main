# Murder‑Mystery‑Bot — Advanced/Admin Commands

Last updated: December 24, 2025

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

- `!create` — permission: none
	- Creates a new lobby and auto-adds you (only if you are not already in a lobby). Debug mode requires `debug.createGame`.

- `!join <id>` — permission: `member.join`
	- Joins a lobby by ID. This command requires an explicit lobby ID and does not create new lobbies.
	- If you have the Discord Administrator permission, add `-overwriteAdminWarning` to join (for example: `!join 0 -overwriteAdminWarning`).

- `!spectate <id>` — permission: `member.spectate`
	- Spectates a game by ID.

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
- `!resetState` — permission: `admin.resetState`
	- Ends all games for this guild and clears in-memory state (players, lobbies, caches). Useful to recover from stuck state.
- `!kick <@member>`: Remove a player from their game
- `!purge <number>` — permission: `admin.purge`
	- Deletes the last `<number>` messages in the current channel.
- `!purgeInfoChannels` — permission: `admin.purge`
	- Cleans up bot info channels created during games.
- `!giveGold <player> <amount>` — permission: `admin.game.giveGold`
	- Gives the specified player extra gold during a game.

## Game Management
- `!createGame [True|False]`: Create an empty game; `True` enables debug mode (debug permission required)
- `!startGame <ID>`: Force a game to start (skips countdown if applicable). Only the lobby owner or admins can run this.
- `!forceStart` (aliases: `!ownerstart`, `!fs`): Lobby owner (or admins) can force start their current lobby immediately
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
- Members can only be in one lobby at a time; creating or joining another lobby requires leaving the current one.

## Debug (Advanced Help)
Arguments in <> are required; [] are optional.

These advanced commands were primarily built for debugging and may be confusing without reading the source code.

⚠️ Some of these commands can break the bot if used incorrectly.

- `!createGame [True/False]` — permission: `debug.createGame`
	- Creates an empty game. Use `True` to enable debugging mode.

- `!addObjectiveProgress <member> <task> <value>` — permission: `debug.objectives.addObjectiveProgress`
	- Adds progress to an objective task.

- `!giveObjective <member> <index>` — permission: `debug.objectives.giveObjective`
	- Sets the member's objective to the specified index. ⚠️ Unexpected behaviour may occur if the index is invalid.

- `!completeCurrentObjective <member>` — permission: `debug.objectives.completeCurrentObjective`
	- Completes the member's current objective.

- `!skipObjectiveTimer <member>` — permission: `debug.objectives.skipObjectiveTimer`
	- Skips the in‑between objective timer for the specified member.

- `!setMoon <game ID> <brightness (1-5)>` — permission: `debug.game.setMoon`
	- Sets moon brightness in the specified game. 1 = no moon, 5 = full moon. Use after the weather forecast and before night starts.

- `!setWeather <game ID> <intensity (0-99)>` — permission: `debug.game.setWeather`
	- Sets weather intensity (0 = not intense, 99 = very intense). Use after the weather forecast and before night starts.

- `!skipNight <game ID>` — permission: `debug.game.skipNight`
	- Skips the night.

- `!skipVotes <game ID>` — permission: `debug.game.skipVotes`
	- Skips voting time.

See also: [Basics](help.md), [Server Settings](help-settings.md), [Terms](tos.md), [Privacy](pp.md), [Code of Conduct](CODE_OF_CONDUCT.md).