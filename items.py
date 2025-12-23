import discord
import random
from roles import broadcast
import objectives
import dataStorage


def getItems(**kwargs):
    list = [rock, gun, ring, shield, potato, ticket, house, dagger]
    for v in kwargs:
        if kwargs[v] == True:
            if v == "broadcasterInGame":
                list.extend([phone, satellite])
        elif v == "role":
            if kwargs[v] == "doctor" or kwargs[v] == "all":
                list.append(bandage)

    return list


async def buy(item, player, channel):
    if player.gold >= item.cost:
        player.gold = player.gold - item.cost
        player.inventory.append(item)
        item.player = player
        await channel.send(
            embed=discord.Embed(title=f":white_check_mark: Successfully bought 1 {item.name}!", color=0x00ff00))
        await player.updateInventory()
    else:
        await channel.send(embed=discord.Embed(title=":coin: You don't have enough gold to buy this item!",
                                               description=f"You need {item.cost - player.gold} more :coin: gold in order to buy this item.",
                                               color=0xff0000))


async def removeFromInventory(item, player):
    for v in player.inventory:
        if v == item:
            player.inventory.remove(item)
            await player.updateInventory()


class rock:
    def __init__(self):
        self.uses = 1
        self.name = ":rock: Rock"
        self.id = "rock"
        self.usage = f"!use {self.id} @<player name>"
        self.description = "Has a 30% chance of killing the specified player"
        self.cost = 3
        self.autoActivate = False
        self.onlyDayTime = True

        self.needArg = True
        self.needPlayerArg = True

    async def use(self, ctx, arg):
        if hasattr(self, "player"):
            if self.uses > 0:
                if self.needPlayerArg:
                    if arg is not None:
                        if not arg.game.nightTime:
                            if ctx.message.channel == arg.game.mainChannel:
                                if random.randint(1, 100) <= 30:
                                    await ctx.send(
                                        embed=discord.Embed(title=f"You hit {arg.member.display_name} with a rock!",
                                                            description=f"You threw a rock at {arg.member.mention}, and it hit!",
                                                            color=0x00ff00))

                                    await arg.game.killPlayer(arg, discord.Embed(
                                        title=f":skull: {arg.member.display_name} died because of {ctx.author.display_name}'s rock!",
                                        description=f"{arg.member.display_name}{arg.role.deadString}",
                                        color=0xff0000),
                                                              discord.Embed(
                                                                  title=f"You died by {ctx.author.display_name}'s rock!",
                                                                  color=0xff0000))
                                    if arg.role.name == "murderer":
                                        objectives.addObjectiveProgress(self.player.member, "killMurdererWithItem", 1)
                                else:
                                    await ctx.send(embed=discord.Embed(title="Your rock throw missed!",
                                                                       description=f"You threw a rock at {arg.member.mention}, but it missed!",
                                                                       color=0xff0000))
                                self.uses = self.uses - 1
                                if self.uses <= 0:
                                    await removeFromInventory(self, self.player)

                        else:
                            await ctx.send(embed=discord.Embed(title=":x: You can only use this item during daytime!",
                                                               description="You have to wait until daytime before you can use this item.",
                                                               color=0xff0000))
                    else:
                        await ctx.send(embed=discord.Embed(title=":x: Failed to find that player!",
                                                           description="he's probably not in this game.",
                                                           color=0xff0000))

                else:
                    pass

            else:
                if self.uses <= 0:
                    await ctx.message.channel.send(embed=discord.Embed(title=":x: This item has no uses left.",
                                                                       description="It will now be removed from your inventory.",
                                                                       color=0xff0000))
                    await removeFromInventory(self, self.player)
                    await self.player.updateInventory()

        else:
            await ctx.message.channel.send(embed=discord.Embed(title=":x: ERROR: Can't find who this item belongs to.",
                                                               description=f"Please report this bug", color=0xff0000))
            print("ERROR: Failed to find player an item belongs to.")


