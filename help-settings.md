# Murder‑Mystery‑Bot — Server Settings Reference

Last updated: September 29, 2026

Admins can change server configuration with `!settings` or the button panel `!settingspanel` / `/settingspanel`. The panel edits the same timer values, plus the prefix, disabled commands, and live lobbies.

## Viewing Settings
- `!settings`: Shows the current values and toggle states.

## Numeric Settings
- `minPlayers <int>`: Minimum players required to start a game (at least 3)
- `maxPlayers <int>`: Maximum players allowed in a game (must be at least `minPlayers`)
- `preGameTimer <int>`: Seconds to wait before starting after threshold reached (≥ 5)
- `votingTime <int>`: Seconds for daytime voting (≥ 5)
- `nightTimeTimer <int>`: Seconds for night phase (≥ 5)

Usage examples:
- `!settings minPlayers 6`
- `!settings maxPlayers 20`
- `!settings preGameTimer 120`

## Toggle Settings
- `voiceChannel`: Create a game voice channel when a game is created
- `lockVoiceChannelDuringNight`: Lock the game voice channel at night (requires Move Members permission)
- `kickOfflinePlayers`: Kick players who go offline during a game

Setup no longer creates tutorial, join, or private role channels. Private role instructions and night prompts are delivered through Discord DMs where possible.

Usage examples:
- `!settings voiceChannel`
- `!settings lockVoiceChannelDuringNight`
- `!settings kickOfflinePlayers`

## Prefix
- `!prefix <new>`: Change the bot prefix (≤ 7 characters). The default comes from `BOT_PREFIX` in `.env` until a server sets its own.
- `!settingspanel`: Change minimum and maximum players, pre-game, voting, and night timers from one form. Timers must be at least 5 seconds, and the minimum player count must be at least 3.

## Permissions
- Some settings require specific Discord permissions (e.g., Move Members).
- The bot uses an internal permission system; ensure admins have appropriate bot permissions.

See also: [Basics](help.md), [Advanced/Admin Commands](help-advanced.md), [Terms](tos.md), [Privacy](pp.md), [Code of Conduct](CODE_OF_CONDUCT.md).