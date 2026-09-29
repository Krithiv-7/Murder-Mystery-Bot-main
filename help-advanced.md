# Murder‑Mystery‑Bot — Advanced/Admin Commands

Last updated: September 29, 2026

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
	- Creates a lobby and shows its code. The host chooses whether to play or spectate. Debug mode requires `debug.createGame`.

- `!join <code>` — permission: `member.join`
	- Joins a lobby by code, such as `MM-7F2A`. This command does not create a lobby.
	- Discord administrators add `-overwriteAdminWarning` (for example: `!join MM-7F2A -overwriteAdminWarning`).

- `!spectate <code>` — permission: `member.spectate`
	- Spectates a game by code. The code can be omitted when only one lobby is open.

- `!list` — permission: `member.list`
	- Shows running games and their codes.

- `!level [player]` — permission: `member.levels.level`
	- Shows the player's level.

- `!objective` — permission: `member.levels.objective`
	- Shows your current objective progress or gives you a new one.

- `!stats [player]` — permission: `member.levels.stats`
	- Shows your or the specified player's stats.

- `!prefix` — permission: none required
	- Shows the bot's prefix for this server.

## Admin & Moderation
- `!setup`: Button-based server setup. It configures permissions and optional summaries without creating tutorial or join channels.
- `!cleanup` (aliases: `!endGames`, `!stopGames`, `!stopAllGames`, `!endAllGames`): End all running games
- `!endGame <code>` (alias: `!stopGame`): End the lobby with that code
- `!resetState` — permission: `admin.resetState`
	- Ends all games for this guild and clears in-memory state (players, lobbies, caches). Useful to recover from stuck state.
- `!kick <@member>`: Remove a player from their game
- `!purge <number>` — permission: `admin.purge`
	- Deletes the last `<number>` messages in the current channel.
- `!giveGold <player> <amount>` — permission: `admin.game.giveGold`
	- Gives the specified player extra gold during a game.

## Game Management
- `!createGame [True|False]`: Create an empty game; `True` enables debug mode (debug permission required)
- `!startGame <code>`: Start that lobby immediately. Only the lobby host or an admin can run this.
- `!forceStart` (aliases: `!ownerstart`, `!fs`): Lobby owner (or admins) can force start their current lobby immediately
- `!skipVotes <code>`: Skip or cut short voting time
- `!skipNight <code>`: Skip the current night
- `!setWeather <code> <int>`: Set weather intensity
- `!setMoon <code> <int>`: Set moon level
- `!settingspanel`: Open the admin panel for active games, timers, disabled commands, and the prefix
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
- Using admin commands while playing is discouraged. Discord administrators may be able to see channels hidden from ordinary players.
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

- `!setMoon <code> <brightness (1-5)>` — permission: `debug.game.setMoon`
	- Sets moon brightness in the specified game. 1 = no moon, 5 = full moon. Use after the weather forecast and before night starts.

- `!setWeather <code> <intensity (0-99)>` — permission: `debug.game.setWeather`
	- Sets weather intensity (0 = not intense, 99 = very intense). Use after the weather forecast and before night starts.

- `!skipNight <code>` — permission: `debug.game.skipNight`
	- Skips the night.

- `!skipVotes <code>` — permission: `debug.game.skipVotes`
	- Skips voting time.

See also: [Basics](help.md), [Server Settings](help-settings.md), [Terms](tos.md), [Privacy](pp.md), [Code of Conduct](CODE_OF_CONDUCT.md).