class gun:
    def __init__(self):
        self.uses = 1
        self.name = "<:real_gun:808105083703001148> Gun"
        self.id = "gun"
        self.usage = f"!use {self.id} @<player name>"
        self.description = "Kills the specified player"
        self.cost = 7
        self.autoActivate = False
        self.onlyDayTime = True

        self.needArg = True
        self.needPlayerArg = True

    async def use(self, ctx, arg):
        if hasattr(self, "player"):
            if self.uses > 0:
                if self.needPlayerArg:
                    if arg is not None:
                        if not arg.game.nightTime:
                            if ctx.message.channel == arg.game.mainChannel:
                                await ctx.send(
                                    embed=discord.Embed(
                                        title=f"<:real_gun:808105083703001148> You shot {arg.member.display_name}!",
                                        color=0x00ff00))

                                await arg.game.killPlayer(arg, discord.Embed(
                                    title=f":skull: {arg.member.display_name} got shot by {ctx.author.display_name}!",
                                    description=f"{arg.member.display_name}{arg.role.deadString}",
                                    color=0xff0000),
                                                          discord.Embed(
                                                              title=f":skull: You died because {ctx.author.display_name} shot you!",
                                                              color=0xff0000))
                                if arg.role.name == "murderer":
                                    objectives.addObjectiveProgress(self.player.member, "killMurdererWithItem", 1)
                                self.uses = self.uses - 1
                                if self.uses <= 0:
                                    await removeFromInventory(self, self.player)

                        else:
                            await ctx.send(embed=discord.Embed(title=":x: You can only use this item during daytime!",
                                                               description="You have to wait until daytime before you can use this item.",
                                                               color=0xff0000))
                    else:
                        await ctx.send(embed=discord.Embed(title=":x: Failed to find that player!",
                                                           description="he's probably not in this game.",
                                                           color=0xff0000))

                else:
                    pass

            else:
                if self.uses <= 0:
                    await ctx.message.channel.send(embed=discord.Embed(title=":x: This item has no uses left.",
                                                                       description="It will now be removed from your inventory.",
                                                                       color=0xff0000))
                    await removeFromInventory(self, self.player)
                    await self.player.updateInventory()

        else:
            await ctx.message.channel.send(embed=discord.Embed(title=":x: ERROR: Can't find who this item belongs to.",
                                                               description=f"Please report this bug", color=0xff0000))
            print("ERROR: Failed to find player an item belongs to.")


class ring:
    def __init__(self):
        self.uses = 1
        self.name = ":ring: Ring Of Life [ring]"
        self.id = "ring"
        self.usage = "This item will activate automatically"
        self.description = "Unless executed, you will not die when you get killed"
        self.cost = 15
        self.autoActivate = True
        self.onlyDayTime = False

        self.needArg = False
        self.needPlayerArg = False

    async def use(self, ctx, arg):
        if hasattr(self, "player"):
            if self.autoActivate:
                await ctx.message.channel.send(embed=discord.Embed(title=":x: This item can't be used!",
                                                                   description="It will activate automatically",
                                                                   color=0xff0000))

        else:
            await ctx.message.channel.send(embed=discord.Embed(title=":x: ERROR: Can't find who this item belongs to.",
                                                               description=f"Please report this bug", color=0xff0000))
            print("ERROR: Failed to find player an item belongs to.")


class shield:
    def __init__(self):
        self.uses = 1
        self.name = ":shield: Shield"
        self.id = "shield"
        self.usage = "This item will activate automatically"
        self.description = "Unless executed, there is a 50% chance that you won't die when killed"
        self.cost = 8
        self.autoActivate = True
        self.onlyDayTime = False

        self.needArg = False
        self.needPlayerArg = False

    async def use(self, ctx, arg):
        if hasattr(self, "player"):
            if self.autoActivate:
                await ctx.message.channel.send(embed=discord.Embed(title=":x: This item can't be used!",
                                                                   description="It will activate automatically",
                                                                   color=0xff0000))

        else:
            await ctx.message.channel.send(embed=discord.Embed(title=":x: ERROR: Can't find who this item belongs to.",
                                                               description=f"Please report this bug", color=0xff0000))
            print("ERROR: Failed to find player an item belongs to.")


