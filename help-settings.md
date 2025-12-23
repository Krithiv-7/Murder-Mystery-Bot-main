# Murder‑Mystery‑Bot — Server Settings Reference

Last updated: December 23, 2025

The `!settings` command lets admins view and change server‑level configuration used by the game.

## Viewing Settings
- `!settings`: Shows the current values and toggle states.

## Numeric Settings
- `minPlayers <int>`: Minimum players required to start a game (≥ 4)
- `maxPlayers <int>`: Maximum players allowed in a game (≥ 4 and > minPlayers)
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

Usage examples:
- `!settings voiceChannel`
- `!settings lockVoiceChannelDuringNight`
- `!settings kickOfflinePlayers`

## Prefix
- `!prefix <new>`: Change the bot prefix (≤ 7 chars; admin permission required)

## Permissions
- Some settings require specific Discord permissions (e.g., Move Members).
- The bot uses an internal permission system; ensure admins have appropriate bot permissions.

See also: [Basics](help.md), [Advanced/Admin Commands](help-advanced.md), [Terms](tos.md), [Privacy](pp.md), [Code of Conduct](CODE_OF_CONDUCT.md).