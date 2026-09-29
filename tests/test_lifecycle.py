import asyncio
from types import SimpleNamespace
from unittest.mock import patch

from core.game import Game
from core.ids import generate_code, normalize_code
from core.lobby import join_block_reason
from core.manager import GameManager, game_manager
from permissions import permissionInPermissionDic


def test_codes_are_stable_and_normalized():
    used = set()
    first = generate_code(used)
    used.add(first)
    second = generate_code(used)
    assert first.startswith("MM-")
    assert first != second
    assert normalize_code(first[-4:]) == first
    assert normalize_code(first.lower()) == first


def test_games_are_isolated_by_guild_and_code():
    manager = GameManager()
    guild_a = SimpleNamespace(id=101)
    guild_b = SimpleNamespace(id=202)
    game_a = SimpleNamespace(guild=guild_a, code=manager.allocate_code())
    game_b = SimpleNamespace(guild=guild_b, code=manager.allocate_code())
    manager.register(game_a)
    manager.register(game_b)

    assert manager.get_game(guild_a.id, game_a.code) is game_a
    assert manager.get_game(guild_b.id, game_a.code) is None
    assert manager.get_games(guild_a.id) == [game_a]

    manager.remove_game(game_a)
    manager.remove_game(game_a)
    assert manager.get_game(guild_a.id, game_a.code) is None


def _member(member_id, name):
    return SimpleNamespace(id=member_id, display_name=name, status=SimpleNamespace(name="online"))


def _player(member, role_name="none", weight=1):
    player = SimpleNamespace(
        member=member,
        voted=False,
        votes=0,
        votedOn=None,
        inGame=True,
        role=SimpleNamespace(name=role_name, voteWeight=weight, deadString=" died."),
        nightChannel=None,
        roleChannel=None,
        inLove=False,
    )
    return player


def test_vote_rules_and_cleanup():
    guild = SimpleNamespace(id=303, members=[])
    game = Game(guild, True)
    game_manager.register(game)
    alice = _player(_member(1, "Alice"))
    bob = _player(_member(2, "Bob"), role_name="mayor", weight=2)
    game.players = [alice, bob]
    game.voteTime = True

    async def run():
        ok, _message = await game.handle_vote(alice.member, bob.member)
        assert ok is True
        assert bob.votes == 1
        again, _message = await game.handle_vote(alice.member, bob.member)
        assert again is False
        game.voteTime = False
        closed, _message = await game.handle_vote(bob.member, alice.member)
        assert closed is False
        game.voteTime = True
        game.players = [bob]
        dead, _message = await game.handle_vote(alice.member, bob.member)
        assert dead is False

        class Channel:
            async def send(self, *args, **kwargs):
                return None

            async def set_permissions(self, *args, **kwargs):
                return None

        game.players = [_player(_member(3, "Cara"), role_name="doctor")]
        game.started = True
        game.mainChannel = Channel()
        game.role = None

        async def stop():
            game.stopped = True

        game.stopGame = stop
        await game.checkWin()
        assert game.victory is True
        assert game.stopped is True
        await game.cleanUp()
        await game.cleanUp()

    try:
        asyncio.run(run())
    finally:
        game_manager.remove_game(game)


def test_add_player_ignores_a_second_join():
    from core.game import Game

    guild = SimpleNamespace(id=909, members=[], get_channel=lambda _channel_id: None)
    game = Game(guild, True)

    class Channel:
        async def send(self, *args, **kwargs):
            return None

    game.mainChannel = Channel()
    member = SimpleNamespace(id=5, display_name="Ada", mention="<@5>")

    async def run():
        with patch("core.game.dataStorage.getGuildData", return_value=4):
            first = await game.addPlayer(member)
            second = await game.addPlayer(member)
        assert first is second
        assert len(game.players) == 1

    asyncio.run(run())


def test_join_block_reasons_do_not_cross_guilds():
    guild = SimpleNamespace(id=404)
    other = SimpleNamespace(id=405)
    game = SimpleNamespace(started=False, players=[], guild=guild, code="MM-JOIN")
    member = _member(9, "Joiner")
    with patch("core.lobby.dataStorage.getGuildData", return_value=30):
        assert join_block_reason(member, guild, None) == "not_found"
        assert join_block_reason(member, guild, game) is None
        game.started = True
        assert join_block_reason(member, guild, game) == "started"
        assert join_block_reason(member, other, game) == "started"
        game.started = False
        game.players = [object()] * 30
        assert join_block_reason(member, guild, game) == "full"


def test_permission_wildcards():
    assert permissionInPermissionDic({"admin": {"*": True}}, "admin.setup")
    assert permissionInPermissionDic({"member": {"join": True}}, "member.join")
    assert not permissionInPermissionDic({"member": {"list": True}}, "member.join")
    assert not permissionInPermissionDic(None, "member.join")
    assert permissionInPermissionDic({"*": True}, "debug.game.skipNight")
