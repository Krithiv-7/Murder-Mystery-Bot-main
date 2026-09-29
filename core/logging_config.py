"""Logging configuration. Never attach tokens or database credentials."""

from __future__ import annotations

import logging
from pathlib import Path

from core.config import log_level

_CONTEXT_FIELDS = ("guild_id", "user_id", "game_id", "command", "phase")


class _ContextDefaults(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        for field in _CONTEXT_FIELDS:
            if not hasattr(record, field):
                setattr(record, field, "-")
        return True


def configure_logging(log_path: Path | None = None) -> None:
    root = logging.getLogger("mmb")
    root.setLevel(log_level())
    root.handlers.clear()
    formatter = logging.Formatter(
        "%(asctime)s %(levelname)s %(name)s "
        "guild=%(guild_id)s user=%(user_id)s game=%(game_id)s "
        "command=%(command)s phase=%(phase)s %(message)s"
    )
    stream = logging.StreamHandler()
    stream.setFormatter(formatter)
    stream.addFilter(_ContextDefaults())
    root.addHandler(stream)
    if log_path is not None:
        log_path.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_path, encoding="utf-8")
        file_handler.setFormatter(formatter)
        file_handler.addFilter(_ContextDefaults())
        root.addHandler(file_handler)
    logging.getLogger("discord").setLevel(logging.INFO)
