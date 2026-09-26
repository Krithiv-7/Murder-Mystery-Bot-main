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
    prefix = "!"
    if message.guild is not None:
        prefix = dataStorage.getGuildData(message.guild, "prefix", default="!")
    return [
        f"<@!{bot.user.id}> ",
        f"<@{bot.user.id}> ",
        f"<@{bot.user.id}>",
        f"<@!{bot.user.id}> ",
        prefix
    ]


client = commands.Bot(
    command_prefix=get_prefix,
    intents=intents,
    case_insensitive=True
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
    await setup_cogs(client)
