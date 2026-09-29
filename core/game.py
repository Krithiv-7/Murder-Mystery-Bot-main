"""Game class for Murder Mystery bot."""
import asyncio
import logging
import random
import discord

import dataStorage
from dataStorage import setPlayerData, getPlayerData, getGuildData
from aiohttp import ClientOSError
import items
import objectives
from roles import role

from .game_state import (
    allPlayers,
    mainGuild, mainGameRolePosition, notificationChannel,
    newGamesRole, gamesStartingRole, joiningChannel
)
from .config import GAME_DEFAULTS, requiredRoles, roles, mainServerInvite
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


class VoteSelect(discord.ui.Select):
    """Dropdown used for the daytime vote."""

    def __init__(self, game):
        self.game = game
        options = [
            discord.SelectOption(
                label=player.member.display_name[:100],
                value=str(player.member.id),
            )
            for player in game.players[:25]
        ]
        super().__init__(
            placeholder="Choose a player to execute",
            options=options,
            min_values=1,
            max_values=1,
        )

    async def callback(self, interaction):
        target_id = int(self.values[0])
        target = next(
            (player.member for player in self.game.players
             if player.member.id == target_id),
            None,
        )
        if target is None:
            await interaction.response.send_message(
                "That player is no longer in the game.", ephemeral=True
            )
            return
        success, message = await self.game.record_vote(
            interaction.user, target
        )
        await interaction.response.send_message(message, ephemeral=True)


class VoteView(discord.ui.View):
    """Interactive voting controls with the text command as fallback."""

    def __init__(self, game):
        super().__init__(timeout=180)
        self.game = game
        self.add_item(VoteSelect(game))

    async def on_timeout(self):
        for item in self.children:
            item.disabled = True


class GameStatusChannel:
    """Public status proxy: no per-game channel is created anymore.

    Wraps the guild's configured setup channel (or the channel the lobby
    was created in) so the rest of the game code can keep calling
    ``self.mainChannel.send(...)`` without the bot provisioning a
    dedicated category/role/channel per game. Messages are tagged with
    the lobby index so concurrent games sharing the channel stay legible.
    """

    def __init__(self, game, channel_id):
        self.game = game
        self.channel_id = channel_id
        self.id = channel_id

    def _resolve(self):
        if self.channel_id is None:
            return None
        return self.game.guild.get_channel(self.channel_id)

    def _tag(self):
        return f"Lobby {getattr(self.game, 'code', '?')}"

    async def send(self, *args, **kwargs):
        channel = self._resolve()
        if channel is None:
            return None
        embed = kwargs.get("embed")
        if embed is not None:
            embed.set_footer(text=self._tag())
        try:
            return await channel.send(*args, **kwargs)
        except discord.HTTPException:
            return None

    async def set_permissions(self, *args, **kwargs):
        return None

    async def edit(self, *args, **kwargs):
        return None

    async def purge(self, *args, **kwargs):
        return None


