"""Player commands for Murder Mystery Bot."""
import discord
from discord.ext import commands

import dataStorage
import permissions
import items
from core.game_state import currentGames, allPlayers
from core.utils import getPlayer


class PlayerCommands(commands.Cog):
    """Commands for in-game players."""
    
    def __init__(self, client):
        self.client = client

    @commands.command()
    async def whisper(self, ctx, member: discord.Member):
        """Start a private whisper channel with another player."""
        player = getPlayer(ctx.author, ctx.message.guild)
        whisperPlayer = getPlayer(member, ctx.message.guild)
        
        if player is None or not player.inGame:
            await ctx.send(":x: You're not in a game!")
            return
            
        if whisperPlayer is None or not whisperPlayer.inGame:
            await ctx.send(":x: That player is not in game!")
            return
            
        if whisperPlayer not in player.game.players:
            await ctx.send(":x: That player is not in the same game as you!")
            return
            
        if ctx.channel != player.game.mainChannel:
            await ctx.send(":x: You can't use that here!")
            return
            
        if whisperPlayer in player.whisperingTo:
            await ctx.send(":x: You're already whispering to that player!")
            return
            
        # Create whisper channel
        name = f"Whisper between {player.member.display_name} and {whisperPlayer.member.display_name}"
        if len(name) >= 100:
            name = "Whisper"
            
        channel = await player.game.category.create_text_channel(name)
        player.game.channels.append(channel)
        player.game.channelsRemoveByNight.append(channel.id)
        player.whisperingTo.append(whisperPlayer)
        whisperPlayer.whisperingTo.append(player)
        
        await channel.set_permissions(player.game.role, read_messages=False, send_messages=False)
        await channel.set_permissions(player.member, read_messages=True, send_messages=True)
        await channel.set_permissions(whisperPlayer.member, read_messages=True, send_messages=True)

        await ctx.send(embed=discord.Embed(
            title=f"{player.member.display_name} and {whisperPlayer.member.display_name} are now whispering",
            description="A private channel has been created. It will be deleted at night.",
            color=0x0088ff
        ))

    @commands.command()
    async def vote(self, ctx, votedMember: discord.Member):
        """Vote to execute someone during voting time."""
        if ctx.guild.id not in allPlayers:
            currentGames[ctx.guild.id] = allPlayers

        player = getPlayer(ctx.author, ctx.message.guild)
        votedPlayer = getPlayer(votedMember, ctx.message.guild)
        
        if player is None or not player.inGame:
            await ctx.send(":x: You can only use this command while you're in game!")
            return
            
        if votedPlayer is None or not votedPlayer.inGame:
            await ctx.send(":x: That player is not in game!")
            return
            
        if votedPlayer.game != player.game:
            await ctx.send(":x: That player is not in the same game as you!")
            return
            
        if ctx.message.channel != player.game.mainChannel:
            await ctx.send(":x: You can't use that here!")
            return
            
        if not player.game.voteTime:
            await ctx.send(":x: You can't vote yet!")
            return
            
        if votedPlayer == player:
            await ctx.send(":x: You can't vote on yourself!")
            return
            
        if not player.voted:
            votedPlayer.votes += 1
            player.voted = True
            player.votedOn = votedPlayer
            await ctx.send(
                f"{ctx.author.mention} voted to execute {votedPlayer.member.mention}! "
                f"They're now at **{votedPlayer.votes}** votes."
            )
            player.game.playersThatVoted.append(player)
            player.game.extendVotingTime = True
        else:
            if player.votedOn != votedPlayer:
                player.votedOn.votes -= 1
                votedPlayer.votes += 1
                await ctx.send(
                    f"{ctx.author.mention} changed their vote from "
                    f"{player.votedOn.member.mention} to {votedPlayer.member.mention}! "
                    f"They're now at **{votedPlayer.votes}** votes."
                )
                player.votedOn = votedPlayer
                player.game.extendVotingTime = True
            else:
                await ctx.send(":x: You already voted on that player!")

    @commands.command()
    async def use(self, ctx, itemName="", *, arg=None):
        """Use an item from your inventory."""
        if itemName == "":
            await ctx.send("Usage: !use [item] [@username/text]")
            return
            
        player = getPlayer(ctx.author, ctx.message.guild)
        if player is None:
            await ctx.send(":x: You can only do this if you're in a game!")
            return
            
        for item in player.inventory:
            if item.id == itemName.lower():
                if arg is not None and item.needArg:
                    if item.needPlayerArg:
                        try:
                            converter = commands.MemberConverter()
                            memberArg = await converter.convert(ctx, arg)
                            playerArg = getPlayer(memberArg, ctx.message.guild)
                        except commands.MemberNotFound:
                            await ctx.message.channel.send(":x: I can't find that player!")
                            return
                        except Exception:
                            await ctx.message.channel.send(":x: An unknown error occurred!")
                            raise
                        else:
                            await item.use(ctx, playerArg)
                    else:
                        await item.use(ctx, arg)
                elif not item.needArg:
                    await item.use(ctx, arg)
                else:
                    await ctx.send(f"Usage: {item.usage}")
                return
                
        # Item not found
        if hasattr(player, "inventoryChannel"):
            await ctx.send(embed=discord.Embed(
                title=":x: Couldn't find that item in your inventory!",
                description=f"View your inventory: {player.inventoryChannel.mention}"
            ))
        else:
            await ctx.send(embed=discord.Embed(
                title=":x: Couldn't find that item in your inventory!"
            ))

    @commands.command()
    async def shop(self, ctx):
        """View the shop during night time."""
        player = getPlayer(ctx.author, ctx.message.guild)
        
        if player is None or not player.inGame:
            await ctx.send(":x: You can only use this command while you're in a game!")
            return
            
        if not player.game.nightTime:
            await ctx.send(":x: You can only use this command during :full_moon: night time!")
            return
            
        if ctx.message.channel != player.nightChannel:
            await ctx.send(f":x: You can only use this command in {player.nightChannel.mention}")
            return
            
        embed = discord.Embed(
            title=f"Shop | :coin: {player.gold}",
            description="To buy something, use !buy [item].",
            color=0x00b8ff
        )
        
        broadcasterInGame = any(p.role.name == "broadcaster" for p in player.game.players)
        
        for itemClass in items.getItems(broadcasterInGame=broadcasterInGame, role=player.role.name):
            item = itemClass()
            embed.add_field(
                name=f"{item.name}",
                value=f"{item.description}\nCost: :coin: {item.cost}\nTo buy, type !buy {item.id}",
                inline=False
            )
        await ctx.send(embed=embed)

    @commands.command(aliases=["money", "gold", "bal"])
    async def balance(self, ctx):
        """Check your gold balance."""
        player = getPlayer(ctx.author, ctx.message.guild)
        
        if player is None or not player.inGame:
            await ctx.send(":x: You can only use this command while you're in a game!")
            return
            
        await ctx.send(f":coin: You have {player.gold} gold.")

    @commands.command()
    async def buy(self, ctx, itemId):
        """Buy an item from the shop."""
        player = getPlayer(ctx.author, ctx.message.guild)
        
        if player is None or not player.inGame:
            await ctx.send(":x: You can only use this command while you're in a game!")
            return
            
        if not player.game.nightTime:
            await ctx.send(":x: You can only use this command during :full_moon: night time!")
            return
            
        if ctx.message.channel != player.nightChannel:
            await ctx.send(f":x: You can only use this command in {player.nightChannel.mention}")
            return
            
        broadcasterInGame = any(p.role.name == "broadcaster" for p in player.game.players)
        
        for itemClass in items.getItems(broadcasterInGame=broadcasterInGame, role=player.role.name):
            if itemClass().id == itemId.lower():
                await items.buy(itemClass(), player, ctx.message.channel)
                return
                
        await ctx.send(embed=discord.Embed(
            title=":x: That's not a valid item!",
            description="Make sure you spelled it correctly!",
            color=0x0000f
        ))

    @commands.command()
    async def leave(self, ctx):
        """Leave the current game."""
        player = getPlayer(ctx.author, ctx.message.guild)
        
        # If player not found via allPlayers, try locating them within currentGames
        if player is None:
            if ctx.guild.id in currentGames:
                for g in currentGames[ctx.guild.id]:
                    for p in g.players:
                        if p.member.id == ctx.author.id:
                            player = p
                            break
                    if player is not None:
                        break
                        
        if player is None or not player.inGame:
            await ctx.send(":x: You can only use this command while you're in a game!")
            return
            
        if not player.game.started:
            await player.game.mainChannel.send(embed=discord.Embed(
                title=f":heavy_minus_sign: {player.member.display_name} left the game",
                color=0xff0000
            ))
        else:
            if not player.game.nightTime:
                await player.game.mainChannel.send(embed=discord.Embed(
                    title=f":heavy_minus_sign: {player.member.display_name} left the game",
                    description=f"{player.member.display_name}{player.role.deadString}",
                    color=0xff0000
                ))
            else:
                await player.game.sendToAllNightChannels(embed=discord.Embed(
                    title=f":heavy_minus_sign: {player.member.display_name} left the game",
                    description=f"{player.member.display_name}{player.role.deadString}",
                    color=0xff0000
                ))
        await player.game.removePlayer(player)

    @commands.command(aliases=["ownerstart", "fs"])
    async def forceStart(self, ctx):
        """Allow the lobby owner (or admins) to force start their current lobby."""
        p = getPlayer(ctx.author, ctx.guild)
        if p is None or not p.inGame:
            await ctx.send(":x: You need to be in a lobby to force start it.")
            return
            
        g = p.game
        is_owner = getattr(g, "owner_id", None) == ctx.author.id
        has_admin = await permissions.hasPermission(ctx, "admin.game.startGame")
        
        if not (is_owner or has_admin):
            await ctx.send(":closed_lock_with_key: Only the lobby owner can force start this game.")
            return
            
        if g.started:
            await ctx.send(":x: The game has already started.")
            return
            
        g.startNow = True
        await ctx.send(":white_check_mark: The game will start immediately!")


async def setup(client):
    """Setup function for cog."""
    await client.add_cog(PlayerCommands(client))