class potato:
    def __init__(self):
        self.uses = 1
        self.name = ":potato: Potato"
        self.id = "potato"
        self.usage = "This item will activate automatically"
        self.description = "Unless executed, there is a 10% chance that you won't die when killed"
        self.cost = 3
        self.autoActivate = True
        self.onlyDayTime = False

        self.needArg = False
        self.needPlayerArg = False

    async def use(self, ctx, arg):
        if hasattr(self, "player"):
            if self.autoActivate:
                await ctx.message.channel.send(embed=discord.Embed(title=":x: This item can't be used!",
                                                                   description="It will activate automatically",
                                                                   color=0xff0000))

        else:
            await ctx.message.channel.send(embed=discord.Embed(title=":x: ERROR: Can't find who this item belongs to.",
                                                               description=f"Please report this bug", color=0xff0000))
            print("ERROR: Failed to find player an item belongs to.")


class ticket:
    def __init__(self):
        self.uses = 1
        self.name = ":tickets: Lottery ticket [ticket]"
        self.id = "ticket"
        self.usage = "This item will activate automatically"
        self.description = "There's a small chance that you'll win the lottery the next morning. The grand prize is 30 gold, but there are smaller prizes too.\n(you can only participate in 1 lottery per day, buying multiple tickets will make them activate the next day.)"
        self.cost = 4
        self.autoActivate = True
        self.onlyDayTime = False

        self.needArg = False
        self.needPlayerArg = False

    async def use(self, ctx, arg):
        if hasattr(self, "player"):
            if self.autoActivate:
                await ctx.message.channel.send(embed=discord.Embed(title=":x: This item can't be used!",
                                                                   description="It will activate automatically",
                                                                   color=0xff0000))

        else:
            await ctx.message.channel.send(embed=discord.Embed(title=":x: ERROR: Can't find who this item belongs to.",
                                                               description=f"Please report this bug", color=0xff0000))
            print("ERROR: Failed to find player an item belongs to.")


class phone:
    def __init__(self):
        self.uses = 1
        self.name = ":telephone: Phone"
        self.id = "phone"
        self.usage = "!use phone <text>"
        self.description = "Allows you to reply to the last broadcast"
        self.cost = 6
        self.autoActivate = False
        self.onlyDayTime = False
        self.onlyNightTime = True

        self.needArg = True
        self.needPlayerArg = False

    async def use(self, ctx, arg):
        if hasattr(self, "player"):
            if self.uses > 0:
                if self.needPlayerArg:
                    if arg is not None:
                        pass

                else:
                    if self.player.game.weatherIntensity > 80 and self.player.game.weatherIntensity <= 90:
                        ctx.send(embed=discord.Embed(
                            title=":thunder_cloud_rain: Because of the stormy weather the satellite isn't working",
                            description="You have to wait until the stormy weather is over before you can use the satellite.",
                            color=0xff0000))
                    else:
                        if arg is not None:
                            if self.onlyNightTime:
                                if self.player.game.nightTime:
                                    if hasattr(self.player, "lastBroadcast"):
                                        if not self.player.lastBroadcast.replied:
                                            senderInGame = False
                                            for player in self.player.game.players:
                                                if player == self.player.lastBroadcast.sender:
                                                    senderInGame = True
                                            if senderInGame:
                                                await self.player.lastBroadcast.reply(arg)
                                                content = arg.replace("```", "")
                                                await ctx.send(embed=discord.Embed(title=":telephone: Reply sent!",
                                                                                   description=f"You replied\n\n```{content}```\n\nto the broadcast\n\n```{self.player.lastBroadcast.content}```",
                                                                                   color=0x00ff00))
                                                self.uses -= 1
                                                if self.uses <= 0:
                                                    await removeFromInventory(self, self.player)
                                            else:
                                                await ctx.send(embed=discord.Embed(
                                                    title=":x: The broadcast sender is no longer in game",
                                                    description="They might've died", color=0xff0000))
                                        else:
                                            await ctx.send(
                                                embed=discord.Embed(title=":x: You already replied to this broadcast!",
                                                                    description="You can only reply to a broadcast once.",
                                                                    color=0xff0000))
                                    else:
                                        await ctx.send(
                                            embed=discord.Embed(title=":x: You don't have any broadcasts yet!",
                                                                description="You can only reply to a broadcast if you actually received one.",
                                                                color=0xff0000))
                                else:
                                    await ctx.send(
                                        embed=discord.Embed(title=":x: You can only use this item at night time",
                                                            description="Please wait until night time before using this item!",
                                                            color=0xff0000))


            else:
                if self.uses <= 0:
                    await ctx.message.channel.send(embed=discord.Embed(title=":x: This item has no uses left.",
                                                                       description="It will now be removed from your inventory.",
                                                                       color=0xff0000))
                    await removeFromInventory(self, self.player)
                    await self.player.updateInventory()

        else:
            await ctx.message.channel.send(embed=discord.Embed(title=":x: ERROR: Can't find who this item belongs to.",
                                                               description=f"Please report this bug", color=0xff0000))
            print("ERROR: Failed to find player an item belongs to.")


