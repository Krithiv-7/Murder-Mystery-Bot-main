"""Main-guild-only events/commands (welcome messages, notification roles,
on_ready channel/role lookups, error routing). These all share a set of
bare module-level globals (mainGuild, joiningChannel, welcomeChannel, ...)
that on_ready populates via `global`, exactly like the original bot.py -
kept together in this one file so that pattern still works unmodified.
"""
import discord
from discord.ext import commands
from discord.utils import get
import traceback as tb

import dataStorage
import permissions
import tutorial
from core.config import testingBot, shortMainServerInvite, noPermissionEmbed
from core.game_state import currentGames
from .client import client
from .helpers import getPlayer, isSpectating

# initialize optional globals to avoid NameError in events
notificationMessage = None


@client.event
async def on_member_join(member):
    if member.guild == mainGuild:
        embed = discord.Embed(
            title=f"{member.display_name} just joined!",
            description=(
                f"Welcome {member.mention}, have fun with playing "
                "Murder Mystery!"
            ),
            color=0x00ff00
        )
        embed.set_thumbnail(url=member.avatar_url)
        await welcomeChannel.send(embed=embed)

        thumb_url = (
            "https://cdn.discordapp.com/attachments/"
            "554234775590666251/819314838949462017/waving-hand_1f44b.png"
        )
        embed = discord.Embed(
            title="Welcome to Murder Mystery!",
            description=(
                "Murder Mystery is a game of murder mystery inside "
                "discord using a custom discord bot."
            ),
            color=0x00b8ff
        )
        embed.set_thumbnail(url=thumb_url)
        embed.add_field(
            name="About the game",
            value=(
                "When a game starts, everyone gets assigned an in-game "
                "role. These roles have different abilities that can be "
                "used in the night. One of those roles is the murderer "
                "who can kill 1 person per night. The goal of the game "
                "is to find this person, convince other people that "
                "they're the murderer, and then vote to execute them "
                "during the day. If you are the murderer, then your "
                "goal is to kill everyone before they find out it's you."
                "\nEvery few minutes the game cycles between day and "
                "night. During the day you can vote to execute on who "
                "you think is the murderer. The player with the most "
                "votes will get executed."
            )
        )
        embed.add_field(
            name="Getting started",
            value=(
                f"Before playing the game, you should read the rules "
                f"in {rulesChannel.mention} and read the tutorial in "
                f"{gameTutorialChannel.mention}, {rolesTutorialChannel.mention}, "
                f"{itemsTutorialChannel.mention} and {commandsTutorialChannel.mention}."
            ),
            inline=False
        )
        embed.add_field(
            name="Joining a game",
            value=(
                f'To join a game simply type "!join" in '
                f'{joiningChannel.mention}'
            ),
            inline=False
        )
        embed.add_field(
            name="Have fun!",
            value="Thank you for playing Murder Mystery and have fun!"
        )
        try:
            await member.send(embed=embed)
        except discord.HTTPException:
            pass


@client.event
async def on_member_remove(member):
    if member.guild == mainGuild:
        embed = discord.Embed(title=f"{member.display_name} just left.", description=f"Goodbye {member.display_name}!",
                              color=0xff0000)
        embed.set_thumbnail(url=member.avatar_url)
        await welcomeChannel.send(embed=embed)



@client.command()
async def showAllRunningGames(ctx):
    if ctx.guild == mainGuild:
        if ctx.message.author.guild_permissions.administrator:
            result = {}
            for v in currentGames:
                result[v] = []
                for g in currentGames[v]:
                    result[v].append([len(g.players), g.started, g.day])
            await ctx.send(f"{result}")
        else:
            await ctx.send(embed=noPermissionEmbed)
    else:
        await ctx.send(":x: Sorry, but you can't do that here! You probably meant: !list")


