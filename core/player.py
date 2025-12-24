"""Player class for Murder Mystery game."""
import discord
from roles import role


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

    def setRole(self, roleName):
        self.role = role(self, roleName)

    async def updateInventory(self):
        if hasattr(self, "inventoryChannel"):
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

            await self.inventoryChannel.purge(limit=5)
            await self.inventoryChannel.send(embed=embed)
        else:
            self.inventoryChannel = await self.game.category.create_text_channel(
                "Inventory"
            )
            await self.inventoryChannel.set_permissions(
                self.game.role, read_messages=False, send_messages=False
            )
            await self.inventoryChannel.set_permissions(
                self.member, read_messages=True, send_messages=False
            )
            self.game.channels.append(self.inventoryChannel)
            await self.updateInventory()


# Alias for backward compatibility
player = Player
