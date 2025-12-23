import permissions

print('--- Smoke Test: permissions.py ---')

# 1) None-safe behavior
print('None dict ->', permissions.permissionInPermissionDic(None, 'member.join'))

# 2) Simple exact match
perm = {'member': {'join': True}}
print('Simple match ->', permissions.permissionInPermissionDic(perm, 'member.join'))

# 3) Wildcard match
perm2 = {'member': {'*': True}}
print('Wildcard ->', permissions.permissionInPermissionDic(perm2, 'member.anything'))

# 4) Load defaults from permissions.json
default_perms = permissions.getDefaultPermissions()
print('Default loaded is dict ->', isinstance(default_perms, dict))
print('Default has member.join ->', permissions.permissionInPermissionDic(default_perms, 'member.join'))
