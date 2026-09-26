"""Misc prefix commands: invite/dc/stats/objectives/gold/setup with no cog yet."""
import datetime

import discord

import dataStorage
from dataStorage import getPlayerData, setPlayerData, deletePlayerData
import objectives
import permissions
import setup
from core.config import mainServerInvite
from core.game_state import currentGames
from .client import client
from .helpers import getPlayer


@client.command(aliases=["discord", "bug", "reportBug", "report", "suggest", "suggestion", "suggestions"])
async def dc(ctx):
    embed = discord.Embed(
        title="Join the Murder Mystery discord server",
        description=(
            "Join the Murder Mystery discord server to suggest features, "
            "report bugs, or play the game with people!"
        ),
        color=0x00b8ff
    )
    thumb_url = (
        "https://cdn.discordapp.com/attachments/"
        "554234775590666251/863863056516513792/dagger_1f5e1-fe0f.png"
    )
    embed.set_thumbnail(url=thumb_url)
    await ctx.send(embed=embed)
    await ctx.send(mainServerInvite)


@client.command()
async def purge(ctx, amount):
    if await permissions.hasPermission(ctx, "admin.purge"):
        await ctx.message.channel.purge(limit=int(amount))


@client.command()
async def giveGold(ctx, member: discord.Member, amount):
    if await permissions.hasPermission(ctx, "admin.game.giveGold"):
        player = getPlayer(member, ctx.message.guild)
        if player is not None:
            if player.inGame:
                intAmount = int(amount)
                player.gold += intAmount
                await ctx.send(f"Gave :coin: {amount} gold to {member.mention}")
            else:
                ctx.send("That player is not in game!")
        else:
            ctx.send("That member is not in game!")


@client.command()
async def skipObjectiveTimer(ctx, member: discord.Member):
    if await permissions.hasPermission(ctx, "debug.objectives.skipObjectiveTimer"):
        setPlayerData(member, "nextObjectiveReceivable", value=datetime.datetime.utcnow().isoformat())
        await ctx.send(f"Skipped objective timer for **{member.display_name}**")


@client.command()
async def resetObjectiveData(ctx, member: discord.Member):
    if await permissions.hasPermission(ctx, "debug.objectives.resetObjectiveData"):
        deletePlayerData(member, "completedObjectives")
        deletePlayerData(member, "objective")
        deletePlayerData(member, "objectiveProgress")
        deletePlayerData(member, "nextObjectiveReceivable")
        deletePlayerData(member, "possibleObjectiveDifficulty")
        await ctx.send("Done!")


@client.command()
async def completeCurrentObjective(ctx, member: discord.Member):
    if await permissions.hasPermission(ctx, "debug.objectives.completeCurrentObjective"):
        await objectives.checkForCompleteObjectives(member, forceComplete=True)
        await ctx.send(f"**{member.mention}**'s objective should be completed now if they had one")


@client.command()
async def giveObjective(ctx, member: discord.Member, index):
    if await permissions.hasPermission(ctx, "debug.objectives.giveObjective"):
        index = int(index)
        if objectives.giveObjective(member, index=index):
            await ctx.send(f"Objective with index **{index}** has been given to **{member.display_name}**")
        else:
            await ctx.send(f":x: There is no objective with index **{index}**!")


@client.command()
async def addObjectiveProgress(ctx, member, key, value=1):
    perm = "debug.levels.addObjectiveProgress"
    if await permissions.hasPermission(ctx, perm):
        if key in objectives.objectiveTasksMeanings:
            objectives.addObjectiveProgress(member, key, value)
        else:
            tasks = ""
            for v in objectives.objectiveTasksMeanings:
                tasks += f"\n{v}"
            await ctx.channel.send(embed=discord.Embed(
                title=":x: That's not a valid objective task",
                description=f"Objective task options:{tasks}",
                color=0xff0000
            ))


