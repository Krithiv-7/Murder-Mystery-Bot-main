import discord
import random
import objectives


class role:
    def __init__(self, player, roleName):
        self.player = player
        self.game = player.game
        self.name = roleName

        if self.name == "murderer":
            self.revealEmbed = discord.Embed(title=":dagger: You are the murderer",
                                             description="At night time you can select someone to kill in the murderer channel.",
                                             color=0xa80700)
            self.revealEmbed.add_field(name="How to win:", value="Kill everyone and be the last one left", inline=False)

            self.abilityUsed = False
            self.fancyName = ":dagger: murderer"
            self.revealString = f" is the {self.fancyName}"
            self.deadString = f" was the {self.fancyName}"

        elif self.name == "detective":
            self.revealEmbed = discord.Embed(title=":spy: You are the detective",
                                             description="At night time you can choose someone to investigate. Their role will be revealed to you the next night.",
                                             color=0x00ff2d)
            self.revealEmbed.add_field(name="How to win:", value="Kill the murderer", inline=False)

            self.abilityUsed = False
            self.fancyName = ":spy: detective"
            self.revealString = f" is the {self.fancyName}"
            self.deadString = f" was the {self.fancyName}"

        elif self.name == "doctor":
            self.revealEmbed = discord.Embed(title=":pill: You are the doctor",
                                             description="If someone gets killed by the murderer you will be notified in the doctor channel, you can choose to revive them or not, but you can only do this once.",
                                             color=0x00ff2d)
            self.revealEmbed.add_field(name="How to win:", value="Kill the murderer", inline=False)

            self.abilityUsed = False
            self.permAbilityUsed = False
            self.roleChannelEmbedSent = False
            self.unlockRoleChannelAtNightTime = False
            self.fancyName = ":pill: doctor"
            self.revealString = f" is the {self.fancyName}"
            self.deadString = f" was the {self.fancyName}"

        elif self.name == "broadcaster":
            self.revealEmbed = discord.Embed(title=":radio: You are the broadcaster",
                                             description="Each night you can choose a role to send a message to without knowing who that role belongs to. The message will be received a night later.",
                                             color=0x00ff2d)
            self.revealEmbed.add_field(name="Warning:",
                                       value="Sending inappropriate broadcasts will result in a ban. The normal chat rules still apply. The broadcasts will be logged.",
                                       inline=False)
            self.revealEmbed.add_field(name="How to win:", value="Kill the murderer", inline=False)

            self.abilityUsed = False
            self.messageMode = False

            self.fancyName = ":radio: broadcaster"
            self.revealString = f" is the {self.fancyName}"
            self.deadString = f" was the {self.fancyName}"

            self.broadcastsToBeSent = []

        elif self.name == "banker":
            self.revealEmbed = discord.Embed(title=":person_in_tuxedo: You are the banker",
                                             description="You start with 3 gold, and you get 1 extra gold per day compared to everyone else",
                                             color=0x00ff00)
            self.revealEmbed.add_field(name="How to win:", value="Kill the murderer", inline=False)

            self.fancyName = ":person_in_tuxedo: banker"
            self.revealString = f" is the {self.fancyName}"
            self.deadString = f" was the {self.fancyName}"

            self.player.gold = 3

        elif self.name == "thief":
            self.revealEmbed = discord.Embed(title=":unlock: You are the thief",
                                             description="Each night, you can choose to steal from someone. There is a 50% chance that you succeed, and if you succeed you steal half of that player's :coin: gold",
                                             color=0x4a4a4a)
            self.revealEmbed.add_field(name="How to win:", value="Kill the murderer", inline=False)

            self.fancyName = ":unlock: Thief"
            self.revealString = f" is the {self.fancyName}"
            self.deadString = f" was the {self.fancyName}"


        elif self.name == "jailer":
            self.revealEmbed = discord.Embed(title=":cop: You are the jailer",
                                             description="Each night you can choose to jail someone. That person will be put in jail the next night. While someone is in jail, they can't use their role's ability or the shop.",
                                             color=0x009eff)
            self.revealEmbed.add_field(name="How to win:", value="Kill the murderer", inline=False)

            self.fancyName = ":cop: jailer"
            self.revealString = f" is the {self.fancyName}"
            self.deadString = f" was the {self.fancyName}"

        elif self.name == "fool":
            self.revealEmbed = discord.Embed(title=":clown: You are the fool",
                                             description="If you get voted to get executed at day time, you win, but if you get killed by something else you lose.",
                                             color=0xfff100)
            self.revealEmbed.add_field(name="How to win:", value="Get voted to be executed", inline=False)

            self.fancyName = ":clown: fool"
            self.revealString = f" is the {self.fancyName}"
            self.deadString = f" was the {self.fancyName}"

        elif self.name == "werewolf":
            self.revealEmbed = discord.Embed(title=":wolf: You are the werewolf",
                                             description="If it's full moon, you have to kill someone. If you don't choose someone to kill someone will be randomly selected. You work together with the murderer. If the murderer dies, you lose too. Their username will be revealed below.",
                                             color=0xffda83)
            self.revealEmbed.add_field(name="How to win:", value="Kill everyone except for the :dagger: murderer",
                                       inline=False)

            self.fancyName = ":wolf: werewolf"
            self.revealString = f" is the {self.fancyName}"
            self.deadString = f" was the {self.fancyName}"

            self.unlockRoleChannelAtNightTime = False

            self.killedSomeone = False

        elif self.name == "hunter":
            self.revealEmbed = discord.Embed(title="<:hunter:863746095930540032> You are the hunter",
                                             description="Each night you can choose to shoot someone, but if they're not the murderer or werewolf you die and they don't.",
                                             color=0xc1694f)
            self.revealEmbed.add_field(name="How to win:", value="Kill the :dagger: murderer", inline=False)

            self.fancyName = "<:hunter:863746095930540032> hunter"
            self.revealString = f" is the {self.fancyName}"
            self.deadString = f" was the {self.fancyName}"

            self.abilityUsed = False
            self.permAbilityUsed = False

        elif self.name == "cupid":
            self.revealEmbed = discord.Embed(title="<:bow_and_heart:841964296765177896> You are the cupid",
                                             description="You can choose to make 2 players (including yourself) fall in love with each other. Players in love can talk to each other during night time, but if one of them dies the other one dies too. If the murderer falls in love with a villager, the murderer must murder everyone except for their lover.",
                                             color=0xf4acba)
            self.revealEmbed.add_field(name="How to win:", value="Kill the :dagger: murderer",
                                       inline=False)

            self.fancyName = "<:bow_and_heart:841964296765177896> cupid"
            self.revealString = f" is the {self.fancyName}"
            self.deadString = f" was the {self.fancyName}"

            self.abilityUsed = False
            self.permAbilityUsed = False

            self.choosingSecondPlayer = False

            self.firstLover = None
            self.secondLover = None

        elif self.name == "none":
            self.revealEmbed = discord.Embed(title="You don't have a special role.",
                                             description="You don't have any special abilities this game. During night time you can use the shop.",
                                             color=0x00ff2d)
            self.revealEmbed.add_field(name="How to win:", value="Kill the murderer")

            self.fancyName = ":bust_in_silhouette: Role-less"
            self.revealString = " doesn't have a special role"
            self.deadString = " didn't have any special role"


        else:
            self.revealEmbed = discord.Embed(title="Something went wrong!",
                                             description="It looks like you somehow got an invalid role. This message shouldn't be able to appear.")
            self.revealEmbed.add_field(name="How to win:", value="Don't ask me, I have no idea.", inline=False)
            self.revealEmbed.add_field(name="Maybe you should report this as a bug",
                                       value="then I might be able to fix it or something", inline=False)

            self.fancyName = "Invalid role (this message shouldn't be able to appear)"
            self.revealString = " somehow has an invalid role, that shouldn't be able to happen. Weird."
            self.deadString = " somehow had an invalid role, that should't be able to happen. Weird."

    def addPlayersToEmbed(self, embed):
        # this is stored in a variable because if someone leaves during the night we don't want it to shift all the indexes and make the player select the wrong person
        if self.name == "murderer":
            if self.game.findRole("werewolf") is not None:
                self.currentPlayerList = self.game.getPlayersListExcluding(
                    [self.player, self.game.findRole("werewolf")])
            else:
                self.currentPlayerList = self.game.getPlayersListExcluding(self.player)
        elif self.name == "werewolf":
            self.currentPlayerList = self.game.getPlayersListExcluding([self.player, self.game.findRole("murderer")])
        elif self.name == "cupid":
            if not self.choosingSecondPlayer:
                self.currentPlayerList = self.game.players.copy()
            else:
                print(f"{self.firstLover.member.display_name}")
                self.currentPlayerList = self.game.getPlayersListExcluding(self.firstLover)
        else:
            self.currentPlayerList = self.game.getPlayersListExcluding(self.player)

        for player in self.currentPlayerList:
            embed.add_field(name=f"{self.currentPlayerList.index(player)}: {player.member.display_name}",
                            value="Type this number to select this player", inline=True)
        return embed

    def getRoleList(self):
        # this is stored in a variable because if someone leaves during the night we don't want it to shift all the indexes and make the player select the wrong person
        self.currentPlayerList = self.game.getPlayersListExcluding(self.player)
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

    async def sendRoleChannelEmbed(self):
        if self.name == "murderer":
            if self.game.moon != 1:
                embed = self.addPlayersToEmbed(
                    discord.Embed(title="Choose someone to kill", description="Type a number bellow to kill someone",
                                  color=0xff0b00))
                await self.player.roleChannel.send(embed=embed)
            else:
                await self.player.roleChannel.send(
                    embed=discord.Embed(title=":new_moon: It's too dark to locate a target",
                                        description="The moon isn't visible, and because of that it's so dark that you can't see anything. You can't murder someone while it's this dark.",
                                        color=0xff0000))
                await self.player.roleChannel.set_permissions(self.player.member, read_messages=True,
                                                              send_messages=False)

        elif self.name == "detective":
            if hasattr(self, "revealedDetectiveEmbed"):
                if not self.revealedDetectiveEmbed:
                    self.revealedDetectiveEmbed = True
                    await self.player.roleChannel.send(embed=self.revealNextNight)

            if self.game.weatherIntensity > 90 and self.game.weatherIntensity <= 95:
                await self.player.roleChannel.send(
                    embed=discord.Embed(title=":fog: Because of the foggy weather you can't investigate a player",
                                        description="You can investigate a player again when there's no foggy weather anymore",
                                        color=0xff0000))
                await self.player.roleChannel.set_permissions(self.player.member, send_messages=False,
                                                              read_messages=True)

            else:
                embed = self.addPlayersToEmbed(discord.Embed(title="Choose someone to reveal their role",
                                                             description="type a number below to reveal their role",
                                                             color=0x00afff))
                await self.player.roleChannel.send(embed=embed)

        elif self.name == "doctor":
            if not self.roleChannelEmbedSent:
                await self.player.roleChannel.send(embed=discord.Embed(title="No one needs to be revived yet!",
                                                                       description="When the murderer kills someone, we'll let you know here. You can choose to revive them or not, but you can only use this ability once.",
                                                                       color=0x00afff))
                self.roleChannelEmbedSent = True

        elif self.name == "broadcaster":
            self.messageMode = False
            if self.game.weatherIntensity > 80 and self.game.weatherIntensity <= 90:
                await self.player.roleChannel.send(embed=discord.Embed(
                    title=":thunder_cloud_rain: Because of the stormy weather your broadcasting equipment isn't working",
                    description="You can't send a broadcast this night.", color=0xff0000))
                await self.player.roleChannel.set_permissions(self.player.member, send_messages=False,
                                                              read_messages=True)

            else:
                embed = self.addRolesToEmbed(discord.Embed(title="Choose a role to send a message to",
                                                           description="Type a number bellow to select a role and the person with that role will receive a message of your choice.",
                                                           color=0x19ff00))
                embed.add_field(name=f"{len(self.currentRolesList)} Everyone",
                                value="Type this number to select everyone",
                                inline=True)

                await self.player.roleChannel.send(embed=embed)

        elif self.name == "thief":
            embed = self.addPlayersToEmbed(discord.Embed(title="Choose someone to steal from",
                                                         description="There is a 50% chance that you will steal half of their :coin: gold",
                                                         color=0x4a4a4a))
            await self.player.roleChannel.send(embed=embed)


        elif self.name == "jailer":
            embed = self.addPlayersToEmbed(discord.Embed(title="Choose someone to put in jail",
                                                         description="They will be put in jail the next night. While in jail, they can't use their role's ability or use the shop.",
                                                         color=0x00b8ff))
            await self.player.roleChannel.send(embed=embed)


        elif self.name == "werewolf":
            if self.game.moon == 5:
                embed = self.addPlayersToEmbed(
                    discord.Embed(title="Choose someone to kill",
                                  description="Type a number bellow to kill someone. If you don't choose someone, someone will be randomly chosen.",
                                  color=0xffda83))
                await self.player.roleChannel.send(embed=embed)
                await self.player.roleChannel.set_permissions(self.player.member, send_messages=True,
                                                              read_messages=True)
            else:
                await self.player.roleChannel.send(
                    embed=discord.Embed(title="You can only use your ability during full moon",
                                        description="When it's full moon, you have to choose to kill someone. If you don't choose someone, someone will be randomly selected.",
                                        color=0x4a4a4a))

        elif self.name == "hunter":
            if not self.permAbilityUsed:
                await self.player.roleChannel.send(embed=self.addPlayersToEmbed(
                    discord.Embed(title="Choose someone to shoot",
                                  description="If they're not the :dagger: murderer or :wolf: werewolf, you die and they don't.",
                                  color=0xc1694f)))


        elif self.name == "cupid":
            if not self.permAbilityUsed:
                self.choosingSecondPlayer = False
                await self.player.roleChannel.send(embed=self.addPlayersToEmbed(
                    discord.Embed(title="Choose 2 players to fall in love",
                                  description="You can choose to make 2 players (including yourself) fall in love with each other. Players in love can talk to each other during night time, but if one of them dies the other one dies too. If the murderer falls in love with a villager, the murderer must murder everyone except for their lover.\n\nChoose the first player now, and then choose the other player. You can only use this ability one",
                                  color=0xf4acba)))

    async def processRoleChannelCommand(self, message):
        if not self.player.inJail:
            if self.name == "murderer":
                if self.game.moon != 1:
                    choice = -1
                    nonNumber = False
                    try:
                        choice = int(message.content)
                    except ValueError:
                        await self.player.roleChannel.send("Please enter a number!")
                        nonNumber = True

                    if choice != -1 and choice >= 0 and choice < len(self.currentPlayerList):
                        if self.abilityUsed == False:
                            if self.currentPlayerList[choice] in self.game.players:
                                # queue the player to die the next morning (if the doctor doesn't heal them)
                                self.game.willDieNextMorning.append(
                                    {"player": self.currentPlayerList[choice], "title": " got killed",
                                     "DM": ":skull: You got killed by the murderer!"})
                                self.abilityUsed = True

                                # part where the doctor gets notified that someone has been killed
                                if self.game.findRole("doctor") is not None:
                                    if self.game.findRole("doctor").inGame:
                                        if not self.game.findRole("doctor").role.permAbilityUsed:
                                            self.game.findRole("doctor").role.healable = self.currentPlayerList[choice]
                                            # send a message to the doctor that someone was killed
                                            if self.currentPlayerList[choice] == self.game.findRole("doctor"):
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

                                            await self.game.findRole("doctor").roleChannel.send(embed=embed)
                                            # set permissions for doctor channel
                                            if not self.game.findRole("doctor").inJail:
                                                await self.game.findRole("doctor").roleChannel.set_permissions(
                                                    self.game.findRole("doctor").member, read_messages=True,
                                                    send_messages=True)

                                # send confirmation message
                                await self.player.roleChannel.send(embed=discord.Embed(
                                    title=f":dagger: You stabbed {self.currentPlayerList[choice].member.display_name}",
                                    description="If they don't get healed by the doctor tonight, they will die next morning.",
                                    color=0xff0b00))
                                # set permissions for murderer channel
                                await self.player.roleChannel.set_permissions(self.player.member, read_messages=True,
                                                                              send_messages=False)

                            else:
                                await self.player.roleChannel.send(
                                    embed=discord.Embed(title="That player is no longer in the game",
                                                        description="They might've left the game, please try a different player!",
                                                        color=0xff0000))
                    else:
                        if not nonNumber:
                            await self.player.roleChannel.send(
                                f"Please enter a number between 0 and {len(self.currentPlayerList) - 1}!")

            elif self.name == "detective":
                nonNumber = False
                choice = -1
                try:
                    choice = int(message.content)
                except ValueError:
                    await self.player.roleChannel.send("Please enter a number!")
                    nonNumber = True

                if choice != -1 and choice >= 0 and choice < len(self.currentPlayerList):
                    if self.abilityUsed == False:
                        if self.currentPlayerList[choice] in self.game.players:
                            self.revealNextNight = discord.Embed(
                                title=f"{self.currentPlayerList[choice].member.display_name}{self.currentPlayerList[choice].role.revealString}",
                                color=0x00a1ff)
                            self.revealedDetectiveEmbed = False
                            await self.player.roleChannel.send(embed=discord.Embed(title="Investigation started!",
                                                                                   description=f"You started investigating {self.currentPlayerList[choice].member.mention}.",
                                                                                   color=0x00a1ff))

                            await self.player.roleChannel.set_permissions(self.player.member, read_messages=True,
                                                                          send_messages=False)

                        else:
                            await self.player.roleChannel.send(
                                embed=discord.Embed(title="That player is no longer in the game",
                                                    description="They might've left the game, please try a different player!",
                                                    color=0xff0000))

                else:
                    if not nonNumber:
                        await self.player.roleChannel.send(
                            f"Please enter a number between 0 and {len(self.currentPlayerList) - 1}!")

            elif self.name == "doctor":
                if not self.permAbilityUsed:
                    if hasattr(self, "healable"):
                        if self.healable in self.game.players:
                            if message.content.strip().lower() == "yes":
                                removedThePlannedDeath = False
                                for deathData in self.game.willDieNextMorning:
                                    if deathData["player"] == self.healable:
                                        self.game.willDieNextMorning.remove(deathData)
                                        removedThePlannedDeath = True

                                if removedThePlannedDeath:
                                    self.permAbilityUsed = True
                                    await self.player.roleChannel.send(
                                        embed=discord.Embed(title=f"You healed this player!",
                                                            description="They will no longer die next morning. Your ability to heal has been used and is no longer usable for the rest of the game.",
                                                            color=0x00ff0d))
                                    await self.player.roleChannel.set_permissions(self.player.member,
                                                                                  read_messages=True,
                                                                                  send_messages=False)
                                else:
                                    self.player.roleChannel.send(embed=discord.Embed(
                                        title=f"Unable to find this person in the list of players that will die next morning!",
                                        description="Somehow they weren't in the list of players that will die next morning, and thus can't be removed from it. Your ability was not used and that player shouldn't die next morning.",
                                        color=0xff000d))
                                    await self.player.roleChannel.set_permissions(self.player.member,
                                                                                  read_messages=True,
                                                                                  send_messages=False)

                            elif message.content.strip().lower() == "no":
                                await self.player.roleChannel.send(
                                    embed=discord.Embed(title=f"You chose to not heal this player.",
                                                        description="They will die next morning.", color=0xff0b00))
                                await self.player.roleChannel.set_permissions(self.player.member, read_messages=True,
                                                                              send_messages=False)
                            else:
                                await self.player.roleChannel.send("Please type yes or no")
                        else:
                            await self.player.roleChannel.send(
                                embed=discord.Embed(title="That player is no longer in the game",
                                                    description="They might've left the game"))
                            await self.player.roleChannel.set_permissions(self.player.member, read_messages=True,
                                                                          send_messages=False)

            elif self.name == "broadcaster":
                if not self.messageMode:
                    if not self.abilityUsed:
                        nonNumber = False
                        choice = -1
                        try:
                            choice = int(message.content)
                        except ValueError:
                            await self.player.roleChannel.send("Please enter a number!")
                            nonNumber = True

                        if choice >= 0 and choice <= len(self.currentRolesList):
                            if choice != len(self.currentRolesList):
                                if self.game.findRole(self.currentRolesList[choice].name) is not None:
                                    self.messageMode = True
                                    self.messageTo = self.game.findRole(self.currentRolesList[choice].name)
                                    embed = discord.Embed(
                                        title=f"What would you like to send to the {self.game.findRole(self.currentRolesList[choice].name).role.fancyName}?",
                                        description="They won't be able to see your username. Keep in mind that the normal chat rules still apply. Please do not send any inappropriate or rude message.",
                                        color=0x19ff00)
                                    embed.add_field(name='To cancel, type "cancel"',
                                                    value='If you want to select a different player, type "cancel".',
                                                    inline=False)
                                    await self.player.roleChannel.send(embed=embed)
                                else:
                                    await self.player.roleChannel.send(
                                        embed=discord.Embed(title="The player with that role is no longer in the game!",
                                                            description="They might've left the game", color=0xff0b00))
                            else:
                                # selected to broadcast to everyone
                                self.messageMode = True
                                self.messageTo = "everyone"
                                embed = discord.Embed(title=f"What would you like to send to everyone?",
                                                      description="They won't be able to see your username. Keep in mind that the normal chat rules still apply. Please do not send any inappropriate or rude message.",
                                                      color=0x19ff00)
                                embed.add_field(name='To cancel, type "cancel"',
                                                value='If you want to select a different role to send a message to, type "cancel".',
                                                inline=False)
                                await self.player.roleChannel.send(embed=embed)

                        else:
                            if not nonNumber:
                                await self.player.roleChannel.send(
                                    f"Please enter a number between 0 and {len(self.currentPlayerList)}!")

                else:
                    if not self.abilityUsed:
                        if message.content.lower() != "cancel":
                            if self.messageTo != "everyone":
                                if self.messageTo in self.game.players:
                                    bc = broadcast(message.content, self.player, self.messageTo, False)
                                    self.broadcastsToBeSent.append(bc)
                                    self.abilityUsed = True
                                    await self.player.roleChannel.set_permissions(self.player.member,
                                                                                  read_messages=True,
                                                                                  send_messages=False)
                                    m = message.content.replace("```", "")
                                    await self.player.roleChannel.send(embed=discord.Embed(title="Broadcast sent!",
                                                                                           description=f"The broadcast won't be received immediately, but next night.\nThe {self.messageTo.role.fancyName} will receive the following message next night: \n \n ```{m}```"))
                                    await self.player.roleChannel.set_permissions(self.player.member,
                                                                                  read_messages=True,
                                                                                  send_messages=False)
                                else:
                                    await self.player.roleChannel.send(
                                        embed=discord.Embed(title="That player is no longer in this game.",
                                                            description="They might've left. Try a different role!",
                                                            color=0xff0b00))
                                    await self.sendRoleChannelEmbed()
                            else:
                                for player in self.game.players:
                                    if player != self.player:
                                        bc = broadcast(message.content, self.player, player, True)
                                        self.broadcastsToBeSent.append(bc)
                                m = message.content.replace("```", "")
                                await self.player.roleChannel.send(embed=discord.Embed(title="Broadcast sent!",
                                                                                       description=f"The broadcast won't be received immediately, but next night.\nEveryone will receive the following message next night: \n \n```{m}```",
                                                                                       color=0x19ff00))
                                await self.player.roleChannel.set_permissions(self.player.member, read_messages=True,
                                                                              send_messages=False)
                        else:
                            await self.sendRoleChannelEmbed()


            elif self.name == "thief":
                if not self.abilityUsed:
                    nonNumber = False
                    choice = -1
                    try:
                        choice = int(message.content)
                    except ValueError:
                        await self.player.roleChannel.send("Please enter a number!")
                        nonNumber = True

                    if choice != -1 and choice >= 0 and choice < len(self.currentPlayerList):
                        if self.abilityUsed == False:
                            if self.currentPlayerList[choice] in self.game.players:
                                if random.randint(0, 1) == 1:
                                    self.abilityUsed = True
                                    moneyStolen = round(self.currentPlayerList[choice].gold / 2 + 0.1)
                                    self.currentPlayerList[choice].gold -= moneyStolen
                                    self.player.gold += moneyStolen
                                    await self.player.roleChannel.send(embed=discord.Embed(
                                        title=f"You stole :coin: {moneyStolen} gold from {self.currentPlayerList[choice].member.display_name}",
                                        color=0x00ff00))

                                    await self.player.roleChannel.set_permissions(self.player.member,
                                                                                  read_messages=True,
                                                                                  send_messages=False)

                                    await self.currentPlayerList[choice].nightChannel.send(embed=discord.Embed(
                                        title=f"The :unlock: thief stole :coin: {moneyStolen} gold from you!",
                                        color=0xff0000))

                                    objectives.addObjectiveProgress(self.player.member, "thiefStealCoins", moneyStolen)

                                else:
                                    self.abilityUsed = True
                                    await self.player.roleChannel.send(embed=discord.Embed(
                                        title=f"You tried to steal from {self.currentPlayerList[choice].member.display_name}, but failed!",
                                        color=0xff0000))

                                    await self.player.roleChannel.set_permissions(self.player.member,
                                                                                  read_messages=True,
                                                                                  send_messages=False)



                            else:
                                await self.player.roleChannel.send(
                                    embed=discord.Embed(title="That player is no longer in the game",
                                                        description="They might've left the game, please try a different player!",
                                                        color=0xff0000))

                    else:
                        if not nonNumber:
                            await self.player.roleChannel.send(
                                f"Please enter a number between 0 and {len(self.currentPlayerList) - 1}!")

            elif self.name == "jailer":
                nonNumber = False
                choice = -1
                try:
                    choice = int(message.content)
                except ValueError:
                    await self.player.roleChannel.send("Please enter a number!")
                    nonNumber = True

                if choice != -1 and choice >= 0 and choice < len(self.currentPlayerList):
                    if not self.abilityUsed:
                        if self.currentPlayerList[choice] in self.game.players:
                            self.abilityUsed = True
                            await self.player.roleChannel.set_permissions(self.player.member, read_messages=True,
                                                                          send_messages=False)
                            self.jailedNext = self.currentPlayerList[choice]
                            await self.player.roleChannel.send(embed=discord.Embed(
                                title=f"{self.currentPlayerList[choice].member.display_name} will be jailed next night",
                                color=0x00ff00))
                            await self.player.game.sendToAllNightChannels(embed=discord.Embed(
                                title=f":cop: {self.jailedNext.member.display_name} will get jailed next night",
                                description="When in jail, they won't be able to use their role's ability or the shop",
                                color=0xff0000))
                        else:
                            await self.player.roleChannel.send(
                                embed=discord.Embed(title="That player is no longer in the game",
                                                    description="They might've left the game, please try a different player!",
                                                    color=0xff0000))
                else:
                    if not nonNumber:
                        await self.player.roleChannel.send(
                            f"Please enter a number between 0 and {len(self.currentPlayerList) - 1}!")

            elif self.name == "werewolf":
                if self.game.moon == 5:
                    choice = -1
                    nonNumber = False
                    try:
                        choice = int(message.content)
                    except ValueError:
                        await self.player.roleChannel.send("Please enter a number!")
                        nonNumber = True

                    if choice != -1 and 0 <= choice < len(self.currentPlayerList):
                        if not self.abilityUsed:
                            if self.game.moon == 5:
                                if self.currentPlayerList[choice] in self.game.players:
                                    # queue the player to die the next morning
                                    self.game.willDieNextMorning.append(
                                        {"player": self.currentPlayerList[choice], "title": " got killed",
                                         "DM": ":skull: You got killed by the werewolf!"})
                                    self.abilityUsed = True

                                    # send confirmation message
                                    await self.player.roleChannel.send(embed=discord.Embed(
                                        title=f":wolf: You killed {self.currentPlayerList[choice].member.display_name}",
                                        description="If they don't have any items protecting them from dying, they will die next morning.",
                                        color=0xffda83))
                                    self.killedSomeone = True
                                    # set permissions for channel
                                    await self.player.roleChannel.set_permissions(self.player.member,
                                                                                  read_messages=True,
                                                                                  send_messages=False)

                                else:
                                    await self.player.roleChannel.send(
                                        embed=discord.Embed(title="That player is no longer in the game",
                                                            description="They might've left the game, please try a different player!",
                                                            color=0xff0000))
                            else:
                                await self.player.roleChannel.send(":x: You can only do this during full moon!")
                    else:
                        if not nonNumber:
                            await self.player.roleChannel.send(
                                f"Please enter a number between 0 and {len(self.currentPlayerList) - 1}!")


            elif self.name == "hunter":
                choice = -1
                nonNumber = False
                try:
                    choice = int(message.content)
                except ValueError:
                    await self.player.roleChannel.send("Please enter a number!")
                    nonNumber = True

                if choice != -1 and 0 <= choice < len(self.currentPlayerList):
                    if not self.permAbilityUsed:
                        if self.currentPlayerList[choice] in self.game.players:
                            if self.currentPlayerList[choice].role.name == "murderer" or self.currentPlayerList[choice].role.name == "werewolf":
                                self.game.willDieNextMorning.append(
                                    {"player": self.currentPlayerList[choice], "title": " got killed",
                                     "DM": ":skull: You got shot by the hunter!"})
                                self.permAbilityUsed = True
                            else:
                                self.game.willDieNextMorning.append({"player": self.player, "title": " got killed",
                                                                     "DM": ":skull: The person you shot wasn't the :dagger: murderer or :wolf: werewolf!"})
                                self.permAbilityUsed = True

                            await self.player.roleChannel.send(embed=discord.Embed(
                                title=f"<:hunter:863746095930540032> You shot {self.currentPlayerList[choice].member.display_name}",
                                description="If they're the :dagger: murderer or :wolf: werewolf, they will die next morning, but if they're not you will die.",
                                color=0xc1694f))
                            await self.player.roleChannel.set_permissions(self.player.member, send_messages=False,
                                                                          read_messages=True)
                        else:
                            await self.player.roleChannel.send(
                                embed=discord.Embed(title="That player is no longer in the game",
                                                    description="They might've left the game, please try a different player!",
                                                    color=0xff0000))
                else:
                    if not nonNumber:
                        await self.player.roleChannel.send(
                            f"Please enter a number between 0 and {len(self.currentPlayerList) - 1}!")

            elif self.name == "cupid":
                choice = -1
                nonNumber = False
                try:
                    choice = int(message.content)
                except ValueError:
                    if message.content.lower() != "cancel":
                        await self.player.roleChannel.send("Please enter a number!")
                        nonNumber = True
                if not message.content.lower() == "cancel":
                    if choice != -1 and 0 <= choice < len(self.currentPlayerList):
                        if not self.permAbilityUsed:
                            if not self.choosingSecondPlayer:
                                if self.currentPlayerList[choice] in self.game.players:
                                    self.firstLover = self.currentPlayerList[choice]
                                    self.choosingSecondPlayer = True
                                    await self.player.roleChannel.send(embed=self.addPlayersToEmbed(discord.Embed(
                                        title="Now choose a second player to fall in love with the first one you selected",
                                        description="""To cancel and go back to selecting the first player, type "cancel".""",
                                        color=0xf4acba)))
                                else:
                                    await self.player.roleChannel.send(
                                        embed=discord.Embed(title="That player is no longer in the game",
                                                            description="They might've left the game, please try a different player!",
                                                            color=0xff0000))
                            else:
                                if self.currentPlayerList[choice] in self.game.players:
                                    if self.firstLover in self.game.players:
                                        self.secondLover = self.currentPlayerList[choice]
                                        await self.player.roleChannel.set_permissions(self.player.member,
                                                                                      read_messages=True,
                                                                                      send_messages=False)
                                        await self.player.roleChannel.send(embed=discord.Embed(
                                            title=f":heart: {self.firstLover.member.display_name} and {self.secondLover.member.display_name} are now in love with each other",
                                            color=0xf4acba))
                                        self.permAbilityUsed = True

                                        self.firstLover.inLove = True
                                        self.firstLover.lover = self.secondLover
                                        self.secondLover.inLove = True
                                        self.secondLover.lover = self.firstLover

                                        await self.firstLover.nightChannel.send(embed=discord.Embed(
                                            title="<:bow_and_heart:841964296765177896> The cupid hit you with a love arrow!",
                                            color=0xf4acba))
                                        await self.secondLover.nightChannel.send(embed=discord.Embed(
                                            title="<:bow_and_heart:841964296765177896> The cupid hit you with a love arrow!",
                                            color=0xf4acba))
                                        self.firstLover.loveChannel = await self.game.category.create_text_channel(
                                            f"talk with {self.secondLover.member.display_name}")
                                        await self.firstLover.loveChannel.set_permissions(self.firstLover.member,
                                                                                          send_messages=True,
                                                                                          read_messages=True)
                                        await self.firstLover.loveChannel.set_permissions(self.secondLover.member,
                                                                                          send_messages=True,
                                                                                          read_messages=True)
                                        self.game.channels.append(self.firstLover.loveChannel)
                                        self.secondLover.loveChannel = self.firstLover.loveChannel
                                        await self.firstLover.nightChannel.send(embed=discord.Embed(
                                            title=f":heart: You are now in love with {self.secondLover.member.display_name}!",
                                            description=f"If they die, you die too. You can talk to them during the night in {self.firstLover.loveChannel.mention}",
                                            color=0xea596e))
                                        await self.secondLover.nightChannel.send(embed=discord.Embed(
                                            title=f":heart: You are now in love with {self.firstLover.member.display_name}!",
                                            description=f"If they die, you die too. You can talk to them during the night in {self.firstLover.loveChannel.mention}",
                                            color=0xea596e))

                                        if self.firstLover.role.name == "murderer":
                                            if self.secondLover.role.name != "werewolf":
                                                await self.secondLover.nightChannel.send(embed=discord.Embed(
                                                    title="Your lover is the :dagger: murderer, your goal has changed!",
                                                    description="Your new goal is to kill everyone except your lover so you're the last 2 left.",
                                                    color=0xff0000))
                                                if self.game.findRole("werewolf") is None:
                                                    await self.firstLover.nightChannel.send(
                                                        embed=discord.Embed(title="Your goal has changed",
                                                                            description="Your new goal is to kill everyone except for your lover. Your lover knows you're the murderer.",
                                                                            color=0x00ff00))
                                                else:
                                                    await self.firstLover.nightChannel.send(
                                                        embed=discord.Embed(title="Your goal has changed",
                                                                            description="Your new goal is to kill everyone except for your lover and the :wolf: werewolf. Your lover knows you're the murderer.",
                                                                            color=0x00ff00))

                                        elif self.secondLover.role.name == "murderer":
                                            if self.firstLover.role.name != "werewolf":
                                                await self.firstLover.nightChannel.send(embed=discord.Embed(
                                                    title="Your lover is the :dagger: murderer, your goal has changed!",
                                                    description="Your new goal is to kill everyone except your lover so you're the last 2 left.",
                                                    color=0xff0000))
                                                if self.game.findRole("werewolf") is None:
                                                    await self.secondLover.nightChannel.send(
                                                        embed=discord.Embed(title="Your goal has changed",
                                                                            description="Your new goal is to kill everyone except for your lover. Your lover knows you're the murderer.",
                                                                            color=0x00ff00))
                                                else:
                                                    await self.secondLover.nightChannel.send(
                                                        embed=discord.Embed(title="Your goal has changed",
                                                                            description="Your new goal is to kill everyone except for your lover and the :wolf: werewolf. Your lover knows you're the murderer.",
                                                                            color=0x00ff00))

                                        elif self.firstLover.role.name == "werewolf":
                                            if self.secondLover.role.name != "murderer":
                                                await self.firstLover.roleChannel.send(
                                                    embed=discord.Embed(title="Your goal has changed",
                                                                        description="Your new goal is to kill everyone except for the :dagger: murderer and your lover. Your lover's goal is still to kill the murderer, and they don't know that you're the werewolf."))


                                        elif self.firstLover.role.name == "werewolf":
                                            if self.secondLover.role.name != "murderer":
                                                await self.firstLover.roleChannel.send(
                                                    embed=discord.Embed(title="Your goal has changed",
                                                                        description="Your new goal is to kill everyone except for the :dagger: murderer and your lover. Your lover's goal is still to kill the murderer, and they don't know that you're the werewolf.",
                                                                        color=0xea596e))

                                        elif self.firstLover.role.name == "fool":
                                            await self.firstLover.nightChannel.send(
                                                embed=discord.Embed(title="Your goal doesn't change",
                                                                    description="Your goal hasn't changed since you've fallen in love. You still need to be executed to win.",
                                                                    color=0xfff100))

                                        elif self.secondLover.role.name == "fool":
                                            await self.firstLover.nightChannel.send(
                                                embed=discord.Embed(title="Your goal doesn't change",
                                                                    description="Your goal hasn't changed since you've fallen in love. You still need to be executed to win.",
                                                                    color=0xfff100))

                                        await self.firstLover.loveChannel.send(embed=discord.Embed(
                                            title=f":heart: {self.firstLover.member.display_name} and {self.secondLover.member.display_name} are now in love with each other",
                                            description="If one of you dies, the other one dies too. If one of you is the murderer, you both must kill everyone except for your lover.",
                                            color=0xea596e))



                                    else:
                                        await self.player.roleChannel.send(embed=discord.Embed(
                                            title="The first player you selected left the game while you were selecting the second one.",
                                            description="Please try again!", color=0xff0000))
                                        self.choosingSecondPlayer = False
                                        await self.sendRoleChannelEmbed()
                                else:
                                    await self.player.roleChannel.send(
                                        embed=discord.Embed(title="That player is no longer in the game",
                                                            description="They might've left the game, please try a different player!",
                                                            color=0xff0000))
                    else:
                        if not nonNumber:
                            await self.player.roleChannel.send(
                                f"Please enter a number between 0 and {len(self.currentPlayerList) - 1}!")
                else:
                    if self.choosingSecondPlayer:
                        self.choosingSecondPlayer = False
                        await self.sendRoleChannelEmbed()
                    else:
                        await self.player.roleChannel.send("Please enter a number!")



        else:
            await self.player.roleChannel.send(
                embed=discord.Embed(title=":x: You can't do that while you're in jail!", color=0xff0000))


