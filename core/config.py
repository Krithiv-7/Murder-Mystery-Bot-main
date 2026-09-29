# Bot configuration settings
import os
from pathlib import Path

import discord

ROOT = Path(__file__).resolve().parent.parent


def load_dotenv() -> None:
    """Load .env without overriding variables that are already set."""
    path = ROOT / ".env"
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


load_dotenv()


def _read_bool_env(name, default):
    """Read a boolean value from the environment without crashing."""
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() not in {"0", "false", "no", "off"}


# Storage settings
# MMB_LOCAL_STORAGE=false keeps the historical MongoDB path when MMB_STORAGE
# is not set. The default self-hosted backend is SQLite.
localStorage = _read_bool_env("MMB_LOCAL_STORAGE", True)
testingBot = _read_bool_env("MMB_TESTING_BOT", True)    # Disable main server integration


def storage_backend() -> str:
    explicit = os.getenv("MMB_STORAGE")
    if explicit:
        return explicit.strip().lower()
    if not localStorage:
        return "mongo"
    return "sqlite"


def sqlite_path() -> Path:
    raw = os.getenv("DATABASE_URL", "sqlite:///data/bot.sqlite")
    if raw.startswith("sqlite:///"):
        relative = raw[len("sqlite:///"):]
        path = Path(relative)
        if not path.is_absolute():
            path = ROOT / path
        return path
    return ROOT / "data" / "bot.sqlite"


def json_data_path() -> Path:
    return ROOT / "data.json"


def legacy_sqlite_path() -> Path:
    return ROOT / "disaster_backup.sqlite"


def data_dir() -> Path:
    path = ROOT / "data"
    path.mkdir(parents=True, exist_ok=True)
    return path


def log_level() -> str:
    return os.getenv("LOG_LEVEL", "INFO").upper()

# Game role configuration
requiredRoles = ["murderer", "doctor"]
roles = {
    "detective": 4,
    "banker": 4,
    "thief": 4,
    "jailer": 5,
    "broadcaster": 6,
    "fool": 6,
    "hunter": 6,
    "werewolf": 7,
    "cupid": 8,
    "mayor": 4,
    "bodyguard": 5,
    "medium": 6,
}

GAME_DEFAULTS = {
    "minPlayers": 4,
    "maxPlayers": 30,
    "preGameTimer": 120,
    "votingTime": 120,
    "nightTimeTimer": 60,
    "prefix": os.getenv("BOT_PREFIX", "!"),
}

# Server links
mainServerInvite = "https://discord.gg/kriti"
shortMainServerInvite = "discord.gg/kriti"

# Common embeds
noPermissionEmbed = discord.Embed(
    title="You don't have permission to do that!",
    description="You don't have permission to use that command here.",
    color=0xff0000
)