@client.command(aliases=["objectives", "quest", "quests"])
async def objective(ctx):
    if await permissions.hasPermission(ctx, "member.levels.objective"):
        if getPlayer(ctx.author, ctx.message.guild) is None:
            await objectives.objectivesCommand(ctx)
        else:
            await ctx.send(embed=discord.Embed(
                title=(
                    ":x: You can't view your objective progress when "
                    "you're in a game!"
                ),
                description=(
                    "Because some objectives, like \"vote on the murderer\", "
                    "can reveal someone's role if the progress increases, "
                    "you can only check your objective progress outside of "
                    "games."
                ),
                color=0xff0000
            ))


@client.command(aliases=["xp", "levels"])
async def level(ctx, member: discord.Member = None):
    if await permissions.hasPermission(ctx, "member.levels.level"):
        if member is not None:
            player_level = getPlayerData(member, "level", default=1)
            current_xp = getPlayerData(member, "xp", default=0)
            next_level_req = objectives.getNextLevelRequirement(player_level)
            xp_needed = next_level_req - current_xp
            embed = discord.Embed(
                title=f"{member.display_name} is level {player_level}",
                description=(
                    f"{objectives.getXpProgressBar(member)}\n"
                    f"{xp_needed} xp required for next level"
                ),
                color=0x00ff00
            )
            embed.set_thumbnail(url=member.avatar_url)
            await ctx.send(embed=embed)
            await objectives.addXP(member, 0)
        else:
            author_level = getPlayerData(ctx.author, "level", default=1)
            author_xp = getPlayerData(ctx.author, "xp", default=0)
            next_req = objectives.getNextLevelRequirement(author_level)
            xp_needed = next_req - author_xp
            embed = discord.Embed(
                title=f"You are level {author_level}",
                description=(
                    f"{objectives.getXpProgressBar(ctx.author)}\n"
                    f"{xp_needed} xp required for next level"
                ),
                color=0x00ff00
            )
            embed.set_thumbnail(url=ctx.author.avatar_url)
            await ctx.send(embed=embed)
            await objectives.addXP(ctx.author, 0)


# I used this when adding !stats to get the stats in the database from the old games. It's commented out but not deleted in case I need it later
"""
@client.command()
async def get_data_from_result_embeds(ctx):
    if ctx.message.author.guild_permissions.administrator:
        messages = [809478299256225792, 809530109534404668, 809533084445179904, 809539497988849744, 809543556796645426,
                    809546628947640350, 809548300645826581, 809551953117708338, 809615182103183380, 809791651441803334,
                    809830171242659890, 809841988135813180, 810251596751306783, 810253910945693737, 810262637174194237,
                    810558325984591892, 810589178990559323, 810591099877195866, 810603500227788860, 810605466773094430,
                    810607671954374687, 810631844185374791, 810728993253752853, 810730945212448828, 810732625362812938,
                    810914246846054490, 810917125886967849, 810919252314816522, 810971851454808095, 810974803661291541,
                    810977617694949417, 810983103098519573, 811020089721094185, 811023344153133096, 811345844322304010,
                    811350417534484480, 811386038881878048, 811724073071149067, 811726959612264509, 811729253719605279,
                    811735553171128370, 811736560898408449, 812035114153803777, 812039264162283540, 812041492478296074,
                    812082187930173441, 812084493568442418, 812095188033339442, 814623570323701830, 814626359556833300,
                    814629805986545675, 814633291163500584, 814635493995970630, 814639817249783869, 814642798564999170,
                    814645835560255488, 814648289193754684, 814650033986732052, 814652772799873055, 814657316418486322,
                    814662026516627507, 814665285817991241, 814669355450761216, 814675242618191934, 814677047087202305,
                    814680377490538567, 814682540145246210, 814685364630847488, 814687548508733460, 814693578256416788,
                    814698285184450610, 814700200492138516, 814706542053556286, 814709206451748874, 814876968666529863,
                    814879345688051743, 814883856985358396, 814886889819209778, 814889092810276864, 814890929864572948,
                    814895128199036950, 814897292338397244, 814904501264711720, 814908490358849576, 814910732281315358,
                    814923724465373204, 814928511961137212, 814930851539189791, 814933998835859566, 814935814609436712,
                    814939284108607488, 814942406168281109, 815241187111338044, 816208691538821120, 816379544965087302,
                    817151667517784125, 818241017810911252]
        channel = client.get_channel(803169209474482190)
        await ctx.send("doing the thing, please wait")
        for msgid in messages:
            msg = await channel.fetch_message(msgid)
            embed = msg.embeds[0]
            victory = True
            if embed.title == "Villagers won!":
                victory = True
            elif embed.title == "Murderer won!":
                victory = False
            else:
                print("Invalid title!")

            for field in embed.fields:
                if field.name != "Game summary":
                    converter = commands.MemberConverter()
                    try:
                        member = await converter.convert(ctx, field.value)
                    except:
                        print("Invalid player!")
                    setPlayerData(member, "gamesPlayed", increase=1)
                    if victory:
                        if field.name != ":dagger: murderer":
                            setPlayerData(member, "villagerWins", increase=1)
                    else:
                        if field.name == ":dagger: murderer":
                            setPlayerData(member, "murdererWins", increase=1)
        await ctx.send("Done!")

    else:
        await ctx.send(embed=noPermissionEmbed)
"""


