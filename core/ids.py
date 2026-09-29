"""Stable, human-friendly lobby codes.

Codes look like ``MM-7F2A``. Characters that are easy to confuse are omitted.
"""

from __future__ import annotations

import secrets

ALPHABET = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
CODE_LENGTH = 4


def normalize_code(token: str) -> str:
    """Accept ``MM-7F2A`` or ``7F2A`` and return the canonical code."""
    raw = str(token).strip().upper()
    if raw.startswith("MM-"):
        return raw
    if len(raw) == CODE_LENGTH and all(char in ALPHABET for char in raw):
        return f"MM-{raw}"
    return raw


def generate_code(used: set[str]) -> str:
    """Return a code that is not already present in ``used``."""
    while True:
        body = "".join(secrets.choice(ALPHABET) for _ in range(CODE_LENGTH))
        code = f"MM-{body}"
        if code not in used:
            return code
