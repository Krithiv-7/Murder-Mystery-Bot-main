import discord
import dataStorage
import permissions
import tutorial

doingSetup = []


async def processSetupReaction(member: discord.member, channel: discord.TextChannel, emoji: discord.emoji):
    if dataStorage.getGuildData(member.guild, "setupStarted", default=False) and member.guild.id not in doingSetup:
        dataStorage.setGuildData(member.guild, "setupStarted", value=False)
    if dataStorage.getGuildData(member.guild, "setupStarted", default=False):
        if dataStorage.getGuildData(member.guild, "setupType") == 0:
            if dataStorage.getGuildData(member.guild, "setupProgress") == 0:
                if emoji.name == "1️⃣":
                    dataStorage.setGuildData(member.guild, "setupType", value=1)
                elif emoji.name == "2️⃣":
                    dataStorage.setGuildData(member.guild, "setupType", value=2)

                if emoji.name == "1️⃣" or emoji.name == "2️⃣":
                    dataStorage.setGuildData(member.guild, "setupProgress", increase=1)
                    dataStorage.setGuildData(member.guild, "awaitingSetupMessage", value=True)
                    await channel.send(embed=discord.Embed(title=":person_in_tuxedo: Please mention all admin roles",
                                                           description="""Mention all roles that you want to be able to execute admin-only commands.\nYou can mention a role by typing @<role name> and clicking the role from the list that appears above your message box.\nNote: you have to mention all the admin roles in the same message.\n\nIf you don't have any admin roles, say "skip".\nIf you want to cancel the setup, say "cancel" """,
                                                           color=0x00b8ff))

            else:
                await channel.send(embed=discord.Embed(title=":x: An error occurred during the setup:",
                                                       description="setupType is 0 but setupProgress is not 0.\n\nplease try running the setup again!",
                                                       color=0xff0000))

        elif dataStorage.getGuildData(member.guild, "setupType") == 2:
            if dataStorage.getGuildData(member.guild, "setupProgress") == 3:
                if emoji.name == "✅":
                    dataStorage.setGuildData(member.guild, "useTutorialChannels", value=True)
                elif emoji.name == "❌":
                    dataStorage.setGuildData(member.guild, "useTutorialChannels", value=False)
                if emoji.name == "✅" or emoji.name == "❌":
                    dataStorage.setGuildData(member.guild, "setupProgress", increase=1)
                    msg = await channel.send(embed=discord.Embed(title=":fast_forward: Use join channel?",
                                                                 description="Create a channel where people can use !join. If you choose no, !join can be used everywhere in the server.",
                                                                 color=0x00b8ff))
                    await msg.add_reaction("✅")
                    await msg.add_reaction("❌")
                    dataStorage.setGuildData(member.guild, "setupMessage", value=msg.id)

            elif dataStorage.getGuildData(member.guild, "setupProgress") == 4:
                if emoji.name == "✅":
                    dataStorage.setGuildData(member.guild, "useJoinChannel", value=True)
                elif emoji.name == "❌":
                    dataStorage.setGuildData(member.guild, "useJoinChannel", value=False)
                if emoji.name == "✅" or emoji.name == "❌":
                    await channel.send(embed=discord.Embed(title="Finishing the setup",
                                                           description="Configuring settings and creating channels, this might take a moment.",
                                                           color=0x00b8ff))
                    await finishSetup(member.guild, dataStorage.getGuildData(member.guild, "setupType"))
                    if dataStorage.getGuildData(member.guild, "useJoinChannel"):
                        await channel.send(embed=discord.Embed(title=":white_check_mark: Setup complete!",
                                                               description=f"The setup is now complete!\nYou can now join a game using !join in {member.guild.get_channel(dataStorage.getGuildData(member.guild, 'joinChannel')).mention}\n\nTo configure more settings, use !settings\nTo configure permissions, use !permissions\nUse !prefix to set the bot's command prefix",
                                                               color=0x00ff00))
                    else:
                        await channel.send(embed=discord.Embed(title=":white_check_mark: Setup complete!",
                                                               description=f"The setup is now complete!\nYou can now join a game using !join\n\nTo configure more settings, use !settings\nTo configure permissions, use !permissions\nUse !prefix to set the bot's command prefix",
                                                               color=0x00ff00))


