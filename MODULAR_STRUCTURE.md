# Murder Mystery Bot - Modular Structure

This document describes the new modular structure created for the Murder Mystery Discord bot.

## Directory Structure

```
Murder-Mystery-Bot-main/
├── bot.py              # Main entry point (original - can be simplified)
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
- Channel and role creation
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

# In on_ready or after client creation:
await setup_cogs(client)
```

## Notes

1. The original bot.py remains functional - the new modules are an extraction/refactor
2. Some commands are duplicated between bot.py and commands/ - you can gradually migrate
3. The Game class in core/game.py is a simplified version - full implementation should copy remaining methods from bot.py
4. Event handlers (on_ready, on_message, etc.) remain in bot.py for now

## Migration Steps

To fully migrate to the modular structure:

1. Replace imports in bot.py:
   ```python
   from core import currentGames, availableGames, allPlayers, Game, Player, getPlayer
   ```

2. Load cogs instead of defining commands inline:
   ```python
   # In on_ready:
   from commands import setup_cogs
   await setup_cogs(client)
   ```

3. Move remaining commands to appropriate cog files

4. Move event handlers to an events.py module if desired

5. Simplify bot.py to just client creation and run
