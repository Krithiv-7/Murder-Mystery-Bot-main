"""All /slash commands - self-contained, no dependency on the mainGuild state."""
from types import SimpleNamespace

import discord

import dataStorage
from dataStorage import getPlayerData
import items
import objectives
import permissions
import setup
import tutorial
from core.game_state import currentGames, availableGames, allPlayers
from .client import client
from core.utils import getPlayer


# Slash commands
# Guard against accidental double-dispatch by tracking handled interaction IDs
_handled_interactions = set()

def _mark_handled(interaction: discord.Interaction) -> bool:
    iid = getattr(interaction, "id", None)
    if iid is None:
        return True  # proceed; no id available
    if iid in _handled_interactions:
        return False
    _handled_interactions.add(iid)
    return True
@client.tree.command(name="ping", description="Check bot latency")
async def ping(interaction: discord.Interaction):
    if not _mark_handled(interaction):
        return
    await interaction.response.send_message(f"Pong! {round(client.latency * 1000)} ms", ephemeral=True)


@client.tree.command(name="help", description="Show basic bot help")
async def slash_help(interaction: discord.Interaction):
    if not _mark_handled(interaction):
        return
    # Respect existing permission system for help
    try:
        allowed = permissions.memberHasPermission(interaction.user, "member.help")
    except Exception:
        allowed = True  # If permission check fails, default to allow showing help

    if not allowed:
        await interaction.response.send_message(":closed_lock_with_key: You don't have permission to view help.", ephemeral=True)
        return

    # Always show a concise help embed with the actual server prefix
    from core.version import __version__
    prefix = dataStorage.getGuildData(interaction.guild, "prefix", default="!")
    help_embed = discord.Embed(
        title=f"Murder Mystery Bot v{__version__}",
        color=0x00b8ff,
    )
    help_embed.add_field(name="Prefix", value=f"Current server prefix: {prefix}", inline=False)
    help_embed.add_field(
        name="Getting Started",
        value=(
            f"Use {prefix}help for detailed help or {prefix}advancedHelp for categories. "
            "Slash commands include /ping, /help, /setup, /create, /list, "
            "/join, /spectate, /stats, /level, /objective, and /balance."
        ),
        inline=False,
    )
    help_embed.add_field(
        name="Common Commands",
        value=f"{prefix}join, {prefix}list, {prefix}spectate [id], {prefix}objective, {prefix}level [@user]",
        inline=False,
    )

    await interaction.response.send_message(embed=help_embed, ephemeral=True)

    # If tutorial embeds are configured, send only the first as follow-up
    try:
        tutorial_embeds = tutorial.getTutorialEmbeds(interaction.guild).get("commands", [])
        if tutorial_embeds:
            await interaction.followup.send(embed=tutorial_embeds[0], ephemeral=True)
    except Exception:
        pass

@client.tree.command(name="create", description="Create a new lobby")
async def slash_create(interaction: discord.Interaction, debug: bool = False):
    if not _mark_handled(interaction):
        return
    has_debug_create = permissions.memberHasPermission(interaction.user, "debug.createGame")
    # Disallow creating while already in a lobby
    existing_player = getPlayer(interaction.user, interaction.guild)
    if existing_player is not None and existing_player.inGame:
        await interaction.response.send_message(
            ":x: You're already in a lobby. Leave it before creating a "
            "new one (use !leave).",
            ephemeral=True
        )
        return
    # Respect debug flag permission
    if debug and not has_debug_create:
        await interaction.response.send_message(
            ":closed_lock_with_key: You need debug permissions to create "
            "a debug lobby.",
            ephemeral=True
        )
        return
    from core.manager import game_manager
    if not game_manager.accepting_new_games:
        await interaction.response.send_message(
            ":x: The bot is shutting down and is not accepting new games.",
            ephemeral=True,
        )
        return
    game = await createNewGame(
        interaction.guild, debug and has_debug_create, reason="slash-create",
        channel=interaction.channel,
    )
    game.owner_id = interaction.user.id
    prefix_val = dataStorage.getGuildData(
        interaction.guild, 'prefix', default='!'
    )
    from commands.game_commands import HostChoiceView
    await interaction.response.send_message(
        f":white_check_mark: Lobby created! Code: {game.code}. You're the host - "
        f"share this code for others to join with {prefix_val}join {game.code}.\n"
        f"Choose whether to play or just spectate your lobby:",
        view=HostChoiceView(game, interaction.user),
        ephemeral=True
    )

