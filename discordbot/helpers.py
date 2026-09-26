"""Small stateless helpers shared across bot.py's command/event modules."""
import discord
import random

from core.game_state import allPlayers, currentGames


def randomizeList(l):
    random.shuffle(l)
    return l


def getKeys(d):
    l = []
    for v in d:
        l.append(v)
    return l


def getPlayer(member, guild):
    if guild is None:
        for players in allPlayers.values():
            for player in players:
                if player.member == member:
                    return player
        return None
    if guild.id not in allPlayers:
        allPlayers[guild.id] = []
    for player in allPlayers[guild.id]:
        if player.member == member:
            return player
    return None


async def createNewGame(guild_or_client, debug_or_guild=False, debug=False, reason: str = "explicit", channel=None):
    """Create a game while keeping the legacy bot API compatible."""
    try:
        import inspect
        caller = inspect.stack()[1].function
        guild_id = getattr(guild_or_client, "id", None)
        print(f"[createNewGame] reason={reason} caller={caller} guild={guild_id}")
    except Exception:
        pass

    from core.utils import createNewGame as shared_create_new_game
    return await shared_create_new_game(
        guild_or_client,
        debug_or_guild=debug_or_guild,
        debug=debug,
        reason=reason,
        channel=channel,
    )


def isSpectating(member: discord.Member):
    if not member.guild.id in currentGames:
        currentGames[member.guild.id] = []
    spectating = False
    for game in currentGames[member.guild.id]:
        if member in game.spectators:
            spectating = True
    return spectating


def getLen(x):
    l = 0
    for v in x:
        l += 1
    return l
