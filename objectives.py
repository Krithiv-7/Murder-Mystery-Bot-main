import discord
import random
import datetime
import math
from dataStorage import getPlayerData, setPlayerData

getNextLevelRequirement = lambda x: (x + 1) * 5 * x

# index 0 is the first objective you get, the others are randomized if they have the right difficulty for that player and if they didn't complete it yet
# When adding new objectives, add them to the end of the list because indexes are used for storing what objectives the user has completed
objectives = [{"difficulty": 1, "tasks": {"villagerWinsNoDeath": 3}, "rewards": {"xp": 50}},
              {"difficulty": 2, "tasks": {"murdererWins": 1}, "rewards": {"xp": 100}},
              {"difficulty": 2, "tasks": {"killMurdererWithItem": 1}, "rewards": {"xp": 150}},
              {"difficulty": 2, "tasks": {"voteOnMurderer": 5}, "rewards": {"xp": 150}},
              {"difficulty": 2, "tasks": {"thiefStealCoins": 6}, "rewards": {"xp": 200}},
              {"difficulty": 3, "tasks": {"dayOneMurdererVote6PlayersOrMore": 1}, "rewards": {"xp": 230}}]

objectiveTasksMeanings = {
    "villagerWinsNoDeath": ["Win as a villager without dying", "Win as a villager {} times without dying"],
    "murdererWins": ["Win as the murderer", "Win as the murderer {} times"],
    "killMurdererWithItem": ["Kill the murderer using an item", "Kill the murderer using a rock or gun {} times"],
    "voteOnMurderer": ["Vote to execute the murderer", "Vote to execute the murderer {} times"],
    "thiefStealCoins": ["Steal a coin from someone as the thief", "Steal {} coins in total from people as the thief"],
    "dayOneMurdererVote6PlayersOrMore": ["Vote the murderer on the first day in a game with 6 or more players",
                                         "Vote the murderer on the first day in a game with 6 or more players {} times"]}


async def addXP(member, amount):
    setPlayerData(member, "xp", increase=amount)
    if getPlayerData(member, "xp", default=0) >= getNextLevelRequirement(getPlayerData(member, "level", default=1)):
        while True:
            setPlayerData(member, "xp", increase=-getNextLevelRequirement(getPlayerData(member, "level", default=1)))
            setPlayerData(member, "level", increase=1)
            print(f'{getPlayerData(member, "xp")} {getNextLevelRequirement(getPlayerData(member, "level", default=1))}')
            if getPlayerData(member, "xp") >= getNextLevelRequirement(getPlayerData(member, "level", default=1)):
                pass
            else:
                break
        embed = discord.Embed(title="Level up!",
                              description=f"""You leveled up to level {getPlayerData(member, "level", default=1)}""",
                              color=0x00ff00)
        try:
            await member.send(embed=embed)
        except discord.DiscordException:
            print(f"Can't DM {member.display_name}")


def giveObjective(member, **kwargs):
    selectedObj = -1
    if "index" not in kwargs:
        completedObjs = getPlayerData(member, "completedObjectives", default=[])
        # take away all the other difficulties that aren't an option from the objectives list
        usableObjs = objectives.copy()
        for obj in objectives:
            print(f'{obj["difficulty"]} {getPlayerData(member, "possibleObjectiveDifficulty", default=1)}')
            if obj["difficulty"] > getPlayerData(member, "possibleObjectiveDifficulty", default=1):
                usableObjs.remove(obj)
            elif objectives.index(obj) in completedObjs:
                usableObjs.remove(obj)
        random.shuffle(usableObjs)
        if len(usableObjs) > 0:
            for obj in usableObjs:
                if objectives.index(obj) not in completedObjs:
                    print(f"selected {obj}")
                    selectedObj = objectives.index(obj)
        else:
            return False
    else:
        if len(objectives) > kwargs["index"] >= 0:
            selectedObj = kwargs["index"]
        else:
            return False

    if selectedObj == -1:
        return False
    setPlayerData(member, "objective", value=selectedObj)
    objectiveProgress = {}
    for task in objectives[selectedObj]["tasks"]:
        objectiveProgress[task] = 0
    setPlayerData(member, "objectiveProgress", value=objectiveProgress)
    return True


def addObjectiveProgress(member, key, value):
    if getPlayerData(member, "objective") is None:
        if not len(getPlayerData(member, "completedObjectives", default=[])) > 0:
            giveObjective(member, index=0)

    if getPlayerData(member, "objective") is not None:
        if key in objectives[getPlayerData(member, "objective")]["tasks"]:
            objectiveProgress = getPlayerData(member, "objectiveProgress", default={})
            if key in objectiveProgress:
                objectiveProgress[key] += value
            else:
                objectiveProgress[key] = value
            setPlayerData(member, "objectiveProgress", value=objectiveProgress)


