"""Game-related commands for Murder Mystery Bot."""
import discord
from discord.ext import commands

import dataStorage
import permissions
from core.game_state import currentGames
from core.lobby import JOIN_MESSAGES, join_block_reason, resolve_guild_game
from core.manager import game_manager
from core.utils import getPlayer, isSpectating


class HostChoiceView(discord.ui.View):
    """Lets a lobby's host pick to play or spectate their own game.

    Hosts are never auto-joined as players; they get an explicit choice,
    defaulting to "Join & Play" if they don't respond in time.
    """

    def __init__(self, game, host_member):
        super().__init__(timeout=60)
        self.game = game
        self.host_member = host_member
        self.decided = False

    async def interaction_check(self, interaction):
        if interaction.user.id != self.host_member.id:
            await interaction.response.send_message(
                "Only the host who created this lobby can use these buttons.",
                ephemeral=True,
            )
            return False
        return True

    @discord.ui.button(label="Join & Play", style=discord.ButtonStyle.success, emoji="\u2705")
    async def join_button(self, interaction, button):
        self.decided = True
        await self.game.addPlayer(self.host_member)
        for item in self.children:
            item.disabled = True
        await interaction.response.edit_message(
            content=":white_check_mark: You joined your lobby as a player.",
            view=self,
        )
        self.stop()

    @discord.ui.button(label="Spectate instead", style=discord.ButtonStyle.secondary, emoji="\U0001F441")
    async def spectate_button(self, interaction, button):
        self.decided = True
        await self.game.addSpectator(self.host_member)
        for item in self.children:
            item.disabled = True
        await interaction.response.edit_message(
            content=":eye: You're now spectating your own lobby.",
            view=self,
        )
        self.stop()

    async def on_timeout(self):
        if not self.decided:
            try:
                await self.game.addPlayer(self.host_member)
            except Exception:
                pass
        for item in self.children:
            item.disabled = True


class LobbyView(discord.ui.View):
    """Dropdown and buttons for selecting and entering a game lobby."""

    def __init__(self, author, games):
        super().__init__(timeout=180)
        self.author_id = author.id
        self.games = games
        self.selected_code = None
        options = [
            discord.SelectOption(
                label=f"Lobby {game.code}",
                description=(
                    f"{len(game.players)} player(s) - "
                    f"{'started' if game.started else 'waiting'}"
                ),
                value=game.code,
            )
            for game in games
        ]
        lobby_select = discord.ui.Select(
            placeholder="Choose a lobby",
            options=options[:25],
            min_values=1,
            max_values=1,
        )
        lobby_select.callback = self.select_lobby
        self.add_item(lobby_select)

    async def interaction_check(self, interaction):
        if interaction.user.id != self.author_id:
            await interaction.response.send_message(
                "Only the person who requested this lobby list can use it.",
                ephemeral=True,
            )
            return False
        return True

    async def select_lobby(self, interaction):
        self.selected_code = interaction.data["values"][0]
        await interaction.response.send_message(
            f"Lobby {self.selected_code} selected. Choose Join or Spectate.",
            ephemeral=True,
        )

    async def _selected_game(self, interaction):
        if self.selected_code is None:
            await interaction.response.send_message(
                "Choose a lobby first.", ephemeral=True
            )
            return None
        game = next((item for item in self.games if item.code == self.selected_code), None)
        if game is None:
            await interaction.response.send_message(
                "That lobby is no longer available.", ephemeral=True
            )
            return None
        return game

    @discord.ui.button(label="Join", style=discord.ButtonStyle.success, emoji="✅")
    async def join_lobby(self, interaction, button):
        game = await self._selected_game(interaction)
        if game is None:
            return
        reason = join_block_reason(interaction.user, interaction.guild, game)
        if reason is not None:
            await interaction.response.send_message(JOIN_MESSAGES[reason], ephemeral=True)
            return
        await game.addPlayer(interaction.user)
        await interaction.response.send_message("You joined the lobby.", ephemeral=True)

    @discord.ui.button(label="Spectate", style=discord.ButtonStyle.secondary, emoji="👁️")
    async def spectate_lobby(self, interaction, button):
        game = await self._selected_game(interaction)
        if game is None:
            return
        if isSpectating(interaction.user, interaction.guild):
            await interaction.response.send_message("You are already spectating.", ephemeral=True)
            return
        await game.addSpectator(interaction.user)
        await interaction.response.send_message("You are now spectating.", ephemeral=True)


