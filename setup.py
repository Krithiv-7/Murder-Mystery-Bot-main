import discord
import dataStorage
import permissions
from core.config import GAME_DEFAULTS

class SetupView(discord.ui.View):
    """Component-based setup controls with no channel provisioning."""

    def __init__(self, author_id):
        super().__init__(timeout=300)
        self.author_id = author_id

    async def interaction_check(self, interaction):
        if interaction.user.id != self.author_id:
            await interaction.response.send_message(
                "Only the administrator who started setup can use these controls.",
                ephemeral=True,
            )
            return False
        return True

    async def _begin_role_setup(self, interaction, use_summary):
        guild = interaction.guild
        dataStorage.setGuildData(guild, "useSummaryEmbeds", value=use_summary)
        dataStorage.setGuildData(
            guild,
            "summaryChannel",
            value=interaction.channel.id if use_summary else None,
        )
        dataStorage.setGuildData(guild, "setupProgress", value=1)
        dataStorage.setGuildData(guild, "awaitingSetupMessage", value=True)
        await interaction.response.send_message(
            embed=discord.Embed(
                title=":shield: Choose administrator roles",
                description=(
                    "Mention every role that may use admin commands in one message. "
                    "Say `skip` for server administrators only, or `cancel` to stop."
                ),
                color=0x00b8ff,
            )
        )
        self.stop()

    @discord.ui.button(
        label="Use this channel for summaries",
        style=discord.ButtonStyle.primary,
        emoji="📊",
    )
    async def enable_summary(self, interaction, button):
        await self._begin_role_setup(interaction, True)

    @discord.ui.button(
        label="Disable summaries",
        style=discord.ButtonStyle.secondary,
        emoji="🔕",
    )
    async def disable_summary(self, interaction, button):
        await self._begin_role_setup(interaction, False)

    @discord.ui.button(
        label="Cancel",
        style=discord.ButtonStyle.danger,
        emoji="✖️",
    )
    async def cancel_setup(self, interaction, button):
        dataStorage.setGuildData(interaction.guild, "setupStarted", value=False)
        dataStorage.setGuildData(interaction.guild, "awaitingSetupMessage", value=False)
        await interaction.response.send_message("Setup cancelled.", ephemeral=True)
        self.stop()

async def processSetupMessage(message: discord.Message):
    if not dataStorage.getGuildData(message.guild, "setupStarted", default=False):
        return
    if dataStorage.getGuildData(message.guild, "setupProgress") != 1:
        return

    if message.content.lower().strip() == "cancel":
        dataStorage.setGuildData(message.guild, "setupStarted", value=False)
        dataStorage.setGuildData(message.guild, "awaitingSetupMessage", value=False)
        await message.channel.send("Setup cancelled.")
        return

    if message.raw_role_mentions:
        for role_id in message.raw_role_mentions:
            admin_role = message.guild.get_role(role_id)
            if admin_role is not None:
                permissions.addPermissionToRole(admin_role, "admin.*")
                permissions.addPermissionToRole(admin_role, "debug.*")
    elif message.content.lower().strip() != "skip":
        await message.channel.send("Mention admin roles, or say `skip`.")
        return

    await finishSetup(message.guild)
    await message.channel.send(
        embed=discord.Embed(
            title=":white_check_mark: Setup complete!",
            description=(
                "The bot is ready. Games use the current server channels "
                "and private player communication is sent by DM.\n\n"
                "Use !settings to adjust timers and permissions."
            ),
            color=0x00ff00,
        )
    )


async def initializeSetup(ctx, gamesRunning):
    if not dataStorage.getGuildData(ctx.guild, "setupStarted", default=False) and not dataStorage.getGuildData(
        ctx.guild, "setupFinished", default=False
    ):
        dataStorage.setGuildData(ctx.guild, "setupStarted", value=True)
        dataStorage.setGuildData(ctx.guild, "awaitingSetupMessage", value=False)
        dataStorage.setGuildData(ctx.guild, "setupFinished", value=False)
        dataStorage.setGuildData(ctx.guild, "setupProgress", value=0)
        dataStorage.setGuildData(ctx.guild, "setupMember", value=ctx.author.id)
        dataStorage.setGuildData(ctx.guild, "setupChannel", value=ctx.channel.id)
        embed = discord.Embed(
            title=":gear: Murder Mystery setup",
            description=(
                "Configure the bot without creating tutorial, join, or game channels. "
                "Private game instructions and role abilities are delivered by DM.\n\n"
                "Choose whether this channel should receive game summaries."
            ),
            color=0x00b8ff,
        )
        await ctx.send(embed=embed, view=SetupView(ctx.author.id))

    else:
        if gamesRunning:
            await ctx.send(embed=discord.Embed(title=":x: All games must be ended before running the setup again!",
                                               description="Use !list to see all running games.\nTo stop all games, use !endAllGames or !cleanup.",
                                               color=0xff0000))
        else:
            dataStorage.setGuildData(ctx.guild, "setupStarted", value=False)
            dataStorage.setGuildData(ctx.guild, "setupFinished", value=False)
            await initializeSetup(ctx, False)


async def finishSetup(guild):
    dataStorage.setGuildData(guild, "setupFinished", value=True)
    dataStorage.setGuildData(guild, "setupStarted", value=False)
    dataStorage.setGuildData(guild, "awaitingSetupMessage", value=False)
    dataStorage.setGuildData(guild, "useTutorialChannels", value=False)
    dataStorage.setGuildData(guild, "useJoinChannel", value=False)
    dataStorage.setGuildData(guild, "useCategory", value=False)
    dataStorage.setGuildData(guild, "category", value=None)
    dataStorage.setGuildData(guild, "joinChannel", value=None)
    dataStorage.setGuildData(guild, "gameTutorialChannel", value=None)
    dataStorage.setGuildData(guild, "rolesTutorialChannel", value=None)
    dataStorage.setGuildData(guild, "itemsTutorialChannel", value=None)
    dataStorage.setGuildData(guild, "commandsTutorialChannel", value=None)

    for key, value in GAME_DEFAULTS.items():
        dataStorage.setGuildData(guild, key, value=value)