async def checkForCompleteObjectives(member, **kwargs):
    if getPlayerData(member, "objective") is None:
        if not len(getPlayerData(member, "completedObjectives", default=[])) > 0:
            giveObjective(member, index=0)

    if getPlayerData(member, "objective") is not None:
        objProgress = getPlayerData(member, "objectiveProgress", default={})
        completedTasks = 0
        for key in objProgress:
            if key in objectives[getPlayerData(member, "objective", default=0)]["tasks"]:
                if objProgress[key] >= objectives[getPlayerData(member, "objective", default=0)]["tasks"][key]:
                    completedTasks += 1

        completedObjective = False
        if completedTasks >= len(objectives[getPlayerData(member, "objective", default=0)]["tasks"]):
            completedObjective = True
        elif "forceComplete" in kwargs:
            if kwargs["forceComplete"]:
                completedObjective = True

        if completedObjective:
            desc = f"""You completed an objective!\n+{objectives[getPlayerData(member, "objective")]["rewards"]["xp"]} xp\n\n{getObjectiveProgressBars(member)}"""
            embed = discord.Embed(title="Objective complete!", description=desc, color=0x00ff00)
            try:
                await member.send(embed=embed)
            except discord.DiscordException:
                print("Can't DM this player")

            completedObjs = getPlayerData(member, "completedObjectives", default=[])
            completedObjs.append(getPlayerData(member, "objective"))
            setPlayerData(member, "completedObjectives", value=completedObjs)
            setPlayerData(member, "objective", value=None)
            setPlayerData(member, "nextObjectiveReceivable",
                          value=(datetime.datetime.utcnow() + datetime.timedelta(hours=3)).isoformat())
            if getPlayerData(member, "possibleObjectiveDifficulty") is None:
                setPlayerData(member, "possibleObjectiveDifficulty", value=1)
            setPlayerData(member, "possibleObjectiveDifficulty", increase=1)


def getObjectiveProgressBars(member):
    if getPlayerData(member, "objective") is None:
        if not len(getPlayerData(member, "completedObjectives", default=[])) > 0:
            giveObjective(member, index=0)

    if getPlayerData(member, "objective") is not None:
        objective = getPlayerData(member, "objective")
        objectiveProgress = getPlayerData(member, "objectiveProgress", default={})
        allBars = ""
        for task in objectiveProgress:
            barLength = round((objectiveProgress[task] / objectives[objective]["tasks"][task]) * 10)
            if barLength > 10:
                barLength = 10

            if objectives[objective]["tasks"][task] == 1:
                barText = objectiveTasksMeanings[task][0]
            else:
                barText = objectiveTasksMeanings[task][1].format(objectives[objective]["tasks"][task])
            bar = f"{barText}\n"
            for i in range(1, 11):
                if i <= barLength:
                    bar += "▓"
                else:
                    bar += "░"
            bar += f""" [{objectiveProgress[task]}/{objectives[objective]["tasks"][task]}]"""
            allBars += bar
        return allBars


def getXpProgressBar(member):
    bar = ""
    barLength = round((getPlayerData(member, "xp", default=0) / getNextLevelRequirement(
        getPlayerData(member, "level", default=1))) * 10)
    for i in range(1, 11):
        if i <= barLength:
            bar += "▓"
        else:
            bar += "░"
    bar += f""" [{getPlayerData(member, "xp", default=0)}/{getNextLevelRequirement(getPlayerData(member, "level", default=1))}]"""
    return bar


async def objectivesCommand(ctx):
    member = ctx.author
    if getPlayerData(member, "objective") is not None:
        embed = discord.Embed(title="Current objective progress", description=getObjectiveProgressBars(
            member) + f"""\n\nReward: +{objectives[getPlayerData(member, "objective")]["rewards"]["xp"]} xp""",
                              color=0x00ff00)
        embed.set_thumbnail(url=member.avatar_url)
        await ctx.send(embed=embed)
        await checkForCompleteObjectives(member)
    else:
        if not len(getPlayerData(member, "completedObjectives", default=[])) > 0:
            giveObjective(member, index=0)
            await objectivesCommand(ctx)
        else:
            if getPlayerData(member, "nextObjectiveReceivable") is None:
                setPlayerData(member, "nextObjectiveReceivable",
                              value=(datetime.datetime.utcnow() + datetime.timedelta(hours=3)).isoformat())

            if datetime.datetime.fromisoformat(
                    getPlayerData(member, "nextObjectiveReceivable")) < datetime.datetime.utcnow():
                if giveObjective(member):
                    embed = discord.Embed(title="New objective!", description=getObjectiveProgressBars(member),
                                          color=0x00ff00)
                    embed.set_thumbnail(url=member.avatar_url)
                    await ctx.send(embed=embed)
                else:
                    embed = discord.Embed(title="You completed all objectives!",
                                          description="There are none left! Congratulations!", color=0xffda83)
                    embed.set_thumbnail(url=member.avatar_url)
                    await ctx.send(embed=embed)
            else:
                hourDifference = 0
                minuteDifference = 0
                secondDifference = round((datetime.datetime.fromisoformat(
                    getPlayerData(member, "nextObjectiveReceivable")) - datetime.datetime.utcnow()).seconds)
                if secondDifference > 60:
                    minuteDifference = math.floor(secondDifference / 60)
                    secondDifference = secondDifference % 60
                    if minuteDifference > 60:
                        hourDifference = math.floor(minuteDifference / 60)
                        minuteDifference = minuteDifference % 60
                units = 0
                hours = ""
                if hourDifference > 0:
                    hours += f"{hourDifference} hour"
                    units += 1
                    if hourDifference > 1:
                        hours += "s"
                minutes = ""
                if minuteDifference > 0:
                    minutes += f"{minuteDifference} minute"
                    units += 1
                    if minuteDifference > 1:
                        minutes += "s"
                seconds = ""
                if secondDifference > 0:
                    seconds += f"{secondDifference} second"
                    units += 1
                    if secondDifference > 1:
                        seconds += "s"
                unitList = [hours, minutes, seconds]
                result = ""
                if units == 1:
                    for v in unitList:
                        if v != "":
                            result = v
                elif units == 2:
                    for v in unitList:
                        if v != "":
                            if result == "":
                                result = v
                            else:
                                result += f" and {v}"
                elif units == 3:
                    result = f"{unitList[0]}, {unitList[1]} and {unitList[2]}"

                await ctx.send(embed=discord.Embed(title="You can't start a new objective yet!",
                                                   description=f"You must wait {result} before you can start a new objective!",
                                                   color=0xff0000))
