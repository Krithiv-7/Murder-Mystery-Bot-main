"""Utility functions for Murder Mystery bot."""
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

