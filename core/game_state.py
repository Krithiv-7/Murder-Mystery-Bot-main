# Shared game state dictionaries
# These are used across the bot to track running games and players

currentGames = {}
availableGames = {}
allPlayers = {}

# Main guild globals (set in on_ready)
mainGuild = None
mainGameRolePosition = 0

# Notification globals
notificationMessage = None
notificationChannel = None
newGamesRole = None
gamesStartingRole = None
joiningChannel = None


def set_main_guild_globals(**kwargs):
    """Update main guild globals from on_ready."""
    global mainGuild, mainGameRolePosition
    global notificationMessage, notificationChannel
    global newGamesRole, gamesStartingRole, joiningChannel
    
    if 'mainGuild' in kwargs:
        mainGuild = kwargs['mainGuild']
    if 'mainGameRolePosition' in kwargs:
        mainGameRolePosition = kwargs['mainGameRolePosition']
    if 'notificationMessage' in kwargs:
        notificationMessage = kwargs['notificationMessage']
    if 'notificationChannel' in kwargs:
        notificationChannel = kwargs['notificationChannel']
    if 'newGamesRole' in kwargs:
        newGamesRole = kwargs['newGamesRole']
    if 'gamesStartingRole' in kwargs:
        gamesStartingRole = kwargs['gamesStartingRole']
    if 'joiningChannel' in kwargs:
        joiningChannel = kwargs['joiningChannel']