class satellite:
    def __init__(self):
        self.uses = 1
        self.name = ":satellite: Satellite"
        self.id = "satellite"
        self.usage = "!use satellite"
        self.description = "Allows you to send broadcasts while pretending to be the broadcaster"
        self.cost = 4
        self.autoActivate = False
        self.onlyDayTime = False
        self.onlyNightTime = True

        self.needArg = False
        self.needPlayerArg = False

        self.messageMode = False
        self.channel = None

        self.player = None

    def getRoleList(self):
        # this is stored because if someone leaves during the night we don't want it to shift all the indexes and make the player select the wrong person
        self.currentPlayerList = self.player.game.getPlayersListExcluding(self.player)
        self.currentRolesList = []
        for player in self.currentPlayerList:
            if player.role.name != "none":
                self.currentRolesList.append(player.role)

    def addRolesToEmbed(self, embed):
        self.getRoleList()
        for role in self.currentRolesList:
            embed.add_field(name=f"{self.currentRolesList.index(role)}: {role.fancyName}",
                            value="Type this number to select this role.", inline=True)

        return embed

    async def use(self, ctx, arg=None):
        if hasattr(self, "player"):
            if self.uses > 0:
                if self.onlyNightTime:
                    if self.player.game.nightTime:
                        if not self.player.satelliteUsed:
                            self.channel = await self.player.game.category.create_text_channel("satellite")
                            self.player.satelliteChannel = self.channel
                            self.player.currentSatellite = self
                            await self.channel.set_permissions(self.player.game.role, read_messages=False,
                                                               send_messages=False)
                            await self.channel.set_permissions(self.player.member, read_messages=True,
                                                               send_messages=True)
                            self.player.game.channels.append(self.channel)
                            self.player.game.channelsRemoveByMorning.append(self.channel)
                            embed = self.addRolesToEmbed(discord.Embed(title="Choose a role to send a message to",
                                                                       description="Type a number bellow to select a role and the person with that role will receive a message of your choice.",
                                                                       color=0x19ff00))
                            embed.add_field(name=f"{len(self.currentRolesList)} Everyone",
                                            value="Type this number to select everyone",
                                            inline=True)
                            await self.player.satelliteChannel.send(embed=embed)
                            await ctx.send(
                                embed=discord.Embed(title="Check the satellite channel to use the satellite!",
                                                    description=f"Please check {self.player.satelliteChannel.mention} to use the satellite!",
                                                    color=0x00ff00))
                        else:
                            await ctx.send(embed=discord.Embed(title=":x: You can only use 1 satellite per night.",
                                                               description=f"You're already using this satellite right now, please check {self.player.satelliteChannel.mention}.",
                                                               color=0xff0000))

                    else:
                        await ctx.send(embed=discord.Embed(title=":x: You can only use this item at night time",
                                                           description="Please wait until night time before using this item!",
                                                           color=0xff0000))

            else:
                if self.uses <= 0:
                    await ctx.message.channel.send(embed=discord.Embed(title=":x: This item has no uses left.",
                                                                       description="It will now be removed from your inventory.",
                                                                       color=0xff0000))
                    await removeFromInventory(self, self.player)
                    await self.player.updateInventory()

    async def processMessage(self, message):
        if not self.messageMode:
            nonNumber = False
            choice = -1
            try:
                choice = int(message.content)
            except ValueError:
                await self.player.satelliteChannel.send("Please enter a number!")
                nonNumber = True

            if choice >= 0 and choice <= len(self.currentRolesList):
                if choice != len(self.currentRolesList):
                    if self.player.game.findRole(self.currentRolesList[choice].name) is not None:
                        self.messageMode = True
                        self.messageTo = self.player.game.findRole(self.currentRolesList[choice].name)
                        embed = discord.Embed(
                            title=f"What would you like to send to the {self.player.game.findRole(self.currentRolesList[choice].name).role.fancyName}?",
                            description="They won't be able to see your username, instead they will see that it was sent by the broadcaster. Keep in mind that the normal chat rules still apply. Please do not send any inappropriate or rude message.",
                            color=0x19ff00)
                        embed.add_field(name='To cancel, type "cancel"',
                                        value='If you want to select a different player, type "cancel".',
                                        inline=False)
                        await self.player.satelliteChannel.send(embed=embed)

                    else:
                        await self.player.satelliteChannel.send(
                            embed=discord.Embed(title="The player with that role is no longer in the game!",
                                                description="They might've left the game", color=0xff0b00))
                else:
                    # selected to broadcast to everyone
                    self.messageMode = True
                    self.messageTo = "everyone"
                    embed = discord.Embed(title=f"What would you like to send to everyone?",
                                          description="They won't be able to see your username, instead they will see that it was sent by the broadcaster. Keep in mind that the normal chat rules still apply. Please do not send any inappropriate or rude message.",
                                          color=0x19ff00)
                    embed.add_field(name='To cancel, type "cancel"',
                                    value='If you want to select a different role to send a message to, type "cancel".',
                                    inline=False)
                    await self.player.satelliteChannel.send(embed=embed)

            else:
                if not nonNumber:
                    await self.player.satelliteChannel.send(
                        f"Please enter a number between 0 and {len(self.currentPlayerList)}!")

        else:
            if message.content.lower() != "cancel":
                if self.messageTo != "everyone":
                    if self.messageTo in self.player.game.players:
                        bc = broadcast(message.content, self.player, self.messageTo, False)
                        await bc.send()
                        await self.player.satelliteChannel.set_permissions(self.player.member, read_messages=True,
                                                                           send_messages=False)
                        m = message.content.replace("```", "")
                        await self.player.satelliteChannel.send(embed=discord.Embed(title="Broadcast sent!",
                                                                                    description=f"The {self.messageTo.role.fancyName} will now receive the following message: \n \n ```{m}```"))
                        self.satelliteUsed = True
                        self.uses -= 1
                        if self.uses <= 0:
                            await removeFromInventory(self, self.player)
                    else:
                        await self.player.satelliteChannel.send(
                            embed=discord.Embed(title="That player is no longer in this game.",
                                                description="They might've left. Try a different role!",
                                                color=0xff0000))
                        embed = self.addRolesToEmbed(discord.Embed(title="Choose a role to send a message to",
                                                                   description="Type a number bellow to select a role and the person with that role will receive a message of your choice.",
                                                                   color=0x19ff00))
                        embed.add_field(name=f"{len(self.currentRolesList)} Everyone",
                                        value="Type this number to select everyone",
                                        inline=True)
                        await self.player.satelliteChannel.send(embed=embed)
                else:
                    for player in self.player.game.players:
                        if player != self.player and player.role.name != "broadcaster":
                            bc = broadcast(message.content, self.player, player, True)
                            await bc.send()
                    m = message.content.replace("```", "")
                    await self.player.satelliteChannel.send(embed=discord.Embed(title="Broadcast sent!",
                                                                                description=f"Everyone will now receive the following message: \n \n```{m}```",
                                                                                color=0x19ff00))
                    self.player.satelliteUsed = True
                    await removeFromInventory(self, self.player)
            else:
                embed = self.addRolesToEmbed(discord.Embed(title="Choose a role to send a message to",
                                                           description="Type a number bellow to select a role and the person with that role will receive a message of your choice.",
                                                           color=0x19ff00))
                embed.add_field(name=f"{len(self.currentRolesList)} Everyone",
                                value="Type this number to select everyone",
                                inline=True)
                await self.player.satelliteChannel.send(embed=embed)


