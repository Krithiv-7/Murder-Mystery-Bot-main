"""Player-facing wiki data: role abilities and faction win conditions.

This is the single source of truth for the in-bot `!wiki` / `/wiki`
commands (see commands/wiki_commands.py). Content mirrors help-roles.md,
kept here as structured data so it can be rendered as Discord embeds.
"""
from .roles import ROLE_WIKI
from .factions import FACTION_WIKI

__all__ = ["ROLE_WIKI", "FACTION_WIKI"]