@client.command()
@commands.cooldown(2, 10, commands.BucketType.user)
async def spectate(ctx, indexStr=None):
    if await permissions.hasPermission(ctx, "member.spectate"):
        if not isSpectating(ctx.author):
            if indexStr is None:
                if len(currentGames[ctx.guild.id]) == 1:
                    indexStr = "0"
                else:
                    if ctx.channel != joiningChannel:
                        await ctx.send(
                            embed=discord.Embed(title="Please enter a game ID",
                                                description="To get a game ID, type !list.",
                                                color=0xff0000))
            player = getPlayer(ctx.author, ctx.message.guild)
            if player is None:
                index = None
                try:
                    index = int(indexStr)
                except ValueError:
                    if ctx.channel != joiningChannel:
                        embed = discord.Embed(
                            title=":x: Please enter a number!",
                            description=(
                                "Please enter a game's ID to spectate "
                                "it. You can get a game's ID with !list."
                            ),
                            color=0xff0000
                        )
                        await ctx.send(embed=embed)
                except Exception:
                    await ctx.send(":x: An unknown error occurred!")
                    raise
                else:
                    games_count = len(currentGames[ctx.guild.id]) - 1
                    if index <= games_count:
                        await currentGames[ctx.guild.id][index].addSpectator(
                            ctx.author
                        )
                        if ctx.channel != joiningChannel:
                            embed = discord.Embed(
                                title="You are now spectating a game",
                                description=(
                                    "The game's channel should appear on "
                                    "the top of your channel list.\n"
                                    "To stop spectating, type !spectate again."
                                ),
                                color=0x0088ff
                            )
                            await ctx.send(embed=embed)
                    else:
                        if ctx.channel != joiningChannel:
                            embed = discord.Embed(
                                title=":x: That game doesn't exist!",
                                description=(
                                    "Please enter a valid game ID. You can "
                                    "get a game's ID with !list."
                                )
                            )
                            await ctx.send(embed=embed)


            else:
                if ctx.channel != joiningChannel:
                    embed = discord.Embed(
                        title=":x: You are already in a game!",
                        description=(
                            "You can't spectate a game while you're "
                            "already in a different game."
                        ),
                        color=0xff0000
                    )
                    await ctx.send(embed=embed)

        else:
            for game in currentGames[ctx.guild.id]:
                if ctx.author in game.spectators:
                    await game.removeSpectator(ctx.author)
                    if ctx.channel != joiningChannel:
                        await ctx.send(embed=discord.Embed(title="You are no longer spectating", color=0x0088ff))

# handling errors
@client.event
async def on_command_error(ctx, error):
    if ctx.guild == mainGuild:
        if ctx.channel.id == dataStorage.getGuildData(mainGuild, "joinChannel"):
            sendTo = errorChannel
        else:
            sendTo = ctx.channel
    else:
        sendTo = ctx.channel
    if isinstance(error, commands.MemberNotFound):
        embed = discord.Embed(
            title=":x: That's not a valid player!",
            description=(
                "Make sure you spelled the username correctly "
                "(including capitalization). You can also mention them "
                "using @username, or by right clicking their username "
                "and pressing mention, or by pressing their username "
                "if you're on mobile."
            ),
            color=0xff0011
        )
        await sendTo.send(embed=embed)
    elif "NotFound: 404 Not Found" in str(error):
        print(str(error))
        raise error

    elif isinstance(error, commands.MissingRequiredArgument):
        embed = discord.Embed(
            title=":x: You need to include more arguments!",
            description="You haven't provided enough arguments for this command.",
            color=0xff0000
        )
        await sendTo.send(embed=embed)
    elif isinstance(error, commands.CommandNotFound):
        if "!d " not in ctx.message.content:
            join_ch = dataStorage.getGuildData(ctx.guild, "joinChannel")
            if ctx.channel.id != join_ch:
                if ctx.guild == mainGuild:
                    embed = discord.Embed(
                        title=":x: Invalid command!",
                        description="Make sure you spelled it correctly!",
                        color=0xff0000
                    )
                    await sendTo.send(embed=embed)
    elif isinstance(error, ValueError):
        try:
            trace = ''.join(
                tb.format_exception(None, error, error.__traceback__)
            )
            embed = discord.Embed(
                title=":x: Value error!",
                description=(
                    f"{trace}\n\n\n"
                    "This error can be caused by giving the incorrect "
                    "data type in a command, but it can also be a bug.\n"
                    "If you think it's a bug, please report it. Otherwise "
                    "try giving the correct data type, like a number "
                    "instead of text."
                ),
                color=0xff0000
            )
            await sendTo.send(embed=embed)
        except Exception:
            print("Failed to send an error")
    else:
        try:
            trace = ''.join(
                tb.format_exception(None, error, error.__traceback__)
            )
            embed = discord.Embed(
                title=":x: An error occurred!",
                description=(
                    f"{trace}\n\n\n"
                    "Please report this error if you think this is a bug."
                ),
                color=0xff0000
            )
            await sendTo.send(embed=embed)
        except Exception:
            print("Failed to send an error")
        raise error


