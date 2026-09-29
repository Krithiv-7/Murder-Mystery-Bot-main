"""Bot client construction: intents, prefix resolution, cog loading."""
import discord
from discord.ext import commands

import dataStorage
import permissions
from commands import setup_cogs

intents = discord.Intents.default()
intents.guilds = True
intents.members = True
intents.messages = True
intents.message_content = True  # Requires enabling in Developer Portal
intents.reactions = True


def get_prefix(bot, message):
    """Get command prefix for the bot."""
    from core.config import GAME_DEFAULTS
    prefix = GAME_DEFAULTS["prefix"]
    if message.guild is not None:
        prefix = dataStorage.getGuildData(
            message.guild, "prefix", default=GAME_DEFAULTS["prefix"]
        )
    return [
        f"<@!{bot.user.id}> ",
        f"<@{bot.user.id}> ",
        f"<@{bot.user.id}>",
        f"<@!{bot.user.id}> ",
        prefix
    ]


class MurderMysteryTree(discord.app_commands.CommandTree):
    """Reject game commands that are not tied to one server."""

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        command_name = getattr(interaction.command, "name", "")
        if interaction.guild is not None or command_name in {"ping", "help"}:
            return True
        if not interaction.response.is_done():
            await interaction.response.send_message(
                "Use this command inside a server.", ephemeral=True
            )
        return False


client = commands.Bot(
    command_prefix=get_prefix,
    intents=intents,
    case_insensitive=True,
    tree_cls=MurderMysteryTree,
)


@client.check
async def enforce_disabled_commands(ctx):
    """Block prefix commands an admin disabled via the settings panel."""
    if ctx.guild is None or ctx.command is None:
        return True
    if permissions.memberHasPermission(ctx.author, "admin.*"):
        return True
    disabled = dataStorage.getGuildData(ctx.guild, "disabledCommands", default=[])
    return ctx.command.qualified_name not in disabled


@client.event
async def setup_hook():
    """Load command cogs at startup to keep bot.py slim."""
    import asyncio

    from core.cli import write_heartbeat

    await setup_cogs(client)

    async def _heartbeat():
        while True:
            write_heartbeat()
            await asyncio.sleep(20)

    asyncio.create_task(_heartbeat())