@client.tree.command(name="list", description="List current lobbies")
async def slash_list(interaction: discord.Interaction):
    if not _mark_handled(interaction):
        return
    if not permissions.memberHasPermission(interaction.user, "member.list"):
        await interaction.response.send_message(
            ":closed_lock_with_key: You don't have permission to list "
            "lobbies.",
            ephemeral=True
        )
        return
    prefix_val = dataStorage.getGuildData(
        interaction.guild, 'prefix', default='!'
    )
    embed = discord.Embed(
        title="Currently running games",
        description=(
            f"Use {prefix_val}join <code> to join a lobby that hasn't "
            f"started yet.\nUse spectate <code> to watch a game."
        ),
        color=0x0088ff
    )
    from core.manager import game_manager
    for game in game_manager.get_games(interaction.guild.id):
        player_mentions = "".join(
            [str(p.member.mention) for p in game.players]
        )
        playerList = player_mentions or "There are no players in this game"
        embed.add_field(
            name=f"ID: {game.code}",
            value=(
                f"Phase: {game.phase}, day {game.day}, "
                f"players: {playerList}"
            )
        )
    await interaction.response.send_message(embed=embed, ephemeral=True)

@client.tree.command(name="join", description="Join a lobby by code")
async def slash_join(interaction: discord.Interaction, lobby_id: str):
    if not _mark_handled(interaction):
        return
    if not permissions.memberHasPermission(interaction.user, "member.join"):
        await interaction.response.send_message(
            ":closed_lock_with_key: You don't have permission to join.",
            ephemeral=True
        )
        return
    from core.lobby import JOIN_MESSAGES, join_block_reason, resolve_guild_game
    game_to_join = resolve_guild_game(interaction.guild, lobby_id)
    reason = join_block_reason(interaction.user, interaction.guild, game_to_join)
    if reason is not None:
        await interaction.response.send_message(JOIN_MESSAGES[reason], ephemeral=True)
        return
    await game_to_join.addPlayer(interaction.user)
    await interaction.response.send_message(
        f":white_check_mark: Joined lobby {game_to_join.code}.", ephemeral=True
    )

@client.tree.command(name="spectate", description="Spectate a game by code")
async def slash_spectate(interaction: discord.Interaction, lobby_id: str):
    if not _mark_handled(interaction):
        return
    perm = "member.spectate"
    if not permissions.memberHasPermission(interaction.user, perm):
        await interaction.response.send_message(
            ":closed_lock_with_key: You don't have permission to spectate.",
            ephemeral=True
        )
        return
    from core.lobby import resolve_guild_game
    game = resolve_guild_game(interaction.guild, lobby_id)
    if game is not None:
        await game.addSpectator(interaction.user)
        await interaction.response.send_message(
            f":white_check_mark: Spectating lobby {game.code}.",
            ephemeral=True
        )
    else:
        await interaction.response.send_message(
            ":x: Lobby not found.", ephemeral=True
        )


@client.tree.command(name="setup", description="Configure this server")
async def slash_setup(interaction: discord.Interaction):
    """Start the same permission-protected setup used by !setup."""
    if not _mark_handled(interaction):
        return
    if interaction.guild is None:
        await interaction.response.send_message(
            ":x: Setup can only be used inside a server.", ephemeral=True
        )
        return
    if not permissions.memberHasPermission(interaction.user, "admin.setup"):
        await interaction.response.send_message(
            ":closed_lock_with_key: You don't have permission to run setup.",
            ephemeral=True,
        )
        return
    games_running = bool(currentGames.get(interaction.guild.id))
    await setup.initializeSetup(interaction, games_running)