class GameCommands(commands.Cog):
    """Commands related to game management."""

    def __init__(self, client):
        self.client = client

    @staticmethod
    def _error_embed(title, description, color=0xff0000):
        return discord.Embed(title=title, description=description, color=color)

    @staticmethod
    def _parse_lobby_code(args):
        for token in args:
            if token.lower() == "-overwriteadminwarning":
                continue
            return token
        return None

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
        tokens = list(args) if args else []
        overwrite_admin = any(
            token.lower() == "-overwriteadminwarning" for token in tokens
        )
        index_str = self._parse_lobby_code(tokens)

        allowed_to_run = True
        join_channel = guild.get_channel(
            dataStorage.getGuildData(ctx.guild, "joinChannel")
        )
        is_admin = ctx.message.author.guild_permissions.administrator

        if (not is_admin) or overwrite_admin:
            if dataStorage.getGuildData(ctx.guild, "useJoinChannel"):
                if join_channel is not None:
                    if channel.id == dataStorage.getGuildData(ctx.guild, "joinChannel"):
                        try:
                            await ctx.message.delete()
                        except discord.HTTPException:
                            pass
                    else:
                        await ctx.send(embed=self._error_embed(
                            ":x: You can't use that command here!",
                            f"Use {join_channel.mention}"
                        ))
                        allowed_to_run = False

            if allowed_to_run:
                if index_str is None:
                    await ctx.send(embed=self._error_embed(
                        ":x: Please provide a lobby code",
                        f"Use {prefix}list to find lobby codes, then run "
                        f"{prefix}join <code>. To create a lobby, use "
                        f"{prefix}create."
                    ))
                    return

                game_to_join = resolve_guild_game(guild, index_str)
                reason = join_block_reason(author, guild, game_to_join)
                if reason == "not_found":
                    await ctx.send(embed=self._error_embed(
                        ":x: Lobby not found",
                        f"Use {prefix}list to find lobby codes such as MM-7F2A."
                    ))
                    return
                if reason == "already_in_game":
                    await channel.send(embed=self._error_embed(
                        "You are already in a game!",
                        "Leave your current game first.",
                        color=0xff000d,
                    ))
                    return
                if reason == "spectating":
                    await channel.send(embed=self._error_embed(
                        "You can't join while spectating!",
                        "Use !spectate to stop spectating first."
                    ))
                    return
                if reason == "started":
                    await ctx.send(embed=self._error_embed(
                        ":x: This lobby has already started",
                        f"Join an available lobby or create a new one with {prefix}create."
                    ))
                    return
                if reason == "full":
                    await ctx.send(embed=self._error_embed(
                        ":x: This lobby is full",
                        "Choose another lobby or create a new one."
                    ))
                    return
                if reason == "offline":
                    await channel.send(embed=self._error_embed(
                        "You can't play if your status is offline!",
                        "Change your status and try again."
                    ))
                    return

                await game_to_join.addPlayer(author)

                confirm_embed = discord.Embed(
                    title=":white_check_mark: You joined lobby!",
                    description=(
                        f"Lobby: {game_to_join.code} | "
                        f"Players: {len(game_to_join.players)}"
                    ),
                    color=0x00ff00
                )
                try:
                    await author.send(embed=confirm_embed)
                except discord.HTTPException:
                    pass

        else:
            embed = discord.Embed(
                title=":warning: You have administrator permissions",
                description=(
                    "This game hides channels from other players. "
                    "With admin perms, you can see all channels.\n\n"
                    "**Use an alt account without admin to play.**\n\n"
                    f"Override: `{prefix}join <code> -overwriteAdminWarning`"
                ),
                color=0xfff100
            )
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
            
        games = currentGames.get(ctx.guild.id, [])
        embed = discord.Embed(
            title="Currently running games",
            description=(
                "Choose a lobby below, then use Join or Spectate. "
                "The text commands remain available as a fallback."
            ),
            color=0x0088ff
        )
        
        if ctx.guild.id not in currentGames:
            currentGames[ctx.guild.id] = []
            
        for game in games:
            playerList = ""
            for player in game.players:
                playerList = playerList + str(player.member.mention)

            if playerList == "":
                playerList = "There are no players in this game"

            embed.add_field(
                name=f"ID: {game.code}",
                value=(
                    f"Phase: {game.phase}, day {game.day}, players: {playerList}"
                ),
            )

        view = LobbyView(ctx.author, games) if games else None
        await ctx.send(embed=embed, view=view)

    @commands.command()
    @commands.cooldown(2, 10, commands.BucketType.user)
    async def spectate(self, ctx, indexStr=None):
        """Spectate a game."""
        if not await permissions.hasPermission(ctx, "member.spectate"):
            return
            
        from core.game_state import joiningChannel
        
        if not isSpectating(ctx.author, ctx.guild):
            games = game_manager.get_games(ctx.guild.id)
            if indexStr is None:
                if len(games) == 1:
                    indexStr = games[0].code
                else:
                    if ctx.channel != joiningChannel:
                        await ctx.send(embed=discord.Embed(
                            title="Please enter a lobby code",
                            description="To get a lobby code, type !list.",
                            color=0xff0000
                        ))
                        return

            player = getPlayer(ctx.author, ctx.message.guild)
            if player is None:
                game = resolve_guild_game(ctx.guild, indexStr)
                if game is not None:
                    await game.addSpectator(ctx.author)
                    if ctx.channel != joiningChannel:
                        await ctx.send(embed=discord.Embed(
                            title="You are now spectating a game",
                            description=(
                                f"Watching {game.code}. "
                                "To stop spectating, type !spectate again."
                            ),
                            color=0x0088ff
                        ))
                else:
                    if ctx.channel != joiningChannel:
                        await ctx.send(embed=discord.Embed(
                            title=":x: That game doesn't exist!",
                            description="Please enter a valid lobby code."
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

    @commands.command(aliases=["create"])
    @commands.cooldown(2, 30, commands.BucketType.user)
    async def createGame(self, ctx, debugStr="False"):
        """Create a new game lobby."""
        existing_player = getPlayer(ctx.author, ctx.guild)
        if existing_player is not None and existing_player.inGame:
            await ctx.send(embed=discord.Embed(
                title=":x: You're already in a lobby",
                description="Leave your current lobby before creating a new one (use !leave).",
                color=0xff0000
            ))
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

        if not game_manager.accepting_new_games:
            await ctx.send(":x: The bot is shutting down and is not accepting new games.")
            return

        from core.utils import createNewGame
        game = await createNewGame(
            ctx.message.guild, debug, reason="prefix-create", channel=ctx.channel
        )
        game.owner_id = ctx.author.id

        prefix = dataStorage.getGuildData(ctx.guild, 'prefix', default='!')
        if not debug:
            embed = discord.Embed(
                title="A new lobby has been created! You're the host.",
                description=(
                    f"Lobby code: {game.code}. Share this code so others can join with "
                    f"{prefix}join {game.code}\n\n"
                    "Choose whether to play or just spectate your lobby:"
                )
            )
        else:
            embed = discord.Embed(
                title="A new lobby has been created in debugging mode!",
                description=f"Lobby code: {game.code}. Choose whether to play or spectate:"
            )
        await ctx.send(embed=embed, view=HostChoiceView(game, ctx.author))


async def setup(client):
    """Setup function for cog."""
    await client.add_cog(GameCommands(client))