@client.command()
async def send_embeds(ctx, mode):
    joinEmbed = discord.Embed(title="Type !join to join a game!", color=0x0088ff)
    if ctx.guild == mainGuild:
        if ctx.message.author.guild_permissions.administrator:
            if mode == "local":
                embeds = tutorial.getTutorialEmbeds(ctx.guild)
                gameTutorialChannel = ctx.guild.get_channel(
                    dataStorage.getGuildData(ctx.guild, "gameTutorialChannel")
                )
                itemsTutorialChannel = ctx.guild.get_channel(
                    dataStorage.getGuildData(ctx.guild, "itemsTutorialChannel")
                )
                rolesTutorialChannel = ctx.guild.get_channel(
                    dataStorage.getGuildData(ctx.guild, "roleTutorialChannel")
                )
                commandsTutorialChannel = ctx.guild.get_channel(
                    dataStorage.getGuildData(ctx.guild, "commandsTutorialChannel")
                )
                all_channels_found = (
                    gameTutorialChannel is not None and
                    itemsTutorialChannel is not None and
                    rolesTutorialChannel is not None and
                    commandsTutorialChannel is not None
                )
                if all_channels_found:
                    await gameTutorialChannel.purge(10)
                    await itemsTutorialChannel.purge(10)
                    await rolesTutorialChannel.purge(10)
                    await commandsTutorialChannel.purge(10)
                    for v in embeds["game"]:
                        await gameTutorialChannel.send(embed=v)
                    for v in embeds["role"]:
                        await rolesTutorialChannel.send(embed=v)
                    for v in embeds["items"]:
                        await itemsTutorialChannel.send(embed=v)
                    for v in embeds["commands"]:
                        await commandsTutorialChannel.send(embed=v)
                else:
                    await ctx.send(":warning: One of the tutorial channels can't be found!")
                joinChannel = dataStorage.getGuildData(ctx.guild, "joinChannel")
                if joinChannel is not None:
                    await joinChannel.purge(20)
                    await joinChannel.send(embed=joinEmbed)
                else:
                    await ctx.send(":x: One of the tutorial channel IDs returns None!")
                await ctx.send(":white_check_mark: Done!")
            elif mode == "global":
                for v in dataStorage.getAllGuilds():
                    guild = client.get_guild(v)
                    if v["useTutorialChannels"]:
                        if guild is not None:
                            gameTutorialChannel = guild.get_channel(v["gameTutorialChannel"])
                            itemsTutorialChannel = guild.get_channel(v["itemsTutorialChannel"])
                            rolesTutorialChannel = guild.get_channel(v["rolesTutorialChannel"])
                            commandsTutorialChannel = guild.get_channel(v["commandsTutorialChannel"])
                            if gameTutorialChannel is not None and itemsTutorialChannel is not None and rolesTutorialChannel is not None and commandsTutorialChannel is not None:
                                try:
                                    embeds = tutorial.getTutorialEmbeds(guild)
                                    await gameTutorialChannel.purge(10)
                                    await itemsTutorialChannel.purge(10)
                                    await rolesTutorialChannel.purge(10)
                                    await commandsTutorialChannel.purge(10)
                                    for v in embeds["game"]:
                                        await gameTutorialChannel.send(embed=v)
                                    for v in embeds["role"]:
                                        await rolesTutorialChannel.send(embed=v)
                                    for v in embeds["items"]:
                                        await itemsTutorialChannel.send(embed=v)
                                    for v in embeds["commands"]:
                                        await commandsTutorialChannel.send(embed=v)
                                except Exception as error:
                                    await ctx.send(embed=discord.Embed(title=f":warning: Error in guild {guild.id}",
                                                                       description=f"{error}", color=0xfff100))
                            else:
                                await ctx.send(
                                    f":warning: Guild {v} uses tutorial channels, but one of the tutorial channels couldn't be found!")
                    if v["useJoinChannel"]:
                        if guild is not None:
                            joinChannel = guild.get_channel(v["joinChannel"])
                            if joinChannel is not None:
                                try:
                                    await joinChannel.purge(20)
                                    await joinChannel.send(embed=joinEmbed)
                                except Exception as error:
                                    await ctx.send(embed=discord.Embed(title=f":warning: Error in guild {guild.id}",
                                                                       description=f"{error}", color=0xfff100))
                            else:
                                await ctx.send(
                                    f":warning: guild {guild.id} uses the join channel, but no join channel could be found!")
                    await ctx.send(":white_check_mark: Done!")

            else:
                await ctx.send(":x: Please select mode local or global!")


        else:
            await ctx.send(embed=noPermissionEmbed)
    else:
        await ctx.send(":x: Sorry, but you can't use this command in this server.")


