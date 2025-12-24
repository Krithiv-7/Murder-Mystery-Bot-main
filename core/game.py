"""Game class for Murder Mystery bot."""
import asyncio
import random
import discord

import dataStorage
import items
import objectives
from roles import role

from .game_state import (
    currentGames, availableGames, allPlayers,
    mainGuild, mainGameRolePosition, notificationChannel,
    newGamesRole, gamesStartingRole, joiningChannel
)
from .config import requiredRoles, roles, mainServerInvite
from .player import Player


def randomizeList(lst):
    """Shuffle a list and return it."""
    result = lst.copy()
    random.shuffle(result)
    return result


def getKeys(d):
    """Get list of keys from a dictionary."""
    result = []
    for v in d:
        result.append(v)
    return result


class Game:
    """Represents a Murder Mystery game instance."""
    
    def __init__(self, guild, debug):
        self.guild = guild
        self.debug = debug
        self.owner_id = None

        # channels & core game info
        self.channels = []
        self.channelsRemoveByMorning = []
        self.channelsRemoveByNight = []
        self.players = []
        self.allPlayers = []
        self.willDieNextMorning = []
        self.started = False
        self.day = 0
        self.nightTime = False
        self.countDown = False
        self.spectators = []
        self.playersThatVoted = []
        self.victory = None
        
        # gold
        self.goldPerDay = 1
        self.fivePlayersLeftGoldIncrease = False
        
        # skipping
        self.startNow = False
        self.skipVotingTime = False
        self.skipNight = False
        
        # voting
        self.extendVotingTime = False
        self.timesVotingTimeExtended = 0
        self.voteTime = False
        
        # fool
        self.foolKilled = False
        self.foolWin = False
        
        # weather
        self.weatherIntensity = 1
        self.moon = 3

    async def createGame(self, client):
        """Create game channels and roles."""
        # Determine role position
        if self.guild != mainGuild:
            gameRolePosition = self.guild.me.top_role.position - 1
        else:
            gameRolePosition = mainGameRolePosition
            
        # Create game role
        self.role = await self.guild.create_role()
        await self.role.edit(
            name="Waiting for game to start",
            permissions=discord.Permissions(
                read_message_history=True, read_messages=True
            ),
            hoist=True
        )
        try:
            await self.role.edit(position=gameRolePosition)
        except discord.HTTPException:
            pass

        # Create spectator role
        self.spectatorRole = await self.guild.create_role()
        if self.guild != mainGuild:
            gameRolePosition = self.guild.me.top_role.position - 1
        else:
            gameRolePosition = mainGameRolePosition - 1
        await self.spectatorRole.edit(
            name="Spectator",
            permissions=discord.Permissions(
                read_message_history=True, read_messages=True
            ),
            hoist=True
        )
        try:
            await self.spectatorRole.edit(position=gameRolePosition)
        except discord.HTTPException:
            pass
            
        # Set join channel permissions
        if dataStorage.getGuildData(self.guild, "useJoinChannel"):
            join_ch = self.guild.get_channel(
                dataStorage.getGuildData(self.guild, "joinChannel")
            )
            if join_ch is not None:
                await join_ch.set_permissions(self.role, read_messages=False)

        # Create category
        self.category = await self.guild.create_category("game")
        try:
            await self.category.edit(position=0)
        except Exception:
            pass
        await self.category.set_permissions(
            self.guild.me, send_messages=True, read_messages=True
        )
        await self.category.set_permissions(
            self.role, read_messages=True, send_messages=True
        )
        await self.category.set_permissions(
            self.guild.default_role, read_messages=False
        )
        await self.category.set_permissions(
            self.spectatorRole, read_messages=False, send_messages=False
        )
        try:
            await asyncio.sleep(0.5)
            await self.category.edit(position=0)
        except Exception:
            pass

        # Create main channel
        self.mainChannel = await self.category.create_text_channel("Game")
        await self.mainChannel.set_permissions(
            self.spectatorRole, read_messages=True, send_messages=False
        )
        self.channels.append(self.mainChannel)

        # Create voice channel if enabled
        self.voiceChannel = None
        if dataStorage.getGuildData(self.guild, "gameVoiceChannel", default=False):
            self.voiceChannel = await self.category.create_voice_channel("Game")
            await self.voiceChannel.set_permissions(
                self.guild.default_role, view_channel=False
            )
            await self.voiceChannel.set_permissions(self.role, view_channel=True)
            self.channels.append(self.voiceChannel)

        # Register game
        if self.guild.id not in currentGames:
            currentGames[self.guild.id] = []
        currentGames[self.guild.id].append(self)
        
        if self.guild.id not in availableGames:
            availableGames[self.guild.id] = []
        availableGames[self.guild.id].append(self)

        # Notify main guild
        if self.guild == mainGuild and not self.debug:
            if notificationChannel and newGamesRole and joiningChannel:
                await notificationChannel.send(
                    f"{newGamesRole.mention}",
                    embed=discord.Embed(
                        title="A new game has just been created!",
                        description=(
                            f"Someone just started a new game. "
                            f"Join using !join in {joiningChannel.mention}"
                        ),
                        color=0x00b8ff
                    )
                )
        print(f"New game in guild {self.guild.id} ({self.guild.member_count} members)")

    async def addPlayer(self, member):
        """Add a player to the game."""
        newPlayer = Player(member, self)
        self.players.append(newPlayer)
        
        if self.guild.id not in allPlayers:
            allPlayers[self.guild.id] = []
        allPlayers[self.guild.id].append(newPlayer)
        
        await member.add_roles(self.role)

        min_players = dataStorage.getGuildData(
            self.guild, "minPlayers", default=4
        )
        needed = min_players - len(self.players)
        
        if needed <= 0:
            embed = discord.Embed(
                title=f":heavy_plus_sign: **{newPlayer.member.display_name} joined!**",
                description="The game will start soon!",
                color=0x0088ff
            )
            await self.mainChannel.send(
                f"{newPlayer.member.mention}", embed=embed
            )
            await self.startCountdown()
        else:
            plural = "" if needed == 1 else "s"
            embed = discord.Embed(
                title=f":heavy_plus_sign: **{newPlayer.member.display_name} joined!**",
                description=f"{needed} more player{plural} required to start.",
                color=0x0088ff
            )
            await self.mainChannel.send(
                f"{newPlayer.member.mention}", embed=embed
            )

    async def addSpectator(self, member):
        """Add a spectator to the game."""
        self.spectators.append(member)
        await member.add_roles(self.spectatorRole)
        await self.mainChannel.send(
            f"{member.mention}",
            embed=discord.Embed(
                title=f"{member.display_name} is now spectating",
                description="They can view this channel but not talk.",
                color=0x0088ff
            )
        )

    async def removeSpectator(self, member):
        """Remove a spectator from the game."""
        if member in self.spectators:
            self.spectators.remove(member)
            await member.remove_roles(self.spectatorRole)

    async def removePlayer(self, player, **kwargs):
        """Remove a player from the game."""
        player.inGame = False
        allPlayers[self.guild.id].remove(player)
        self.players.remove(player)

        # Clean up player channels
        for attr in ["nightChannel", "roleChannel", "broadcastChannel"]:
            if hasattr(player, attr):
                ch = getattr(player, attr)
                if ch in self.channels:
                    self.channels.remove(ch)
                await ch.delete()

        await player.member.remove_roles(self.role)

        # Handle lovers
        checkWin = True
        if player.inLove:
            if player.lover.dyingNow:
                checkWin = False
            player.lover.inLove = False
            player.inLove = False
            await player.loveChannel.delete()
            
        if checkWin:
            await self.checkWin()

        if len(self.players) <= 0:
            await self.cleanUp()

    async def killPlayer(self, player, mainEmbed, DMEmbed, **kwargs):
        """Attempt to kill a player (may be blocked by items)."""
        shouldDie = True
        bypassItems = kwargs.get("bypassItems", False)
        
        if not bypassItems:
            for item in player.inventory:
                if not shouldDie:
                    break
                    
                item_type = type(item).__name__
                saved = False
                
                if item_type == "ring":
                    saved = True
                elif item_type == "shield" and random.randint(0, 1) == 1:
                    saved = True
                elif item_type == "potato" and random.randint(1, 10) == 1:
                    saved = True
                    
                if saved:
                    shouldDie = False
                    await self.mainChannel.send(embed=discord.Embed(
                        title=f"{player.member.display_name} almost died, "
                              f"but their {item.name} saved them!",
                        description="It now disappeared from their inventory.",
                        color=0x00ff00
                    ))
                    await items.removeFromInventory(item, player)

        if shouldDie:
            if player.role == "fool":
                self.foolKilled = True

            await self.mainChannel.send(embed=mainEmbed)
            try:
                await player.member.send(embed=DMEmbed)
            except discord.HTTPException:
                pass
                
            # Kill lover too
            if player.inLove and not player.lover.dyingNow:
                player.dyingNow = True
                await self.killPlayer(
                    player.lover,
                    discord.Embed(
                        title=f":skull: {player.lover.member.display_name} "
                              "died because their lover died",
                        description=f"{player.lover.member.display_name}"
                                    f"{player.lover.role.deadString}",
                        color=0xff0000
                    ),
                    discord.Embed(
                        title=":skull: You died because your lover died",
                        color=0xff0000
                    )
                )

            player.dyingNow = False
            await self.removePlayer(player)
            return True
        return False

    async def startCountdown(self):
        """Start the pre-game countdown."""
        if self.countDown:
            return
            
        self.countDown = True
        countDownCanceled = False
        countDown = dataStorage.getGuildData(
            self.guild, "preGameTimer", default=120
        )

        # Notify main guild
        if self.guild == mainGuild and not self.debug:
            if notificationChannel and gamesStartingRole and joiningChannel:
                await notificationChannel.send(
                    f"{gamesStartingRole.mention}",
                    embed=discord.Embed(
                        title="A new game is about to start!",
                        description=(
                            f"Join in {countDown} seconds using !join "
                            f"in {joiningChannel.mention}"
                        ),
                        color=0x00b8ff
                    )
                )

        # Countdown loop
        while countDown > 0:
            if countDown in [120, 90, 60, 30, 10, 5]:
                await self.mainChannel.send(embed=discord.Embed(
                    title=f"Game starts in {countDown} seconds",
                    description="Waiting for more players to join.",
                    color=0x0088ff
                ))

            await asyncio.sleep(1)
            countDown -= 1

            min_players = dataStorage.getGuildData(
                self.guild, 'minPlayers', default=4
            )
            if len(self.players) < min_players:
                self.countDown = False
                countDownCanceled = True
                await self.mainChannel.send(embed=discord.Embed(
                    title="Countdown canceled",
                    description="Someone left - not enough players.",
                    color=0xff0000
                ))
                break

            if self.startNow:
                self.countDown = False
                break

        if not countDownCanceled:
            await self.mainChannel.send("Game is starting, please wait...")
            availableGames[self.guild.id].remove(self)
            await self.initializeGame()

    async def initializeGame(self):
        """Initialize the game after countdown."""
        random.shuffle(self.players)
        self.started = True
        self.day = 0
        
        await self.role.edit(
            permissions=discord.Permissions(
                read_message_history=True, read_messages=False
            )
        )
        
        # Set permissions on all channels
        for channel in self.guild.channels:
            if self.voiceChannel is not None:
                if channel != self.mainChannel and channel.id != self.voiceChannel.id:
                    try:
                        await channel.set_permissions(
                            self.role, read_messages=False
                        )
                    except discord.HTTPException:
                        pass
            else:
                if channel != self.mainChannel:
                    try:
                        await channel.set_permissions(
                            self.role, read_messages=False
                        )
                    except discord.HTTPException:
                        pass

        await self.mainChannel.set_permissions(
            self.role, read_messages=True, send_messages=True
        )
        await self.mainChannel.edit(name="Day time")
        await self.role.edit(name="In game")

        # Assign roles
        playersToGiveRolesTo = randomizeList(self.players.copy())
        availableRoles = requiredRoles.copy()
        
        while playersToGiveRolesTo and availableRoles:
            playersToGiveRolesTo[0].setRole(availableRoles[0])
            playersToGiveRolesTo.pop(0)
            availableRoles.pop(0)

        availableRoles = randomizeList(getKeys(roles).copy())
        while playersToGiveRolesTo:
            if not availableRoles:
                playersToGiveRolesTo[0].setRole("none")
                playersToGiveRolesTo.pop(0)
            elif roles[availableRoles[0]] > len(self.players):
                availableRoles.pop(0)
            else:
                playersToGiveRolesTo[0].setRole(availableRoles[0])
                playersToGiveRolesTo.pop(0)
                availableRoles.pop(0)

        # Create player channels
        for player in self.players:
            player.nightChannel = await self.category.create_text_channel(
                "Night time"
            )
            await player.nightChannel.set_permissions(
                self.role, read_messages=False
            )
            self.channels.append(player.nightChannel)

            role_name = player.role.name
            if role_name not in ["none", "banker", "fool"]:
                player.roleChannel = await self.category.create_text_channel(
                    role_name
                )
                await player.roleChannel.set_permissions(
                    self.role, read_messages=False
                )
                self.channels.append(player.roleChannel)

            self.allPlayers = self.players.copy()
            
        if self.voiceChannel is not None:
            await self.voiceChannel.set_permissions(self.role, view_channel=True)

        await self.firstDay()

    async def firstDay(self):
        """Run the first day introduction."""
        embed = discord.Embed(
            title="Welcome to Murder Mystery!",
            description=(
                "There is a murderer here! Find and vote to execute them. "
                "If you're the murderer, kill everyone to win."
            ),
            color=0x0088ff
        )
        embed.add_field(
            name="Day time",
            value="Vote to execute someone with !vote <player>",
            inline=False
        )
        embed.add_field(
            name="Night time",
            value="Use !shop and !buy to get items. Use them with !use <item>",
            inline=False
        )
        embed.add_field(
            name="Special roles",
            value="Some players have abilities usable at night.",
            inline=False
        )
        embed.add_field(
            name="Good luck!",
            value="Your role will be revealed at night."
        )
        await self.mainChannel.send(f"{self.role.mention}", embed=embed)
        
        if not self.debug:
            await asyncio.sleep(15)
            
        await self.mainChannel.send(embed=discord.Embed(
            title=":sunny: Day 0",
            description="Night will approach soon! Your role will be revealed.",
            color=0xfff100
        ))
        
        if not self.debug:
            await asyncio.sleep(10)

        await self.makeNightTime()

    # Note: makeNightTime, dayTime, checkWin, stopGame, cleanUp methods
    # would continue here but are omitted for brevity
    # They follow the same pattern from the original bot.py

    async def sendToAllNightChannels(self, **kwargs):
        """Send a message to all player night channels."""
        if not self.nightTime:
            return
            
        msg = kwargs.get("msg")
        embed = kwargs.get("embed")
        
        for plr in self.players:
            if msg and embed:
                await plr.nightChannel.send(msg, embed=embed)
            elif msg:
                await plr.nightChannel.send(msg)
            elif embed:
                await plr.nightChannel.send(embed=embed)

    def getPlayersListExcluding(self, arg):
        """Get players list excluding specified player(s)."""
        copy = self.players.copy()
        if isinstance(arg, list):
            for plr in arg:
                if plr in copy:
                    copy.remove(plr)
        elif arg in copy:
            copy.remove(arg)
        return copy

    def findRole(self, roleName):
        """Find player with a specific role."""
        for player in self.players:
            if player.role.name == roleName:
                return player
        return None

    async def checkWin(self):
        """Check if the game has been won."""
        if not self.started:
            return
            
        foundMurderer = any(p.role.name == "murderer" for p in self.players)

        if foundMurderer:
            werewolf = self.findRole("werewolf")
            murderer = self.findRole("murderer")
            
            if len(self.players) <= 2:
                await self._murdererWins(murderer)
            elif len(self.players) == 3 and werewolf:
                await self._murdererWins(murderer, with_werewolf=True)
        else:
            await self._villagersWin()

    async def _murdererWins(self, murderer, with_werewolf=False):
        """Handle murderer victory."""
        for player in self.players:
            await player.nightChannel.set_permissions(
                player.member, read_messages=False, send_messages=False
            )
            if hasattr(player, "roleChannel"):
                await player.roleChannel.set_permissions(
                    player.member, read_messages=False, send_messages=False
                )

        if murderer.inLove:
            title = ":dagger: :couple_with_heart: Murderer and lover win!"
            if with_werewolf:
                title = ":dagger: :couple_with_heart: :wolf: Murderer, lover, and werewolf win!"
        else:
            title = ":dagger: Murderer wins!"
            if with_werewolf:
                title = ":dagger: :wolf: Murderer and werewolf win!"

        await self.mainChannel.send(embed=discord.Embed(
            title=title,
            description="Game will end in 10 seconds...",
            color=0xa80700
        ))
        await self.mainChannel.set_permissions(
            self.role, read_messages=True, send_messages=True
        )
        self.victory = False
        await asyncio.sleep(10)
        await self.stopGame()

    async def _villagersWin(self):
        """Handle villager victory."""
        for player in self.players:
            await player.nightChannel.set_permissions(
                player.member, read_messages=False, send_messages=False
            )
            if hasattr(player, "roleChannel"):
                await player.roleChannel.set_permissions(
                    player.member, read_messages=False, send_messages=False
                )

        await self.mainChannel.send(embed=discord.Embed(
            title=":tada: Victory!",
            description="The murderer has been killed! Villagers won!\n\n"
                        "Game will end in 10 seconds...",
            color=0x00ff00
        ))
        await self.mainChannel.set_permissions(
            self.role, read_messages=True, send_messages=True
        )
        self.victory = True
        await asyncio.sleep(10)
        await self.stopGame()

    async def stopGame(self):
        """Stop the game and show summary."""
        try:
            await self.role.delete()
        except Exception:
            pass
        # Summary embed would be created here
        await self.cleanUp()

    async def cleanUp(self):
        """Clean up all game resources."""
        # Remove roles from members
        try:
            for m in list(self.guild.members):
                roles_to_remove = []
                if self.role and self.role in m.roles:
                    roles_to_remove.append(self.role)
                if self.spectatorRole and self.spectatorRole in m.roles:
                    roles_to_remove.append(self.spectatorRole)
                if roles_to_remove:
                    try:
                        await m.remove_roles(*roles_to_remove)
                    except Exception:
                        pass
        except Exception:
            pass

        # Mark players as not in game
        for player in self.players:
            player.inGame = False
            if self.guild.id in allPlayers and player in allPlayers[self.guild.id]:
                allPlayers[self.guild.id].remove(player)

        # Delete roles
        for r in [self.role, self.spectatorRole]:
            if r:
                try:
                    await r.delete()
                except Exception:
                    pass

        # Delete channels
        for channel in self.channels:
            try:
                await channel.delete()
            except discord.HTTPException:
                pass
        try:
            await self.category.delete()
        except discord.HTTPException:
            pass

        # Remove from tracking
        if self.guild.id in currentGames and self in currentGames[self.guild.id]:
            currentGames[self.guild.id].remove(self)
        if self.guild.id in availableGames and self in availableGames[self.guild.id]:
            availableGames[self.guild.id].remove(self)


# Alias for backward compatibility
game = Game
