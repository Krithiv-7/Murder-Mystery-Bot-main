"""Import legacy JSON or the old SQLite mirror into the current database."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from core.config import json_data_path, legacy_sqlite_path, sqlite_path
from storage.sqlite_store import SqliteStore


def import_legacy(database: Path | None = None, source: Path | None = None) -> int:
    store = SqliteStore(database or sqlite_path())
    store.migrate()
    payload_path = source or json_data_path()
    imported = 0
    if payload_path.exists():
        payload = json.loads(payload_path.read_text(encoding="utf-8"))
        if isinstance(payload, dict):
            imported = store.import_legacy_document(payload)
    mirror = legacy_sqlite_path()
    if mirror.exists() and imported == 0:
        store.import_kv_backup(mirror)
    store.close()
    return imported


def main() -> None:
    parser = argparse.ArgumentParser(description="Import data.json into SQLite")
    parser.add_argument("--source", type=Path, default=None)
    args = parser.parse_args()
    count = import_legacy(source=args.source)
    print(f"Imported {count} guilds into SQLite. The original file was left in place.")


if __name__ == "__main__":
    main()
