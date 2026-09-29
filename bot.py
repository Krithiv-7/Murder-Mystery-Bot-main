"""Entry point: wires up the Discord client and starts the bot."""
import asyncio
import logging
import os
import signal

from core.config import localStorage
from core.logging_config import configure_logging
from dataStorage import flush, initializeDataStorage

logger = logging.getLogger("mmb.startup")
configure_logging()
logger.info("Loading configuration")
logger.info("Connecting to database")
initializeDataStorage(localStorage)
logger.info("Loading commands")
logger.info("Loading game systems")

from core.utils import createNewGame
from discordbot.client import client
import discordbot.events  # noqa: F401
import discordbot.legacy  # noqa: F401
import discordbot.debug_commands  # noqa: F401
import discordbot.misc_commands  # noqa: F401
import discordbot.help_commands  # noqa: F401
import discordbot.permission_commands  # noqa: F401
import discordbot.slash_commands  # noqa: F401


def resolve_token():
    """Resolve the bot token from the environment."""
    token = os.environ.get("DISCORD_TOKEN", "").strip()
    if token:
        return token

    token_path = os.path.join(os.path.dirname(__file__), "token.txt")
    try:
        with open(token_path, "r", encoding="utf-8") as token_file:
            token = token_file.read().strip()
    except FileNotFoundError:
        token = ""
    if token:
        return token
    raise RuntimeError(
        "ERROR: DISCORD_TOKEN is missing.\nSet DISCORD_TOKEN in .env."
    )


async def _serve(token: str) -> None:
    from core.manager import game_manager

    loop = asyncio.get_running_loop()

    async def _shutdown():
        logger.info("Shutting down")
        game_manager.request_shutdown()
        flush()
        await client.close()

    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(sig, lambda: asyncio.create_task(_shutdown()))
        except NotImplementedError:
            signal.signal(sig, lambda *_args: asyncio.get_event_loop().call_soon_threadsafe(
                lambda: asyncio.create_task(_shutdown())
            ))

    logger.info("Connecting to Discord")
    try:
        await client.start(token)
    finally:
        flush()
        logger.info("Discord connection closed")


def main():
    try:
        token = resolve_token()
    except RuntimeError as exc:
        logger.error("%s", exc)
        raise SystemExit(1) from exc
    try:
        asyncio.run(_serve(token))
    except KeyboardInterrupt:
        logger.info("Interrupted")


if __name__ == "__main__":
    main()