@client.tree.command(name="stats", description="Show player statistics")
async def slash_stats(
    interaction: discord.Interaction,
    member: discord.Member = None,
):
    if not _mark_handled(interaction):
        return
    if not permissions.memberHasPermission(interaction.user, "member.levels.stats"):
        await interaction.response.send_message(
            ":closed_lock_with_key: You don't have permission to view stats.",
            ephemeral=True,
        )
        return
    target = member or interaction.user
    embed = discord.Embed(
        title=f"Stats for {target.display_name}",
        description=(
            f":video_game: Games played: {getPlayerData(target, 'gamesPlayed', default=0)}\n\n"
            f":adult: Villager wins: {getPlayerData(target, 'villagerWins', default=0)}\n"
            f":dagger: Murderer wins: {getPlayerData(target, 'murdererWins', default=0)}\n"
            f":clown: Fool wins: {getPlayerData(target, 'foolWins', default=0)}\n"
            f":wolf: Werewolf wins: {getPlayerData(target, 'werewolfWins', default=0)}"
        ),
        color=0x00ff00,
    )
    await interaction.response.send_message(embed=embed, ephemeral=True)


@client.tree.command(name="level", description="Show player level")
async def slash_level(
    interaction: discord.Interaction,
    member: discord.Member = None,
):
    if not _mark_handled(interaction):
        return
    if not permissions.memberHasPermission(interaction.user, "member.levels.level"):
        await interaction.response.send_message(
            ":closed_lock_with_key: You don't have permission to view levels.",
            ephemeral=True,
        )
        return
    target = member or interaction.user
    player_level = getPlayerData(target, "level", default=1)
    current_xp = getPlayerData(target, "xp", default=0)
    xp_needed = objectives.getNextLevelRequirement(player_level) - current_xp
    embed = discord.Embed(
        title=f"{target.display_name} is level {player_level}",
        description=(
            f"{objectives.getXpProgressBar(target)}\n"
            f"{xp_needed} xp required for next level"
        ),
        color=0x00ff00,
    )
    await interaction.response.send_message(embed=embed, ephemeral=True)


@client.tree.command(name="objective", description="Show your objective")
async def slash_objective(interaction: discord.Interaction):
    if not _mark_handled(interaction):
        return
    if not permissions.memberHasPermission(interaction.user, "member.levels.objective"):
        await interaction.response.send_message(
            ":closed_lock_with_key: You don't have permission to view objectives.",
            ephemeral=True,
        )
        return
    if getPlayer(interaction.user, interaction.guild) is not None:
        await interaction.response.send_message(
            ":x: You can't view objective progress while in a game.",
            ephemeral=True,
        )
        return

    class ObjectiveContext:
        author = interaction.user

        async def send(self, *args, **kwargs):
            return await interaction.response.send_message(
                *args, ephemeral=True, **kwargs
            )

    await objectives.objectivesCommand(ObjectiveContext())


@client.tree.command(name="balance", description="Show your gold balance")
async def slash_balance(interaction: discord.Interaction):
    if not _mark_handled(interaction):
        return
    player = getPlayer(interaction.user, interaction.guild)
    if player is None:
        await interaction.response.send_message(
            ":x: You can only use this command while you're in a game.",
            ephemeral=True,
        )
        return
    await interaction.response.send_message(
        f":coin: You have {player.gold} gold.", ephemeral=True
    )


@client.tree.command(name="leave", description="Leave your current game")
async def slash_leave(interaction: discord.Interaction):
    if not _mark_handled(interaction):
        return
    player = getPlayer(interaction.user, interaction.guild)
    if player is None or not player.inGame:
        await interaction.response.send_message(
            ":x: You can only use this command while in a game.", ephemeral=True
        )
        return
    await player.game.removePlayer(player)
    await interaction.response.send_message(
        ":white_check_mark: You left the game.", ephemeral=True
    )


@client.tree.command(name="vote", description="Vote to execute a player")
async def slash_vote(interaction: discord.Interaction, member: discord.Member):
    if not _mark_handled(interaction):
        return
    player = getPlayer(interaction.user, interaction.guild)
    voted_player = getPlayer(member, interaction.guild)
    if player is None or voted_player is None or not player.inGame or not voted_player.inGame:
        await interaction.response.send_message(
            ":x: Both players must be in the same game.", ephemeral=True
        )
        return
    if player.game != voted_player.game or not player.game.voteTime:
        await interaction.response.send_message(
            ":x: Voting is not available for that player right now.", ephemeral=True
        )
        return
    if voted_player == player:
        await interaction.response.send_message(
            ":x: You can't vote for yourself.", ephemeral=True
        )
        return
    _, message = await player.game.record_vote(interaction.user, member)
    await interaction.response.send_message(message, ephemeral=True)