async def processSetupMessage(message: discord.Message):
    if dataStorage.getGuildData(message.guild, "setupStarted", default=False) and message.guild.id not in doingSetup:
        dataStorage.setGuildData(message.guild, "setupStarted", value=False)
    if dataStorage.getGuildData(message.guild, "setupStarted", default=False):
        if dataStorage.getGuildData(message.guild, "setupProgress") == 1:
            if len(message.raw_role_mentions) > 0:
                for v in message.raw_role_mentions:
                    if message.guild.get_role(v) is not None:
                        permissions.addPermissionToRole(message.guild.get_role(v), "admin.*")
                        permissions.addPermissionToRole(message.guild.get_role(v), "debug.*")
                    else:
                        await message.channel.send(embed=discord.Embed(title=":x: Couldn't find that role!",
                                                                       description=f"That role couldn't be found. It might not be part of this server!\nPlease only mention roles that are part of this server.\n\nmessage.guild.get_role({v}) returned None.\nPlease report this error if you think it's a bug.",
                                                                       color=0xff0000))

                if dataStorage.getGuildData(message.guild, "setupType") == 1:
                    dataStorage.setGuildData(message.guild, "setupProgress", increase=1)
                elif dataStorage.getGuildData(message.guild, "setupType") == 2:
                    dataStorage.setGuildData(message.guild, "setupProgress", increase=1)
                else:
                    await message.channel.send(":x: setupType is not 1 or 2!")

                msg = await message.channel.send(
                    embed=discord.Embed(title=":page_with_curl: Choose a channel for game summaries",
                                        description="Mention a channel where game summaries will be sent.\nWhen a game is finished, a summary of the game will be sent there, with who won, what day it was, how many players there where and who what role was.\nPlease mention a channel to send those summaries in. You can mention a channel with #<channel name>.\nIf you want to automatically create a new channel, say 'new'.\nIf you don't want summary messages, say 'skip'\nIf you want to cancel the setup, say 'cancel'",
                                        color=0x00b8ff))
                dataStorage.setGuildData(message.guild, "setupMessage", value=msg.id)



            elif message.content.lower().strip() == "skip":
                dataStorage.setGuildData(message.guild, "setupProgress", increase=1)
                msg = await message.channel.send(embed=discord.Embed(title=":page_with_curl: Choose a channel for game summaries",
                                                                     description="Mention a channel where game summaries will be sent.\nWhen a game is finished, a summary of the game will be sent there, with who won, what day it was, how many players there where and who what role was.\nPlease mention a channel to send those summaries in. You can mention a channel with #<channel name>.\nIf you want to automatically create a new channel, say 'new'.\nIf you don't want summary messages, say 'skip'\nIf you want to cancel the setup, say 'cancel'",
                                                                     color=0x00b8ff))
                dataStorage.setGuildData(message.guild, "setupMessage", value=msg.id)
            elif message.content.lower().strip() == "cancel":
                dataStorage.setGuildData(message.guild, "setupStarted", value=False)
                await message.channel.send(":white_check_mark: Setup has been cancelled")
            else:
                await message.channel.send(embed=discord.Embed(title=":x: You didn't mention any roles!",
                                                               description="Mention all roles that you want to be able to execute admin-only commands.\nYou can mention a role by typing @<role name> and clicking the role from the list that appears above your message box.\nNote: you have to mention all the admin roles in the same message.",
                                                               color=0xff0000))
        elif dataStorage.getGuildData(message.guild, "setupProgress") == 2:
            continueSetup = True
            if len(message.raw_channel_mentions) > 0:
                if message.guild.get_channel(message.raw_channel_mentions[0]) is not None:
                    dataStorage.setGuildData(message.guild, "useSummaryEmbeds", value=True)
                    dataStorage.setGuildData(message.guild, "summaryChannel", value=message.raw_channel_mentions[0])
                    dataStorage.setGuildData(message.guild, "awaitingSetupMessage", value=False)
                else:
                    await message.channel.send(embed=discord.Embed(title=":x: You didn't mention an existing channel!",
                                                                   description=f"Please try mentioning a different channel\nIf you want to automatically create a new channel, say 'new'.\nIf you don't want summary messages, say 'skip'\nIf you want to cancel the setup, say 'cancel'\n\nmessage.guild.get_channel({message.raw_channel_mentions[0]}) returned None.\nPlease report this error if you think it's a bug.",
                                                                   color=0xff0000))
            elif message.content.lower().strip() == "skip":
                dataStorage.setGuildData(message.guild, "useSummaryEmbeds", value=False)
            elif message.content.lower().strip() == "new":
                dataStorage.setGuildData(message.guild, "useSummaryEmbeds", value=True)
                dataStorage.setGuildData(message.guild, "summaryChannel", value=None)
            elif message.content.lower().strip() == "cancel":
                dataStorage.setGuildData(message.guild, "setupStarted", value=False)
                await message.channel.send(":white_check_mark: Setup has been cancelled")
                continueSetup = False
            else:
                await message.channel.send(embed=discord.Embed(title=":x: You didn't mention any channel!",
                                                               description="You can mention a channel by typing #<channel name> and selecting",
                                                               color=0xff0000))
                continueSetup = False
            if continueSetup:
                if dataStorage.getGuildData(message.guild, "setupType") == 1:
                    await message.channel.send(embed=discord.Embed(title="Finishing the setup",
                                                                   description="Configuring settings and creating channels, this might take a moment.",
                                                                   color=0x00b8ff))
                    await finishSetup(message.guild, dataStorage.getGuildData(message.guild, "setupType"))
                    await message.channel.send(embed=discord.Embed(title=":white_check_mark: Setup complete!",
                                                                   description=f"The setup is now complete!\nYou can now join a game using !join in {message.guild.get_channel(dataStorage.getGuildData(message.guild, 'joinChannel')).mention}\n\nTo configure more settings, use !settings\nTo configure permissions, use !permissions\nUse !prefix to set the bot's command prefix",
                                                                   color=0x00ff00))
                elif dataStorage.getGuildData(message.guild, "setupType") == 2:
                    dataStorage.setGuildData(message.guild, "setupProgress", increase=1)
                    msg = await message.channel.send(embed=discord.Embed(title=":student: Use tutorial channels?",
                                                                         description="Channels will be made with a tutorial for the game so new people know how to play the game",
                                                                         color=0x00b8ff))
                    await msg.add_reaction("✅")
                    await msg.add_reaction("❌")
                    dataStorage.setGuildData(message.guild, "setupMessage", value=msg.id)
        else:
            await message.channel.send(":x: setupType is not 1 or 2!")


