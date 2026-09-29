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
        from core.commands_meta import category_help_lines
        from core.version import __version__
        prefix = dataStorage.getGuildData(ctx.guild, "prefix", default="!")
        embed = discord.Embed(
            title=f"Murder Mystery Bot v{__version__}",
            description=f"Prefix: `{prefix}`. Categories: member, game, admin, debug.",
            color=0x00b8ff,
        )
        for category in ("game", "member", "admin"):
            lines = category_help_lines(category, prefix)[:8]
            if lines:
                embed.add_field(
                    name=category,
                    value="\n".join(lines)[:1024],
                    inline=False,
                )
        await ctx.send(embed=embed)
        for v in tutorial.getTutorialEmbeds(ctx.guild)["commands"]:
            await ctx.send(embed=v)


@client.command()
async def advancedHelp(ctx, category=None):
    if await permissions.hasPermission(ctx, "member.help"):
        p = dataStorage.getGuildData(ctx.guild, "prefix", default="!")
        from core.commands_meta import category_help_lines
        if category is not None:
            lines = category_help_lines(category, p)
            if not lines:
                await ctx.send("Unknown help category. Try member, game, admin, or debug.")
                return
            embed = discord.Embed(
                title=f"Advanced help — {category}",
                description="\n".join(lines)[:4000],
                color=0x00b8ff,
            )
            await ctx.send(embed=embed)
            return
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


