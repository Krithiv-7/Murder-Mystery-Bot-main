"""Commands package for Murder Mystery Bot."""
from .game_commands import GameCommands
from .admin_commands import AdminCommands
from .player_commands import PlayerCommands


async def setup_cogs(client):
    """Add all cogs to the client."""
    await client.add_cog(GameCommands(client))
    await client.add_cog(AdminCommands(client))
    await client.add_cog(PlayerCommands(client))
