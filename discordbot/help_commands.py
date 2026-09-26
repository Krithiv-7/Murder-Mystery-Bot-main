"""!help/!advancedHelp/!settings/!prefix prefix commands."""
import discord

import dataStorage
import permissions
import tutorial
from .client import client


client.remove_command("help")


@client.command(aliases=["command", "commands"])
async def help(ctx):
    if await permissions.hasPermission(ctx, "member.help"):
        for v in tutorial.getTutorialEmbeds(ctx.guild)["commands"]:
            await ctx.send(embed=v)


@client.command()
async def advancedHelp(ctx, category=None):
    if await permissions.hasPermission(ctx, "member.help"):
        p = dataStorage.getGuildData(ctx.guild, "prefix", default="!")
        if category is None:
            embed = discord.Embed(title="Advanced help", color=0x00b8ff)
            embed.add_field(name=":adult: Member",
                            value=f"{p}advancedHelp member - views all commands under the member permission group.",
                            inline=False)
            embed.add_field(name=":video_game: Game",
                            value=f"{p}advancedHelp game - views all commands usable during game.", inline=False)
            embed.add_field(name=":person_in_tuxedo: Admin",
                            value=f"{p}advancedHelp admin - views all commands under the admin permission group.",
                            inline=False)
            embed.add_field(name=":scroll: Debug",
                            value=f"{p}advancedHelp debug - views all commands under the debug permission group.",
                            inline=False)
            await ctx.send(embed=embed)
        elif category == "member":
            embed = discord.Embed(title="Advanced help - :adult: Member",
                                  description="Arguments in <> are required, arguments in [] are optional",
                                  color=0x00b8ff)
            embed.add_field(name=f"{p}help", value="permission: member.help\n\nViews a list of all simple commands",
                            inline=False)
            embed.add_field(name=f"{p}advancedHelp [category]",
                            value="permission: member.help\n\nViews a list of all commands", inline=False)
            embed.add_field(name=f"{p}join",
                            value="permission: member.join\n\nJoins a game. Depending on how the server is configured, this command might only be usable in a join channel.",
                            inline=False)
            embed.add_field(name=f"{p}spectate [id]",
                            value="permission: member.spectate\n\nSpectates a game. If only one game is running, no ID has to be given.",
                            inline=False)
            embed.add_field(name=f"{p}list",
                            value="permission: member.list\n\nShows all currently running games and their IDs",
                            inline=False)
            embed.add_field(name=f"{p}level [player]",
                            value="permission: member.levels.level\n\nShows the player's level", inline=False)
            embed.add_field(name=f"{p}objective",
                            value="permission: member.levels.objective\n\nShows your current objective progress or gives you a new one",
                            inline=False)
            embed.add_field(name=f"{p}stats [player]",
                            value="permission: member.levels.stats\n\nShows your or the player's stats", inline=False)
            embed.add_field(name=f"{p}prefix",
                            value="permission: no permissions needed\n\nShows the bot's prefix for this server",
                            inline=False)
            await ctx.send(embed=embed)
        elif category == "admin":
            embed = discord.Embed(title="Advanced help - :person_in_tuxedo: Admin",
                                  description="Arguments in <> are required, arguments in [] are optional",
                                  color=0x00b8ff)
            embed.add_field(
                name=f"{p}purge <number>",
                value=(
                    "permission: admin.purge\n\n"
                    "Deletes the last <number> amount of messages"
                ),
                inline=False
            )
            embed.add_field(
                name=f"{p}endAllGames",
                value=(
                    f"permission: admin.endAllGames\n\n"
                    f"Ends all currently running games. {p}cleanup does "
                    "the same."
                ),
                inline=False
            )
            embed.add_field(
                name=f"{p}endGame <game ID>",
                value=(
                    f"permission: admin.endGame\n\n"
                    f"Ends the game with the specified ID. Game IDs can "
                    f"be obtained with {p}list"
                ),
                inline=False
            )
            embed.add_field(
                name=f"{p}setup",
                value="permission: admin.setup\n\nReruns the setup",
                inline=False
            )
            embed.add_field(
                name=f"{p}settings [setting] [value]",
                value=(
                    "permission: admin.settings\n\n"
                    "Set different kind of settings on how the game "
                    "behaves, like the amount of players needed to start "
                    "a game, how long night time takes, ect..."
                ),
                inline=False
            )
            embed.add_field(
                name=f"{p}prefix [new prefix]",
                value=(
                    "permission: admin.prefix\n\n"
                    "Shows the bot's current prefix or sets a new one. "
                    "Members can run this command as well but can't "
                    "change the prefix without the admin.prefix permission."
                ),
                inline=False
            )
            embed.add_field(
                name=f"{p}addPermission <member/role> <permission>",
                value=(
                    "permission: admin.permissions.addPermission\n\n"
                    "Adds a permission to a role or member"
                ),
                inline=False
            )
            embed.add_field(
                name=f"{p}removePermission <member/role> <permission>",
                value=(
                    "permission: admin.permissions.removePermissions\n\n"
                    "Removes a permission from a role or member"
                ),
                inline=False
            )
            embed.add_field(
                name=f"{p}permissions [member/role]",
                value=(
                    "permission: admin.permissions\n\n"
                    "Views the permissions for the member/role. If no "
                    "argument is given, it will show all possible permissions."
                ),
                inline=False
            )
            embed.add_field(
                name=f"{p}giveGold <player> <amount>",
                value=(
                    "permission: admin.game.giveGold\n\n"
                    "Gives the specified player the specified amount of "
                    "extra gold in game"
                ),
                inline=False
            )
            embed.add_field(
                name=f"{p}kick <player>",
                value=(
                    "permission: admin.game.kick\n\n"
                    "Kicks the specified player out of the game"
                ),
                inline=False
            )
            embed.add_field(
                name=f"{p}startGame <game ID>",
                value=(
                    "permission: admin.game.startGame\n\n"
                    "Skips the pre-game timer"
                ),
                inline=False
            )
            await ctx.send(embed=embed)
        elif category == "debug":
            embed = discord.Embed(
                title="Advanced help - :scroll: Debug",
                description=(
                    "Arguments in <> are required, arguments in [] are "
                    "optional\n\n"
                    "**These are advanced commands not meant to be used. "
                    "Feel free to mess around, but most of these commands "
                    "were made for debugging purposes and will be confusing "
                    "if you don't have the source code**\n\n"
                    "**:warning: Some of these commands could break the bot "
                    "if used incorrectly :warning:**"
                ),
                color=0x00b8ff
            )
            embed.add_field(
                name=f"{p}createGame [True/False]",
                value=(
                    f"permission: debug.createGame\n\n"
                    f"Creates an empty game. If you want to start the game "
                    f"in debugging mode, use {p}createGame True."
                ),
                inline=False
            )
            embed.add_field(
                name=f"{p}addObjectiveProgress <member> <task> <value>",
                value="permission: debug.objectives.addObjectiveProgress\n\nAdds objective progress",
                inline=False
            )
            embed.add_field(
                name=f"{p}giveObjective <member> <index>",
                value=(
                    "permission: debug.objectives.giveObjective\n\n"
                    "Sets the objective of the player to the specified index."
                    "\n:warning: Unexpected behaviour might occur if set to "
                    "an invalid index."
                ),
                inline=False
            )
            embed.add_field(
                name=f"{p}completeCurrentObjective <member>",
                value=(
                    "permission: debug.objectives.completeCurrentObjective"
                    "\n\nCompletes the specified member's current objective"
                ),
                inline=False
            )
            embed.add_field(
                name=f"{p}skipObjectiveTimer <member>",
                value=(
                    "permission: debug.objectives.skipObjectiveTimer\n\n"
                    "Skips the in-between objective timer of the specified "
                    "member"
                ),
                inline=False
            )
            embed.add_field(
                name=f"{p}setMoon <game ID> <brightness (1-5)",
                value=(
                    "permission: debug.game.setMoon\n\n"
                    "Sets the moon brightness in the specified game. "
                    "1 is no moon, 5 is full moon.\n"
                    "Please only use this command after the weather forecast, "
                    "and before night time starts"
                ),
                inline=False
            )
            embed.add_field(
                name=f"{p}setWeather <game ID> <intensity (0-99)>",
                value=(
                    "permission: debug.game.setWeather\n\n"
                    "Sets the weather intensity. 0 for not intense and "
                    "99 for very intense.\n"
                    "Please only use this command after the weather forecast, "
                    "and before night time starts"
                ),
                inline=False
            )
            embed.add_field(
                name=f"{p}skipNight <game ID>",
                value="permission: debug.game.skipNight\n\nSkips the night",
                inline=False
            )
            embed.add_field(
                name=f"{p}skipVotes <game ID>",
                value="permission: debug.game.skipVotes\n\nSkips voting time",
                inline=False
            )
            await ctx.send(embed=embed)
        elif category == "game":
            embed = discord.Embed(
                title="Advanced help - :video_game Game",
                description=(
                    "Arguments in <> are required, arguments in [] are "
                    "optional\nThe commands below do not have any permission "
                    "settings, because they can only be used in game which "
                    "can only be accessed with the permission 'member.join'."
                ),
                color=0x00b8ff
            )
            embed.add_field(
                name=f"{p}vote <player>",
                value="Vote on the specified player to be executed during game",
                inline=False
            )
            embed.add_field(
                name=f"{p}shop",
                value="Views all shop items",
                inline=False
            )
            embed.add_field(
                name=f"{p}buy <item>",
                value="Buy an item from the shop",
                inline=False
            )
            embed.add_field(
                name=f"{p}use <item> [argument]",
                value=(
                    "Use an item. The argument being required or not "
                    "depends on the item."
                ),
                inline=False
            )
            embed.add_field(
                name=f"{p}whisper <player>",
                value=(
                    "Creates a private channel for the command runner "
                    "and the specified player to talk in"
                ),
                inline=False
            )
            embed.add_field(
                name=f"{p}leave",
                value="Leaves the game"
            )
            await ctx.send(embed=embed)