@client.command()
async def sendNotificationMessage(ctx):
    if ctx.guild == mainGuild:
        if ctx.message.author.guild_permissions.administrator:
            embed = discord.Embed(
                title="Notification settings",
                description=(
                    "Here you can change what notifications you want. "
                    "React the corresponding emojis to what notifications "
                    "you want."
                ),
                color=0x00b8ff
            )
            embed.add_field(
                name=":one: Bot updates",
                value="Get notified whenever the bot updates",
                inline=False
            )
            embed.add_field(
                name=":two: New games",
                value="Get notified whenever a new game is created",
                inline=False
            )
            embed.add_field(
                name=":three: Games starting",
                value=(
                    "Get notified whenever a new game is about to start "
                    "(so when there are enough players to start and the "
                    "countdown to starting begins)"
                ),
                inline=False
            )
            message = await notificationSettingsChannel.send(embed=embed)
            # NOTE: in some editors these might appear like normal numbers, but these are actually emojis.
            await message.add_reaction("1️⃣")
            await message.add_reaction("2️⃣")
            await message.add_reaction("3️⃣")
            global notificationMessage
            notificationMessage = message
            notificationMessageFile = open("notificationMessageID", "w")
            notificationMessageFile.write(str(notificationMessage.id))
            notificationMessageFile.close()
        else:
            await ctx.send(embed=noPermissionEmbed)




@client.command()
async def reloadCache(ctx):
    if ctx.guild == mainGuild:
        if ctx.message.author.guild_permissions.administrator:
            await ctx.send(":hourglass: Reloading cache, please wait...")
            dataStorage.reloadCache()
            await ctx.send(":white_check_mark: Cache has been reloaded!")
        else:
            await ctx.send(embed=noPermissionEmbed)


