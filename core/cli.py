"""Container-friendly administration commands."""

from __future__ import annotations

import argparse
import shutil
import sys
import time
from datetime import UTC, datetime
from pathlib import Path

from core.config import data_dir, sqlite_path
from core.runtime import status_snapshot


def _heartbeat_path() -> Path:
    return data_dir() / "heartbeat"


def write_heartbeat() -> None:
    path = _heartbeat_path()
    path.write_text(str(time.time()), encoding="utf-8")


def heartbeat_fresh(max_age: float = 90) -> bool:
    path = _heartbeat_path()
    if not path.exists():
        return False
    try:
        written = float(path.read_text(encoding="utf-8").strip())
    except ValueError:
        return False
    return (time.time() - written) <= max_age


def backup_database(directory: Path | None = None) -> Path:
    folder = directory or (Path(__file__).resolve().parent.parent / "backups")
    folder.mkdir(parents=True, exist_ok=True)
    destination = folder / f"backup-{datetime.now(UTC).date().isoformat()}.sqlite"
    import dataStorage

    if dataStorage._repo is not None:
        return dataStorage._repo.backup_to(destination)
    source = sqlite_path()
    if source.exists():
        shutil.copy2(source, destination)
        return destination
    raise FileNotFoundError("No SQLite database is available to back up.")


def cmd_status() -> int:
    snapshot = status_snapshot()
    for key, value in snapshot.items():
        print(f"{key}: {value}")
    return 0


def cmd_health() -> int:
    import dataStorage

    database_ok = dataStorage.storage_status() in {"ok", "json", "mongo"}
    alive = heartbeat_fresh()
    if database_ok and alive:
        print("ok")
        return 0
    print("unhealthy")
    return 1


def cmd_backup() -> int:
    path = backup_database()
    print(path)
    return 0


def cmd_migrate() -> int:
    from scripts.migrate import import_legacy

    count = import_legacy()
    print(f"Imported {count} guilds.")
    return 0


def main(argv: list[str] | None = None) -> int:
    from core.config import localStorage
    from dataStorage import initializeDataStorage

    initializeDataStorage(localStorage)
    parser = argparse.ArgumentParser(prog="python -m core.cli")
    parser.add_argument("command", choices=["status", "backup", "migrate", "health"])
    args = parser.parse_args(argv)
    commands = {
        "status": cmd_status,
        "backup": cmd_backup,
        "migrate": cmd_migrate,
        "health": cmd_health,
    }
    return commands[args.command]()


if __name__ == "__main__":
    sys.exit(main())
