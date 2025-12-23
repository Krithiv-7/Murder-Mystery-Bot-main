import discord
import dataStorage
import json

defaultPermissions = None
permissionsList = None


async def hasPermission(ctx, permission, **kwargs):
    if "bypassRoles" in kwargs:
        if memberHasPermission(ctx.author, permission, bypassRoles=kwargs["bypassRoles"]):
            return True
    else:
        if memberHasPermission(ctx.author, permission):
            return True

    await ctx.send(embed=discord.Embed(title=":closed_lock_with_key: You don't have permission to do that!",
                                       description=f"You're missing the following permission: {permission}\n\nIf you think you're supposed to have this permission, then ask an admin to execute the following command:\n!addPermission {ctx.author.mention} {permission}",
                                       color=0xff0000))
    return False


def memberHasPermission(member, permission: str, **kwargs):
    if member.guild_permissions.administrator:
        return True
    elif permissionInPermissionDic(dataStorage.getPlayerData(member, "permissions", default={}), permission):
        return True
    elif permissionInPermissionDic(getDefaultPermissions(guild=member.guild), permission):
        if not permissionInPermissionDic(dataStorage.getPlayerData(member, "removedFromDefaultPermissions", default={}),
                                         permission):
            return True
    else:
        bypassRoles = False
        if "bypassRoles" in kwargs:
            bypassRoles = kwargs["bypassRoles"]

        if not bypassRoles:
            for v in member.roles:
                if roleHasPermission(v, permission):
                    return True
        return False


def permissionInPermissionDic(dic: dict, permission: str) -> bool:
    gotPermission = False
    permissionList = permission.split(".")
    currentPermissionPosition = dic
    for v in permissionList:
        if v in currentPermissionPosition:
            if type(currentPermissionPosition[v]).__name__ == "dict":
                currentPermissionPosition = currentPermissionPosition[v]
                continue
            else:
                gotPermission = True
        elif "*" in currentPermissionPosition:
            return True

    if gotPermission:
        return True
    return False


def roleHasPermission(role, permission):
    roles = dataStorage.getGuildData(role.guild, "roles", default={})
    if f"{role.id}" not in roles:
        roles[f"{role.id}"] = {}
    if "permissions" not in roles[f"{role.id}"]:
        roles[f"{role.id}"]["permissions"] = {}
    # if "removedFromDefaultPermissions" not in roles[f"{role.id}"]:
    #     roles[f"{role.id}"]["removedFromDefaultPermissions"] = {}
    # if permissionInPermissionDic(getDefaultPermissions(guild=role.guild), permission):
    #     return not permissionInPermissionDic(roles[f"{role.id}"]["removedFromDefaultPermissions"], permission)
    return permissionInPermissionDic(roles[f"{role.id}"]["permissions"], permission)


def getPermissionList():
    global permissionsList, defaultPermissions
    if permissionsList is None:
        try:
            permissionsFile = open("permissions.json", "r")
            jsonData = json.load(permissionsFile)
            permissionsList = jsonData["permissions"]
            defaultPermissions = jsonData["defaultPermissions"]
            permissionsFile.close()
        except FileNotFoundError:
            print("ERROR: permissions.json not found! Permissions might not work properly.")

    return permissionsList


def getDefaultPermissions(**kwargs) -> dict:
    global permissionsList, defaultPermissions
    if "guild" in kwargs:
        p = dataStorage.getGuildData(kwargs["guild"], "defaultPermissions")
        if p is not None:
            return p
    if defaultPermissions is None:
        try:
            permissionsFile = open("permissions.json", "r")
            jsonData = json.load(permissionsFile)
            permissionsList = jsonData["permissions"]
            defaultPermissions = jsonData["defaultPermissions"]
            permissionsFile.close()
        except FileNotFoundError:
            print("ERROR: permissions.json not found! Permissions might not work properly.")

    return defaultPermissions


def isValidPermission(permission):
    if isinstance(permission, str):
        if "." in permission:
            permissionList = permission.split(".")
            if "" not in permissionList:
                currentPermissionPosition = getPermissionList()
                while len(permissionList) > 0:
                    if permissionList[0] in currentPermissionPosition:
                        currentPermissionPosition = currentPermissionPosition[permissionList[0]]
                        permissionList.pop(0)
                    elif permissionList[0] == "*":
                        return True
                    else:
                        return False
                return True
    return False


def addPermissionToMember(member, permission):
    permissions = dataStorage.getPlayerData(member, "permissions", default={})
    splitPermission = permission.split(".")
    dataStorage.setPlayerData(member, "permissions", value=addPermissionToDic(permissions, splitPermission))


def removePermissionFromMember(member, permission):
    permissions = dataStorage.getPlayerData(member, "permissions", default={})
    splitPermission = permission.split(".")

    if permissionInPermissionDic(getDefaultPermissions(guild=member.guild), permission):
        dataStorage.setPlayerData(member, "permissions", value=addPermissionToDic(
            dataStorage.getPlayerData(member, "removedFromDefaultPermissions", default={}), permission.split(".")))
    else:
        dataStorage.setPlayerData(member, "permissions", value=removePermissionFromDic(permissions, splitPermission))