@client.command()
async def get_player_data(ctx, member: discord.Member, key):
    perm = "debug.dataStorage.get_player_data"
    if await permissions.hasPermission(ctx, perm):
        value = getPlayerData(member, key)
        await ctx.send(f"{value}")





@client.command()
async def stats(ctx, memberArg: discord.Member = None):
    if await permissions.hasPermission(ctx, "member.levels.stats"):
        member = None
        if memberArg is None:
            member = ctx.author
        else:
            member = memberArg

        games_played = getPlayerData(member, "gamesPlayed", default=0)
        villager_wins = getPlayerData(member, "villagerWins", default=0)
        murderer_wins = getPlayerData(member, "murdererWins", default=0)
        fool_wins = getPlayerData(member, "foolWins", default=0)
        werewolf_wins = getPlayerData(member, "werewolfWins", default=0)
        stats_desc = (
            f":video_game: Games played: {games_played}\n\n"
            f":adult: Villager wins: {villager_wins}\n"
            f":dagger: Murderer wins: {murderer_wins}\n"
            f":clown: Fool wins: {fool_wins}\n"
            f":wolf: Werewolf wins: {werewolf_wins}\n"
        )
        embed = discord.Embed(
            title=f"Stats for {member.display_name}",
            description=stats_desc,
            color=0x00ff00
        )
        embed.set_thumbnail(url=member.avatar_url)
        player_level = dataStorage.getPlayerData(
            member, "level", default=1
        )
        current_xp = getPlayerData(member, "xp", default=0)
        next_level_req = objectives.getNextLevelRequirement(
            getPlayerData(member, "level", default=1)
        )
        xp_needed = next_level_req - current_xp
        embed.add_field(
            name=f'Level {player_level}',
            value=(
                f'{objectives.getXpProgressBar(member)}\n'
                f'{xp_needed} xp required for next level'
            ),
            inline=True
        )
        await ctx.send(embed=embed)
        await objectives.addXP(member, 0)


@client.command(aliases=["setup"])
async def startSetup(ctx):
    if await permissions.hasPermission(ctx, "admin.setup"):
        gamesRunning = False
        if ctx.guild.id not in currentGames:
            currentGames[ctx.guild.id] = []
        if len(currentGames[ctx.guild.id]) > 0:
            gamesRunning = True
        await setup.initializeSetup(ctx, gamesRunning)


@client.command()
async def invite(ctx):
    invite_url = (
        "https://discord.com/api/oauth2/authorize?"
        "client_id=590980247801954304&permissions=2434133072&scope=bot"
    )
    await ctx.send(embed=discord.Embed(
        title="Invite Murder Mystery to your own server!",
        description=f"Click this link to invite this bot to your server: {invite_url}",
        color=0x00b8ff
    ))
@client.command()
async def error(ctx):
    int("e")


