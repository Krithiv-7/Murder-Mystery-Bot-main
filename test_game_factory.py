import asyncio
import importlib
import os

import discord

os.environ.setdefault("DISCORD_TOKEN", "test-token")

import bot
core_game_module = importlib.import_module("core.game")


class DummyModernGame:
    def __init__(self, guild, debug):
        self.guild = guild
        self.debug = debug
        self.created = False

    async def createGame(self, client=None):
        self.created = True


class DummyLegacyGame:
    def __init__(self, guild, debug):
        self.guild = guild
        self.debug = debug

    async def createGame(self):
        return None


def test_createNewGame_uses_modular_game_factory():
    original_modern = core_game_module.Game
    original_legacy = bot.game

    core_game_module.Game = DummyModernGame
    bot.game = DummyLegacyGame

    try:
        async def run_test():
            game_obj = await bot.createNewGame(object(), False)
            assert isinstance(game_obj, DummyModernGame)
            assert game_obj.created is True

        asyncio.run(run_test())
    finally:
        core_game_module.Game = original_modern
        bot.game = original_legacy


def test_removePlayer_handles_stale_state_without_crashing():
    from types import SimpleNamespace

    guild = SimpleNamespace(id=42)
    game = core_game_module.Game(guild, False)
    member = SimpleNamespace(id=7)
    player = SimpleNamespace(
        member=member,
        inGame=True,
        inventory=[],
        inLove=False,
        lover=None,
        dyingNow=False,
        loveChannel=None,
        nightChannel=None,
        roleChannel=None,
        broadcastChannel=None,
        role=SimpleNamespace(name='none'),
        game=game,
    )

    game.players = [player]
    game.channels = []
    game.guild.id = 42

    original_all_players = core_game_module.allPlayers.get(guild.id, [])
    try:
        core_game_module.allPlayers[guild.id] = []

        async def run_test():
            await game.removePlayer(player)
            assert player.inGame is False
            assert player not in game.players

        asyncio.run(run_test())
    finally:
        if original_all_players:
            core_game_module.allPlayers[guild.id] = original_all_players
        else:
            core_game_module.allPlayers.pop(guild.id, None)


def test_modular_game_has_all_lifecycle_methods():
    required_methods = [
        "ensure_main_channel",
        "createGame",
        "makeNightTime",
        "dayTime",
        "safe_send",
        "sendToAllNightChannels",
        "checkWin",
        "stopGame",
        "cleanUp",
    ]
    for method in required_methods:
        assert hasattr(core_game_module.Game, method), f"Missing method {method} in core.game.Game"


def test_player_update_inventory_sends_inventory_by_dm():
    from types import SimpleNamespace
    from core.player import Player

    sent = []

    async def send(*args, **kwargs):
        sent.append((args, kwargs))

    async def safe_send(channel, *args, **kwargs):
        await channel.send(*args, **kwargs)

    game = SimpleNamespace(role=SimpleNamespace(), safe_send=safe_send)
    member = SimpleNamespace(id=1, display_name="TestUser", send=send)
    p = Player(member, game)

    asyncio.run(p.updateInventory())
    assert len(sent) == 1
    assert "embed" in sent[0][1]


def test_game_commands_cog_has_create():
    from commands.game_commands import GameCommands
    cog = GameCommands(bot.client)
    assert hasattr(cog, "createGame")
    cmd = cog.createGame
    assert "create" in cmd.aliases


def test_core_utils_create_new_game():
    from core.utils import createNewGame
    from types import SimpleNamespace

    created = False

    class DummyGame:
        def __init__(self, guild, debug):
            self.guild = guild
            self.debug = debug

        async def createGame(self, client=None):
            nonlocal created
            created = True

    original = core_game_module.Game
    core_game_module.Game = DummyGame
    try:
        guild = SimpleNamespace(id=1, channels=[])
        res = asyncio.run(createNewGame(guild, False))
        assert isinstance(res, DummyGame)
        assert created is True
    finally:
        core_game_module.Game = original

