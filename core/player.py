"""Player class for Murder Mystery game."""
import discord
from roles import role


class PrivateChannel:
    """Compatibility adapter for legacy channel-based role handlers."""

    def __init__(self, member):
        self.member = member
        self.mention = "your DMs"

    async def send(self, *args, **kwargs):
        return await self.member.send(*args, **kwargs)

    async def set_permissions(self, *args, **kwargs):
        return None

    async def delete(self):
        return None


class Player:
    """Represents a player in a Murder Mystery game."""
    
    def __init__(self, member, game):
        self.member = member
        self.game = game

        self.inGame = True

        self.voted = False
        self.votes = 0

        self.gold = 1
        self.inventory = []

        self.inJail = False

        self.whisperingTo = []

        self.inLove = False
        self.lover = None
        self.loveChannel = None
        self.dyingNow = False
        self.nightChannel = PrivateChannel(member)
        self.roleChannel = PrivateChannel(member)

    def setRole(self, roleName):
        self.role = role(self, roleName)

    async def send_private(self, *args, **kwargs):
        """Send game-private content through the player's Discord DM."""
        return await self.game.safe_send(self.member, *args, **kwargs)

    async def updateInventory(self, _retry: bool = True):
        usableData = []
        for item in self.inventory:
            foundItem = False
            for v in usableData:
                if v[0].id == item.id:
                    foundItem = True
                    v[1] = v[1] + 1

            if not foundItem:
                usableData.append([item, 1])

        embed = discord.Embed(
            title="Inventory",
            description=(
                "Here's a list of all the items you currently own. "
                "To buy more items, use !shop at night time."
            ),
            color=0x00b8ff
        )
        for v in usableData:
            if v[0].autoActivate:
                embed.add_field(
                    name=f"x{v[1]} {v[0].name}",
                    value=f"{v[0].description}\nThis item will activate automatically",
                    inline=False
                )
            else:
                embed.add_field(
                    name=f"x{v[1]} {v[0].name}",
                    value=f"{v[0].description}\nUsage: {v[0].usage}",
                    inline=False
                )

        await self.send_private(embed=embed)


# Alias for backward compatibility
player = Player