# channels & roles
@client.event
async def on_ready():
    global mainGuild, modRole, generalChannel, joiningChannel, rulesChannel, introductionChannel, gameTutorialChannel, rolesTutorialChannel, itemsTutorialChannel, bugChannel, errorChannel, infoChannels, welcomeChannel, commandsTutorialChannel, newGamesRole, gamesStartingRole, botUpdatesRole, nonGameRoles, mainGameRolePosition, notificationSettingsChannel, notificationChannel, notificationMessage, data
    print(f"Logged in as {client.user}")

    mainGuild = None
    if not testingBot:
        mainGuild = client.get_guild(803169209474482187)
        modRole = get(mainGuild.roles, id=809356484252794921)

        generalChannel = client.get_channel(803169209474482190)
        joiningChannel = client.get_channel(863871059367690250)
        rulesChannel = client.get_channel(809086129462706186)
        introductionChannel = client.get_channel(809086505581543514)
        gameTutorialChannel = client.get_channel(809091142040944656)
        rolesTutorialChannel = client.get_channel(809091154675105803)
        itemsTutorialChannel = client.get_channel(809091166950653982)
        commandsTutorialChannel = client.get_channel(809740266298540042)

        notificationSettingsChannel = client.get_channel(810533611228758067)
        notificationChannel = client.get_channel(810533716655865907)

        infoChannels = [joiningChannel, rulesChannel, introductionChannel, gameTutorialChannel, rolesTutorialChannel,
                        itemsTutorialChannel, commandsTutorialChannel]

        bugChannel = client.get_channel(809355113566306355)
        errorChannel = client.get_channel(809098068069974056)
        welcomeChannel = client.get_channel(809466910961696809)

        newGamesRole = get(mainGuild.roles, id=810528878341652490)
        gamesStartingRole = get(mainGuild.roles, id=856300184244846614)
        botUpdatesRole = get(mainGuild.roles, id=810528944456597536)

        nonGameRoles = [newGamesRole, gamesStartingRole, botUpdatesRole]
        # I know this isn't really a good way to do this but it's easy and it works
        notificationMessageFile = None
        try:
            notificationMessageFile = open("notificationMessageID", "r")
            msg_id = int(notificationMessageFile.read())
            notificationMessage = await notificationSettingsChannel.fetch_message(
                msg_id
            )
        except FileNotFoundError:
            print(
                "Notification message ID file not found. If you are not "
                "running this bot on the main murder mystery server, then "
                "please ignore this."
            )
        except Exception:
            raise
        finally:
            if notificationMessageFile is not None:
                notificationMessageFile.close()

        mainGameRolePosition = 0
        for r in nonGameRoles:
            if r.position > mainGameRolePosition:
                mainGameRolePosition = r.position
        mainGameRolePosition += 1

    # Sync slash commands (app commands)
    try:
        synced = await client.tree.sync()
        print(f"Synced {len(synced)} slash command(s)")
    except Exception as e:
        print(f"Failed to sync app commands: {e}")

    await client.change_presence(
        status=discord.Status.online,
        activity=discord.Game(
            f"!help | !setup | {shortMainServerInvite}"
        )
    )


# reaction roles
@client.event
async def on_raw_reaction_add(payload):
    if payload.guild_id is not None:
        member = payload.member
        channel = await client.fetch_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)
        guild = await client.fetch_guild(payload.guild_id)
        # Only handle notification reactions if notification message known
        notification_id = getattr(notificationMessage, "id", None)
        if notificationMessage is not None and message.id == notification_id:
            # NOTE: in some editors these might appear like normal numbers, but these are actually emojis.
            if payload.emoji.name == "1️⃣":
                await member.add_roles(botUpdatesRole)
            elif payload.emoji.name == "2️⃣":
                await member.add_roles(newGamesRole)
            elif payload.emoji.name == "3️⃣":
                await member.add_roles(gamesStartingRole)
            else:
                print(payload.emoji.name)


@client.event
async def on_raw_reaction_remove(payload):
    if payload.guild_id is not None:
        guild = await client.fetch_guild(payload.guild_id)
        member = await guild.fetch_member(payload.user_id)
        channel = await client.fetch_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)
        notification_id = getattr(notificationMessage, "id", None)
        if notificationMessage is not None and message.id == notification_id:
            # NOTE: These might appear like normal numbers but are emojis.
            if payload.emoji.name == "1️⃣":
                await member.remove_roles(botUpdatesRole)
            elif payload.emoji.name == "2️⃣":
                await member.remove_roles(newGamesRole)
            elif payload.emoji.name == "3️⃣":
                await member.remove_roles(gamesStartingRole)
            else:
                print(payload.emoji.name)


@client.command()
async def purgeInfoChannels(ctx):
    if ctx.guild == mainGuild:
        if ctx.message.author.guild_permissions.administrator:
            for channel in infoChannels:
                await channel.purge(limit=100)


