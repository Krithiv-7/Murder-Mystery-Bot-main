"""Debug-only prefix commands with no cog equivalent (skip/set game state)."""
import permissions
from core.manager import game_manager
from .client import client


async def _debug_game(ctx, code, permission):
    if not await permissions.hasPermission(ctx, permission):
        return None
    game = game_manager.get_game(ctx.guild.id, code)
    if game is None:
        await ctx.send(":x: There's no game with that code!")
        return None
    return game


@client.command()
async def skipVotes(ctx, code):
    game = await _debug_game(ctx, code, "debug.game.skipVotes")
    if game is None:
        return
    game.skipVotingTime = True
    await ctx.send(f"Game **{game.code}** has skipped the voting time!")


@client.command()
async def skipNight(ctx, code):
    game = await _debug_game(ctx, code, "debug.game.skipNight")
    if game is None:
        return
    game.skipNight = True
    await ctx.send(f"Game **{game.code}** has skipped night!")


@client.command()
async def setWeather(ctx, code, num):
    game = await _debug_game(ctx, code, "debug.game.setWeather")
    if game is None:
        return
    game.weatherIntensity = int(num)
    await ctx.send(f"Game **{game.code}**'s weather has been set to **{num}**!")


@client.command()
async def setMoon(ctx, code, num):
    game = await _debug_game(ctx, code, "debug.game.setMoon")
    if game is None:
        return
    game.moon = int(num)
    await ctx.send(f"Game **{game.code}**'s moon has been set to **{num}**!")
