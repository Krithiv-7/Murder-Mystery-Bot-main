"""Master settings panel: active games, command toggles, prefix, roles."""
import discord
from discord import app_commands
from discord.ext import commands

import dataStorage
import permissions
from core.game_state import currentGames

TOGGLEABLE_COMMANDS = [
    "join", "list", "spectate", "createGame", "vote", "shop", "buy", "use",
    "leave", "whisper", "stats", "level", "objective", "balance",
]


def _is_admin(user) -> bool:
    return permissions.memberHasPermission(user, "admin.*")


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
            for name in TOGGLEABLE_COMMANDS
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
            label=f"End lobby #{idx}", style=discord.ButtonStyle.danger, row=idx % 5
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
        games = currentGames.get(self.guild.id, [])
        embed = discord.Embed(title=":video_game: Active games", color=0x00b8ff)
        if not games:
            embed.description = "No games are currently running."
        else:
            for idx, game in enumerate(games):
                embed.add_field(
                    name=f"Lobby #{idx}",
                    value=(
                        f"Players: {len(game.players)} | Started: {game.started} | "
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
                description="Manage active games, commands, prefix, and permissions.",
                color=0x00b8ff,
            ),
            view=MasterSettingsView(ctx.guild, ctx.author.id),
        )

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


async def setup(client):
    """Setup function for cog."""
    await client.add_cog(SettingsPanelCommands(client))
