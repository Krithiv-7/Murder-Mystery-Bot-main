"""Admin commands for Murder Mystery Bot."""
import discord
from discord.ext import commands

import dataStorage
import permissions
from core.game_state import currentGames, availableGames, allPlayers
from core.utils import getPlayer


class AdminCommands(commands.Cog):
    """Admin-only commands."""
    
    def __init__(self, client):
        self.client = client

    @commands.command()
    async def resetState(self, ctx):
        """Admin-only: Clear in-memory state for this guild."""
        if not await permissions.hasPermission(ctx, "admin.resetState"):
            return
            
        gid = ctx.guild.id
        # End games first to clean channels if any
        if gid in currentGames and len(currentGames[gid]) > 0:
            await ctx.send(":hourglass: Ending all games before resetting state...")
            while len(currentGames[gid]) > 0:
                g = currentGames[gid][0]
                try:
                    await g.cleanUp()
                except Exception:
                    pass
        # Clear in-memory indices
        if gid in allPlayers:
            allPlayers[gid] = []
        if gid in availableGames:
            availableGames[gid] = []
        if gid in currentGames:
            currentGames[gid] = []
        # Clear any cached guild data
        try:
            if gid in dataStorage.cache:
                dataStorage.cache.pop(gid, None)
        except Exception:
            pass
        await ctx.send(":white_check_mark: State reset complete for this guild.")

    @commands.command()
    async def startGame(self, ctx, indexStr):
        """Start a lobby immediately. Allowed for lobby owner or admins."""
        # parse index
        try:
            index = int(indexStr)
        except ValueError:
            await ctx.send(":x: Please provide a numeric lobby ID.")
            return

        games = currentGames.get(ctx.guild.id, [])
        if not (0 <= index < len(games)):
            await ctx.send(":x: There's no game with that ID! Use !list to view all games.")
            return

        game = games[index]
        is_owner = getattr(game, "owner_id", None) == ctx.author.id
        has_admin = await permissions.hasPermission(ctx, "admin.game.startGame")

        if not (is_owner or has_admin):
            await ctx.send(
                ":closed_lock_with_key: Only the lobby owner or an admin can start this game."
            )
            return

        if game.started:
            await ctx.send(":x: This lobby has already started.")
            return

        game.startNow = True
        await ctx.send(
            f":white_check_mark: Game {indexStr} will start now or skip the countdown if it begins."
        )

    @commands.command(aliases=["endGames", "endAllGames", "stopGames", "stopAllGames"])
    async def cleanup(self, ctx):
        """End all running games."""
        if not await permissions.hasPermission(ctx, "admin.endAllGames"):
            return
            
        if ctx.message.author.guild_permissions.administrator:
            await ctx.send(":hourglass: Ending all running games, Please wait...")
            if ctx.guild.id not in currentGames:
                currentGames[ctx.guild.id] = []
            while len(currentGames[ctx.guild.id]) >= 1:
                currentGame = currentGames[ctx.guild.id][0]
                await currentGame.cleanUp()
            await ctx.send(":white_check_mark: All games have been stopped!")

    @commands.command(aliases=["stopGame"])
    async def endGame(self, ctx, indexStr=None):
        """End a specific game by ID."""
        if not await permissions.hasPermission(ctx, "admin.endGame"):
            return
            
        if ctx.guild.id not in currentGames:
            currentGames[ctx.guild.id] = []
        try:
            index = int(indexStr)
        except (ValueError, TypeError):
            prefix = dataStorage.getGuildData(ctx.guild, 'prefix', default='!')
            await ctx.send(f":x: Please give a game ID! Use {prefix}list.")
        else:
            if len(currentGames[ctx.guild.id]) > index:
                await ctx.send(f":hourglass: Ending game with ID {index}...")
                await currentGames[ctx.guild.id][index].cleanUp()
                await ctx.send(f":white_check_mark: Game with ID {index} has been ended!")
            else:
                await ctx.send(":x: There's no game with that index!")

    @commands.command()
    async def kick(self, ctx, member: discord.Member):
        """Kick a player from a game."""
        if not await permissions.hasPermission(ctx, "admin.game.kick"):
            return
            
        player = getPlayer(member, ctx.guild)
        if player is not None:
            if player.inGame:
                if not player.game.started:
                    await player.game.mainChannel.send(embed=discord.Embed(
                        title=f":heavy_minus_sign: {player.member.display_name} got kicked by {ctx.author.display_name}",
                        color=0xff0000
                    ))
                else:
                    if not player.game.nightTime:
                        await player.game.mainChannel.send(embed=discord.Embed(
                            title=f":heavy_minus_sign: {player.member.display_name} got kicked by {ctx.author.display_name}",
                            description=f"{player.member.display_name}{player.role.deadString}",
                            color=0xff0000
                        ))
                    else:
                        await player.game.sendToAllNightChannels(embed=discord.Embed(
                            title=f":heavy_minus_sign: {player.member.display_name} got kicked by {ctx.author.display_name}",
                            description=f"{player.member.display_name}{player.role.deadString}",
                            color=0xff0000
                        ))
                try:
                    await member.send(embed=discord.Embed(
                        title=f"You got kicked out of the game by {ctx.author.display_name}!",
                        color=0xff0000
                    ))
                except discord.HTTPException:
                    pass
                await player.game.removePlayer(player)
            else:
                await ctx.send(embed=discord.Embed(title="That player is not in game!", color=0xff0000))
        else:
            await ctx.send(embed=discord.Embed(title="I can't find that player in any game!", color=0xff0000))

    @commands.command()
    async def purge(self, ctx, amount):
        """Delete messages in a channel."""
        if not await permissions.hasPermission(ctx, "admin.purge"):
            return
        await ctx.message.channel.purge(limit=int(amount))

    @commands.command()
    async def giveGold(self, ctx, member: discord.Member, amount):
        """Give gold to a player in a game."""
        if not await permissions.hasPermission(ctx, "admin.game.giveGold"):
            return
            
        player = getPlayer(member, ctx.message.guild)
        if player is not None:
            if player.inGame:
                intAmount = int(amount)
                player.gold += intAmount
                await ctx.send(f"Gave :coin: {amount} gold to {member.mention}")
            else:
                await ctx.send("That player is not in game!")
        else:
            await ctx.send("That member is not in game!")


async def setup(client):
    """Setup function for cog."""
    await client.add_cog(AdminCommands(client))
