"""Single catalog for help text, disabled commands, and permission metadata."""

from __future__ import annotations

COMMANDS = {
    "join": {
        "category": "game",
        "disableable": True,
        "description": "Join a lobby by its code",
        "permission": "member.join",
    },
    "list": {
        "category": "game",
        "disableable": True,
        "description": "List open and running lobbies",
        "permission": "member.list",
    },
    "spectate": {
        "category": "game",
        "disableable": True,
        "description": "Spectate a lobby, or stop spectating",
        "permission": "member.spectate",
    },
    "createGame": {
        "category": "game",
        "disableable": True,
        "description": "Create a lobby. Alias: create",
        "permission": "member.join",
    },
    "leave": {
        "category": "game",
        "disableable": True,
        "description": "Leave your current lobby or game",
        "permission": "member.leave",
    },
    "vote": {
        "category": "game",
        "disableable": True,
        "description": "Vote to execute a player during the day",
        "permission": "member.vote",
    },
    "shop": {
        "category": "game",
        "disableable": True,
        "description": "Show items you can buy",
        "permission": "member.shop",
    },
    "buy": {
        "category": "game",
        "disableable": True,
        "description": "Buy an item from the shop",
        "permission": "member.shop",
    },
    "use": {
        "category": "game",
        "disableable": True,
        "description": "Use an item from your inventory",
        "permission": "member.use",
    },
    "whisper": {
        "category": "game",
        "disableable": True,
        "description": "Send a private message to another living player",
        "permission": "member.whisper",
    },
    "balance": {
        "category": "game",
        "disableable": True,
        "description": "Show your gold. Aliases: money, gold, bal",
        "permission": "member.balance",
    },
    "forceStart": {
        "category": "game",
        "disableable": False,
        "description": "Host or admin: start the lobby countdown immediately",
        "permission": "admin.game.startGame",
    },
    "stats": {
        "category": "member",
        "disableable": True,
        "description": "Show games played and wins",
        "permission": "member.levels.stats",
    },
    "level": {
        "category": "member",
        "disableable": True,
        "description": "Show XP and level",
        "permission": "member.levels.level",
    },
    "objective": {
        "category": "member",
        "disableable": True,
        "description": "Show or claim objective progress",
        "permission": "member.levels.objective",
    },
    "help": {
        "category": "member",
        "disableable": False,
        "description": "Show command help",
        "permission": "member.help",
    },
    "prefix": {
        "category": "admin",
        "disableable": False,
        "description": "Show or change this server's command prefix",
        "permission": "admin.settings",
    },
    "settings": {
        "category": "admin",
        "disableable": False,
        "description": "View or change game settings",
        "permission": "admin.settings",
    },
    "settingspanel": {
        "category": "admin",
        "disableable": False,
        "description": "Open the admin settings panel",
        "permission": "admin.*",
    },
    "status": {
        "category": "admin",
        "disableable": False,
        "description": "Show bot status, latency, and active games",
        "permission": "admin.*",
    },
    "startGame": {
        "category": "admin",
        "disableable": False,
        "description": "Start a lobby by code",
        "permission": "admin.game.startGame",
    },
    "endGame": {
        "category": "admin",
        "disableable": False,
        "description": "End one lobby by code. Alias: stopGame",
        "permission": "admin.endGame",
    },
    "cleanup": {
        "category": "admin",
        "disableable": False,
        "description": "End every lobby in this server",
        "permission": "admin.endAllGames",
    },
    "kick": {
        "category": "admin",
        "disableable": False,
        "description": "Remove a player from their game",
        "permission": "admin.game.kick",
    },
    "giveGold": {
        "category": "admin",
        "disableable": False,
        "description": "Give gold to a player in a game",
        "permission": "admin.game.giveGold",
    },
    "resetState": {
        "category": "admin",
        "disableable": False,
        "description": "End games and clear this server's in-memory state",
        "permission": "admin.resetState",
    },
    "addPermission": {
        "category": "admin",
        "disableable": False,
        "description": "Grant a permission to a member or role",
        "permission": "admin.permissions.add",
    },
    "removePermission": {
        "category": "admin",
        "disableable": False,
        "description": "Revoke a permission from a member or role",
        "permission": "admin.permissions.remove",
    },
    "permission": {
        "category": "admin",
        "disableable": False,
        "description": "Show permissions for a member or role",
        "permission": "admin.permissions.view",
    },
    "skipVotes": {
        "category": "debug",
        "disableable": False,
        "description": "Skip the current vote timer",
        "permission": "debug.game.skipVotes",
    },
    "skipNight": {
        "category": "debug",
        "disableable": False,
        "description": "Skip the current night",
        "permission": "debug.game.skipNight",
    },
    "setWeather": {
        "category": "debug",
        "disableable": False,
        "description": "Set the weather intensity for a lobby",
        "permission": "debug.game.setWeather",
    },
    "setMoon": {
        "category": "debug",
        "disableable": False,
        "description": "Set the moon level for a lobby",
        "permission": "debug.game.setMoon",
    },
}


def disableable_command_names() -> list[str]:
    return [name for name, meta in COMMANDS.items() if meta.get("disableable")]


def commands_in_category(category: str) -> list[tuple[str, dict]]:
    return [
        (name, meta)
        for name, meta in COMMANDS.items()
        if meta.get("category") == category
    ]


def category_help_lines(category: str, prefix: str) -> list[str]:
    lines = []
    for name, meta in commands_in_category(category):
        lines.append(
            f"`{prefix}{name}` — {meta['description']} ({meta['permission']})"
        )
    return lines