@client.tree.command(name="shop", description="View the nighttime shop")
async def slash_shop(interaction: discord.Interaction):
    if not _mark_handled(interaction):
        return
    player = getPlayer(interaction.user, interaction.guild)
    if player is None or not player.inGame:
        await interaction.response.send_message(
            ":x: You can only use this command while in a game.", ephemeral=True
        )
        return
    if not player.game.nightTime:
        await interaction.response.send_message(
            ":x: The shop is only available at night.", ephemeral=True
        )
        return
    broadcaster = any(p.role.name == "broadcaster" for p in player.game.players)
    embed = discord.Embed(
        title=f"Shop | :coin: {player.gold}",
        description="Use `/buy item` or `!buy item` to purchase an item.",
        color=0x00b8ff,
    )
    for item_class in items.getItems(
        broadcasterInGame=broadcaster, role=player.role.name
    ):
        item = item_class()
        embed.add_field(
            name=item.name,
            value=f"{item.description}\nCost: :coin: {item.cost}",
            inline=False,
        )
    await interaction.response.send_message(embed=embed, ephemeral=True)


class _SlashContext:
    """Small context adapter for existing item handlers."""

    def __init__(self, interaction):
        self.interaction = interaction
        self.author = interaction.user
        self.guild = interaction.guild
        self.channel = self
        self.message = SimpleNamespace(
            author=interaction.user,
            guild=interaction.guild,
            channel=self,
        )

    async def send(self, *args, **kwargs):
        return await self.interaction.followup.send(
            *args, ephemeral=True, **kwargs
        )


@client.tree.command(name="buy", description="Buy an item during the night")
async def slash_buy(interaction: discord.Interaction, item_id: str):
    if not _mark_handled(interaction):
        return
    player = getPlayer(interaction.user, interaction.guild)
    if player is None or not player.inGame or not player.game.nightTime:
        await interaction.response.send_message(
            ":x: You can only buy items during the night while in a game.",
            ephemeral=True,
        )
        return
    broadcaster = any(p.role.name == "broadcaster" for p in player.game.players)
    item_class = next(
        (
            item_type
            for item_type in items.getItems(
                broadcasterInGame=broadcaster, role=player.role.name
            )
            if item_type().id == item_id.lower()
        ),
        None,
    )
    if item_class is None:
        await interaction.response.send_message(
            ":x: That's not a valid item.", ephemeral=True
        )
        return
    await interaction.response.defer(ephemeral=True)
    await items.buy(item_class(), player, _SlashContext(interaction))


@client.tree.command(name="use", description="Use an item from your inventory")
async def slash_use(
    interaction: discord.Interaction,
    item_id: str,
    text: str = None,
    target: discord.Member = None,
):
    if not _mark_handled(interaction):
        return
    player = getPlayer(interaction.user, interaction.guild)
    if player is None or not player.inGame:
        await interaction.response.send_message(
            ":x: You can only use items while in a game.", ephemeral=True
        )
        return
    item = next(
        (owned_item for owned_item in player.inventory if owned_item.id == item_id.lower()),
        None,
    )
    if item is None:
        await interaction.response.send_message(
            ":x: That item is not in your inventory.", ephemeral=True
        )
        return
    argument = text
    player_target = getPlayer(target, interaction.guild) if target else None
    if item.needArg and item.needPlayerArg and player_target is None:
        await interaction.response.send_message(
            ":x: This item requires a target member.", ephemeral=True
        )
        return
    if item.needArg and not item.needPlayerArg and argument is None:
        await interaction.response.send_message(
            f"Usage: {item.usage}", ephemeral=True
        )
        return
    await interaction.response.defer(ephemeral=True)
    await item.use(_SlashContext(interaction), player_target or argument)


@client.tree.command(name="settings", description="View or change game settings")
async def slash_settings(
    interaction: discord.Interaction,
    setting: str = None,
    value: str = None,
):
    if not _mark_handled(interaction):
        return
    await interaction.response.defer(ephemeral=True)
    await settings.callback(_SlashContext(interaction), setting, value)


