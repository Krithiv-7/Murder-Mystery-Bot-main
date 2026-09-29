"""Player-facing wiki data: role abilities and faction win conditions.

This is the single source of truth for the in-bot `!wiki` / `/wiki`
commands (see commands/wiki_commands.py). Longer written guides live in
wiki/guides/. Role text here is what `!wiki` and `/wiki` render.
"""
from .roles import ROLE_WIKI
from .factions import FACTION_WIKI

__all__ = ["ROLE_WIKI", "FACTION_WIKI"]
