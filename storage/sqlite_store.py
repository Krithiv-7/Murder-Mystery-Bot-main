"""SQLite persistence for guild settings, player stats, and permissions.

Runtime games are not stored here. Values stay JSON so existing callers can
keep using arbitrary keys.
"""

from __future__ import annotations

import json
import sqlite3
from datetime import UTC, datetime
from pathlib import Path


class SqliteStore:
    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(self.path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row

    def close(self) -> None:
        self.conn.close()

    def ping(self) -> bool:
        try:
            self.conn.execute("SELECT 1")
            return True
        except sqlite3.Error:
            return False

    def migrate(self) -> None:
        self.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS schema_migrations (
                version INTEGER PRIMARY KEY,
                applied_at TEXT NOT NULL
            )
            """
        )
        applied = {
            row[0]
            for row in self.conn.execute("SELECT version FROM schema_migrations")
        }
        migrations = sorted((Path(__file__).parent / "migrations").glob("*.sql"))
        for path in migrations:
            version = int(path.name.split("_", 1)[0])
            if version in applied:
                continue
            self.conn.executescript(path.read_text(encoding="utf-8"))
            self.conn.execute(
                "INSERT INTO schema_migrations(version, applied_at) VALUES(?, ?)",
                (version, _now()),
            )
        self.conn.commit()

    def flush(self) -> None:
        self.conn.commit()

    def backup_to(self, destination: Path) -> Path:
        destination.parent.mkdir(parents=True, exist_ok=True)
        self.conn.commit()
        target = sqlite3.connect(destination)
        try:
            self.conn.backup(target)
        finally:
            target.close()
        return destination

    def guild_count(self) -> int:
        row = self.conn.execute("SELECT COUNT(*) FROM guilds").fetchone()
        return int(row[0])

    def import_legacy_document(self, payload: dict) -> int:
        """Import a data.json object. Returns the number of guilds copied."""
        imported = 0
        for guild_id, body in payload.items():
            if not isinstance(body, dict):
                continue
            self._ensure_guild(str(guild_id))
            members = body.get("members") or {}
            for key, value in body.items():
                if key == "members":
                    continue
                self.set_guild(str(guild_id), key, value=value)
            if isinstance(members, dict):
                for member_id, stats in members.items():
                    if not isinstance(stats, dict):
                        continue
                    for key, value in stats.items():
                        self.set_player(str(guild_id), str(member_id), key, value=value)
            imported += 1
        self.conn.commit()
        return imported

    def import_kv_backup(self, sqlite_path: Path) -> None:
        """Copy rows from the old disaster_backup.sqlite key-value mirror."""
        if not sqlite_path.exists():
            return
        source = sqlite3.connect(sqlite_path)
        source.row_factory = sqlite3.Row
        try:
            tables = {
                row[0]
                for row in source.execute(
                    "SELECT name FROM sqlite_master WHERE type='table'"
                )
            }
            if "guild_kv" in tables:
                for row in source.execute("SELECT guild_id, key, value_json FROM guild_kv"):
                    self.set_guild(row["guild_id"], row["key"], value=json.loads(row["value_json"]))
            if "member_kv" in tables:
                query = "SELECT guild_id, member_id, key, value_json FROM member_kv"
                for row in source.execute(query):
                    self.set_player(
                        row["guild_id"],
                        row["member_id"],
                        row["key"],
                        value=json.loads(row["value_json"]),
                    )
        finally:
            source.close()
        self.conn.commit()

    def set_guild(self, guild_id, key, *, value=None, increase=None):
        self._ensure_guild(str(guild_id))
        if increase is not None:
            current = self.get_guild(guild_id, key, default=0)
            value = current + increase
        self.conn.execute(
            """
            INSERT INTO guild_settings(guild_id, key, value_json)
            VALUES(?, ?, ?)
            ON CONFLICT(guild_id, key) DO UPDATE SET value_json=excluded.value_json
            """,
            (str(guild_id), key, json.dumps(value)),
        )
        self._mirror_permission("guild", str(guild_id), key, value)
        self.conn.commit()

    def get_guild(self, guild_id, key, **kwargs):
        self._ensure_guild(str(guild_id))
        row = self.conn.execute(
            "SELECT value_json FROM guild_settings WHERE guild_id=? AND key=?",
            (str(guild_id), key),
        ).fetchone()
        if row is not None:
            return json.loads(row["value_json"])
        if "default" in kwargs:
            self.set_guild(guild_id, key, value=kwargs["default"])
            return kwargs["default"]
        return None

    def delete_guild(self, guild_id, key):
        row = self.conn.execute(
            "SELECT value_json FROM guild_settings WHERE guild_id=? AND key=?",
            (str(guild_id), key),
        ).fetchone()
        if row is None:
            return None
        self.conn.execute(
            "DELETE FROM guild_settings WHERE guild_id=? AND key=?",
            (str(guild_id), key),
        )
        self.conn.commit()
        return json.loads(row["value_json"])

    def set_player(self, guild_id, member_id, key, *, value=None, increase=None):
        self._ensure_player(str(guild_id), str(member_id))
        if increase is not None:
            current = self.get_player(guild_id, member_id, key, default=0)
            value = current + increase
        self.conn.execute(
            """
            INSERT INTO player_stats(guild_id, member_id, key, value_json)
            VALUES(?, ?, ?, ?)
            ON CONFLICT(guild_id, member_id, key)
            DO UPDATE SET value_json=excluded.value_json
            """,
            (str(guild_id), str(member_id), key, json.dumps(value)),
        )
        if key in {"permissions", "removedFromDefaultPermissions"}:
            self._mirror_permission(
                "member", str(member_id), key, value, guild_id=str(guild_id)
            )
        self.conn.commit()

    def get_player(self, guild_id, member_id, key, **kwargs):
        self._ensure_player(str(guild_id), str(member_id))
        row = self.conn.execute(
            """
            SELECT value_json FROM player_stats
            WHERE guild_id=? AND member_id=? AND key=?
            """,
            (str(guild_id), str(member_id), key),
        ).fetchone()
        if row is not None:
            return json.loads(row["value_json"])
        if "default" in kwargs:
            self.set_player(guild_id, member_id, key, value=kwargs["default"])
            return kwargs["default"]
        return None

    def delete_player(self, guild_id, member_id, key):
        row = self.conn.execute(
            """
            SELECT value_json FROM player_stats
            WHERE guild_id=? AND member_id=? AND key=?
            """,
            (str(guild_id), str(member_id), key),
        ).fetchone()
        if row is None:
            return None
        self.conn.execute(
            "DELETE FROM player_stats WHERE guild_id=? AND member_id=? AND key=?",
            (str(guild_id), str(member_id), key),
        )
        self.conn.commit()
        return json.loads(row["value_json"])

    def all_guilds(self) -> list[dict]:
        guilds = []
        for row in self.conn.execute("SELECT guild_id FROM guilds"):
            guild_id = row["guild_id"]
            document = {"_id": int(guild_id) if str(guild_id).isdigit() else guild_id}
            settings = self.conn.execute(
                "SELECT key, value_json FROM guild_settings WHERE guild_id=?",
                (guild_id,),
            )
            for setting in settings:
                document[setting["key"]] = json.loads(setting["value_json"])
            guilds.append(document)
        return guilds

    def _ensure_guild(self, guild_id: str) -> None:
        self.conn.execute(
            "INSERT OR IGNORE INTO guilds(guild_id, created_at) VALUES(?, ?)",
            (guild_id, _now()),
        )

    def _ensure_player(self, guild_id: str, member_id: str) -> None:
        self._ensure_guild(guild_id)
        self.conn.execute(
            "INSERT OR IGNORE INTO players(guild_id, member_id) VALUES(?, ?)",
            (guild_id, member_id),
        )

    def _mirror_permission(self, subject_type, subject_id, key, value, guild_id=None):
        if key not in {"permissions", "roles", "defaultPermissions", "removedFromDefaultPermissions"}:
            return
        stored_guild = guild_id or subject_id
        self.conn.execute(
            """
            INSERT INTO permissions(guild_id, subject_type, subject_id, tree_json)
            VALUES(?, ?, ?, ?)
            ON CONFLICT(guild_id, subject_type, subject_id)
            DO UPDATE SET tree_json=excluded.tree_json
            """,
            (stored_guild, subject_type, subject_id, json.dumps(value)),
        )


def _now() -> str:
    return datetime.now(UTC).isoformat()