class dagger:
    def __init__(self):
        self.name = ":dagger: dagger"
        self.id = "dagger"
        self.usage = f"!use {self.id}"
        self.description = "Allows you to kill someone at night time, so nobody knows that you're the person that killed them"
        self.cost = 10
        self.autoActivate = False
        self.onlyDayTime = False
        self.onlyNightTime = True
        self.needArg = False
        self.needPlayerArg = False
        self.uses = 1

    async def use(self, ctx, arg=None):
        if hasattr(self, "player"):
            if self.uses > 0:
                if self.onlyNightTime:
                    if self.player.game.nightTime:
                        self.channel = await self.player.game.category.create_text_channel("Dagger")
                        self.player.daggerChannel = self.channel
                        self.player.currentDagger = self
                        await self.channel.set_permissions(self.player.game.role, read_messages=False,
                                                           send_messages=False)
                        await self.channel.set_permissions(self.player.member, read_messages=True, send_messages=True)
                        self.player.game.channels.append(self.channel)
                        self.player.game.channelsRemoveByMorning.append(self.channel)
                        embed = self.addPlayersToEmbed(discord.Embed(title="Choose someone to kill",
                                                                     description="Type a number below to kill that player.",
                                                                     color=0xff0b00))
                        await self.player.daggerChannel.send(embed=embed)
                        await ctx.send(embed=discord.Embed(title="Check the dagger channel to select someone to kill!",
                                                           description=f"Please check {self.player.daggerChannel.mention} to select someone to kill.",
                                                           color=0xff0b00))

                    else:
                        await ctx.send(embed=discord.Embed(title=":x: You can only use this item at night time!",
                                                           description="Please wait until its night time before you can use this item!",
                                                           color=0xff0000))

        else:
            await ctx.message.channel.send(embed=discord.Embed(title=":x: ERROR: Can't find who this item belongs to.",
                                                               description=f"Please report this bug", color=0xff0000))
            print("ERROR: Failed to find player an item belongs to.")

    def addPlayersToEmbed(self, embed):
        # this is stored in a variable because if someone leaves during the night we don't want it to shift all the indexes and make the player select the wrong person
        if self.name == "murderer":
            if self.player.game.findRole("werewolf") is not None:
                self.currentPlayerList = self.player.game.getPlayersListExcluding(
                    [self.player, self.player.game.findRole("werewolf")])
            else:
                self.currentPlayerList = self.player.game.getPlayersListExcluding(self.player)
        elif self.name == "werewolf":
            self.currentPlayerList = self.player.game.getPlayersListExcluding(
                [self.player, self.player.game.findRole("murderer")])
        else:
            self.currentPlayerList = self.player.game.getPlayersListExcluding(self.player)

        for player in self.currentPlayerList:
            embed.add_field(name=f"{self.currentPlayerList.index(player)}: {player.member.display_name}",
                            value="Type this number to select this player", inline=True)
        return embed

    async def processMessage(self, message):
        if not self.player.inJail:
            choice = -1
            nonNumber = False
            try:
                choice = int(message.content)
            except ValueError:
                await self.player.roleChannel.send("Please enter a number!")
                nonNumber = True

            if choice != -1 and choice >= 0 and choice < len(self.currentPlayerList):
                if self.uses > 0:
                    if self.currentPlayerList[choice] in self.player.game.players:
                        # queue the player to die the next morning
                        self.player.game.willDieNextMorning.append(
                            {"player": self.currentPlayerList[choice], "title": " got killed",
                             "DM": ":skull: You got killed!", "deathCause": "itemUsedOnPlayer", "killer": self.player})

                        self.uses -= 1
                        if self.uses <= 0:
                            await removeFromInventory(self, self.player)
                        # send confirmation message
                        await self.player.daggerChannel.send(embed=discord.Embed(
                            title=f":dagger: You stabbed {self.currentPlayerList[choice].member.display_name}",
                            description="If they don't get healed by the doctor tonight, they will die next morning.",
                            color=0xff0b00))
                        # set permissions for murderer channel
                        await self.player.daggerChannel.set_permissions(self.player.member, read_messages=True,
                                                                       send_messages=False)

                    else:
                        await self.player.daggerChannel.send(
                            embed=discord.Embed(title="That player is no longer in the game",
                                                description="They might've left the game, please try a different player!"))
            else:
                if not nonNumber:
                    await self.player.daggerChannel.send(
                        f"Please enter a number between 0 and {len(self.currentPlayerList) - 1}!")
        else:
            await message.channel.send(":x: You can't do that while in jail")


