CREATE TABLE IF NOT EXISTS guilds (
    guild_id TEXT PRIMARY KEY,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS guild_settings (
    guild_id TEXT NOT NULL,
    key TEXT NOT NULL,
    value_json TEXT NOT NULL,
    PRIMARY KEY (guild_id, key)
);

CREATE TABLE IF NOT EXISTS players (
    guild_id TEXT NOT NULL,
    member_id TEXT NOT NULL,
    PRIMARY KEY (guild_id, member_id)
);

CREATE TABLE IF NOT EXISTS player_stats (
    guild_id TEXT NOT NULL,
    member_id TEXT NOT NULL,
    key TEXT NOT NULL,
    value_json TEXT NOT NULL,
    PRIMARY KEY (guild_id, member_id, key)
);

CREATE TABLE IF NOT EXISTS permissions (
    guild_id TEXT NOT NULL,
    subject_type TEXT NOT NULL,
    subject_id TEXT NOT NULL,
    tree_json TEXT NOT NULL,
    PRIMARY KEY (guild_id, subject_type, subject_id)
);
