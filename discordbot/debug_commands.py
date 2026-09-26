"""Debug-only prefix commands with no cog equivalent (skip/set game state)."""
import permissions
from core.game_state import currentGames
from .client import client


@client.command()
async def skipVotes(ctx, indexStr):
    if await permissions.hasPermission(ctx, "debug.game.skipVotes"):
        index = int(indexStr)
        if index <= len(currentGames[ctx.guild.id]) - 1:
            currentGames[ctx.guild.id][index].skipVotingTime = True
            await ctx.send(
                f"Game with index **{indexStr}** has skipped the voting time!")
        else:
            await ctx.send(":x: There's no game with that index!")


@client.command()
async def skipNight(ctx, indexStr):
    if await permissions.hasPermission(ctx, "debug.game.skipNight"):
        index = int(indexStr)
        if index <= len(currentGames[ctx.guild.id]) - 1:
            currentGames[ctx.guild.id][index].skipNight = True
            await ctx.send(
                f"Game with index **{indexStr}** has skipped night!")
        else:
            await ctx.send(":x: There's no game with that index!")


@client.command()
async def setWeather(ctx, indexStr, num):
    if await permissions.hasPermission(ctx, "debug.game.setWeather"):
        index = int(indexStr)
        if index <= len(currentGames[ctx.guild.id]) - 1:
            currentGames[ctx.guild.id][index].weatherIntensity = int(num)
            await ctx.send(
                f"Game with index **{indexStr}**'s weather has been set to **{num}**!")
        else:
            await ctx.send(":x: There's no game with that index!")


@client.command()
async def setMoon(ctx, indexStr, num):
    if await permissions.hasPermission(ctx, "debug.game.setMoon"):
        index = int(indexStr)
        if index <= len(currentGames[ctx.guild.id]) - 1:
            currentGames[ctx.guild.id][index].moon = int(num)
            await ctx.send(
                f"Game with index **{indexStr}**'s moon has been set to **{num}**!")
        else:
            await ctx.send(":x: There's no game with that index!")