@client.command(aliases=["setting", "options", "option", "config", "configuration"])
async def settings(ctx, setting=None, value=None):
    if await permissions.hasPermission(ctx, "admin.settings"):
        if setting is None:
            if dataStorage.getGuildData(ctx.guild, "gameVoiceChannel", default=False):
                voiceChannelValueSting = "Yes"
            else:
                voiceChannelValueSting = "No"
            if dataStorage.getGuildData(ctx.guild, "lockVoiceChannelDuringNight", default=False):
                voiceChannelLockString = "Yes"
            else:
                voiceChannelLockString = "No"
            # Display reflects default of allowing offline players unless explicitly enabled
            if dataStorage.getGuildData(ctx.guild, "kickOfflinePlayers", default=False):
                kickOfflinePlayersString = "Yes"
            else:
                kickOfflinePlayersString = "No"
            settings_desc = (
                f"minPlayers:{dataStorage.getGuildData(ctx.guild, 'minPlayers')}\n"
                "Set the minimal amount of players required to start a game\n\n"
                f"maxPlayers: {dataStorage.getGuildData(ctx.guild, 'maxPlayers')}\n"
                "Set the maximum players that can fit in a game\n\n"
                f"preGameTimer: {dataStorage.getGuildData(ctx.guild, 'preGameTimer')}\n"
                "Sets the amount of time in seconds that it takes for a game "
                "to start when the game has enough players\n\n"
                f"votingTime: {dataStorage.getGuildData(ctx.guild, 'votingTime')}\n"
                "Sets the amount of time in seconds that it takes before "
                "voting time ends\n\n"
                f"nightTimeTimer: {dataStorage.getGuildData(ctx.guild, 'nightTimeTimer')}\n"
                "Sets the amount of time in seconds that it takes for night "
                "time to end\n\n"
                "Use !settings <setting> <value> to set a setting\n"
                "The settings below don't need a value, but they will change "
                "from 'yes' to 'no' with !settings <setting>\n\n"
                f"voiceChannel: {voiceChannelValueSting}\n"
                "Create a voice channel for the game when a game is created\n\n"
                f"lockVoiceChannelDuringNight: {voiceChannelLockString}\n"
                "Locks the game's voice channel when it becomes night "
                "(needs voiceChannel to be set to 'yes')\n\n"
                f"kickOfflinePlayers: {kickOfflinePlayersString}\n"
                "Kicks players out of a game when they go offline\n\n\n"
                "To set permissions, use !permissions and !setPermissions\n"
                "To change the bot's prefix, use !prefix"
            )
            await ctx.send(embed=discord.Embed(
                title="List of settings",
                description=settings_desc,
                color=0x00b8ff
            ))
        else:
            if setting.lower().strip() == "voicechannel":
                if dataStorage.getGuildData(ctx.guild, "gameVoiceChannel", default=False):
                    dataStorage.setGuildData(
                        ctx.guild, "gameVoiceChannel", value=False
                    )
                    await ctx.send(embed=discord.Embed(
                        title=(
                            ":white_check_mark: The bot will no longer make "
                            "a voice channel for a game when the game is "
                            "created!"
                        ),
                        color=0x00ff00
                    ))
                else:
                    dataStorage.setGuildData(
                        ctx.guild, "gameVoiceChannel", value=True
                    )
                    await ctx.send(embed=discord.Embed(
                        title=(
                            ":white_check_mark: The bot will now make a "
                            "voice channel for a game when the game is "
                            "created!"
                        ),
                        color=0x00ff00
                    ))

            elif setting.lower().strip() == "lockvoicechannelduringnight":
                bot_member = ctx.guild.get_member(client.user.id)
                if bot_member.guild_permissions.move_members:
                    if dataStorage.getGuildData(
                        ctx.guild, "lockVoiceChannelDuringNight", default=False
                    ):
                        dataStorage.setGuildData(
                            ctx.guild,
                            "lockVoiceChannelDuringNight",
                            value=False
                        )
                        await ctx.send(embed=discord.Embed(
                            title=(
                                ":white_check_mark: The bot will no longer "
                                "lock the game's voice channel during the "
                                "night!"
                            ),
                            color=0x00ff00
                        ))
                    else:
                        dataStorage.setGuildData(
                            ctx.guild,
                            "lockVoiceChannelDuringNight",
                            value=True
                        )
                        await ctx.send(embed=discord.Embed(
                            title=(
                                ":white_check_mark: The bot will now lock "
                                "the game's voice channel during the night!"
                            ),
                            color=0x00ff00
                        ))
                else:
                    await ctx.send(embed=discord.Embed(
                        title=(
                            ":x: This setting requires the permission "
                            "'move members'."
                        ),
                        description=(
                            "Please add the permission 'move members' to the "
                            "bot's role in your server's settings"
                        ),
                        color=0xff0000
                    ))

            elif setting.lower().strip() == "kickofflineplayers":
                # Toggle, using default False (allow offline by default)
                if dataStorage.getGuildData(
                    ctx.guild, "kickOfflinePlayers", default=False
                ):
                    dataStorage.setGuildData(
                        ctx.guild, "kickOfflinePlayers", value=False
                    )
                    await ctx.send(embed=discord.Embed(
                        title=(
                            ":white_check_mark: Offline players will no "
                            "longer be kicked!"
                        ),
                        color=0x00ff00
                    ))
                else:
                    dataStorage.setGuildData(
                        ctx.guild, "kickOfflinePlayers", value=True
                    )
                    await ctx.send(embed=discord.Embed(
                        title=(
                            ":white_check_mark: Offline players will now "
                            "be kicked!"
                        ),
                        color=0x00ff00
                    ))


            else:
                try:
                    intSetting = int(value)
                except TypeError:
                    await ctx.send(":x: Please enter a number after the setting!")
                except ValueError:
                    await ctx.send(":x: Please enter a number after the setting!")
                else:
                    if setting.lower().strip() == "minplayers":
                        if intSetting >= 4:
                            max_players = dataStorage.getGuildData(
                                ctx.guild, "maxPlayers"
                            )
                            if intSetting < max_players:
                                dataStorage.setGuildData(
                                    ctx.guild, "minPlayers", value=intSetting
                                )
                                await ctx.send(
                                    f":white_check_mark: The setting "
                                    f"minPlayers has been set to {intSetting}"
                                )
                            else:
                                await ctx.send(
                                    ":x: This setting must be lower than the "
                                    "setting 'maxPlayers'!"
                                )
                        else:
                            await ctx.send(
                                ":x: This setting can't be lower than 4!"
                            )
                    elif setting.lower().strip() == "maxplayers":
                        if intSetting >= 4:
                            min_players = dataStorage.getGuildData(
                                ctx.guild, "minPlayers"
                            )
                            if intSetting > min_players:
                                dataStorage.setGuildData(
                                    ctx.guild, "maxPlayers", value=intSetting
                                )
                                await ctx.send(
                                    f":white_check_mark: The setting "
                                    f"maxPlayers has been set to {intSetting}"
                                )
                            else:
                                await ctx.send(
                                    ":x: This setting must be higher than "
                                    "the setting 'minPlayers'!"
                                )
                        else:
                            await ctx.send(
                                ":x: This setting can't be lower than 4!"
                            )
                    elif setting.lower().strip() == "pregametimer":
                        if intSetting >= 5:
                            dataStorage.setGuildData(
                                ctx.guild, "preGameTimer", value=intSetting
                            )
                            await ctx.send(
                                f":white_check_mark: The setting preGameTimer "
                                f"has been set to {intSetting}"
                            )
                        else:
                            await ctx.send(
                                ":x: This setting must be higher than 5!"
                            )
                    elif setting.lower().strip() == "votingtime":
                        if intSetting >= 5:
                            dataStorage.setGuildData(
                                ctx.guild, "votingTime", value=intSetting
                            )
                            await ctx.send(
                                f":white_check_mark: The setting votingTime "
                                f"has been set to {intSetting}"
                            )
                        else:
                            await ctx.send(
                                ":x: This setting must be higher than 5!"
                            )
                    elif setting.lower().strip() == "nighttimetimer":
                        if intSetting >= 5:
                            dataStorage.setGuildData(
                                ctx.guild, "nightTimeTimer", value=intSetting
                            )
                            await ctx.send(
                                f":white_check_mark: The setting "
                                f"nightTimeTimer has been set to {intSetting}"
                            )
                        else:
                            await ctx.send(
                                ":x: This setting must be higher than 5!"
                            )
                    else:
                        prefix_val = dataStorage.getGuildData(
                            ctx.guild, 'prefix', default='!'
                        )
                        await ctx.send(
                            f":x: '{setting}' is not a valid setting! Use "
                            f"{prefix_val}settings to see a list of all "
                            f"settings"
                        )


