"""!addPermission/!removePermission/!permissions prefix commands."""
import discord
from discord.ext import commands

import permissions
from .client import client


@client.command()
async def addPermission(ctx, arg=None, perm=None):
    perm_check = "admin.permissions.addPermission"
    if await permissions.hasPermission(ctx, perm_check):
        if arg is not None and perm is not None:
            member = None
            roleArg = None
            try:
                converter = commands.MemberConverter()
                member = await converter.convert(ctx, arg)
            except commands.MemberNotFound:
                try:
                    converter = commands.RoleConverter()
                    roleArg = await converter.convert(ctx, arg)
                except commands.RoleNotFound:
                    await ctx.send(embed=discord.Embed(
                        title=":x: Couldn't find that member or role! correct usage: !removePermission <member/role> <permission>"))
                except Exception:
                    await ctx.message.channel.send(":x: an unknown error occurred!")
                    raise
            except Exception:
                await ctx.message.channel.send(":x: an unknown error occurred!")
                raise
            if member is not None:
                if permissions.isValidPermission(perm):
                    has_perm = permissions.memberHasPermission(
                        member, perm, bypassRoles=True
                    )
                    if not has_perm:
                        permissions.addPermissionToMember(member, perm)
                        name = member.display_name
                        await ctx.send(embed=discord.Embed(
                            title=(
                                f":white_check_mark: {perm} has been added "
                                f"to {name}'s permissions"
                            ),
                            color=0x00ff00
                        ))
                    else:
                        name = member.display_name
                        await ctx.send(embed=discord.Embed(
                            title=(
                                f":x: {name} already has the permission "
                                f"{perm}."
                            ),
                            description=(
                                f"Use !permissions {member.mention} to view "
                                "their permissions"
                            ),
                            color=0xff0000
                        ))
                else:
                    valid_perms_desc = (
                        "To view a list of all permissions, use "
                        "!permissions.\n\nExamples of valid permissions:\n"
                        "admin.permissions.addPermission\nadmin.*\n"
                        "admin.permissions.*\nmember.*\nmember.help\n"
                        "(* means all permissions in that permission group)"
                    )
                    await ctx.send(embed=discord.Embed(
                        title=f":x: {perm} is not a valid permission.",
                        description=valid_perms_desc,
                        color=0xff0000
                    ))
            elif roleArg is not None:
                if permissions.isValidPermission(perm):
                    if not permissions.roleHasPermission(roleArg, perm):
                        permissions.addPermissionToRole(roleArg, perm)
                        await ctx.send(embed=discord.Embed(
                            title=(
                                f":white_check_mark: {perm} has been added "
                                f"to the permissions \"{roleArg}\""
                            ),
                            color=0x00ff00
                        ))
                    else:
                        await ctx.send(embed=discord.Embed(
                            title=(
                                f":x: the role {roleArg.name} already has "
                                f"the permission {perm}"
                            ),
                            description=(
                                f"to view its permissions, do "
                                f"!permissions {roleArg.mention}"
                            ),
                            color=0xff0000
                        ))
                else:
                    valid_perms_desc = (
                        "To view a list of all permissions, use "
                        "!permissions.\n\nExamples of valid permissions:\n"
                        "admin.permissions.addPermission\nadmin.*\n"
                        "admin.permissions.*\nmember.*\nmember.help\n"
                        "(* means all permissions in that permission group)"
                    )
                    await ctx.send(embed=discord.Embed(
                        title=f":x: {perm} is not a valid permission.",
                        description=valid_perms_desc,
                        color=0xff0000
                    ))
        else:
            await ctx.send(embed=discord.Embed(
                title=":x: Incorrect command usage",
                description=(
                    "correct usage: !addPermission <member> <permission>\n"
                    "use !permissions to view a list of permissions"
                ),
                color=0xff0000
            ))


