"""Shared lobby checks used by prefix commands and slash commands."""

from __future__ import annotations

import dataStorage
from core.config import GAME_DEFAULTS
from core.manager import game_manager
from core.utils import getPlayer, isSpectating


def join_block_reason(member, guild, game) -> str | None:
    """Return a stable reason code when a member cannot join ``game``."""
    if game is None:
        return "not_found"
    existing = getPlayer(member, guild)
    if existing is not None and getattr(existing, "inGame", False):
        return "already_in_game"
    if isSpectating(member, guild):
        return "spectating"
    if game.started:
        return "started"
    max_players = dataStorage.getGuildData(
        guild, "maxPlayers", default=GAME_DEFAULTS["maxPlayers"]
    )
    if len(game.players) >= max_players:
        return "full"
    status = getattr(member, "status", None)
    kick_offline = dataStorage.getGuildData(guild, "kickOfflinePlayers", default=False)
    status_name = getattr(status, "name", None)
    if kick_offline and (status_name == "offline" or str(status) == "offline"):
        return "offline"
    return None


def resolve_guild_game(guild, token):
    if guild is None:
        return None
    return game_manager.get_game(guild.id, token)


JOIN_MESSAGES = {
    "not_found": "Lobby not found. Use list to see codes such as MM-7F2A.",
    "already_in_game": "You are already in a game. Leave it before joining another.",
    "spectating": "You can't join while spectating. Stop spectating first.",
    "started": "This lobby has already started.",
    "full": "This lobby is full.",
    "offline": "You can't play while your status is offline.",
}
