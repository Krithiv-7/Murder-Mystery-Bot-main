# Commands

Last updated: September 29, 2026

Prefix and slash commands share the same game rules. Lobby codes look like `MM-7F2A`. One person cannot take two seats in a lobby.

In-game role lists are also available with `!wiki` and `/wiki`.

## Lobby

| Action | Prefix | Slash | Permission |
| --- | --- | --- | --- |
| Create | `!create` | `/create` | none; debug mode needs `debug.createGame` |
| Join | `!join <code>` | `/join` | `member.join` |
| List | `!list` | `/list` | `member.list` |
| Spectate | `!spectate <code>` | `/spectate` | `member.spectate` |
| Leave | `!leave` | `/leave` | in a game |
| Force start | `!forceStart` | `/force-start` | lobby host or admin |
| Start a code | `!startGame <code>` | `/start-game` | lobby host or `admin.game.startGame` |

`!create` shows the code plus **Join & Play**, **Spectate instead**, and **Allow DMs from this bot**. Joining also sends a DM. If that DM is blocked, the status channel mentions the player and shows the same button. If only one lobby is open, `!spectate` can omit the code. Discord administrators join with `-overwriteAdminWarning`.

## During a game

| Action | Prefix | Slash |
| --- | --- | --- |
| Vote | `!vote @player` | `/vote` |
| Shop | `!shop` | `/shop` |
| Buy | `!buy <item>` | `/buy` |
| Use an item | `!use <item> [argument]` | `/use` |
| Whisper | `!whisper @player` | `/whisper` |
| Gold | `!balance` | `/balance` |

Voting is daytime only. The shop is nighttime only, in a DM or by slash command. A whisper is a DM, not a server channel. `!balance` also answers to `!money`, `!gold`, and `!bal`.

## Progress

| Action | Prefix | Slash | Permission |
| --- | --- | --- | --- |
| Help | `!help` | `/help` | `member.help` |
| Level | `!level [player]` | `/level` | `member.levels.level` |
| Objective | `!objective` | `/objective` | `member.levels.objective` |
| Stats | `!stats [player]` | `/stats` | `member.levels.stats` |
| Prefix | `!prefix` | `/prefix` | viewing needs no permission |

## Admin

These need the matching admin permission, or Discord administrator.

- `!setup` or `/setup` configures the server. It does not create channels.
- `!settings` or `/settings`, and `!settingspanel` or `/settingspanel`, change timers, the prefix, disabled commands, and live lobbies. See [settings](settings.md).
- `!cleanup` ends every lobby. Aliases: `!endGames`, `!stopGames`, `!endAllGames`, `!stopAllGames`. Slash: `/cleanup`.
- `!endGame <code>` ends one lobby. Alias: `!stopGame`. Slash: `/end-game`.
- `!kick @member` or `/kick` removes a player.
- `!giveGold <player> <amount>` or `/give-gold` adds gold during a game. Permission: `admin.game.giveGold`.
- `!resetState` or `/reset-state` ends games and clears this server's in-memory lobbies. Permission: `admin.resetState`.
- `!status` or `/status` shows bot health. Needs `admin.*`.
- `!addPermission`, `!removePermission`, and `!permissions` edit the permission tree.

There is no `!purge` command and no voice-channel setting.

## Debug

Debug commands can break a running game. They need the listed permission.

- `!createGame True` creates a short debug lobby. Permission: `debug.createGame`.
- `!skipVotes <code>` and `/skip-votes`. Permission: `debug.game.skipVotes`.
- `!skipNight <code>` and `/skip-night`. Permission: `debug.game.skipNight`.
- `!setWeather <code> <0-99>` and `/set-weather`. Permission: `debug.game.setWeather`.
- `!setMoon <code> <1-5>` and `/set-moon`. Permission: `debug.game.setMoon`.
- `!giveObjective`, `!addObjectiveProgress`, `!completeCurrentObjective`, and `!skipObjectiveTimer` edit objectives. These stay prefix-only.