class house:
    def __init__(self):
        self.name = ":house: House"
        self.id = "house"
        self.usage = "This item will activate automatically"
        self.description = "When there's a tornado, there's a 100% chance that you will survive. There's a 30% chance that your house will break after the tornado."
        self.cost = 4
        self.autoActivate = True
        self.onlyDayTime = False

        self.needArg = False
        self.needPlayerArg = False

    async def use(self, ctx, arg):
        if hasattr(self, "player"):
            if self.autoActivate:
                await ctx.message.channel.send(embed=discord.Embed(title=":x: This item can't be used!",
                                                                   description="It will activate automatically",
                                                                   color=0xff0000))

        else:
            await ctx.message.channel.send(embed=discord.Embed(title=":x: ERROR: Can't find who this item belongs to.",
                                                               description=f"Please report this bug", color=0xff0000))
            print("ERROR: Failed to find player an item belongs to.")


class bandage:
    def __init__(self):
        self.name = ":adhesive_bandage: Bandage"
        self.id = "bandage"
        self.description = "If you're the doctor, you can use your ability again if you already used it.\nThis item can only be bought by the :pill: doctor."
        self.usage = "!use bandage"
        self.cost = 6
        self.autoActivate = False
        self.onlyDayTime = False
        self.onlyNightTime = False
        self.needArg = False
        self.needPlayerArg = False
        self.uses = 1

    async def use(self, ctx, arg=None):
        if hasattr(self, "player"):
            if self.player.role.name == "doctor":
                if self.player.role.permAbilityUsed:
                    self.player.role.permAbilityUsed = False
                    await ctx.send(embed=discord.Embed(title="You can use your healing ability again!", description=f"You can now use your ability in {self.player.roleChannel.mention} again.", color=0x00ff00))
                    someoneDied = False
                    if hasattr(self.player.role, "healable"):
                        for deathData in self.player.game.willDieNextMorning:
                            if deathData["player"] == self.healable:
                                someoneDied = True
                    if someoneDied:
                        await self.player.roleChannel.set_permissions(self.player.member, read_messages=True, send_messages=True)
                        if self.player.role.healable == self.player:
                            embed = discord.Embed(
                                title=f"You just got killed by the murderer, revive yourself?",
                                description="Type yes or no to revive them or not.", color=0x16ff00)
                            embed.add_field(name="Warning:",
                                            value="You can only use this ability once. If you choose to not heal yourself, a healing item such as the ring of life could still heal you.",
                                            inline=False)
                        else:
                            embed = discord.Embed(
                                title=f"Someone just got killed by the murderer, revive them?",
                                description="Type yes or no to revive them or not.", color=0x16ff00)
                            embed.add_field(name="Warning:",
                                            value="You can only use this ability once.",
                                            inline=False)
                        await self.player.roleChannel.send(embed=embed)

                    await removeFromInventory(self, self.player)
                else:
                    await ctx.send(embed=discord.Embed(title=":x: You haven't used your ability yet!",
                                                       description="This item can only be used if you already used your healing ability"))
            else:
                await ctx.send(":x: This item can only be used by the :pill: doctor")
        else:
            await ctx.message.channel.send(embed=discord.Embed(title=":x: ERROR: Can't find who this item belongs to.",
                                                               description=f"Please report this bug", color=0xff0000))
            print("ERROR: Failed to find player an item belongs to.")
