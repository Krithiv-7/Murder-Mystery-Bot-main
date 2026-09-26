"""Entry point: wires up the Discord client and starts the bot.

The bulk of bot.py's implementation now lives under discordbot/ (see
MODULAR_STRUCTURE.md) - importing each module below registers its
events/commands onto the shared `client` as a side effect.
"""
import logging
import os

from dataStorage import initializeDataStorage
from core.config import localStorage

initializeDataStorage(localStorage)

from discordbot.client import client
from discordbot.helpers import createNewGame
import discordbot.events  # noqa: F401  (registers on_message/on_guild_join/...)
import discordbot.legacy  # noqa: F401  (registers on_ready and main-guild-only commands)
import discordbot.debug_commands  # noqa: F401
import discordbot.game_commands  # noqa: F401
import discordbot.misc_commands  # noqa: F401
import discordbot.help_commands  # noqa: F401
import discordbot.permission_commands  # noqa: F401
import discordbot.slash_commands  # noqa: F401

# Prefer cog-based commands; remove legacy inline registrations to avoid duplicates
LEGACY_COMMANDS = [
    "join", "list", "spectate", "create", "creategame",
    "resetstate", "startgame", "cleanup", "endgame", "kick", "purge", "givegold",
    "whisper", "vote", "use", "shop", "balance", "buy", "leave", "forcestart"
]


def _remove_legacy_commands():
    for name in LEGACY_COMMANDS:
        cmd = client.get_command(name)
        if cmd is not None:
            client.remove_command(name)


_remove_legacy_commands()


def resolve_token():
    """Resolve the bot token from environment variables or local config."""
    token = os.environ.get("DISCORD_TOKEN")
    if token:
        return token

    token_path = os.path.join(os.path.dirname(__file__), "token.txt")
    try:
        with open(token_path, "r", encoding="utf-8") as token_file:
            return token_file.read().strip()
    except FileNotFoundError as exc:
        raise RuntimeError(
            "Bot token not found. Set DISCORD_TOKEN env var or create token.txt next to bot.py."
        ) from exc


def main():
    """Start the Discord bot once the module is executed as a script."""
    logger = logging.getLogger('discord')
    logger.setLevel(logging.INFO)
    log_path = os.path.join(os.path.dirname(__file__), 'log.log')
    handler = logging.FileHandler(
        filename=log_path, encoding='utf-8', mode='w'
    )
    log_format = '%(asctime)s:%(levelname)s:%(name)s: %(message)s'
    handler.setFormatter(logging.Formatter(log_format))
    logger.addHandler(handler)

    client.run(resolve_token())


if __name__ == "__main__":
    main()