class broadcast:
    def __init__(self, content, sender, receiver, toEveryone):
        self.content = content.replace("```", "")
        self.receiver = receiver
        self.game = self.receiver.game
        self.receiver.lastBroadcast = self
        self.replied = False
        if toEveryone:
            self.receiverName = "everyone"
        else:
            self.receiverName = self.receiver.role.fancyName
        self.embed = discord.Embed(title=":radio: Incoming broadcast!",
                                   description=f"sender: :radio: Broadcaster\nreceiver: {self.receiverName}\n\n```{self.content}```",
                                   color=0x19ff00)
        self.sender = sender

    async def send(self):
        if hasattr(self.receiver, "broadcastChannel"):
            await self.receiver.broadcastChannel.send(embed=self.embed)
        else:
            self.receiver.broadcastChannel = await self.game.category.create_text_channel("Broadcasts")
            await self.receiver.broadcastChannel.set_permissions(self.game.role, read_messages=False,
                                                                 send_messages=False)
            await self.receiver.broadcastChannel.set_permissions(self.receiver.member, read_messages=True,
                                                                 send_messages=False)
            self.game.channels.append(self.receiver.broadcastChannel)
            await self.send()

    async def reply(self, content):
        if hasattr(self.sender, "repliesChannel"):
            self.replied = True
            usableContent = content.replace("```", "")
            await self.sender.repliesChannel.send(embed=discord.Embed(title=":radio: Incoming reply!",
                                                                      description=f"sender: {self.receiver.role.fancyName}\nreceiver: {self.sender.role.fancyName}\n\n```{usableContent}```",
                                                                      color=0x00ff00))
        else:
            self.sender.repliesChannel = await self.game.category.create_text_channel("Broadcast replies")
            await self.sender.repliesChannel.set_permissions(self.game.role, read_messages=False, send_messages=False)
            await self.sender.repliesChannel.set_permissions(self.sender.member, read_messages=True,
                                                             send_messages=False)
            self.game.channels.append(self.sender.repliesChannel)
            await self.reply(content)