@client.tree.command(name="prefix", description="View or change the server prefix")
async def slash_prefix(interaction: discord.Interaction, new_prefix: str = None):
    if not _mark_handled(interaction):
        return
    await interaction.response.defer(ephemeral=True)
    await prefix.callback(_SlashContext(interaction), new_prefix)


@client.tree.command(name="whisper", description="Whisper to another player")
async def slash_whisper(interaction: discord.Interaction, member: discord.Member, message: str):
    if not _mark_handled(interaction):
        return
    player = getPlayer(interaction.user, interaction.guild)
    other_player = getPlayer(member, interaction.guild)
    if player is None or other_player is None or not player.inGame or not other_player.inGame:
        await interaction.response.send_message(":x: Both players must be in the same game.", ephemeral=True)
        return
    if other_player.game != player.game:
        await interaction.response.send_message(":x: That player is not in your game.", ephemeral=True)
        return
    if player.game.nightTime:
        await interaction.response.send_message(":x: You can't whisper during night time!", ephemeral=True)
        return
    try:
        await other_player.member.send(embed=discord.Embed(
            title=f":speech_balloon: Whisper from {player.member.display_name}",
            description=message,
            color=0x0088ff
        ))
    except discord.HTTPException:
        await interaction.response.send_message(
            ":x: Couldn't deliver the whisper - they may have DMs disabled.", ephemeral=True
        )
        return
    await interaction.response.send_message(
        f":white_check_mark: Whisper sent to {other_player.member.display_name}", ephemeral=True
    )



async def _slash_debug_game(interaction, permission, lobby_id, attribute, value=None):
    if not await _slash_admin_check(interaction, permission):
        return
    from core.manager import game_manager
    game = game_manager.get_game(interaction.guild.id, lobby_id)
    if game is None:
        await interaction.response.send_message(":x: Lobby not found.", ephemeral=True)
        return
    if value is None:
        setattr(game, attribute, True)
    else:
        setattr(game, attribute, value)
    await interaction.response.send_message(
        f":white_check_mark: Lobby {lobby_id} updated.", ephemeral=True
    )


@client.tree.command(name="skip-votes", description="Skip voting time")
async def slash_skip_votes(interaction: discord.Interaction, lobby_id: str):
    if not _mark_handled(interaction):
        return
    await _slash_debug_game(interaction, "debug.game.skipVotes", lobby_id, "skipVotingTime")


@client.tree.command(name="skip-night", description="Skip the current night")
async def slash_skip_night(interaction: discord.Interaction, lobby_id: str):
    if not _mark_handled(interaction):
        return
    await _slash_debug_game(interaction, "debug.game.skipNight", lobby_id, "skipNight")


@client.tree.command(name="set-weather", description="Set weather intensity")
async def slash_set_weather(interaction: discord.Interaction, lobby_id: str, intensity: int):
    if not _mark_handled(interaction):
        return
    await _slash_debug_game(
        interaction, "debug.game.setWeather", lobby_id, "weatherIntensity", intensity
    )


@client.tree.command(name="set-moon", description="Set moon level")
async def slash_set_moon(interaction: discord.Interaction, lobby_id: str, level: int):
    if not _mark_handled(interaction):
        return
    await _slash_debug_game(interaction, "debug.game.setMoon", lobby_id, "moon", level)


@client.tree.command(name="force-start", description="Force-start your lobby")
async def slash_force_start(interaction: discord.Interaction):
    if not _mark_handled(interaction):
        return
    player = getPlayer(interaction.user, interaction.guild)
    if player is None or not player.inGame or player.game.started:
        await interaction.response.send_message(
            ":x: You need to own an active lobby.", ephemeral=True
        )
        return
    is_owner = getattr(player.game, "owner_id", None) == interaction.user.id
    is_admin = permissions.memberHasPermission(
        interaction.user, "admin.game.startGame"
    )
    if not (is_owner or is_admin):
        await interaction.response.send_message(
            ":closed_lock_with_key: Only the lobby owner or an admin can force start it.",
            ephemeral=True,
        )
        return
    player.game.startNow = True
    await interaction.response.send_message(
        ":white_check_mark: The lobby will start shortly.", ephemeral=True
    )


