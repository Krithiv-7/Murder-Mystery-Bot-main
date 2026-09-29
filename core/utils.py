"""Utility functions for Murder Mystery bot."""
import random

from core.game_state import currentGames, allPlayers


def _resolve_game_factory_args(guild_or_client, debug_or_guild=False, debug=False):
    """Normalize the accepted legacy and modular factory call signatures."""
    client = None
    if hasattr(guild_or_client, "id") and hasattr(guild_or_client, "channels"):
        guild = guild_or_client
        actual_debug = debug_or_guild if isinstance(debug_or_guild, bool) else debug
    else:
        client = guild_or_client
        guild = debug_or_guild
        actual_debug = debug
    return guild, client, actual_debug


def randomizeList(lst):
    """Shuffle a list and return it."""
    result = lst.copy()
    random.shuffle(result)
    return result


def getKeys(d):
    """Get list of keys from a dictionary."""
    result = []
    for v in d:
        result.append(v)
    return result


def getPlayer(member, guild):
    """Find a player by member and guild."""
    if guild.id not in allPlayers:
        allPlayers[guild.id] = []
    for player in allPlayers[guild.id]:
        if player.member.id == member.id:
            return player
    return None


async def createNewGame(guild_or_client, debug_or_guild=False, debug=False, reason: str = "explicit", channel=None):
    """Create and initialize a new Game instance."""
    guild, client, actual_debug = _resolve_game_factory_args(
        guild_or_client,
        debug_or_guild=debug_or_guild,
        debug=debug,
    )

    from core.manager import game_manager

    return await game_manager.create_game(
        guild, actual_debug, client=client, channel=channel
    )


def isSpectating(member, guild):
    """Check if a member is spectating any game."""
    if guild.id not in currentGames:
        return False
    for game in currentGames[guild.id]:
        if member in game.spectators:
            return True
    return False


def getLen(guild):
    """Get the length of the lobby ID (for unique IDs)."""
    if guild.id not in currentGames:
        return 1
    count = len(currentGames[guild.id])
    if count < 10:
        return 1
    elif count < 100:
        return 2
    elif count < 1000:
        return 3
    else:
        return 4


def getAvailableGame(guild, lobby_id=None):
    """Get an available game to join, optionally by stable lobby code."""
    from core.game_state import availableGames
    from core.ids import normalize_code

    if guild.id not in availableGames:
        return None

    games = availableGames[guild.id]
    if not games:
        return None

    if lobby_id is not None:
        wanted = normalize_code(str(lobby_id))
        for game in games:
            if getattr(game, "code", None) == wanted:
                return game
        return None

    return games[0]


def findGameByPlayer(member, guild):
    """Find the game a player is in."""
    player = getPlayer(member, guild)
    if player and player.inGame:
        return player.game
    return None
