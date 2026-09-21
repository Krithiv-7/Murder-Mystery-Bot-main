# Murder Mystery Bot - Modular Structure

This document describes the current modular structure of the Murder Mystery Discord bot.

## Directory Structure

```
Murder-Mystery-Bot-main/
├── bot.py              # Main entry point, events, startup, and compatibility handlers
├── core/               # Core game modules
│   ├── __init__.py     # Package exports
│   ├── config.py       # Bot configuration constants
│   ├── game_state.py   # Shared mutable state dictionaries
│   ├── player.py       # Player class
│   ├── game.py         # Game class
│   └── utils.py        # Utility functions
├── commands/           # Command cogs (discord.py Cogs)
│   ├── __init__.py     # Package exports and setup function
│   ├── game_commands.py    # Game-related commands (join, list, spectate)
│   ├── admin_commands.py   # Admin commands (kick, cleanup, etc.)
│   └── player_commands.py  # In-game player commands (vote, shop, buy, etc.)
└── ... (other existing files)
```

## Module Overview

### core/config.py
Contains bot configuration constants:
- `localStorage` - Whether to use local JSON storage
- `testingBot` - Testing mode flag
- `requiredRoles` - Roles required in every game
- `roles` - Available game roles with player requirements
- `mainServerInvite` - Main server invite link
- `noPermissionEmbed` - Standard no-permission embed
- `GAME_DEFAULTS` - Shared player, timer, and prefix defaults

### core/game_state.py
Shared mutable state dictionaries:
- `currentGames` - Dictionary of active games by guild ID
- `availableGames` - Dictionary of joinable games by guild ID
- `allPlayers` - Dictionary of all players by guild ID
- `mainGuild`, `mainGameRolePosition`, etc. - Main guild globals
- `set_main_guild_globals()` - Function to set globals from on_ready

### core/player.py
The `Player` class representing a player in a game:
- Inventory management
- Role assignment
- Game state tracking (votes, gold, etc.)

### core/game.py
The `Game` class representing a game instance:
- Public game channel and role creation
- DM-first delivery for private role instructions and night prompts
- Player management
- Game flow (countdown, initialization, day/night cycle)
- Win condition checking

### core/utils.py
Utility functions:
- `getPlayer(member, guild)` - Find a player by member
- `isSpectating(member, guild)` - Check if spectating
- `createNewGame(client, guild, debug)` - Create new game
- `getAvailableGame(guild, lobby_id)` - Get available game

### commands/
Discord.py Cogs for commands:
- `GameCommands` - join, list, spectate
- `AdminCommands` - resetState, startGame, cleanup, endGame, kick, etc.
- `PlayerCommands` - whisper, vote, use, shop, buy, leave, forceStart

## Usage

### Importing modules
```python
from core import (
    currentGames, availableGames, allPlayers,
    Game, Player, getPlayer, isSpectating
)
from core.config import localStorage, roles, requiredRoles
```

### Using cogs (in bot.py)
```python
from commands import setup_cogs

# Loaded in client.setup_hook to keep bot.py slim:
@client.event
async def setup_hook():
   await setup_cogs(client)
```

### Command ownership
Command cogs are the active implementation for migrated game, player, and admin commands. `bot.py` retains event handlers, startup, slash commands, and a small compatibility surface. New prefix commands should be added to the appropriate cog rather than duplicated in `bot.py`.

## Operational boundaries

1. `core.game.Game` is the canonical game lifecycle implementation.
2. `core.player.Player` is the canonical player model and provides the DM private-message transport.
3. `core.utils.createNewGame` is the canonical game factory.
4. `commands/` owns migrated prefix command implementations.
5. `bot.py` owns Discord event handlers, startup, slash commands, and compatibility code that has not yet been extracted.
6. The game creates a public game channel. Private role instructions are sent by DM where possible; some ability-specific temporary channels may still exist.

When refactoring remaining compatibility code, update call sites and tests first, then remove the old implementation rather than maintaining a second behavior path.

5. Simplify bot.py to just client creation and run
