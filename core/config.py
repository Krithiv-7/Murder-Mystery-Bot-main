# Bot configuration settings
import discord

# Storage settings
localStorage = True  # Use JSON instead of mongoDB
testingBot = True    # Disable main server integration

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
    "cupid": 8
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