async def initializeSetup(ctx, gamesRunning):
    if dataStorage.getGuildData(ctx.guild, "setupStarted", default=False) and ctx.guild.id not in doingSetup:
        dataStorage.setGuildData(ctx.guild, "setupStarted", value=False)
    if not dataStorage.getGuildData(ctx.guild, "setupStarted", default=False) or not dataStorage.getGuildData(ctx.guild,
                                                                                                              "setupFinished",
                                                                                                              default=False):
        dataStorage.setGuildData(ctx.guild, "setupStarted", value=True)
        doingSetup.append(ctx.guild.id)
        dataStorage.setGuildData(ctx.guild, "awaitingSetupMessage", value=False)
        dataStorage.setGuildData(ctx.guild, "setupFinished", value=False)
        dataStorage.setGuildData(ctx.guild, "setupType", value=0)  # 0 = unset, 1 = simple, 2 = advanced
        dataStorage.setGuildData(ctx.guild, "setupProgress", value=0)
        dataStorage.setGuildData(ctx.guild, "setupMember", value=ctx.author.id)
        dataStorage.setGuildData(ctx.guild, "setupChannel", value=ctx.channel.id)
        embed = discord.Embed(title=":question: Choose your setup type", color=0x00b8ff)
        embed.add_field(name=":one: Simple", value="Automatically configures most settings.", inline=False)
        embed.add_field(name=":two: Advanced",
                        value="You can choose if you want to use a join command channel and tutorial channel")
        msg = await ctx.send(embed=embed)
        await msg.add_reaction("1️⃣")
        await msg.add_reaction("2️⃣")
        dataStorage.setGuildData(ctx.guild, "setupMessage", value=msg.id)

    else:
        if gamesRunning:
            await ctx.send(embed=discord.Embed(title=":x: All games must be ended before running the setup again!",
                                               description="Use !list to see all running games.\nTo stop all games, use !endAllGames or !cleanup.",
                                               color=0xff0000))
        else:
            dataStorage.setGuildData(ctx.guild, "setupStarted", value=False)
            dataStorage.setGuildData(ctx.guild, "setupFinished", value=False)
            await initializeSetup(ctx, False)