@client.command()
async def removePermission(ctx, arg=None, perm: str = None):
    perm_check = "admin.permissions.removePermission"
    if await permissions.hasPermission(ctx, perm_check):
        if arg is not None and perm is not None:
            member = None
            roleArg = None
            try:
                converter = commands.MemberConverter()
                member = await converter.convert(ctx, arg)
            except commands.MemberNotFound:
                try:
                    converter = commands.RoleConverter()
                    roleArg = await converter.convert(ctx, arg)
                except commands.RoleNotFound:
                    await ctx.send(embed=discord.Embed(
                        title=(
                            ":x: Couldn't find that member or role! "
                            "correct usage: !removePermission "
                            "<member/role> <permission>"
                        )
                    ))
                except Exception:
                    await ctx.message.channel.send(":x: an unknown error occurred!")
                    raise
            except Exception:
                await ctx.message.channel.send(":x: an unknown error occurred!")
                raise
            if member is not None:
                if permissions.isValidPermission(perm):
                    has_perm = permissions.memberHasPermission(
                        member, perm, bypassRoles=True
                    )
                    if has_perm:
                        permissions.removePermissionFromMember(member, perm)
                        name = member.display_name
                        await ctx.send(embed=discord.Embed(
                            title=(
                                f":white_check_mark: {perm} has been "
                                f"removed from {name}'s permissions"
                            ),
                            color=0x00ff00
                        ))
                    else:
                        name = member.display_name
                        await ctx.send(embed=discord.Embed(
                            title=(
                                f":x: {name} doesn't have the permission "
                                f"{perm}."
                            ),
                            description=(
                                f"Use !permissions {member.mention} to view "
                                "their permissions"
                            ),
                            color=0xff0000
                        ))
                else:
                    valid_perms_desc = (
                        "To view a list of all permissions, use "
                        "!permissions.\n\nExamples of valid permissions:\n"
                        "admin.permissions.addPermission\nadmin.*\n"
                        "admin.permissions.*\nmember.*\nmember.help\n"
                        "(* means all permissions in that permission group)"
                    )
                    await ctx.send(embed=discord.Embed(
                        title=f":x: {perm} is not a valid permission.",
                        description=valid_perms_desc,
                        color=0xff0000
                    ))
            elif roleArg is not None:
                if permissions.isValidPermission(perm):
                    if permissions.roleHasPermission(roleArg, perm):
                        permissions.removePermissionFromRole(roleArg, perm)
                        await ctx.send(embed=discord.Embed(
                            title=(
                                f":white_check_mark: The permissions {perm} "
                                f"has been removed from the role "
                                f"{roleArg.name}"
                            ),
                            color=0x00ff00
                        ))
                    else:
                        await ctx.send(embed=discord.Embed(
                            title=(
                                f":x: The role {roleArg.name} doesn't have "
                                f"the permission {perm}"
                            ),
                            description=(
                                f"Use !permissions {roleArg.mention} to view "
                                "its permissions"
                            ),
                            color=0xff0000
                        ))
                else:
                    valid_perms_desc = (
                        "To view a list of all permissions, use "
                        "!permissions.\n\nExamples of valid permissions:\n"
                        "admin.permissions.addPermission\nadmin.*\n"
                        "admin.permissions.*\nmember.*\nmember.help\n"
                        "(* means all permissions in that permission group)"
                    )
                    await ctx.send(embed=discord.Embed(
                        title=f":x: {perm} is not a valid permission.",
                        description=valid_perms_desc,
                        color=0xff0000
                    ))
        else:
            await ctx.send(embed=discord.Embed(
                title=":x: Incorrect command usage",
                description=(
                    "correct usage: !removePermission <member> <permission>\n"
                    "use !permissions to view a list of permissions"
                ),
                color=0xff0000
            ))


@client.command(aliases=["permissions"])
async def permission(ctx, arg=None):
    perm_check = "admin.permissions.permissions"
    if await permissions.hasPermission(ctx, perm_check):
        if arg is not None:
            member = None
            roleArg = None
            try:
                converter = commands.MemberConverter()
                member = await converter.convert(ctx, arg)
            except commands.MemberNotFound:
                try:
                    converter = commands.RoleConverter()
                    roleArg = await converter.convert(ctx, arg)
                except commands.RoleNotFound:
                    await ctx.send(embed=discord.Embed(
                        title=(
                            ":x: Couldn't find that member or role! "
                            "correct usage: !removePermission "
                            "<member/role> <permission>"
                        )
                    ))
                except Exception:
                    await ctx.message.channel.send(
                        ":x: an unknown error occurred!"
                    )
                    raise
            except Exception:
                await ctx.message.channel.send(
                    ":x: an unknown error occurred!"
                )
                raise
            if member is not None:
                member_perms = permissions.getMemberPermissions(member)
                perm_tree = permissions.getPermissionTree(member_perms)
                desc = (
                    f"{perm_tree}\n\n"
                    f"To add/remove permissions, use "
                    f"!addPermission {member.mention} <permission> or "
                    f"!removePermission {member.mention} <permission>\n"
                    "Use !permissions to view a full list of permissions\n"
                    "Use . between permission groups. Use * to select "
                    "everything in a permission group.\n"
                    "Examples of valid permissions:\n"
                    "admin.permissions.addPermission\nadmin.*\n"
                    "admin.permissions.*\nmember.*\nmember.help"
                )
                await ctx.send(embed=discord.Embed(
                    title=f"Permissions of {member.display_name}",
                    description=desc,
                    color=0x00b8ff
                ))

            elif roleArg is not None:
                role_perms = permissions.getRolePermissions(roleArg)
                perm_tree = permissions.getPermissionTree(role_perms)
                desc = (
                    f"{perm_tree}\n\n"
                    f"To add/remove permissions, use "
                    f"!addPermission {roleArg.mention} <permission> or "
                    f"!removePermission {roleArg.mention} <permission>\n"
                    "Use !permissions to view a full list of permissions\n"
                    "Use . between permission groups. Use * to select "
                    "everything in a permission group.\n"
                    "Examples of valid permissions:\n"
                    "admin.permissions.addPermission\nadmin.*\n"
                    "admin.permissions.*\nmember.*\nmember.help"
                )
                await ctx.send(embed=discord.Embed(
                    title=f"Permissions of \"{roleArg.name}\"",
                    description=desc,
                    color=0x00b8ff
                ))
        else:
            perm_list = permissions.getPermissionList()
            perm_tree = permissions.getPermissionTree(perm_list)
            desc = (
                f"{perm_tree}\n\n"
                "To add/remove permissions, use "
                "!addPermission <player/role> <permission> or "
                "!removePermission <player/role> <permission>\n"
                "Use . between permission groups. Use * to select "
                "everything in a permission group.\n"
                "Examples of valid permissions:\n"
                "admin.permissions.addPermission\nadmin.*\n"
                "admin.permissions.*\nmember.*\nmember.help"
            )
            await ctx.send(embed=discord.Embed(
                title="List of permissions",
                description=desc,
                color=0x00b8ff
            ))


