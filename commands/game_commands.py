"""Game-related commands for Murder Mystery Bot."""
import discord
from discord.ext import commands

import dataStorage
import permissions
from core.game_state import currentGames, availableGames, allPlayers
from core.utils import getPlayer, isSpectating


class GameCommands(commands.Cog):
    """Commands related to game management."""
    
    def __init__(self, client):
        self.client = client

    @commands.command()
    @commands.cooldown(2, 10, commands.BucketType.user)
    async def join(self, ctx, *args):
        """Join a game lobby by ID. Admins must use -overwriteAdminWarning flag."""
        if not await permissions.hasPermission(ctx, "member.join"):
            return
            
        author = ctx.author
        guild = ctx.guild
        channel = ctx.message.channel
        prefix = dataStorage.getGuildData(ctx.guild, 'prefix', default='!')

        # Parse flags and lobby id from args (order-independent)
        tokens = list(args) if args else []
        overwrite_admin = any(
            t.lower() == "-overwriteadminwarning" for t in tokens
        )
        # Extract first numeric token as lobby id
        indexStr = None
        for t in tokens:
            if t.lstrip('-').isdigit():
                indexStr = t
                break

        allowedToRunCommandHere = True
        joinChannel = guild.get_channel(
            dataStorage.getGuildData(ctx.guild, "joinChannel")
        )
        is_admin = ctx.message.author.guild_permissions.administrator

        if (not is_admin) or overwrite_admin:
            if dataStorage.getGuildData(ctx.guild, "useJoinChannel"):
                if joinChannel is not None:
                    if channel.id == dataStorage.getGuildData(ctx.guild, "joinChannel"):
                        try:
                            await ctx.message.delete()
                        except discord.HTTPException:
                            pass
                    else:
                        await ctx.send(embed=discord.Embed(
                            title=":x: You can't use that command here!",
                            description=f"Use {joinChannel.mention}",
                            color=0xff0000))
                        allowedToRunCommandHere = False

            if allowedToRunCommandHere:
                # Require an ID argument
                if indexStr is None:
                    await ctx.send(embed=discord.Embed(
                        title=":x: Please provide a lobby ID",
                        description=(
                            f"Use {prefix}list to find lobby IDs, then run "
                            f"{prefix}join <ID>. To create a lobby, use "
                            f"{prefix}create."
                        ),
                        color=0xff0000))
                    return

                existing = getPlayer(author, guild)
                if existing is not None and existing.inGame:
                    embed = discord.Embed(
                        title="You are already in a game!",
                        description="Leave your current game first.",
                        color=0xff000d)
                    await channel.send(embed=embed)
                    return

                if isSpectating(author, guild):
                    embed = discord.Embed(
                        title="You can't join while spectating!",
                        description="Use !spectate to stop spectating first.",
                        color=0xff0000)
                    await channel.send(embed=embed)
                    return

                # Parse lobby index
                try:
                    index = int(indexStr)
                except ValueError:
                    await ctx.send(embed=discord.Embed(
                        title=":x: Invalid ID",
                        description="Please provide a numeric lobby ID.",
                        color=0xff0000))
                    return

                if guild.id not in currentGames:
                    currentGames[guild.id] = []

                if not (0 <= index < len(currentGames[guild.id])):
                    await ctx.send(embed=discord.Embed(
                        title=":x: Lobby not found",
                        description=f"Use {prefix}list to find lobby IDs.",
                        color=0xff0000))
                    return

                game_to_join = currentGames[guild.id][index]

                # Check lobby state
                if game_to_join.started:
                    await ctx.send(embed=discord.Embed(
                        title=":x: This lobby has already started",
                        description=(
                            "Join an available lobby or create a new one "
                            f"with {prefix}create."
                        ),
                        color=0xff0000))
                    return

                max_players = dataStorage.getGuildData(
                    ctx.guild, "maxPlayers", default=30
                )
                if len(game_to_join.players) >= max_players:
                    await ctx.send(embed=discord.Embed(
                        title=":x: This lobby is full",
                        description=(
                            f"Max players: {max_players}. "
                            "Choose another lobby or create a new one."
                        ),
                        color=0xff0000))
                    return

                # Offline check
                kick_offline = dataStorage.getGuildData(
                    guild, "kickOfflinePlayers", default=False
                )
                if author.status == discord.Status.offline and kick_offline:
                    await channel.send(embed=discord.Embed(
                        title="You can't play if your status is offline!",
                        description="Change your status and try again.",
                        color=0xff0000))
                    return

                # Success: add player
                await game_to_join.addPlayer(author)

                # Confirmation message
                confirm_embed = discord.Embed(
                    title=":white_check_mark: You joined lobby!",
                    description=(
                        f"Lobby ID: {index} | "
                        f"Players: {len(game_to_join.players)}"
                    ),
                    color=0x00ff00)
                try:
                    await author.send(embed=confirm_embed)
                except discord.HTTPException:
                    pass  # DMs disabled

        else:
            # Admin warning
            embed = discord.Embed(
                title=":warning: You have administrator permissions",
                description=(
                    "This game hides channels from other players. "
                    "With admin perms, you can see all channels.\n\n"
                    "**Use an alt account without admin to play.**\n\n"
                    f"Override: `{prefix}join <ID> -overwriteAdminWarning`"
                ),
                color=0xfff100)
            if dataStorage.getGuildData(ctx.guild, "useJoinChannel"):
                try:
                    await author.send(embed=embed)
                except discord.HTTPException:
                    pass
                try:
                    await ctx.message.delete()
                except discord.HTTPException:
                    pass
            else:
                await channel.send(embed=embed)

    @commands.command()
    @commands.cooldown(2, 10, commands.BucketType.user)
    async def list(self, ctx):
        """List all current games."""
        if not await permissions.hasPermission(ctx, "member.list"):
            return
            
        embed = discord.Embed(
            title="Currently running games",
            description=(
                "Here is a list of all currently running games.\n"
                "Use !join <ID> to join a lobby that hasn't started yet.\n"
                "Use !spectate <ID> to watch a game."
            ),
            color=0x0088ff
        )
        
        if ctx.guild.id not in currentGames:
            currentGames[ctx.guild.id] = []
            
        for game in currentGames[ctx.guild.id]:
            playerList = ""
            for player in game.players:
                playerList = playerList + str(player.member.mention)

            if playerList == "":
                playerList = "There are no players in this game"

            embed.add_field(
                name=f"ID: {currentGames[ctx.guild.id].index(game)}",
                value=f"Started: {game.started}, day {game.day}, players: {playerList}"
            )

        await ctx.send(embed=embed)

    @commands.command()
    @commands.cooldown(2, 10, commands.BucketType.user)
    async def spectate(self, ctx, indexStr=None):
        """Spectate a game."""
        if not await permissions.hasPermission(ctx, "member.spectate"):
            return
            
        from core.game_state import joiningChannel
        
        if not isSpectating(ctx.author, ctx.guild):
            if indexStr is None:
                if len(currentGames.get(ctx.guild.id, [])) == 1:
                    indexStr = "0"
                else:
                    if ctx.channel != joiningChannel:
                        await ctx.send(embed=discord.Embed(
                            title="Please enter a game ID",
                            description="To get a game ID, type !list.",
                            color=0xff0000
                        ))
                        return
                        
            player = getPlayer(ctx.author, ctx.message.guild)
            if player is None:
                try:
                    index = int(indexStr)
                except ValueError:
                    if ctx.channel != joiningChannel:
                        await ctx.send(embed=discord.Embed(
                            title=":x: Please enter a number!",
                            description="Please enter a game's ID to spectate it.",
                            color=0xff0000
                        ))
                    return
                except Exception:
                    await ctx.send(":x: An unknown error occurred!")
                    raise
                else:
                    if index <= len(currentGames.get(ctx.guild.id, [])) - 1:
                        await currentGames[ctx.guild.id][index].addSpectator(ctx.author)
                        if ctx.channel != joiningChannel:
                            await ctx.send(embed=discord.Embed(
                                title="You are now spectating a game",
                                description="To stop spectating, type !spectate again.",
                                color=0x0088ff
                            ))
                    else:
                        if ctx.channel != joiningChannel:
                            await ctx.send(embed=discord.Embed(
                                title=":x: That game doesn't exist!",
                                description="Please enter a valid game ID."
                            ))
            else:
                if ctx.channel != joiningChannel:
                    await ctx.send(embed=discord.Embed(
                        title=":x: You are already in a game!",
                        description="You can't spectate while in a game.",
                        color=0xff0000
                    ))
        else:
            for game in currentGames.get(ctx.guild.id, []):
                if ctx.author in game.spectators:
                    await game.removeSpectator(ctx.author)
                    from core.game_state import joiningChannel
                    if ctx.channel != joiningChannel:
                        await ctx.send(embed=discord.Embed(
                            title="You are no longer spectating",
                            color=0x0088ff
                        ))


async def setup(client):
    """Setup function for cog."""
    await client.add_cog(GameCommands(client))
