import json
from pathlib import Path

from storage.sqlite_store import SqliteStore


def test_sqlite_migration_import_and_backup(tmp_path: Path):
    database = tmp_path / "bot.sqlite"
    store = SqliteStore(database)
    store.migrate()
    store.migrate()
    guild = type("Guild", (), {"id": 7})()
    store.set_guild(guild.id, "prefix", value="?")
    store.set_player(guild.id, 3, "villagerWins", increase=2)
    store.set_player(guild.id, 3, "permissions", value={"member": {"join": True}})
    assert store.get_guild(guild.id, "prefix") == "?"
    assert store.get_player(guild.id, 3, "villagerWins") == 2

    legacy = tmp_path / "data.json"
    legacy.write_text(
        json.dumps({"8": {"prefix": "!", "members": {"4": {"gamesPlayed": 3}}}}),
        encoding="utf-8",
    )
    fresh = SqliteStore(tmp_path / "imported.sqlite")
    fresh.migrate()
    count = fresh.import_legacy_document(json.loads(legacy.read_text(encoding="utf-8")))
    assert count == 1
    assert fresh.get_guild(8, "prefix") == "!"
    assert fresh.get_player(8, 4, "gamesPlayed") == 3

    backup = fresh.backup_to(tmp_path / "backup-test.sqlite")
    assert backup.exists()
    store.close()
    fresh.close()


def test_command_registry_is_the_toggle_source():
    from commands.game_commands import GameCommands
    from core.commands_meta import COMMANDS, disableable_command_names
    from discordbot.slash_commands import slash_join

    names = disableable_command_names()
    assert "join" in names
    assert "createGame" in names
    assert COMMANDS["join"]["permission"] == "member.join"
    import inspect

    assert GameCommands.join.callback.__name__ == "join"
    assert slash_join.callback.__name__ == "slash_join"
    assert "join_block_reason" in inspect.getsource(slash_join.callback)
    assert "join_block_reason" in inspect.getsource(GameCommands.join.callback)
