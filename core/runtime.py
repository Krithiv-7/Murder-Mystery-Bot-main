"""Process-wide runtime facts that do not belong on the Discord client."""

from __future__ import annotations

import time

from core.manager import game_manager
from core.version import __version__

STARTED_AT = time.time()


def format_uptime(seconds: float) -> str:
    total = max(0, int(seconds))
    hours, remainder = divmod(total, 3600)
    minutes, secs = divmod(remainder, 60)
    return f"{hours}h {minutes}m {secs}s"


def status_snapshot(client=None) -> dict:
    games = 0
    players = 0
    for guild_games in game_manager.current_games.values():
        games += len(guild_games)
        for game in guild_games:
            players += len(getattr(game, "players", []))
    latency = "n/a"
    guilds = 0
    ready = False
    if client is not None:
        try:
            latency = f"{client.latency * 1000:.0f} ms"
        except (TypeError, AttributeError):
            latency = "n/a"
        guilds = len(getattr(client, "guilds", []) or [])
        ready = getattr(client, "is_ready", lambda: False)()
    import dataStorage

    return {
        "version": __version__,
        "status": "ready" if ready else "starting",
        "latency": latency,
        "uptime": format_uptime(time.time() - STARTED_AT),
        "guilds": guilds,
        "games": games,
        "players": players,
        "database": dataStorage.storage_status(),
        "accepting_games": game_manager.accepting_new_games,
    }