def addPermissionToRole(role, permission):
    roles = dataStorage.getGuildData(role.guild, "roles", default={})
    splitPermission = permission.split(".")
    if f"{role.id}" not in roles:
        roles[f"{role.id}"] = {}
    if "permissions" not in roles[f"{role.id}"]:
        roles[f"{role.id}"]["permissions"] = {}
    roles[f"{role.id}"]["permissions"] = addPermissionToDic(roles[f"{role.id}"]["permissions"], splitPermission)
    dataStorage.setGuildData(role.guild, "roles", value=roles)


def removePermissionFromRole(role, permission):
    roles = dataStorage.getGuildData(role.guild, "roles", default={})
    splitPermission = permission.split(".")
    if f"{role.id}" not in roles:
        roles[f"{role.id}"] = {}
    if "permissions" not in roles[f"{role.id}"]:
        roles[f"{role.id}"]["permissions"] = {}
    if "removedFromDefaultPermissions" not in roles[f"{role.id}"]:
        roles[f"{role.id}"]["removedFromDefaultPermissions"] = {}

    if permissionInPermissionDic(getDefaultPermissions(guild=role.guild), permission):
        roles[f"{role.id}"]["removedFromDefaultPermissions"] = addPermissionToDic(
            roles[f"{role.id}"]["removedFromDefaultPermissions"], permission)
    else:
        roles[f"{role.id}"]["permissions"] = removePermissionFromDic(roles[f"{role.id}"]["permissions"],
                                                                     splitPermission)
    dataStorage.setGuildData(role.guild, "roles", value=roles)


def getMemberPermissions(member) -> dict:
    d = dataStorage.getPlayerData(member, "permissions", default={})
    for v in getAllPermissionsInPermissionDic(getDefaultPermissions(guild=member.guild)):
        d = addPermissionToDic(d, v.split("."))
    for v in getAllPermissionsInPermissionDic(
            dataStorage.getPlayerData(member, "removedFromDefaultPermissions", default={})):
        if v in getAllPermissionsInPermissionDic(d):
            d = removePermissionFromDic(d, v.split("."))
    return d


def getRolePermissions(role) -> dict:
    roles = dataStorage.getGuildData(role.guild, "roles", default={})
    if f"{role.id}" not in roles:
        roles[f"{role.id}"] = {}
    if "permissions" not in roles[f"{role.id}"]:
        roles[f"{role.id}"]["permissions"] = {}
    return roles[f"{role.id}"]["permissions"]


def getAllPermissionsInPermissionDic(dic: dict, **kwargs) -> list:
    if "currentlyAt" not in kwargs:
        currentlyAt = ""
    else:
        currentlyAt = kwargs["currentlyAt"]
    l = []
    for k in dic:
        if isinstance(dic[k], dict):
            currentlyAt = f"{k}."
            l.extend(getAllPermissionsInPermissionDic(dic[k], currentlyAt=currentlyAt))
        else:
            l.append(f"{currentlyAt}{k}")
    return l



def addPermissionToDefaultPermissions(guild, permission: str):
    dataStorage.setGuildData(guild, "defaultPermissions",
                             value=addPermissionToDic(getDefaultPermissions(guild=guild), permission.split(".")))


def removePermissionFromDefaultPermissions(guild, permission: str):
    dataStorage.setGuildData(guild, "defaultPermissions",
                             value=removePermissionFromDic(getDefaultPermissions(guild=guild), permission.split(".")))


def addPermissionToDic(dic: dict, permission: list):
    if len(permission) == 1:
        dic[permission[0]] = True
    else:
        if permission[0] not in dic:
            dic[permission[0]] = {}
        p = permission.copy()
        p.pop(0)
        dic[permission[0]] = addPermissionToDic(dic[permission[0]], p)
    return dic


def removePermissionFromDic(dic: dict, permission: list):
    if len(permission) == 1:
        dic.pop(permission[0])
    else:
        if permission[0] not in dic:
            dic[permission[0]] = {}
        p = permission.copy()
        p.pop(0)
        dic[permission[0]] = removePermissionFromDic(dic[permission[0]], p)
    dic = clean_empty(dic)
    return dic


# copied this function from stackoverflow
def clean_empty(d):
    if isinstance(d, dict):
        return {
            k: v
            for k, v in ((k, clean_empty(v)) for k, v in d.items())
            if v
        }
    if isinstance(d, list):
        return [v for v in map(clean_empty, d) if v]
    return d


def getPermissionTree(permissions, **kwargs):
    result = ""
    prefix = ""
    nextIndent = 1
    if "indent" in kwargs:
        for i in range(1, kwargs["indent"] + 1):
            prefix += "┃"
        nextIndent = kwargs["indent"] + 1

    for v in permissions:
        if type(permissions[v]).__name__ == "dict":
            result += f"""\n{prefix}{v}:{getPermissionTree(permissions[v], indent=nextIndent)}"""
        else:
            result += f"\n{prefix}{v}"
    return result