async def _slash_admin_check(interaction, permission):
    if not permissions.memberHasPermission(interaction.user, permission):
        await interaction.response.send_message(
            ":closed_lock_with_key: You don't have permission to use this command.",
            ephemeral=True,
        )
        return False
    return True


@client.tree.command(name="start-game", description="Start a lobby immediately")
async def slash_start_game(interaction: discord.Interaction, lobby_id: str):
    if not _mark_handled(interaction):
        return
    from core.manager import game_manager
    game = game_manager.get_game(interaction.guild.id, lobby_id)
    if game is None:
        await interaction.response.send_message(":x: Lobby not found.", ephemeral=True)
        return
    if getattr(game, "owner_id", None) != interaction.user.id and not permissions.memberHasPermission(
        interaction.user, "admin.game.startGame"
    ):
        await interaction.response.send_message(
            ":closed_lock_with_key: Only the lobby owner or an admin can start it.",
            ephemeral=True,
        )
        return
    game.startNow = True
    await interaction.response.send_message(
        f":white_check_mark: Lobby {lobby_id} will start shortly.", ephemeral=True
    )


@client.tree.command(name="cleanup", description="End all running games")
async def slash_cleanup(interaction: discord.Interaction):
    if not _mark_handled(interaction):
        return
    if not await _slash_admin_check(interaction, "admin.endAllGames"):
        return
    for game in list(currentGames.get(interaction.guild.id, [])):
        await game.cleanUp()
    await interaction.response.send_message(
        ":white_check_mark: All games have been stopped.", ephemeral=True
    )


@client.tree.command(name="end-game", description="End one running game")
async def slash_end_game(interaction: discord.Interaction, lobby_id: str):
    if not _mark_handled(interaction):
        return
    from core.manager import game_manager
    game = game_manager.get_game(interaction.guild.id, lobby_id)
    if game is None:
        await interaction.response.send_message(":x: Lobby not found.", ephemeral=True)
        return
    if getattr(game, "owner_id", None) != interaction.user.id and not permissions.memberHasPermission(
        interaction.user, "admin.endGame"
    ):
        await interaction.response.send_message(
            ":closed_lock_with_key: Only the lobby's host or an admin can end it.",
            ephemeral=True,
        )
        return
    await game.cleanUp()
    await interaction.response.send_message(
        f":white_check_mark: Lobby {lobby_id} has been ended.", ephemeral=True
    )


@client.tree.command(name="kick", description="Remove a player from a game")
async def slash_kick(interaction: discord.Interaction, member: discord.Member):
    if not _mark_handled(interaction):
        return
    if not await _slash_admin_check(interaction, "admin.game.kick"):
        return
    player = getPlayer(member, interaction.guild)
    if player is None or not player.inGame:
        await interaction.response.send_message(":x: Player not found in a game.", ephemeral=True)
        return
    await player.game.removePlayer(player)
    await interaction.response.send_message(
        f":white_check_mark: Removed {member.display_name} from the game.", ephemeral=True
    )


@client.tree.command(name="give-gold", description="Give gold to a player")
async def slash_give_gold(interaction: discord.Interaction, member: discord.Member, amount: int):
    if not _mark_handled(interaction):
        return
    if not await _slash_admin_check(interaction, "admin.game.giveGold"):
        return
    player = getPlayer(member, interaction.guild)
    if player is None or not player.inGame:
        await interaction.response.send_message(":x: Player not found in a game.", ephemeral=True)
        return
    player.gold += amount
    await interaction.response.send_message(
        f":white_check_mark: Gave :coin: {amount} gold to {member.mention}.",
        ephemeral=True,
    )


@client.tree.command(name="reset-state", description="Reset this server's bot state")
async def slash_reset_state(interaction: discord.Interaction):
    if not _mark_handled(interaction):
        return
    if not await _slash_admin_check(interaction, "admin.resetState"):
        return
    guild_id = interaction.guild.id
    for game in list(currentGames.get(guild_id, [])):
        await game.cleanUp()
    currentGames[guild_id] = []
    availableGames[guild_id] = []
    allPlayers[guild_id] = []
    if guild_id in dataStorage.cache:
        dataStorage.cache.pop(guild_id, None)
    await interaction.response.send_message(
        ":white_check_mark: Server state reset.", ephemeral=True
    )


