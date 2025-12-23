import discord
import items
import dataStorage


def getTutorialEmbeds(guild) -> dict:
    p = dataStorage.getGuildData(guild, "prefix", default="!")
    embeds = {}
    embeds["game"], embeds["roles"], embeds["items"], embeds["commands"] = [], [], [], []
    embeds["game"].append(discord.Embed(title="Welcome to Murder Mystery!",
                          description="This is a game of Murder Mystery inside of discord. Every player receives a role, and one of them is the murderer. All the other players must figure out who the murderer and kill them is before the murderer kills them first!",
                          color=0x00b8ff))
    gameTutorialChannel, rolesTutorialChannel, itemsTutorialChannel, commandsTutorialChannel = guild.get_channel(dataStorage.getGuildData(guild, 'gameTutorialChannel')), guild.get_channel(dataStorage.getGuildData(guild, "rolesTutorialChannel")), guild.get_channel(dataStorage.getGuildData(guild, "itemsTutorialChannel")), guild.get_channel(dataStorage.getGuildData(guild, "commandsTutorialChannel"))
    if dataStorage.getGuildData(guild, "useTutorialChannels") and gameTutorialChannel is not None and rolesTutorialChannel is not None and itemsTutorialChannel is not None and commandsTutorialChannel is not None:
        embed = discord.Embed(title="Tutorial",
                              description=f"This tutorial is split in 4 parts: \n{guild.get_channel(dataStorage.getGuildData(guild, 'gameTutorialChannel')).mention} is about how the game itself works\n{rolesTutorialChannel.mention} is a list of all roles in the game\n{itemsTutorialChannel.mention} is for a list of all items in the game\n{commandsTutorialChannel.mention} is a list of all commands you can use during the game",
                              color=0x00b8ff)
        if dataStorage.getGuildData(guild, "useJoinChannel") and guild.get_channel(dataStorage.getGuildData(guild, "joinChannel")) is not None:
            embed.add_field(name="Joining a game",
                            value=f'To join a game type "{p}join" in {guild.get_channel(dataStorage.getGuildData(guild, "joinChannel")).mention}',
                            inline=False)
        else:
            embed.add_field(name="Joining a game",
                            value=f'To join a game, use the command "{p}join"',
                            inline=False)
        # Fallback: if rolesTutorialChannel is not configured, avoid referencing .mention
        if rolesTutorialChannel is not None:
            roles_ref = rolesTutorialChannel.mention
        else:
            roles_ref = f"the roles list (use {p}advancedHelp or see help-roles)"
        embed.add_field(name="Roles",
                        value=f"Everyone gets a special role assigned, such as murderer, detective, doctor, etc. That role will have special abilities that can only be used at night time. A full list of all roles can be found here: {roles_ref}",
                        inline=False)
        embed.add_field(name="Day/night cycle",
                        value="In the game there's a day/night cycle that will cycle through every few minutes. During the day and night there are multiple things that can happen:",
                        inline=False)
        embeds["game"].append(embed)
        embed = discord.Embed(title=":sunny: During daytime",
                              description="The following things will happen during daytime (in order):", color=0xfff100)
        embed.add_field(name="Sunrise",
                        value="All players will get locked out of their night channels and the daytime channel will open")
        embed.add_field(name="(optional) List of who died that night",
                        value="If someone got killed last night, everyone will be notified when it becomes daytime.",
                        inline=False)
        embed.add_field(name="(optional) Gold per day increase",
                        value="Every day everyone will receive a certain amount of gold. This amount starts at 1, but every 3 days it will increase by 1. If 5 or less players are remaining, it will also increase by 1.",
                        inline=False)
        embed.add_field(name="Everyone will receive gold",
                        value="Gold, the currency of the game, will be given to everyone every morning. The amount can vary depending on the gold per day.",
                        inline=False)
        embed.add_field(name="Vote someone to execute",
                        value="Every day, someone will be voted to be executed. Vote on whoever you think the murderer is, because if the murderer gets executed, you win! You can vote using !vote <player>",
                        inline=False)
        embed.add_field(name="Most voted player gets executed",
                        value="The vote results will be shown and the most voted player will get executed.",
                        inline=False)
        embed.add_field(name="Weather forecast",
                        value="Here the upcoming weather and amount of moonlight for tonight will be shown. Different weather can have different effects on different roles.",
                        inline=False)
        embed.add_field(name="Sunset",
                        value="All players will get locked out of the daytime channel and the nighttime channels will open",
                        inline=False)
        embeds["game"].append(embed)
        embed = discord.Embed(title=":full_moon: During nighttime",
                              description="Unlike day time, night time won't follow a specific order of event that will happen, rather, things will happen based on what you/other players do.\nThe following things can happen during night time:")
        embed.add_field(name="Shop",
                        value=f"During night time, you can access the shop with !shop. In the shop you can spend the gold you earned on a variety of items. For a full list of all available items, see {itemsTutorialChannel.mention}.",
                        inline=False)
        embed.add_field(name="Use your role's special ability",
                        value=f"During the night you can use your role's special ability. For more information, see {rolesTutorialChannel.mention}",
                        inline=False)
        embed.add_field(name="And more!",
                        value=f"What happens during night time depends on what your role is, what other people's roles are, what items you use, ect... For more information, see {rolesTutorialChannel.mention} and {itemsTutorialChannel.mention}.",
                        inline=False)
        embeds["game"].append(embed)
        embed = discord.Embed(title="Items and roles",
                              description=f"For more information about the different roles and items, see {rolesTutorialChannel.mention} and {itemsTutorialChannel.mention}.",
                              color=0x00b8ff)
        embeds["game"].append(embed)

        embed = discord.Embed(title="Roles",
                              description=f"This tutorial is split in 4 parts: \n{gameTutorialChannel.mention} is about how the game itself works\n{rolesTutorialChannel.mention} is a list of all roles in the game\n{itemsTutorialChannel.mention} is for a list of all items in the game\n{commandsTutorialChannel.mention} is a list of all commands you can use during the game\n\nBelow is a list of all roles and their abilities",
                              color=0x00b8ff)
        embed.add_field(name=":dagger: Murderer",
                        value="The murderer can kill 1 player every night.\nGoal: kill everyone\nThis role will always be in the game",
                        inline=False)
        embed.add_field(name=":pill: Doctor",
                        value="When the murderer kills someone, the doctor will get notified. The doctor can choose to heal them or not, but they only can only heal someone 1 time.\nGoal: kill the murderer\nThis role will always be in the game",
                        inline=False)
        embed.add_field(name=":spy: Detective",
                        value="The detective can look at what someone's role is during night time. The role of that player will be revealed next night.\nGoal: kill the murderer\nminimum amount of players needed for this role to appear: 4",
                        inline=False)
        embed.add_field(name=":person_in_tuxedo: banker",
                        value="The banker starts with 3 gold, and receives 1 extra gold per day.\nGoal: kill the murderer\nminimum amount of players needed for this role to appear: 4",
                        inline=False)
        embed.add_field(name=":unlock: thief",
                        value="The thief can choose to steal :coin: gold from someone every night. There is a 50% chance that they will steal half of that player's gold\nGoal: kill the murderer\nminimum amount of players needed for this role to appear: 4",
                        inline=False)
        embed.add_field(name=":cop: jailer",
                        value="Each night the jailer can choose someone to jail. They will be put in jail the next night. While in jail the jailed person cannot use the shop or their role's ability.\ngoal: kill the murderer\nminimum amount of players needed for this role to appear: 5")
        embed.add_field(name=":radio: Broadcaster",
                        value="The broadcaster can send a message to people with a specific role at night time, without knowing who that role belongs to. They can also send a message to everyone at night time. The messages will be received a night later.\nGoal: kill the murderer\nminimum amount of players needed for this role to appear: 6",
                        inline=False)
        embed.add_field(name=":clown: Fool",
                        value="If the fool gets voted to be executed, they win, but if they get killed another way they lose.\nGoal: get voted for execution\nminimum amount of players needed for this role to appear: 6",
                        inline=False)
        embed.add_field(name="<:hunter:863746095930540032> Hunter",
                        value="The hunter can choose to shoot someone during night time, but if their target is not the :dagger: murderer or the :wolf: werewolf then the hunter dies and their target doesn't\nGoal: kill the murderer\nminimum amount of players needed for this role to appear: 6",
                        inline=False)
        embed.add_field(name=":wolf: Werewolf",
                        value="The werewolf works together with the murderer. Every night there is a chance for it to become full moon, and when its full moon the werewolf has to kill someone.\nGoal: kill everyone except the murderer\nminimum amount of players needed for this role to appear: 7",
                        inline=False)
        embed.add_field(name="<:bow_and_heart:841964296765177896> Cupid",
                        value="The cupid can choose 2 players (including themself) and make them fall in love. If a player's lover dies, then they die too. Players in love can talk to each other during night time. If one of the lovers is the :dagger: murderer, then their goal changes to  kill everyone but them\nGoal: kill the murderer\nminimum amount of players needed for this role to appear: 8",
                        inline=False)
        embeds["roles"].append(embed)

        embed = discord.Embed(title="Items",
                              description=f"This tutorial is split in 4 parts: \n{gameTutorialChannel.mention} is about how the game itself works\n{rolesTutorialChannel.mention} is a list of all roles in the game\n{itemsTutorialChannel.mention} is for a list of all items in the game\n{commandsTutorialChannel.mention} is a list of all commands you can use during the game\n\nBelow is a list of all items. While in-game, you can show this list during night time with !shop. Items can be bought at night with !buy <item> and can be used with !use <item> [optional argument].\nSome items have spaces in their names, the name you have to type in to buy or use them is displayed in [] next to the name.",
                              color=0x00b8ff)
        for itemClass in items.getItems(broadcasterInGame=True, role="all"):
            item = itemClass()
            embed.add_field(name=f"{item.name}",
                            value=f"{item.description}\nCost: :coin: {item.cost}\nUsage: {item.usage}\nTo buy, use !buy {item.id}",
                            inline=False)
        embeds["items"].append(embed)

        embed = discord.Embed(title="Commands during game",
                              description=f"This tutorial is split in 4 parts: \n{gameTutorialChannel.mention} is about how the game itself works\n{rolesTutorialChannel.mention} is a list of all roles in the game\n{itemsTutorialChannel.mention} is for a list of all items in the game\n{commandsTutorialChannel.mention} is a list of all commands you can use during the game\n\nBelow is a list of all commands you can use during the game",
                              color=0x00b8ff)
        embed.add_field(name=f"{p}vote @<player>",
                        value="This command is only usable during :sunny: day time\nDuring voting time, use this command to vote on what player should be executed",
                        inline=False)
        embed.add_field(name=f"{p}shop",
                        value="This command is only usable during :full_moon: night time\nUse this command to view the shop.",
                        inline=False)
        embed.add_field(name=f"{p}buy <item>",
                        value="This command is only usable during :full_moon: night time\nUse this command to buy an item from the shop",
                        inline=False)
        embed.add_field(name=f"{p}use <item> [optional argument]",
                        value="Whenever this command is usable during :sunny: day time or :full_moon: night time depends on the item\nUse this command to use an item from your inventory",
                        inline=False)
        embed.add_field(name=f"{p}whisper <player>",
                        value="This command is only usable during :sunny: day time\nUse this command to create a private discussion channel between you and the specified player",
                        inline=False)
        embed.add_field(name=f"{p}leave", value="Use this command to leave the game", inline=False)
        embeds["commands"].append(embed)
        embed = discord.Embed(title="Other commands",
                              description="Below is a list of commands usable outside of a game", color=0x00b8ff)
        if dataStorage.getGuildData(guild, "useJoinChannel") and guild.get_channel(dataStorage.getGuildData(guild, "joinChannel")) is not None:
            embed.add_field(name=f"{p}join",
                            value=f"""Will join a game if one is available or create a new game. Please use this command in {guild.get_channel(dataStorage.getGuildData(guild, "joinChannel")).mention}""",
                            inline=False)
        else:
            embed.add_field(name=f"{p}join",
                            value=f"Will join a game if one is available or create a new game.",
                            inline=False)
        embed.add_field(name=f"{p}list",
                        value="Shows you all running games with their IDs. Useful for when you need a game ID to spectate a game.",
                        inline=False)
        embed.add_field(name=f"{p}spectate <game ID>",
                        value="Spectate a game with the specified game ID. To stop spectating, use !spectate again.",
                        inline=False)
        embed.add_field(name=f"{p}stats <user>",
                        value="Shows you the stats of someone, like how many games they played and how many times they won.",
                        inline=False)
        embed.add_field(name=f"{p}level", value="Checks what level you are and how much XP you need to level up", inline=False)
        embed.add_field(name=f"{p}objective",
                        value="Gives you a new objective or shows how much progress you made in completing your current objective\n\n\nThis is a list of all simple commands. For a list of all possible commands, use **!advancedHelp**",
                        inline=False)
        embeds["commands"].append(embed)
    else:
        embed = discord.Embed(title="Tutorial", color=0x00b8ff)
        if dataStorage.getGuildData(guild, "useJoinChannel") and guild.get_channel(
                dataStorage.getGuildData(guild, "joinChannel")) is not None:
            embed.add_field(name="Joining a game",
                            value=f'To join a game type f"{p}join" in {guild.get_channel(dataStorage.getGuildData(guild, "joinChannel")).mention}',
                            inline=False)
        else:
            embed.add_field(name="Joining a game",
                            value=f'To join a game, use the command f"{p}join"',
                            inline=False)
        embed.add_field(name="Roles",
                        value=f"Everyone gets a special role assigned, such as murderer, detective, doctor, ect... That role will have special abilities that can only be used at night time. A full list of all roles can be found here: {rolesTutorialChannel.mention}",
                        inline=False)
        embed.add_field(name="Day/night cycle",
                        value="In the game there's a day/night cycle that will cycle through every few minutes. During the day and night there are multiple things that can happen:",
                        inline=False)
        embeds["game"].append(embed)
        embed = discord.Embed(title=":sunny: During daytime",
                              description="The following things will happen during daytime (in order):", color=0xfff100)
        embed.add_field(name="Sunrise",
                        value="All players will get locked out of their night channels and the daytime channel will open")
        embed.add_field(name="(optional) List of who died that night",
                        value="If someone got killed last night, everyone will be notified when it becomes daytime.",
                        inline=False)
        embed.add_field(name="(optional) Gold per day increase",
                        value="Every day everyone will receive a certain amount of gold. This amount starts at 1, but every 3 days it will increase by 1. If 5 or less players are remaining, it will also increase by 1.",
                        inline=False)
        embed.add_field(name="Everyone will receive gold",
                        value="Gold, the currency of the game, will be given to everyone every morning. The amount can vary depending on the gold per day.",
                        inline=False)
        embed.add_field(name="Vote someone to execute",
                        value="Every day, someone will be voted to be executed. Vote on whoever you think the murderer is, because if the murderer gets executed, you win! You can vote using !vote <player>",
                        inline=False)
        embed.add_field(name="Most voted player gets executed",
                        value="The vote results will be shown and the most voted player will get executed.",
                        inline=False)
        embed.add_field(name="Weather forecast",
                        value="Here the upcoming weather and amount of moonlight for tonight will be shown. Different weather can have different effects on different roles.",
                        inline=False)
        embed.add_field(name="Sunset",
                        value="All players will get locked out of the daytime channel and the nighttime channels will open",
                        inline=False)
        embeds["game"].append(embed)
        embed = discord.Embed(title=":full_moon: During nighttime",
                              description="Unlike day time, night time won't follow a specific order of event that will happen, rather, things will happen based on what you/other players do.\nThe following things can happen during night time:")
        embed.add_field(name="Shop",
                        value=f"During night time, you can access the shop with !shop. In the shop you can spend the gold you earned on a variety of items.",
                        inline=False)
        embed.add_field(name="Use your role's special ability",
                        value=f"During the night you can use your role's special ability.",
                        inline=False)
        embed.add_field(name="And more!",
                        value=f"What happens during night time depends on what your role is, what other people's roles are, what items you use, ect...",
                        inline=False)
        embeds["game"].append(embed)

        embed = discord.Embed(title="Roles",
                              color=0x00b8ff)
        embed.add_field(name=":dagger: Murderer",
                        value="The murderer can kill 1 player every night.\nGoal: kill everyone\nThis role will always be in the game",
                        inline=False)
        embed.add_field(name=":pill: Doctor",
                        value="When the murderer kills someone, the doctor will get notified. The doctor can choose to heal them or not, but they only can only heal someone 1 time.\nGoal: kill the murderer\nThis role will always be in the game",
                        inline=False)
        embed.add_field(name=":spy: Detective",
                        value="The detective can look at what someone's role is during night time. The role of that player will be revealed next night.\nGoal: kill the murderer\nminimum amount of players needed for this role to appear: 4",
                        inline=False)
        embed.add_field(name=":person_in_tuxedo: banker",
                        value="The banker starts with 3 gold, and receives 1 extra gold per day.\nGoal: kill the murderer\nminimum amount of players needed for this role to appear: 4",
                        inline=False)
        embed.add_field(name=":unlock: thief",
                        value="The thief can choose to steal :coin: gold from someone every night. There is a 50% chance that they will steal half of that player's gold\nGoal: kill the murderer\nminimum amount of players needed for this role to appear: 4",
                        inline=False)
        embed.add_field(name=":cop: jailer",
                        value="Each night the jailer can choose someone to jail. They will be put in jail the next night. While in jail the jailed person cannot use the shop or their role's ability.\ngoal: kill the murderer\nminimum amount of players needed for this role to appear: 5")
        embed.add_field(name=":radio: Broadcaster",
                        value="The broadcaster can send a message to people with a specific role at night time, without knowing who that role belongs to. They can also send a message to everyone at night time. The messages will be received a night later.\nGoal: kill the murderer\nminimum amount of players needed for this role to appear: 6",
                        inline=False)
        embed.add_field(name=":clown: Fool",
                        value="If the fool gets voted to be executed, they win, but if they get killed another way they lose.\nGoal: get voted for execution\nminimum amount of players needed for this role to appear: 6",
                        inline=False)
        embed.add_field(name="<:hunter:863746095930540032> Hunter",
                        value="The hunter can choose to shoot someone during night time, but if their target is not the :dagger: murderer or the :wolf: werewolf then the hunter dies and their target doesn't\nGoal: kill the murderer\nminimum amount of players needed for this role to appear: 6",
                        inline=False)
        embed.add_field(name=":wolf: Werewolf",
                        value="The werewolf works together with the murderer. Every night there is a chance for it to become full moon, and when its full moon the werewolf has to kill someone.\nGoal: kill everyone except the murderer\nminimum amount of players needed for this role to appear: 7",
                        inline=False)
        embed.add_field(name="<:bow_and_heart:841964296765177896> Cupid",
                        value="The cupid can choose 2 players (including themself) and make them fall in love. If a player's lover dies, then they die too. Players in love can talk to each other during night time. If one of the lovers is the :dagger: murderer, then their goal changes to  kill everyone but them\nGoal: kill the murderer\nminimum amount of players needed for this role to appear: 8",
                        inline=False)
        embeds["roles"].append(embed)

        embed = discord.Embed(title="Items",
                              description=f"Below is a list of all items. While in-game, you can show this list during night time with !shop. Items can be bought at night with !buy <item> and can be used with !use <item> [optional argument].\nSome items have spaces in their names, the name you have to type in to buy or use them is displayed in [] next to the name.",
                              color=0x00b8ff)
        for itemClass in items.getItems(broadcasterInGame=True, role="all"):
            item = itemClass()
            embed.add_field(name=f"{item.name}",
                            value=f"{item.description}\nCost: :coin: {item.cost}\nUsage: {item.usage}\nTo buy, use !buy {item.id}",
                            inline=False)
        embeds["items"].append(embed)

        embed = discord.Embed(title="Commands during game",
                              description=f"Below is a list of all commands you can use during the game",
                              color=0x00b8ff)
        embed.add_field(name=f"{p}vote @<player>",
                        value="This command is only usable during :sunny: day time\nDuring voting time, use this command to vote on what player should be executed",
                        inline=False)
        embed.add_field(name=f"{p}shop",
                        value="This command is only usable during :full_moon: night time\nUse this command to view the shop.",
                        inline=False)
        embed.add_field(name=f"{p}buy <item>",
                        value="This command is only usable during :full_moon: night time\nUse this command to buy an item from the shop",
                        inline=False)
        embed.add_field(name=f"{p}use <item> [optional argument]",
                        value="Whenever this command is usable during :sunny: day time or :full_moon: night time depends on the item\nUse this command to use an item from your inventory",
                        inline=False)
        embed.add_field(name=f"{p}whisper <player>",
                        value="This command is only usable during :sunny: day time\nUse this command to create a private discussion channel between you and the specified player",
                        inline=False)
        embed.add_field(name=f"{p}leave", value="Use this command to leave the game", inline=False)
        embeds["commands"].append(embed)
        embed = discord.Embed(title="Other commands",
                              description="Below is a list of commands usable outside of a game", color=0x00b8ff)
        if dataStorage.getGuildData(guild, "useJoinChannel") and guild.get_channel(
                dataStorage.getGuildData(guild, "joinChannel")) is not None:
            embed.add_field(name=f"{p}join",
                            value=f"""Will join a game if one is available or create a new game. Please use this command in {guild.get_channel(dataStorage.getGuildData(guild, "joinChannel")).mention}""",
                            inline=False)
        else:
            embed.add_field(name=f"{p}join",
                            value=f"Will join a game if one is available or create a new game.",
                            inline=False)
        embed.add_field(name=f"{p}list",
                        value="Shows you all running games with their IDs. Useful for when you need a game ID to spectate a game.",
                        inline=False)
        embed.add_field(name=f"{p}spectate <game ID>",
                        value="Spectate a game with the specified game ID. To stop spectating, use !spectate again.",
                        inline=False)
        embed.add_field(name=f"{p}stats <user>",
                        value="Shows you the stats of someone, like how many games they played and how many times they won.",
                        inline=False)
        embed.add_field(name=f"{p}level", value="Checks what level you are and how much XP you need to level up",
                        inline=False)
        embed.add_field(name=f"{p}objective",
                        value="Gives you a new objective or shows how much progress you made in completing your current objective\n\n\nThis is a list of all simple commands. For a list of all possible commands, use **!advancedHelp**",
                        inline=False)
        embeds["commands"].append(embed)
    return embeds

