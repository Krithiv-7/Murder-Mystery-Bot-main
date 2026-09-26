"""Prefix commands for lobby lifecycle: create/join/list/cleanup/end."""
import discord
from discord.ext import commands

import dataStorage
import permissions
from core.game_state import currentGames
from .client import client
from .helpers import getPlayer, isSpectating, createNewGame


@client.command()
@commands.cooldown(2, 10, commands.BucketType.user)
async def join(ctx, *args):
    """Join a game lobby by ID. Admins must use -overwriteAdminWarning flag."""
    if not await permissions.hasPermission(ctx, "member.join"):
        return
    
    author = ctx.author
    guild = ctx.guild
    channel = ctx.message.channel
    prefix = dataStorage.getGuildData(ctx.guild, 'prefix', default='!')

    # Parse flags and lobby id from args (order-independent)
    overwrite_admin = False
    indexStr = None
    for arg in args:
        arg_lower = str(arg).lower()
        if arg_lower == "-overwriteadminwarning":
            overwrite_admin = True
        elif str(arg).lstrip('-').isdigit():
            if indexStr is None:
                indexStr = str(arg)

    allowedToRunCommandHere = True
    joinChannel = guild.get_channel(
        dataStorage.getGuildData(ctx.guild, "joinChannel")
    )
    is_admin = ctx.message.author.guild_permissions.administrator

    if (not is_admin) or overwrite_admin:
        if dataStorage.getGuildData(ctx.guild, "useJoinChannel"):
            if joinChannel is not None:
                if channel.id == dataStorage.getGuildData(
                        ctx.guild, "joinChannel"):
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

            if isSpectating(author):
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


@client.command(aliases=["endGames", "endAllGames", "stopGames", "stopAllGames"])
async def cleanup(ctx):
    if await permissions.hasPermission(ctx, "admin.endAllGames"):
        if ctx.message.author.guild_permissions.administrator:
            await ctx.send(":hourglass: Ending all running games, Please wait...")
            if ctx.guild.id not in currentGames:
                currentGames[ctx.guild.id] = []
            while len(currentGames[ctx.guild.id]) >= 1:
                currentGame = currentGames[ctx.guild.id][0]
                await currentGame.cleanUp()
            await ctx.send(":white_check_mark: All games have been stopped!")


@client.command(aliases=["stopGame"])
async def endGame(ctx, indexStr=None):
    if await permissions.hasPermission(ctx, "admin.endGame"):
        if ctx.guild.id not in currentGames:
            currentGames[ctx.guild.id] = []
        try:
            index = int(indexStr)
        except ValueError:
            prefix = dataStorage.getGuildData(
                ctx.guild, 'prefix', default='!'
            )
            msg = (
                f":x: Please give a game ID! You can find a game id "
                f"with {prefix}list."
            )
            await ctx.send(msg)
        else:
            if len(currentGames[ctx.guild.id]) > index:
                await ctx.send(f":hourglass: Ending game with ID {index}, please wait...")
                await currentGames[ctx.guild.id][index].cleanUp()
                await ctx.send(f":white_check_mark: Game with ID {index} has been ended!")
            else:
                await ctx.send(f":x: There's no game with that index!")


# command for creating a new empty game
@client.command(aliases=["create"])
@commands.cooldown(2, 30, commands.BucketType.user)
async def createGame(ctx, debugStr="False"):
    # Anyone can create a lobby if not currently in one.
    # Debug flag still requires permission.

    # Disallow creating a lobby while already in one
    existing_player = getPlayer(ctx.author, ctx.guild)
    if existing_player is not None and existing_player.inGame:
        await ctx.send(embed=discord.Embed(title=":x: You're already in a lobby",
                                           description="Leave your current lobby before creating a new one (use !leave).",
                                           color=0xff0000))
        return

    if debugStr == "True":
        has_debug_create = permissions.memberHasPermission(ctx.author, "debug.createGame")
        if has_debug_create:
            debug = True
        else:
            await ctx.send(":closed_lock_with_key: You need debug permissions to create a debug lobby.")
            return
    else:
        debug = False

    game = await createNewGame(ctx.message.guild, debug, reason="prefix-create")
    # Assign owner and add the creator
    game.owner_id = ctx.author.id
    # Add the creator to the newly created lobby
    try:
        await game.addPlayer(ctx.author)
    except Exception:
        pass
    idx = currentGames[ctx.guild.id].index(game)
    prefix = dataStorage.getGuildData(ctx.guild, 'prefix', default='!')
    if not debug:
        embed = discord.Embed(
            title="A new lobby has been created!",
            description=(
                f"Lobby ID: {idx}. You've been added to this lobby. "
                f"Share this ID for others to join with "
                f"{prefix}join {idx}"
            )
        )
    else:
        embed = discord.Embed(
            title="A new lobby has been created in debugging mode!",
            description=(
                f"Lobby ID: {idx}. You've been added to this lobby."
            )
        )
    await ctx.send(embed=embed)


@client.command()
@commands.cooldown(2, 10, commands.BucketType.user)
async def list(ctx):
    if await permissions.hasPermission(ctx, "member.list"):
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

            idx = currentGames[ctx.guild.id].index(game)
            value = (
                f"Started: {game.started}, day {game.day}, "
                f"players: {playerList}"
            )
            embed.add_field(name=f"ID: {idx}", value=value)

        await ctx.send(embed=embed)


