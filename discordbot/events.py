"""Guild-agnostic events: message routing, guild join welcome, AFK kick."""
import discord

import dataStorage
import setup
from core.game_state import allPlayers
from .client import client
from core.utils import getPlayer


@client.event
async def on_message(message):
    if isinstance(message.channel, discord.DMChannel):
        for players in allPlayers.values():
            player = next(
                (
                    candidate
                    for candidate in players
                    if getattr(candidate.member, "id", None) == message.author.id
                ),
                None,
            )
            if player is not None and player.inGame:
                if not message.content.startswith("!"):
                    if getattr(player, "currentSatellite", None) is not None:
                        await player.currentSatellite.processMessage(message)
                        return
                    if getattr(player, "currentDagger", None) is not None:
                        await player.currentDagger.processMessage(message)
                        return
                    if player.game.nightTime:
                        await player.role.processRoleChannelCommand(message)
                await client.process_commands(message)
                return
        await client.process_commands(message)
        return

    if not isinstance(message.channel, discord.channel.DMChannel):
        if not message.guild.id in allPlayers:
            allPlayers[message.guild.id] = []
        player = getPlayer(message.author, message.guild)
        if player is not None:
            if player.inGame == True:
                if hasattr(player, "roleChannel"):
                    if message.channel == player.roleChannel:
                        await player.role.processRoleChannelCommand(message)

        if dataStorage.getGuildData(message.guild, "useJoinChannel"):
            if message.channel == message.guild.get_channel(dataStorage.getGuildData(message.guild, "joinChannel")):
                prefix = dataStorage.getGuildData(message.guild, "prefix", default="!")
                allowed_starts = (f"{prefix}join", f"{prefix}create")
                if not any(message.content.strip().lower().startswith(s) for s in allowed_starts):
                    if message.author != client.user:
                        try:
                            await message.delete()
                        except Exception:
                            pass

        if message.author.id == dataStorage.getGuildData(message.guild, "setupMember"):
            if message.channel.id == dataStorage.getGuildData(message.guild, "setupChannel"):
                if dataStorage.getGuildData(message.guild, "awaitingSetupMessage", default=False):
                    await setup.processSetupMessage(message)

        if not dataStorage.getGuildData(message.guild, "setupFinished", default=False):
            if message.content.lower().strip().startswith("!"):
                if message.content.lower().strip() != "!setup":
                    embed = discord.Embed(
                        title=":x: Please run !setup before using any commands!",
                        description=(
                            "An admin has to use !setup before this bot "
                            "can execute any commands."
                        ),
                        color=0xff0000
                    )
                    await message.channel.send(embed=embed)
                else:
                    await client.process_commands(message)
        else:
            await client.process_commands(message)

@client.event
async def on_guild_join(guild):
    channels = guild.channels
    selected = None
    if guild.system_channel is not None:
        if guild.system_channel.permissions_for(guild.get_member(client.user.id)).send_messages:
            selected = guild.system_channel
    if selected is None:
        if guild.public_updates_channel is not None:
            if guild.public_updates_channel.permissions_for(guild.get_member(client.user.id)).send_messages:
                selected = guild.public_updates_channel
    if selected is None:
        for v in channels:
            if isinstance(v, discord.TextChannel):
                if "general" in v.name or "chat" in v.name:
                    if v.permissions_for(guild.get_member(client.user.id)).send_messages:
                        selected = v
    if selected is None:
        for v in channels:
            if isinstance(v, discord.TextChannel):
                if v.permissions_for(guild.get_member(client.user.id)).send_messages:
                    selected = v
    if selected is not None:
        embed = discord.Embed(
            title="Thanks for inviting Murder Mystery!",
            description=(
                "This bot brings a full on murder mystery game "
                "inside of discord!"
            ),
            color=0x00b8ff
        )
        embed.add_field(
            name='Before you can use this bot, type "!setup"',
            value=(
                "A few things need to be setup before you can use "
                'this bot. Please use "!setup" to set up the bot.'
            ),
            inline=False
        )
        thumb_url = (
            "https://cdn.discordapp.com/attachments/"
            "554234775590666251/819314838949462017/waving-hand_1f44b.png"
        )
        embed.set_thumbnail(url=thumb_url)
        try:
            await selected.send(embed=embed)
        except discord.HTTPException:
            pass
    print(f"Joined new guild with ID {guild.id} and {guild.member_count} members")

@client.event
async def on_member_update(before, after):
    if after.status == discord.Status.offline:
        # Respect guild setting; default now allows offline players
        kick_offline = dataStorage.getGuildData(
            after.guild, "kickOfflinePlayers", default=False
        )
        if kick_offline:
            player = getPlayer(after, after.guild)
            if player is not None:
                if player.inGame:
                    name = player.member.display_name
                    if not player.game.started:
                        embed = discord.Embed(
                            title=(
                                f":heavy_minus_sign: {name} got kicked "
                                "out of the game because they went offline"
                            ),
                            color=0xff0000
                        )
                        await player.game.mainChannel.send(embed=embed)
                    else:
                        if not player.game.night:
                            embed = discord.Embed(
                                title=(
                                    f":heavy_minus_sign: {name} got kicked "
                                    "out because they went offline"
                                ),
                                description=f"{name}{player.role.deadString}",
                                color=0xff0000
                            )
                            await player.game.mainChannel.send(embed=embed)
                        else:
                            embed = discord.Embed(
                                title=(
                                    f":heavy_minus_sign: {name} got kicked "
                                    "out because they went offline"
                                ),
                                description=f"{name}{player.role.deadString}",
                                color=0xff0000
                            )
                            await player.game.sendToAllNightChannels(
                                embed=embed
                            )
                    try:
                        embed = discord.Embed(
                            title=(
                                "You got kicked out of the game because "
                                "you went offline!"
                            ),
                            description=(
                                "When you change your status to offline, "
                                "you automatically get kicked so the game "
                                "doesn't get filled with AFK people."
                            ),
                            color=0xff0000
                        )
                        await after.send(embed=embed)
                    except discord.HTTPException:
                        pass
                    await player.game.removePlayer(player)


