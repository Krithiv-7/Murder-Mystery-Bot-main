"""Utility functions for Murder Mystery bot."""
import random

from core.game_state import currentGames, allPlayers


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


def createNewGame(client, guild, debug=False):
    """Create a new game instance."""
    from core.game import Game
    return Game(guild, debug)


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
    """Get an available game to join, optionally by lobby ID."""
    from core.game_state import availableGames
    
    if guild.id not in availableGames:
        return None
    
    games = availableGames[guild.id]
    if not games:
        return None
    
    if lobby_id is not None:
        # Find game by lobby ID
        try:
            idx = int(lobby_id)
            if 0 <= idx < len(games):
                return games[idx]
        except (ValueError, TypeError):
            pass
        return None
    
    # Return first available game
    return games[0] if games else None


def findGameByPlayer(member, guild):
    """Find the game a player is in."""
    player = getPlayer(member, guild)
    if player and player.inGame:
        return player.game
    return None