class Game:
    """Represents a Murder Mystery game instance."""

    def __init__(self, guild, debug):
        self.guild = guild
        self.debug = debug
        self.owner_id = None
        from core.manager import game_manager
        self.code = game_manager.allocate_code()
        self._cleaned = False
        self._cancel_phase = False
        self._phase_task = None

        # no per-game roles/channels are created anymore; comms are DM +
        # the shared setup channel (see GameStatusChannel/createGame)
        self.role = None
        self.spectatorRole = None
        self.category = None
        self.voiceChannel = None
        self.mainChannel = None

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
        self.statusMessage = None

        # fool
        self.foolKilled = False
        self.foolWin = False

        # weather
        self.weatherIntensity = 1
        self.moon = 3

    def _register_game(self):
        """Ensure the game is tracked in the shared guild registries."""
        from core.manager import game_manager
        game_manager.register(self)

    @property
    def phase(self) -> str:
        """Coarse lifecycle label for status displays."""
        if self.victory is not None or self.foolWin:
            return "game_over"
        if not self.started:
            return "starting" if self.countDown else "lobby"
        if self.voteTime:
            return "voting"
        if self.nightTime:
            return "night"
        return "day"

    async def handle_vote(self, voter_member, target_member):
        """Adapter used by Discord commands. Core voting stays in record_vote."""
        return await self.record_vote(voter_member, target_member)

    async def record_vote(self, voter_member, target_member):
        """Record or change a player's vote for any command/UI entry point."""
        voter = next(
            (player for player in self.players if player.member == voter_member),
            None,
        )
        target = next(
            (player for player in self.players if player.member == target_member),
            None,
        )
        if voter is None or target is None or not self.voteTime:
            return False, "Voting is not available for that player right now."
        if voter == target:
            return False, "You can't vote for yourself."

        vote_weight = getattr(getattr(voter, "role", None), "voteWeight", 1)
        if not voter.voted:
            target.votes += vote_weight
            voter.voted = True
            voter.votedOn = target
            self.playersThatVoted.append(voter)
            self.extendVotingTime = True
            return True, f"You voted for {target.member.display_name}."
        if voter.votedOn == target:
            return False, "You already voted for that player."

        voter.votedOn.votes -= vote_weight
        target.votes += vote_weight
        voter.votedOn = target
        self.extendVotingTime = True
        return True, f"You changed your vote to {target.member.display_name}."

    async def _notify_new_game(self):
        """Notify the main guild when a non-debug game is created."""
        if self.guild != mainGuild or self.debug:
            return
        if notificationChannel and newGamesRole and joiningChannel:
            await notificationChannel.send(
                f"{newGamesRole.mention}",
                embed=discord.Embed(
                    title="A new game has just been created!",
                    description=(
                        f"Someone just started a new game. "
                        f"Join using !join in {joiningChannel.mention}"
                    ),
                    color=0x00b8ff,
                ),
            )

    async def update_status(self):
        """Create or update the single game status message."""
        if getattr(self, "mainChannel", None) is None:
            return
        phase = "Voting" if self.voteTime else ("Night" if self.nightTime else "Day")
        embed = discord.Embed(
            title=":scroll: Game status",
            color=0x00b8ff if phase == "Day" else 0x34495e,
        )
        embed.add_field(name="Phase", value=f"{phase} {self.day}", inline=True)
        embed.add_field(name="Players", value=str(len(self.players)), inline=True)
        embed.add_field(name="Weather", value=str(self.weatherIntensity), inline=True)
        embed.add_field(name="Moon", value=str(self.moon), inline=True)
        try:
            if self.statusMessage is None:
                self.statusMessage = await self.mainChannel.send(embed=embed)
            else:
                await self.statusMessage.edit(embed=embed)
        except (discord.HTTPException, AttributeError):
            self.statusMessage = None

    async def _delete_channel(self, channel):
        """Safely delete a channel and remove it from the tracked set."""
        if channel is None:
            return
        if channel in self.channels:
            self.channels.remove(channel)
        try:
            await channel.delete()
        except discord.HTTPException:
            pass
        except AttributeError:
            pass

    async def ensure_main_channel(self):
        """No-op: the status channel resolves lazily, nothing to recreate."""
        return

    async def createGame(self, client=None, channel=None):
        """Register the game; no roles/categories/channels are provisioned.

        Public status updates go to the guild's configured setup channel
        (falling back to the channel the lobby was created in). All private
        game/role communication happens over DM via ``Player.send_private``.
        The ``client``/``channel`` parameters remain optional to preserve
        compatibility with existing call sites.
        """
        status_channel_id = dataStorage.getGuildData(self.guild, "setupChannel")
        status_channel = (
            self.guild.get_channel(status_channel_id) if status_channel_id else None
        )
        if status_channel is None and channel is not None:
            status_channel = channel

        self.mainChannel = GameStatusChannel(
            self, getattr(status_channel, "id", None)
        )

        self._register_game()
        await self._notify_new_game()
        logging.getLogger("mmb.game").info(
            "New game %s in guild %s",
            self.code,
            self.guild.id,
            extra={"guild_id": self.guild.id, "game_id": self.code},
        )

    async def addPlayer(self, member):
        """Add a player to the game. A second join is ignored."""
        for existing in self.players:
            if getattr(existing.member, "id", None) == member.id and existing.inGame:
                return existing
        newPlayer = Player(member, self)
        self.players.append(newPlayer)
        
        if self.guild.id not in allPlayers:
            allPlayers[self.guild.id] = []
        allPlayers[self.guild.id].append(newPlayer)

        min_players = dataStorage.getGuildData(
            self.guild, "minPlayers", default=GAME_DEFAULTS["minPlayers"]
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
        return newPlayer

    async def addSpectator(self, member):
        """Add a spectator to the game."""
        if any(getattr(existing, "id", None) == member.id for existing in self.spectators):
            return
        self.spectators.append(member)
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

    async def removePlayer(self, player, **kwargs):
        """Remove a player from the game."""
        if player is None:
            return

        player.inGame = False

        if self.guild.id in allPlayers and player in allPlayers[self.guild.id]:
            allPlayers[self.guild.id].remove(player)

        if player in self.players:
            self.players.remove(player)

        # Clean up player channels
        for attr in ["nightChannel", "roleChannel", "broadcastChannel"]:
            ch = getattr(player, attr, None)
            if ch is not None:
                await self._delete_channel(ch)

        role_to_remove = getattr(self, "role", None)
        if role_to_remove is not None and hasattr(player, "member"):
            try:
                await player.member.remove_roles(role_to_remove)
            except Exception:
                pass

        # Handle lovers
        checkWin = True
        if getattr(player, "inLove", False):
            lover = getattr(player, "lover", None)
            if lover is not None and getattr(lover, "dyingNow", False):
                checkWin = False
            if lover is not None:
                lover.inLove = False
            player.inLove = False
            love_channel = getattr(player, "loveChannel", None)
            if love_channel is not None:
                try:
                    await love_channel.delete()
                except Exception:
                    pass

        if checkWin and self.started:
            await self.checkWin()

        if len(self.players) <= 0:
            await self.cleanUp()

    async def killPlayer(self, player, mainEmbed, DMEmbed, **kwargs):
        """Attempt to kill a player (may be blocked by items)."""
        shouldDie = True
        bypassItems = kwargs.get("bypassItems", False)

        bodyguard = getattr(getattr(player, "role", None), "protectedBy", None)
        if bodyguard in self.players and bodyguard is not player and not bypassItems:
            player.role.protectedBy = None
            await self.mainChannel.send(embed=discord.Embed(
                title=f":shield: {bodyguard.member.display_name} died protecting "
                      f"{player.member.display_name}",
                description=(
                    f"{bodyguard.member.display_name}{bodyguard.role.deadString}"
                ),
                color=0x3498db,
            ))
            await bodyguard.send_private(embed=discord.Embed(
                title=":shield: You died protecting another player",
                description="Your bodyguard ability saved them from the attack.",
                color=0x3498db,
            ))
            await self.killPlayer(
                bodyguard,
                discord.Embed(
                    title=f":shield: {bodyguard.member.display_name} died protecting "
                          f"{player.member.display_name}",
                    description=f"{bodyguard.member.display_name}{bodyguard.role.deadString}",
                    color=0x3498db,
                ),
                discord.Embed(
                    title=":skull: You died protecting another player",
                    color=0x3498db,
                ),
                bypassItems=True,
            )
            return False
        
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
        self._phase_task = asyncio.current_task()
        countDownCanceled = False
        countDown = dataStorage.getGuildData(
            self.guild, "preGameTimer", default=GAME_DEFAULTS["preGameTimer"]
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
            if self._cancel_phase:
                self.countDown = False
                return
            if countDown in [120, 90, 60, 30, 10, 5]:
                await self.mainChannel.send(embed=discord.Embed(
                    title=f"Game starts in {countDown} seconds",
                    description="Waiting for more players to join.",
                    color=0x0088ff
                ))

            await asyncio.sleep(1)
            countDown -= 1

            min_players = dataStorage.getGuildData(
                self.guild, 'minPlayers', default=GAME_DEFAULTS["minPlayers"]
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
            from core.manager import game_manager
            game_manager.mark_unavailable(self)
            await self.initializeGame()

    async def initializeGame(self):
        """Initialize the game after countdown."""
        random.shuffle(self.players)
        self.started = True
        self.day = 0

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

        # Private game communication is sent through DMs instead of channels.
        self.allPlayers = self.players.copy()
            
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
        mentions = " ".join(p.member.mention for p in self.players)
        from core.action_views import application_id, dm_link_view

        app_id = application_id(self.guild)
        embed.add_field(
            name="Private chat",
            value=(
                "Your role and night actions are sent by DM. "
                "If nothing arrives, press **Allow DMs from this bot**."
            ),
            inline=False,
        )
        await self.mainChannel.send(
            mentions,
            embed=embed,
            view=dm_link_view(app_id) if app_id else None,
        )
        
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

    async def safe_send(self, channel, *args, **kwargs):
        """Send a message to a channel with retry and error handling."""
        retries = kwargs.pop("retries", 1)
        delay = kwargs.pop("delay", 1)
        for attempt in range(retries + 1):
            try:
                return await channel.send(*args, **kwargs)
            except (ClientOSError, ConnectionResetError, OSError, asyncio.TimeoutError) as exc:
                if attempt >= retries:
                    logging.getLogger("mmb.game").warning(
                        "Send failed to channel %s: %s",
                        getattr(channel, "id", "unknown"),
                        exc,
                    )
                    return None
                await asyncio.sleep(delay)
            except discord.HTTPException as exc:
                if attempt >= retries:
                    logging.getLogger("mmb.game").warning(
                        "HTTP send failed to channel %s: %s",
                        getattr(channel, "id", "unknown"),
                        exc,
                    )
                    return None
                await asyncio.sleep(delay)
        return None

    async def _remove_night_channels(self):
        """Delete channels scheduled for removal when night begins."""
        while self.channelsRemoveByNight:
            target = self.channelsRemoveByNight.pop(0)
            channel = None
            if isinstance(target, (int, str)):
                try:
                    channel_id = int(target)
                    channel = self.guild.get_channel(channel_id)
                    if channel is None:
                        channel = await self.guild.fetch_channel(channel_id)
                except Exception:
                    channel = None
            elif hasattr(target, "delete"):
                channel = target

            if channel is not None:
                try:
                    await channel.delete()
                except discord.HTTPException:
                    pass
                if channel in self.channels:
                    self.channels.remove(channel)

    async def _run_night_timer(self):
        """Wait for night actions and announce the approaching sunrise."""
        count = dataStorage.getGuildData(
            self.guild, "nightTimeTimer", default=GAME_DEFAULTS["nightTimeTimer"]
        )
        if self.debug:
            count = min(count, 3)

        while count >= 0:
            if self._cancel_phase:
                break
            if self.skipNight:
                self.skipNight = False
                break
            if not self.debug:
                if count == 30:
                    title = ":first_quarter_moon: The sun is about to rise!"
                    description = "The sun will rise in 30 seconds."
                elif count == 15:
                    title = ":waxing_crescent_moon: The sun is about to rise!"
                    description = "The sun will rise in 15 seconds."
                elif count == 10:
                    title = ":sunrise_over_mountains: The sun is about to rise!"
                    description = "The sun will rise in 5 seconds."
                else:
                    title = None

                if title is not None:
                    embed = discord.Embed(
                        title=title,
                        description=description,
                    )
                    for player in self.players:
                        await player.send_private(embed=embed)

            await asyncio.sleep(1)
            count -= 1

    async def makeNightTime(self):
        """Handle night time phase."""
        await self.ensure_main_channel()

        self.nightTime = True
        await self.mainChannel.set_permissions(self.role, send_messages=False)
        await self.update_status()

        await self._remove_night_channels()

        jailer = None
        emoji = ""
        for player in self.players:
            player.satelliteUsed = False
            player.role.abilityUsed = False
            player.whisperingTo = []
            if hasattr(player.role, "protectedPlayer"):
                player.role.protectedPlayer = None
            if hasattr(player.role, "protectedBy"):
                player.role.protectedBy = None
            if self.moon == 1:
                emoji = ":new_moon:"
            elif self.moon == 2:
                emoji = ":waning_crescent_moon:"
            elif self.moon == 3:
                emoji = ":last_quarter_moon:"
            elif self.moon == 4:
                emoji = ":waning_gibbous_moon:"
            elif self.moon == 5:
                emoji = ":full_moon:"
            embed = discord.Embed(
                title=f"{emoji} Night time",
                description=(
                    "It's now night time. You can't talk to other "
                    "people in night time, but you can use !shop "
                    "to use the shop during night time."
                )
            )
            if self.day == 0:
                embed.add_field(
                    name="First night:",
                    value=(
                        "Your role will be revealed below. Some roles "
                        "have special abilities that can be used during "
                        "night time, and instructions will be sent here."
                    )
                )
            await player.send_private(embed=embed)

            if self.day == 0:
                await player.send_private(embed=player.role.revealEmbed)

        if self.day == 0:
            werewolf = self.findRole("werewolf")
            murderer = self.findRole("murderer")
            if werewolf is not None and murderer is not None:
                werewolf_name = werewolf.member.display_name
                murderer_name = murderer.member.display_name
                embed1 = discord.Embed(
                    title=(
                        f":wolf: {werewolf_name} is the werewolf, "
                        "and you're a team with them."
                    ),
                    description=(
                        "The werewolf has to kill someone when it "
                        "becomes full moon. You're teaming up with them "
                        "to kill everyone else.\n"
                        "**Do not try to kill them, they're your teammate.**"
                    ),
                    color=0xffda83
                )
                await murderer.send_private(embed=embed1)
                embed2 = discord.Embed(
                    title=(
                        f":dagger: {murderer_name} is the murderer, "
                        "and you're a team with them."
                    ),
                    description=(
                        "You will team up with the murderer to kill "
                        "everyone else. If the murderer dies, you "
                        "automatically lose too.\n"
                        "**Do not try to kill them, they're your teammate.**"
                    ),
                    color=0xa80700
                )
                await werewolf.send_private(embed=embed2)

        for player in self.players:
            if random.randint(1, 10) == 1:
                player.gold += 2
                embed = discord.Embed(
                    title="You found :coin: 2 gold",
                    description=(
                        "You found :coin: 2 gold lying on the floor. "
                        "Lucky you!"
                    ),
                    color=0x00ff00
                )
                await player.send_private(embed=embed)

            if 60 < self.weatherIntensity <= 80:
                num = random.randint(1, 10)
                goldNum = 0
                if 5 <= num <= 7:
                    goldNum = 1
                elif num == 8:
                    goldNum = 2
                elif num == 9:
                    goldNum = 3
                elif num == 10:
                    goldNum = 4

                if goldNum != 0:
                    player.gold += goldNum
                    embed = discord.Embed(
                        title=f":dash: The wind blew :coin: {goldNum} gold!",
                        description="Lucky you!",
                        color=0x00ff00
                    )
                    await player.send_private(embed=embed)

            await player.role.sendRoleChannelEmbed()

            if player.role.name == "broadcaster":
                for bc in player.role.broadcastsToBeSent:
                    await bc.send()

            elif player.role.name == "jailer":
                jailer = player

            elif player.role.name == "werewolf":
                player.role.killedSomeone = False

        if jailer is not None:
            if hasattr(jailer.role, "jailedNext") and jailer.role.jailedNext is not None:
                if jailer.role.jailedNext in self.players:
                    jailer.role.jailedNext.inJail = True
                    jailed = jailer.role.jailedNext

                    embed = discord.Embed(
                        title="You are now in jail",
                        description=(
                            "While in jail, you can't use the shop "
                            "or your role's ability."
                        ),
                        color=0x4a4a4a
                    )
                    await jailed.send_private(embed=embed)

                    jailer.role.jailedNext = None

        if self.weatherIntensity > 95:
            embed = discord.Embed(
                title=":warning: :cloud_tornado: Tornado warning! :warning:",
                description=(
                    "There will soon be a tornado. If you don't have a "
                    ":house: house, there's a 30% chance that you will "
                    "die next morning.\n"
                    "You can buy a :house: house from !shop"
                ),
                color=0xff0000
            )
            await self.sendToAllNightChannels(embed=embed)

        await self._run_night_timer()

        await self.dayTime()

    async def _grant_daily_gold_and_lottery(self):
        """Apply daily gold income and lottery ticket resolution."""
        if len(self.players) <= 5:
            if not self.fivePlayersLeftGoldIncrease:
                self.goldPerDay += 1
                self.fivePlayersLeftGoldIncrease = True
                embed = discord.Embed(
                    title=":chart_with_upwards_trend: Gold per day increased",
                    description=(
                        f"Because 5 or less players are remaining, the "
                        f"gold received per day increased from "
                        f"{self.goldPerDay - 1} to {self.goldPerDay}"
                    ),
                    color=0x00ff00,
                )
                await self.mainChannel.send(embed=embed)

        if self.day % 3 == 0:
            self.goldPerDay += 1
            embed = discord.Embed(
                title=":chart_with_upwards_trend: Gold per day increased",
                description=(
                    f"Every 3 days the gold earned by day increases by "
                    f"1. The gold received per day is now {self.goldPerDay}."
                ),
                color=0x00ff00,
            )
            await self.mainChannel.send(embed=embed)

        for player in self.players:
            if player.role.name != "banker":
                player.gold += self.goldPerDay
            else:
                player.gold += self.goldPerDay + 1

        embed = discord.Embed(
            title=f":coin: Everyone received {self.goldPerDay} gold",
            description=(
                f"Every morning, everyone will receive :coin: "
                f"{self.goldPerDay} gold.\nIf there is a "
                f":person_in_tuxedo: banker, then they received "
                f":coin: {self.goldPerDay + 1} gold."
            ),
            color=0x00b8ff,
        )
        await self.mainChannel.send(embed=embed)

        for player in self.players:
            if player.inJail:
                player.inJail = False

            for item in list(player.inventory):
                if type(item).__name__ == "ticket":
                    gold_before_prize = player.gold
                    won_prize = False
                    if random.randint(0, 100) == 1:
                        player.gold += 30
                        won_prize = True
                    elif random.randint(0, 50) == 1 and not won_prize:
                        player.gold += 20
                        won_prize = True
                    elif random.randint(0, 20) == 1 and not won_prize:
                        player.gold += 10
                        won_prize = True
                    elif random.randint(0, 7) == 1 and not won_prize:
                        player.gold += 5
                        won_prize = True

                    if won_prize:
                        prize = player.gold - gold_before_prize
                        name = player.member.display_name
                        embed = discord.Embed(
                            title=(
                                f":moneybag: {name} won :coin: "
                                f"{prize} gold in the lottery!"
                            ),
                            description=(
                                "Their lottery ticket is now no longer "
                                "in their inventory"
                            ),
                            color=0x00ff00,
                        )
                        await self.mainChannel.send(embed=embed)
                    else:
                        name = player.member.display_name
                        embed = discord.Embed(
                            title=f":money_with_wings: {name} lost the lottery",
                            description=(
                                "Their lottery ticket is now no longer "
                                "in their inventory"
                            ),
                            color=0xff0000,
                        )
                        await self.mainChannel.send(embed=embed)
                    await items.removeFromInventory(item, player)
                    break

    async def _run_vote_cycle(self):
        """Handle the vote phase and any immediate execution that follows."""
        for player in self.players:
            player.voted = False
            player.votes = 0
        self.voteTime = True
        await self.update_status()
        desc = (
            "Vote on who you think is the murderer with "
            "!vote <@username>.\n\nYou will have 120 seconds to vote."
        )
        fool_threshold = roles.get("fool", 6)
        if len(self.allPlayers) >= fool_threshold and not self.foolKilled:
            desc += (
                "\n\nIt's possible that there is a :clown: fool here, "
                "if they get voted to be executed they win."
            )
        embed = discord.Embed(
            title="Vote to execute a player",
            description=desc + "\n\nYou can use the dropdown or the !vote command.",
            color=0x00b8ff,
        )
        await self.mainChannel.send(embed=embed, view=VoteView(self))

        extendedTooMuchMessageSent = False
        count = dataStorage.getGuildData(
            self.guild, "votingTime", default=GAME_DEFAULTS["votingTime"]
        )
        if self.debug:
            count = min(count, 3)

        while count >= 0:
            if self._cancel_phase:
                break
            if len(self.playersThatVoted) == len(self.players):
                if count > 16:
                    embed = discord.Embed(
                        title=(
                            "Everyone has voted, voting time has been "
                            "set to 15 seconds"
                        ),
                        description=(
                            "Because everyone has voted, the voting time "
                            "has been set to 15 seconds. If you want to "
                            "change your vote, do it now."
                        ),
                        color=0x0088ff,
                    )
                    await self.mainChannel.send(embed=embed)
                    count = 15

            if self.skipVotingTime:
                self.skipVotingTime = False
                break

            if not self.debug:
                reminders = [90, 60, 30, 15, 10, 5]
                if count in reminders:
                    await self.mainChannel.send(f"Voting ends in {count} seconds!")

            count -= 1

            if self.extendVotingTime:
                if count <= 15:
                    if self.timesVotingTimeExtended < 7:
                        count = 15
                        embed = discord.Embed(
                            title=(
                                f"Voting time has been extended to "
                                f"{count} seconds"
                            ),
                            description=(
                                "To prevent people from submitting their "
                                "votes last-second and changing the voting "
                                "result without other players knowing, the "
                                f"voting time has been extended to "
                                f"{count} seconds."
                            ),
                            color=0x0088ff,
                        )
                        await self.mainChannel.send(embed=embed)
                    else:
                        if not extendedTooMuchMessageSent:
                            count = 15
                            embed = discord.Embed(
                                title=(
                                    f"Voting time has been extended to "
                                    f"{count} seconds"
                                ),
                                description=(
                                    "To prevent people from submitting "
                                    "their votes last-second and changing "
                                    "the voting result without other "
                                    f"players knowing, the voting time has "
                                    f"been extended to {count} seconds."
                                ),
                                color=0x0088ff,
                            )
                            await self.mainChannel.send(embed=embed)
                            embed2 = discord.Embed(
                                title="Voting time will not get extended anymore",
                                description=(
                                    "The voting time got extended too many "
                                    "times and will no longer get extended"
                                ),
                                color=0xff0000,
                            )
                            await self.mainChannel.send(embed=embed2)
                            extendedTooMuchMessageSent = True
                self.extendVotingTime = False

            await asyncio.sleep(1)

        self.voteTime = False
        votes = self.players.copy()
        votes.sort(reverse=True, key=lambda x: x.votes)

        tie = False
        if len(votes) >= 2 and votes[0].votes == votes[1].votes:
            voteResultEmbedTitle = "There was a tie, no one will be executed."
            tie = True
        elif votes:
            name = votes[0].member.display_name
            voteResultEmbedTitle = (
                f"Vote results are in, {name} will be executed"
            )
        else:
            voteResultEmbedTitle = "No votes were recorded."
            tie = True

        embedDesc = (
            "These are the results of the vote. The player with the "
            "most votes will get executed.\n"
        )
        for player in votes:
            embedDesc = embedDesc + f"\n{player.member.mention}: {player.votes}"
        embed = discord.Embed(
            title=voteResultEmbedTitle,
            description=embedDesc,
            color=0x00b8ff,
        )
        await self.mainChannel.send(embed=embed)
        self.playersThatVoted = []

        for player in self.players:
            if player.voted:
                voted_role = getattr(getattr(player, "votedOn", None), "role", None)
                voted_role_name = getattr(voted_role, "name", str(voted_role))
                if voted_role_name == "murderer":
                    objectives.addObjectiveProgress(
                        player.member, "voteOnMurderer", 1
                    )
                    if self.day == 1:
                        if len(self.allPlayers) >= 6:
                            objectives.addObjectiveProgress(
                                player.member,
                                "dayOneMurdererVote6PlayersOrMore", 1
                            )

        if not self.debug:
            await asyncio.sleep(2)

        if not tie and votes:
            executed_player = votes[0]
            if executed_player.role.name != "fool":
                name = executed_player.member.display_name
                main_embed = discord.Embed(
                    title=f"{name} got executed",
                    description=f"{name}{executed_player.role.deadString}",
                    color=0xff000d,
                )
                dm_embed = discord.Embed(
                    title=":skull: You died because you got executed.",
                    description=(
                        "Try convincing the other players that you're "
                        "not the murderer next time!"
                    ),
                    color=0xff000d,
                )
                await self.killPlayer(
                    executed_player, main_embed, dm_embed, bypassItems=True
                )
            else:
                name = executed_player.member.display_name
                embed = discord.Embed(
                    title=f"{name} got executed",
                    description=f"{name}{executed_player.role.deadString}",
                    color=0xff000d,
                )
                await self.mainChannel.send(embed=embed)
                self.foolWin = True
                await asyncio.sleep(1)
                embed2 = discord.Embed(
                    title=":clown: Fool wins!",
                    description="The fool has won because he got executed!",
                    color=0xfff100,
                )
                await self.mainChannel.send(embed=embed2)
                if not self.debug:
                    await asyncio.sleep(10)
                await self.stopGame()
                return

        if not self.debug:
            await asyncio.sleep(10)

        if self.victory is None:
            embed = discord.Embed(
                title=":white_sun_small_cloud: The sun is about to set!",
                description="Night will approach in 20 seconds.",
                color=0xffe800,
            )
            await self.mainChannel.send(embed=embed)
            if not self.debug:
                await asyncio.sleep(2)

            self.weatherIntensity = random.randint(1, 100)
            self.moon = random.randint(1, 5)
            desc = (
                "Welcome to today's weather forecast. Here is the "
                "predicted weather for tonight:\n\n"
            )
            if self.weatherIntensity <= 60:
                desc += (
                    ":milky_way: Tonight there will be a clear sky "
                    "without any clouds or extreme weather."
                )
            elif 60 < self.weatherIntensity <= 80:
                desc += (
                    ":dash: Tonight it will be a bit windy. If you're "
                    "lucky some :coin: gold might even blow to your home!"
                )
            elif 80 < self.weatherIntensity <= 90:
                desc += (
                    ":thunder_cloud_rain: Tonight there will be a "
                    "thunderstorm and broadcasting communication "
                    "systems might not work."
                )
            elif 90 < self.weatherIntensity <= 95:
                desc += (
                    ":fog: Tonight it will be very foggy and the "
                    ":spy: detective might not be able to do their work."
                )
            elif self.weatherIntensity > 95:
                desc += (
                    ":cloud_tornado: Tonight there will be a tornado. "
                    "It is highly recommended to seek shelter for tonight! "
                    "The shop will sell a :house: house for you to hide "
                    "in during the tornado."
                )
            desc += "\n"
            if self.moon == 1:
                desc += (
                    ":new_moon: Also tonight the moon won't be visible. "
                    "It will be very dark and the :dagger: murderer might "
                    "not have enough light locate someone to kill."
                )
            elif self.moon == 2:
                desc += (
                    ":waning_crescent_moon: Also tonight the moon will "
                    "be partially visible."
                )
            elif self.moon == 3:
                desc += (
                    ":last_quarter_moon: Also tonight the moon will be "
                    "partially visible."
                )
            elif self.moon == 4:
                desc += (
                    ":waning_gibbous_moon: Also tonight the moon will be "
                    "partially visible."
                )
            elif self.moon == 5:
                desc += (
                    ":full_moon: Also tonight there will be a full moon. "
                    "If there is a :wolf: werewolf then they might kill "
                    "someone."
                )
            desc += "\n\nThat was the weather report for upcoming night. Goodbye!"

            embed = discord.Embed(
                title=":radio: Weather forecast",
                description=desc,
                color=0x00ff00,
            )
            await self.mainChannel.send(embed=embed)

            if not self.debug:
                await asyncio.sleep(8)
                embed = discord.Embed(
                    title=":white_sun_cloud: The sun is about to set!",
                    description="Night will approach in 10 seconds.",
                    color=0xffe800,
                )
                await self.mainChannel.send(embed=embed)
                await asyncio.sleep(5)
                embed = discord.Embed(
                    title=":city_sunset: The sun is about to set!",
                    description="Night will approach in 5 seconds.",
                    color=0xffe800,
                )
                await self.mainChannel.send(embed=embed)
                await asyncio.sleep(5)

            await self.makeNightTime()

    async def dayTime(self):
        """Handle daytime phase."""
        await self.ensure_main_channel()
        self.nightTime = False
        self.day = self.day + 1
        await self.update_status()

        await self.mainChannel.set_permissions(
            self.role, send_messages=True, read_messages=True
        )
        embed = discord.Embed(
            title=f":sunny: Day {self.day}",
            description="The sun is rising, good morning everyone!",
            color=0xfff100,
        )
        await self.mainChannel.send(embed=embed)
        for channel in list(self.channelsRemoveByMorning):
            self.channelsRemoveByMorning.remove(channel)
            if channel in self.channels:
                self.channels.remove(channel)
            try:
                await channel.delete()
            except discord.HTTPException:
                pass

        # Werewolf full moon kill
        if self.findRole("werewolf") is not None:
            if self.moon == 5:
                werewolf = self.findRole("werewolf")
                if not getattr(werewolf.role, "killedSomeone", False):
                    murderer = self.findRole("murderer")
                    exclude = [werewolf]
                    if murderer is not None:
                        exclude.append(murderer)
                    playersList = self.getPlayersListExcluding(exclude)
                    if playersList:
                        random.shuffle(playersList)
                        self.willDieNextMorning.append({
                            "player": playersList[0],
                            "title": " got killed",
                            "DM": ":skull: You got killed by the werewolf!"
                        })

        # Process morning deaths
        for deathData in list(self.willDieNextMorning):
            plr = deathData["player"]
            if plr in self.players:
                embedTitle = deathData["title"]
                main_embed = discord.Embed(
                    title=f":skull: {plr.member.display_name} {embedTitle}",
                    description=(
                        f"{plr.member.display_name}{plr.role.deadString}"
                    ),
                    color=0xff000d,
                )
                dm_embed = discord.Embed(
                    title=deathData["DM"],
                    description=f"You almost made it to day {self.day}",
                    color=0xff000d,
                )
                if await self.killPlayer(
                    deathData["player"], main_embed, dm_embed
                ):
                    if "deathCause" in deathData:
                        cause = deathData["deathCause"]
                        if cause == "itemUsedOnPlayer":
                            if "killer" in deathData:
                                objectives.addObjectiveProgress(
                                    deathData["killer"].member,
                                    "killMurdererWithItem", 1
                                )

                if deathData in self.willDieNextMorning:
                    self.willDieNextMorning.remove(deathData)

        if self.weatherIntensity > 95:
            for player in list(self.players):
                hasHouse = False
                house = None
                for item in player.inventory:
                    if type(item).__name__ == "house":
                        hasHouse = True
                        house = item
                if random.randint(0, 10) <= 3:
                    if hasHouse:
                        await items.removeFromInventory(house, player)
                        name = player.member.display_name
                        embed = discord.Embed(
                            title=(
                                f":house_abandoned: :cloud_tornado: "
                                f"{name}'s house got destroyed by tornado"
                            ),
                            description="But they survived themselves!",
                            color=0xff0000,
                        )
                        await self.mainChannel.send(embed=embed)
                    else:
                        name = player.member.display_name
                        main_embed = discord.Embed(
                            title=(
                                f":skull: :cloud_tornado: "
                                f"{name} died in the tornado"
                            ),
                            description=(
                                f"{name}{player.role.deadString}"
                            ),
                            color=0xff0000,
                        )
                        dm_embed = discord.Embed(
                            title=":skull: :cloud_tornado: You died in a tornado",
                            description="Next time buy a :house: house",
                            color=0xff0000,
                        )
                        await self.killPlayer(
                            player, main_embed, dm_embed
                        )

        await self._grant_daily_gold_and_lottery()

        if not self.debug:
            await asyncio.sleep(10)

        await self._run_vote_cycle()

    async def sendToAllNightChannels(self, **kwargs):
        """Send a message to all players by DM during the night phase."""
        if not self.nightTime:
            return

        msg = kwargs.get("msg")
        embed = kwargs.get("embed")

        for plr in self.players:
            if msg and embed:
                await plr.send_private(msg, embed=embed)
            elif msg:
                await plr.send_private(msg)
            elif embed:
                await plr.send_private(embed=embed)

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
            if hasattr(player, "role") and player.role.name == roleName:
                return player
        return None

    async def checkWin(self):
        """Check if the game has been won."""
        if not self.started:
            return

        foundMurderer = any(getattr(getattr(p, "role", None), "name", None) == "murderer" for p in self.players)

        if foundMurderer:
            if len(self.players) <= 2:
                for player in self.players:
                    if hasattr(player, "nightChannel") and player.nightChannel is not None:
                        await player.nightChannel.set_permissions(
                            player.member, read_messages=False, send_messages=False
                        )
                    if hasattr(player, "roleChannel") and player.roleChannel is not None:
                        await player.roleChannel.set_permissions(
                            player.member, read_messages=False, send_messages=False
                        )

                murderer = self.findRole("murderer")
                if murderer is not None and getattr(murderer, "inLove", False):
                    embed = discord.Embed(
                        title=":dagger: :couple_with_heart: Murderer and their lover win!",
                        description=(
                            "The murderer killed everyone except their lover!\n\n\n"
                            "Game will end in 10 seconds..."
                        ),
                        color=0xa80700
                    )
                else:
                    embed = discord.Embed(
                        title=":dagger: Murderer wins!",
                        description=(
                            "Only 1 player besides the murderer is still alive. "
                            "The murderer kills the remaining player and wins the game!\n\n\n"
                            "Game will end in 10 seconds..."
                        ),
                        color=0xa80700
                    )
                await self.mainChannel.send(embed=embed)
                await self.mainChannel.set_permissions(
                    self.role, read_messages=True, send_messages=True
                )
                self.victory = False
                if not self.debug:
                    await asyncio.sleep(10)
                await self.stopGame()

            elif len(self.players) == 3:
                if self.findRole("werewolf") is not None:
                    for player in self.players:
                        if hasattr(player, "nightChannel") and player.nightChannel is not None:
                            await player.nightChannel.set_permissions(
                                player.member, read_messages=False, send_messages=False
                            )
                        if hasattr(player, "roleChannel") and player.roleChannel is not None:
                            await player.roleChannel.set_permissions(
                                player.member, read_messages=False, send_messages=False
                            )
                    murderer = self.findRole("murderer")
                    if murderer is not None and getattr(murderer, "inLove", False):
                        embed = discord.Embed(
                            title=":dagger: :couple_with_heart: :wolf: Murderer, their lover and the werewolf win!",
                            description=(
                                "The murderer and werewolf killed everybody except the murderer's lover!\n\n\n"
                                "Game will end in 10 seconds..."
                            ),
                            color=0xa80700
                        )
                    else:
                        embed = discord.Embed(
                            title=":dagger: :wolf: Murderer and werewolf win!",
                            description=(
                                "The murderer and werewolf killed everybody!\n\n\n"
                                "Game will end in 10 seconds..."
                            ),
                            color=0xa80700
                        )
                    await self.mainChannel.send(embed=embed)
                    await self.mainChannel.set_permissions(
                        self.role, read_messages=True, send_messages=True
                    )
                    self.victory = False
                    if not self.debug:
                        await asyncio.sleep(10)
                    await self.stopGame()
        else:
            for player in self.players:
                if hasattr(player, "nightChannel") and player.nightChannel is not None:
                    await player.nightChannel.set_permissions(
                        player.member, read_messages=False, send_messages=False
                    )
                if hasattr(player, "roleChannel") and player.roleChannel is not None:
                    await player.roleChannel.set_permissions(
                        player.member, read_messages=False, send_messages=False
                    )

            await self.mainChannel.send(embed=discord.Embed(
                title=":tada: Victory!",
                description=(
                    "The murderer has been killed! Villagers won!\n\n"
                    "Game will end in 10 seconds..."
                ),
                color=0x00ff00
            ))
            await self.mainChannel.set_permissions(
                self.role, read_messages=True, send_messages=True
            )
            self.victory = True
            if not self.debug:
                await asyncio.sleep(10)
            await self.stopGame()

    async def stopGame(self):
        """Stop the game, update stats/XP, and clean up."""
        if not self.foolWin:
            if self.victory:
                embed = discord.Embed(
                    title=":tada: Villagers won!",
                    description="A game just ended because the murderer got killed!",
                    color=0x00ff00
                )
                for plr in self.allPlayers:
                    role_name = getattr(getattr(plr, "role", None), "name", None)
                    if role_name not in ["murderer", "werewolf", "fool"]:
                        setPlayerData(plr.member, "villagerWins", increase=1)
                for plr in self.players:
                    role_name = getattr(getattr(plr, "role", None), "name", None)
                    if role_name not in ["murderer", "werewolf", "fool"]:
                        objectives.addObjectiveProgress(plr.member, "villagerWinsNoDeath", 1)
            else:
                werewolf = self.findRole("werewolf")
                murderer = self.findRole("murderer")
                if werewolf is not None:
                    if murderer is not None and getattr(murderer, "inLove", False):
                        embed = discord.Embed(
                            title=":dagger: :couple_with_heart: :wolf: Murderer, their lover and the werewolf won!",
                            description="A game just ended because the murderer and werewolf killed everybody!",
                            color=0xff0000
                        )
                        if murderer.lover is not None:
                            setPlayerData(murderer.lover.member, "villagerWins", increase=1)
                    else:
                        embed = discord.Embed(
                            title=":dagger: :wolf: Murderer and werewolf won!",
                            description="A game just ended because the murderer and werewolf killed everybody!",
                            color=0xff0000
                        )
                    setPlayerData(werewolf.member, "werewolfWins", increase=1)
                else:
                    if murderer is not None and getattr(murderer, "inLove", False):
                        embed = discord.Embed(
                            title=":dagger: :couple_with_heart: Murderer and their lover won!",
                            description="A game just ended because the murderer killed everybody!",
                            color=0xff0000
                        )
                        if murderer.lover is not None:
                            setPlayerData(murderer.lover.member, "villagerWins", increase=1)
                    else:
                        embed = discord.Embed(
                            title=":dagger: Murderer won!",
                            description="A game just ended because the murderer killed everybody!",
                            color=0xff0000
                        )
                if murderer is not None:
                    setPlayerData(murderer.member, "murdererWins", increase=1)
                    objectives.addObjectiveProgress(murderer.member, "murdererWins", 1)
        else:
            embed = discord.Embed(
                title=":clown: Fool won!",
                description="A game just ended because the fool got executed",
                color=0xfff100
            )
            fool = self.findRole("fool")
            if fool is not None:
                setPlayerData(fool.member, "foolWins", increase=1)

        summary_value = (
            f":sunny: Day {self.day}\n"
            f":busts_in_silhouette: Total players: {len(self.allPlayers)}\n"
            f":bust_in_silhouette: Players remaining: {len(self.players)}\n\n"
        )
        embed.add_field(
            name="Game summary",
            value=summary_value,
            inline=False
        )
        rolelessPlayers = []
        for player in self.allPlayers:
            player_role = getattr(player, "role", None)
            role_name = getattr(player_role, "name", "none")
            if role_name != "none":
                fancy = getattr(player_role, "fancyName", role_name)
                embed.add_field(
                    name=f"{fancy}",
                    value=f"{player.member.mention}",
                    inline=True
                )
            else:
                rolelessPlayers.append(player)
            setPlayerData(player.member, "gamesPlayed", increase=1)

        rolelessPlayersFieldValue = " ".join(p.member.mention for p in rolelessPlayers)
        if rolelessPlayersFieldValue != "":
            embed.add_field(
                name=":bust_in_silhouette: no role",
                value=rolelessPlayersFieldValue,
                inline=True
            )

        use_summary = dataStorage.getGuildData(self.guild, "useSummaryEmbeds")
        if use_summary:
            summary_ch_id = dataStorage.getGuildData(self.guild, "summaryChannel")
            summaryChannel = self.guild.get_channel(summary_ch_id)
            if summaryChannel is not None:
                try:
                    await summaryChannel.send(embed=embed)
                except discord.HTTPException:
                    pass

        for plr in self.players:
            await objectives.addXP(plr.member, self.day * 5)
            plr_role = getattr(plr, "role", None)
            plr_role_name = getattr(plr_role, "name", None)
            is_murderer = plr_role_name == "murderer"
            is_werewolf = plr_role_name == "werewolf"
            is_fool = plr_role_name == "fool"
            murderer_won = not self.victory and is_murderer
            werewolf_won = not self.victory and is_werewolf
            fool_won = self.foolWin and is_fool
            if murderer_won or werewolf_won or fool_won:
                await objectives.addXP(plr.member, 20)
            elif self.victory and not is_murderer and not is_werewolf and not is_fool:
                await objectives.addXP(plr.member, 10)

        for plr in self.allPlayers:
            await objectives.checkForCompleteObjectives(plr.member)
            if self.guild != mainGuild:
                promo_sent = dataStorage.getPlayerData(
                    plr.member, "promotionalMessageSent", default=False
                )
                if not promo_sent:
                    dataStorage.setPlayerData(
                        plr.member, "promotionalMessageSent", value=True
                    )
                    embed = discord.Embed(
                        title="Thank you for playing Murder Mystery!",
                        description=(
                            "If you liked the game, I would highly "
                            "appreciate if you joined the discord server! "
                            "There you can also play the game with other "
                            "people as well as suggest new features, report "
                            "bugs, and more!\n\n"
                            "Also, give the bot a review on top.gg: "
                            "https://top.gg/bot/1452886075621249024\n\n"
                            "Thanks for playing!\n"
                            "-Murder Mystery's developer"
                        ),
                        color=0x00b8ff
                    )
                    thumb_url = (
                        "https://cdn.discordapp.com/attachments/"
                        "554234775590666251/863864464688676884/"
                        "blue-heart_1f499.png"
                    )
                    embed.set_thumbnail(url=thumb_url)
                    try:
                        await plr.member.send(embed=embed)
                        await plr.member.send(mainServerInvite)
                    except discord.HTTPException:
                        pass

        await self.cleanUp()

    async def cleanUp(self):
        """Clean up all game resources. A second call is a no-op."""
        if self._cleaned:
            return
        self._cleaned = True
        self._cancel_phase = True
        try:
            for m in list(getattr(self.guild, "members", [])):
                roles_to_remove = []
                game_role = getattr(self, "role", None)
                spectator_role = getattr(self, "spectatorRole", None)
                if game_role is not None and game_role in getattr(m, "roles", []):
                    roles_to_remove.append(game_role)
                if spectator_role is not None and spectator_role in getattr(m, "roles", []):
                    roles_to_remove.append(spectator_role)
                if roles_to_remove:
                    try:
                        await m.remove_roles(*roles_to_remove)
                    except Exception:
                        pass
        except Exception:
            pass

        for player in list(getattr(self, "players", [])):
            player.inGame = False
            if self.guild.id in allPlayers and player in allPlayers[self.guild.id]:
                allPlayers[self.guild.id].remove(player)

        for r in [getattr(self, "role", None), getattr(self, "spectatorRole", None)]:
            if r is not None:
                try:
                    await r.delete()
                except Exception:
                    pass

        for channel in list(getattr(self, "channels", [])):
            try:
                await channel.delete()
            except discord.HTTPException:
                pass

        category = getattr(self, "category", None)
        if category is not None:
            try:
                await category.delete()
            except discord.HTTPException:
                pass

        from core.manager import game_manager
        game_manager.remove_game(self)


# Alias for backward compatibility
game = Game