async def finishSetup(guild, setupType):
    dataStorage.setGuildData(guild, "setupFinished", value=True)
    dataStorage.setGuildData(guild, "setupStarted", value=False)
    dataStorage.setGuildData(guild, "awaitingSetupMessage", value=False)
    if setupType == 1:
        dataStorage.setGuildData(guild, "useTutorialChannels", value=True)
        dataStorage.setGuildData(guild, "useJoinChannel", value=True)
        dataStorage.setGuildData(guild, "useCategory", value=True)
    elif setupType == 2:
        if dataStorage.getGuildData(guild, "useTutorialChannels") or dataStorage.getGuildData(guild, "useJoinChannel"):
            dataStorage.setGuildData(guild, "useCategory", value=True)
        else:
            dataStorage.setGuildData(guild, "useCategory", value=False)

    if dataStorage.getGuildData(guild, "useCategory"):
        category = await guild.create_category("Murder Mystery")
        dataStorage.setGuildData(guild, "category", value=category.id)

    if dataStorage.getGuildData(guild, "useJoinChannel"):
        joinChannel = await category.create_text_channel("join")
        dataStorage.setGuildData(guild, "joinChannel", value=joinChannel.id)
        if dataStorage.getGuildData(guild, "useTutorialChannels"):
            await joinChannel.send(embed=discord.Embed(title='Type "!join" to join a game',
                                                       description=f"It is recommended to read the tutorial before playing",
                                                       color=0x00b8ff))
        else:
            await joinChannel.send(embed=discord.Embed(title='Type "!join" to join a game', color=0x00b8ff))

    if dataStorage.getGuildData(guild, "useTutorialChannels"):
        gameTutorialChannel = await category.create_text_channel("game")
        await gameTutorialChannel.set_permissions(guild.default_role, send_messages=False)
        await gameTutorialChannel.set_permissions(guild.me, send_messages=True)
        dataStorage.setGuildData(guild, "gameTutorialChannel", value=gameTutorialChannel.id)
        rolesTutorialChannel = await category.create_text_channel("roles")
        await rolesTutorialChannel.set_permissions(guild.default_role, send_messages=False)
        await rolesTutorialChannel.set_permissions(guild.me, send_messages=True)
        dataStorage.setGuildData(guild, "rolesTutorialChannel", value=rolesTutorialChannel.id)
        itemsTutorialChannel = await category.create_text_channel("items")
        await itemsTutorialChannel.set_permissions(guild.default_role, send_messages=False)
        await itemsTutorialChannel.set_permissions(guild.me, send_messages=True)
        dataStorage.setGuildData(guild, "itemsTutorialChannel", value=itemsTutorialChannel.id)
        commandsTutorialChannel = await category.create_text_channel("commands")
        await commandsTutorialChannel.set_permissions(guild.default_role, send_messages=False)
        await commandsTutorialChannel.set_permissions(guild.me, send_messages=True)
        dataStorage.setGuildData(guild, "commandsTutorialChannel", value=commandsTutorialChannel.id)

        embeds = tutorial.getTutorialEmbeds(guild)
        for v in embeds["game"]:
            await gameTutorialChannel.send(embed=v)
        for v in embeds["roles"]:
            await rolesTutorialChannel.send(embed=v)
        for v in embeds["items"]:
            await itemsTutorialChannel.send(embed=v)
        for v in embeds["commands"]:
            await commandsTutorialChannel.send(embed=v)

    if dataStorage.getGuildData(guild, "useSummaryEmbeds", default=False) and dataStorage.getGuildData(guild,
                                                                                                       "summaryChannel") is None:
        summaryChannel = await category.create_text_channel("game summaries")
        await summaryChannel.set_permissions(guild.default_role, send_messages=False)
        await summaryChannel.set_permissions(guild.me, send_messages=True)
        dataStorage.setGuildData(guild, "summaryChannel", value=summaryChannel.id)
    dataStorage.setGuildData(guild, "minPlayers", value=4)
    dataStorage.setGuildData(guild, "maxPlayers", value=30)
    dataStorage.setGuildData(guild, "preGameTimer", value=120)
    dataStorage.setGuildData(guild, "votingTime", value=120)
    dataStorage.setGuildData(guild, "nightTimeTimer", value=60)
    dataStorage.setGuildData(guild, "prefix", value="!")
