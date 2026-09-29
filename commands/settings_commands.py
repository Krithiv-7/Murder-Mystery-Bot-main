"""Master settings panel: active games, command toggles, prefix, roles."""
import discord
from discord import app_commands
from discord.ext import commands

import dataStorage
import permissions
from core.commands_meta import disableable_command_names
from core.config import GAME_DEFAULTS
from core.manager import game_manager
from core.runtime import status_snapshot


def _is_admin(user) -> bool:
    return permissions.memberHasPermission(user, "admin.*")


class GameSettingsModal(discord.ui.Modal, title="Game settings"):
    min_players = discord.ui.TextInput(label="Minimum players", max_length=3)
    max_players = discord.ui.TextInput(label="Maximum players", max_length=3)
    pre_game = discord.ui.TextInput(label="Pre-game timer (seconds)", max_length=5)
    voting = discord.ui.TextInput(label="Voting timer (seconds)", max_length=5)
    night = discord.ui.TextInput(label="Night timer (seconds)", max_length=5)

    def __init__(self, guild):
        super().__init__()
        self.guild = guild
        self.min_players.default = str(
            dataStorage.getGuildData(guild, "minPlayers", default=GAME_DEFAULTS["minPlayers"])
        )
        self.max_players.default = str(
            dataStorage.getGuildData(guild, "maxPlayers", default=GAME_DEFAULTS["maxPlayers"])
        )
        self.pre_game.default = str(
            dataStorage.getGuildData(guild, "preGameTimer", default=GAME_DEFAULTS["preGameTimer"])
        )
        self.voting.default = str(
            dataStorage.getGuildData(guild, "votingTime", default=GAME_DEFAULTS["votingTime"])
        )
        self.night.default = str(
            dataStorage.getGuildData(guild, "nightTimeTimer", default=GAME_DEFAULTS["nightTimeTimer"])
        )

    async def on_submit(self, interaction: discord.Interaction):
        try:
            values = {
                "minPlayers": int(str(self.min_players)),
                "maxPlayers": int(str(self.max_players)),
                "preGameTimer": int(str(self.pre_game)),
                "votingTime": int(str(self.voting)),
                "nightTimeTimer": int(str(self.night)),
            }
        except ValueError:
            await interaction.response.send_message(
                ":x: Every setting must be a whole number.", ephemeral=True
            )
            return
        if values["minPlayers"] < 3 or values["maxPlayers"] < values["minPlayers"]:
            await interaction.response.send_message(
                ":x: Maximum players must be at least the minimum, and the minimum must be at least 3.",
                ephemeral=True,
            )
            return
        if min(values["preGameTimer"], values["votingTime"], values["nightTimeTimer"]) < 5:
            await interaction.response.send_message(
                ":x: Timers must be at least 5 seconds.", ephemeral=True
            )
            return
        for key, value in values.items():
            dataStorage.setGuildData(self.guild, key, value=value)
        await interaction.response.send_message(
            ":white_check_mark: Game settings saved.", ephemeral=True
        )


class PrefixModal(discord.ui.Modal, title="Change server prefix"):
    new_prefix = discord.ui.TextInput(label="New prefix", max_length=7, min_length=1)

    def __init__(self, guild):
        super().__init__()
        self.guild = guild

    async def on_submit(self, interaction: discord.Interaction):
        value = str(self.new_prefix).strip()
        dataStorage.setGuildData(self.guild, "prefix", value=value)
        await interaction.response.send_message(
            f":white_check_mark: Prefix updated to `{value}`.", ephemeral=True
        )


class CommandToggleSelect(discord.ui.Select):
    """Multi-select of prefix commands to disable server-wide."""

    def __init__(self, guild):
        self.guild = guild
        disabled = dataStorage.getGuildData(guild, "disabledCommands", default=[])
        options = [
            discord.SelectOption(
                label=name,
                value=name,
                description="Currently disabled" if name in disabled else "Currently enabled",
                default=name in disabled,
            )
            for name in disableable_command_names()
        ]
        super().__init__(
            placeholder="Select commands to DISABLE (unselected = enabled)",
            options=options,
            min_values=0,
            max_values=len(options),
        )

    async def callback(self, interaction: discord.Interaction):
        dataStorage.setGuildData(self.guild, "disabledCommands", value=list(self.values))
        await interaction.response.send_message(
            f":white_check_mark: Disabled commands: {', '.join(self.values) or 'none'}",
            ephemeral=True,
        )


class GameEndButton(discord.ui.Button):
    def __init__(self, game, idx):
        super().__init__(
            label=f"End {game.code}",
            style=discord.ButtonStyle.danger,
            row=idx % 5,
        )
        self.game = game

    async def callback(self, interaction: discord.Interaction):
        await self.game.cleanUp()
        await interaction.response.send_message(":white_check_mark: Lobby ended.", ephemeral=True)


