# Bot configuration settings
import os

import discord


def _read_bool_env(name, default):
    """Read a boolean value from the environment without crashing."""
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() not in {"0", "false", "no", "off"}


# Storage settings
localStorage = _read_bool_env("MMB_LOCAL_STORAGE", True)  # Use JSON instead of mongoDB
testingBot = _read_bool_env("MMB_TESTING_BOT", True)    # Disable main server integration

# Game role configuration
requiredRoles = ["murderer", "doctor"]
roles = {
    "detective": 4,
    "banker": 4,
    "thief": 4,
    "jailer": 5,
    "broadcaster": 6,
    "fool": 6,
    "hunter": 6,
    "werewolf": 7,
    "cupid": 8,
    "mayor": 4,
    "bodyguard": 5,
    "medium": 6,
}

GAME_DEFAULTS = {
    "minPlayers": 4,
    "maxPlayers": 30,
    "preGameTimer": 120,
    "votingTime": 120,
    "nightTimeTimer": 60,
    "prefix": "!",
}

# Server links
mainServerInvite = "https://discord.gg/kriti"
shortMainServerInvite = "discord.gg/kriti"

# Common embeds
noPermissionEmbed = discord.Embed(
    title="You don't have permission to do that!",
    description="You don't have permission to use that command here.",
    color=0xff0000
)