@client.command(aliases=["prefixes", "setPrefix", "changePrefix", "getPrefix"])
async def prefix(ctx, newValue=None):
    if newValue is None:
        current_prefix = dataStorage.getGuildData(
            ctx.guild, 'prefix', default='!'
        )
        await ctx.send(
            f"My current prefix for this server is: {current_prefix}"
        )
    else:
        if permissions.memberHasPermission(ctx.author, "admin.prefix"):
            if 7 >= len(str(newValue).strip().lower()) > 0:
                new_prefix = str(newValue).strip().lower()
                dataStorage.setGuildData(
                    ctx.guild, "prefix", value=new_prefix
                )
                await ctx.send(
                    f":white_check_mark: My prefix has been set to "
                    f"'{new_prefix}'"
                )
            else:
                await ctx.send(
                    ":x: The prefix can't be bigger than 7 characters!"
                )
        else:
            await ctx.send(embed=discord.Embed(
                title=(
                    ":closed_lock_with_key: You don't have permission to "
                    "do that!"
                ),
                description=(
                    "You're missing the following permission: admin.prefix"
                    f"\n\nIf you think you're supposed to have this "
                    f"permission, then ask an admin to execute the "
                    f"following command:\n!addPermission {ctx.author.mention} "
                    f"admin.prefix"
                ),
                color=0xff0000
            ))