class MasterSettingsView(discord.ui.View):
    """Paginated admin-only settings panel."""

    def __init__(self, guild, author_id):
        super().__init__(timeout=180)
        self.guild = guild
        self.author_id = author_id

    async def interaction_check(self, interaction):
        if interaction.user.id != self.author_id and not _is_admin(interaction.user):
            await interaction.response.send_message(
                "Only an admin can use this panel.", ephemeral=True
            )
            return False
        return True

    @discord.ui.button(label="Active games", style=discord.ButtonStyle.primary, emoji="\U0001F3AE")
    async def show_games(self, interaction, button):
        games = game_manager.get_games(self.guild.id)
        embed = discord.Embed(title=":video_game: Active games", color=0x00b8ff)
        if not games:
            embed.description = "No games are currently running."
        else:
            for game in games:
                embed.add_field(
                    name=f"Lobby {game.code}",
                    value=(
                        f"Players: {len(game.players)} | Phase: {game.phase} | "
                        f"Day: {game.day} | Host: <@{getattr(game, 'owner_id', None)}>"
                    ),
                    inline=False,
                )
        view = discord.ui.View(timeout=60)
        for idx, game in enumerate(games[:20]):
            view.add_item(GameEndButton(game, idx))
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

    @discord.ui.button(label="Toggle commands", style=discord.ButtonStyle.secondary, emoji="\U0001F9E9")
    async def toggle_commands(self, interaction, button):
        view = discord.ui.View(timeout=60)
        view.add_item(CommandToggleSelect(self.guild))
        await interaction.response.send_message(
            "Choose which commands should be disabled on this server:",
            view=view,
            ephemeral=True,
        )

    @discord.ui.button(label="Set prefix", style=discord.ButtonStyle.secondary, emoji="\U0001F524")
    async def set_prefix(self, interaction, button):
        await interaction.response.send_modal(PrefixModal(self.guild))

    @discord.ui.button(label="Game settings", style=discord.ButtonStyle.secondary, emoji="\u23F1")
    async def game_settings(self, interaction, button):
        await interaction.response.send_modal(GameSettingsModal(self.guild))

    @discord.ui.button(label="Roles & permissions", style=discord.ButtonStyle.secondary, emoji="\U0001F6E1")
    async def roles_help(self, interaction, button):
        prefix = dataStorage.getGuildData(self.guild, "prefix", default="!")
        await interaction.response.send_message(
            embed=discord.Embed(
                title=":shield: Managing roles & users",
                description=(
                    f"Use `{prefix}addPermission <member/role> <permission>` and "
                    f"`{prefix}removePermission <member/role> <permission>` to grant "
                    f"or revoke access. Use `{prefix}permissions [member/role]` to "
                    "view current permissions."
                ),
                color=0x00b8ff,
            ),
            ephemeral=True,
        )


class SettingsPanelCommands(commands.Cog):
    """Master settings entry point (admin-only)."""

    def __init__(self, client):
        self.client = client

    @commands.command(aliases=["mastersettings", "panel", "adminpanel"])
    async def settingspanel(self, ctx):
        """Open the admin-only master settings panel."""
        if not _is_admin(ctx.author):
            await ctx.send(embed=discord.Embed(
                title=":closed_lock_with_key: Admins only",
                description="This panel is restricted to server admins.",
                color=0xff0000,
            ))
            return
        await ctx.send(
            embed=discord.Embed(
                title=":gear: Master settings",
                description="Manage active games, timers, commands, prefix, and permissions.",
                color=0x00b8ff,
            ),
            view=MasterSettingsView(ctx.guild, ctx.author.id),
        )

    @commands.command()
    async def status(self, ctx):
        """Show bot health. Restricted to administrators."""
        if not _is_admin(ctx.author):
            await ctx.send(":closed_lock_with_key: This command is restricted to server admins.")
            return
        await ctx.send(embed=_status_embed(self.client))

    @app_commands.command(
        name="settingspanel",
        description="Open the master settings panel (admin-only)",
    )
    async def slash_settingspanel(self, interaction: discord.Interaction):
        if not _is_admin(interaction.user):
            await interaction.response.send_message(
                ":closed_lock_with_key: This panel is restricted to server admins.",
                ephemeral=True,
            )
            return
        await interaction.response.send_message(
            embed=discord.Embed(
                title=":gear: Master settings",
                description="Manage active games, commands, prefix, and permissions.",
                color=0x00b8ff,
            ),
            view=MasterSettingsView(interaction.guild, interaction.user.id),
            ephemeral=True,
        )

    @app_commands.command(name="status", description="Show bot status (admin-only)")
    async def slash_status(self, interaction: discord.Interaction):
        if not _is_admin(interaction.user):
            await interaction.response.send_message(
                ":closed_lock_with_key: This command is restricted to server admins.",
                ephemeral=True,
            )
            return
        await interaction.response.send_message(
            embed=_status_embed(interaction.client), ephemeral=True
        )


def _status_embed(client):
    snapshot = status_snapshot(client)
    embed = discord.Embed(
        title=f"Murder Mystery Bot v{snapshot['version']}",
        color=0x00b8ff,
    )
    embed.add_field(name="Status", value=snapshot["status"], inline=True)
    embed.add_field(name="Latency", value=snapshot["latency"], inline=True)
    embed.add_field(name="Uptime", value=snapshot["uptime"], inline=True)
    embed.add_field(name="Guilds", value=str(snapshot["guilds"]), inline=True)
    embed.add_field(name="Active games", value=str(snapshot["games"]), inline=True)
    embed.add_field(name="Active players", value=str(snapshot["players"]), inline=True)
    embed.add_field(name="Database", value=snapshot["database"], inline=True)
    return embed


async def setup(client):
    """Setup function for cog."""
    await client.add_cog(SettingsPanelCommands(client))
