# Murder Mystery Bot

A self-hostable Discord game of social deduction. One bot process can run many games in many servers at the same time. Server data stays on your machine in SQLite.

Guild invite: https://discord.com/oauth2/authorize?client_id=1452886075621249024&permissions=137439332416&integration_type=0&scope=applications.commands+bot

`client_id` is the Discord application id. The scope always includes `applications.commands`. In the developer portal, enable the **Message Content** and **Server Members** intents before inviting the bot.

Support server: https://discord.gg/kriti

## Features

- Lobbies, day and night rounds, voting, and win conditions
- Roles including murderer, doctor, detective, banker, thief, jailer, broadcaster, fool, hunter, werewolf, cupid, mayor, bodyguard, and medium
- Prefix commands (`!join`) and slash commands (`/join`) that share the same game rules
- Admin settings panel for timers, disabled commands, prefix, and live games
- Wildcard permissions such as `admin.*` and `member.join`

## Requirements

- Docker, or Python 3.11+
- A Discord application with the Message Content and Server Members intents enabled
- A bot token

## Quick start

```bash
git clone https://github.com/Krithiv-7/Murder-Mystery-Bot-main.git
cd Murder-Mystery-Bot-main
cp .env.example .env
```

Put your token in `.env`:

```env
DISCORD_TOKEN=your-token
```

Start the bot:

```bash
docker compose up -d
docker compose logs -f bot
```

Stop, restart, and update:

```bash
docker compose down
docker compose restart
git pull
docker compose build --pull
docker compose up -d
```

Other useful commands:

```bash
docker compose ps
docker compose logs -f
```

Persistent files live in `./data` (the SQLite database and heartbeat). The database uses WAL mode and an in-memory cache so many servers can read settings without waiting on disk. Backups are written to `./backups`. Logs are written to `./logs`. Those directories are mounted into the container, so `docker compose down` does not delete them.

## Documentation

Player and operator guides in this repository:

- [How to play](wiki/guides/playing.md)
- [Commands](wiki/guides/commands.md)
- [Roles](wiki/guides/roles.md)
- [Items](wiki/guides/items.md)
- [Server settings](wiki/guides/settings.md)
- [Privacy](wiki/guides/privacy.md) and [terms](wiki/guides/terms.md)

## Commands

Lobby codes look like `MM-7F2A`. Use the code from `!list` or `/list`.

| Action | Prefix | Slash |
| --- | --- | --- |
| Create a lobby | `!create` | `/create` |
| List lobbies | `!list` | `/list` |
| Join | `!join MM-7F2A` | `/join` |
| Spectate | `!spectate MM-7F2A` | `/spectate` |
| Help | `!help` | `/help` |
| Settings panel | `!settingspanel` | `/settingspanel` |
| Bot status | `!status` | `/status` |

`!help` and `/help` show Murder Mystery Bot v2.0.0 plus the command catalog. `!status` is limited to people with `admin.*` or Discord administrator.

## Permissions

Permissions are a tree. A stored `admin.*` grant allows every admin command. Discord administrators bypass the tree. Grants can be given to a member or a role. Removing a permission from a member blocks that permission even when the server default would have allowed it.

```text
!addPermission @User member.join
!removePermission @Role admin.settings
!permissions @User
```

Only people who already have the matching admin permission can grant, revoke, reset a server, force-start or end games, or change configuration.

## Configuration

Environment defaults live in `.env`. Each server can override the prefix and the game timers from `!settings` or the settings panel.

| Variable | Purpose |
| --- | --- |
| `DISCORD_TOKEN` | Bot token. Required. |
| `DATABASE_URL` | Default `sqlite:///data/bot.sqlite` |
| `BOT_PREFIX` | Default prefix when a server has not chosen one |
| `LOG_LEVEL` | `INFO` by default |
| `MMB_STORAGE` | `sqlite` (default), `json`, or `mongo` |
| `MMB_TESTING_BOT` | `true` skips official-server-only setup |

MongoDB is optional. Install it with `pip install pymongo dnspython` and set `MMB_STORAGE=mongo`. The default Docker setup does not run MongoDB.

## Backup and restore

```bash
docker compose exec bot python -m core.cli backup
```

That writes `backups/backup-YYYY-MM-DD.sqlite`. To restore, stop the bot, replace `data/bot.sqlite` with that file, and start the bot again.

Import an older `data.json` without deleting it:

```bash
docker compose exec bot python -m core.cli migrate
```

The first SQLite startup also imports `data.json` automatically when the database has no guilds yet.

## Development

```bash
make install
make test
make lint
make run
```

`make run` uses the local Python environment. `make docker` starts Compose. Tests do not connect to Discord.

## Troubleshooting

- `ERROR: DISCORD_TOKEN is missing.` Add the token to `.env` and run `docker compose up -d` again.
- The bot is online but ignores `!` commands. Enable the Message Content intent, and check that an admin has not disabled the command in the settings panel.
- A player never receives role DMs. Joining sends a DM. If Discord blocks it, the status channel mentions that player and shows **Allow DMs from this bot**.
- `docker compose ps` shows the container as unhealthy. Wait for the start period, then check `docker compose logs -f bot`. The health check only looks at a heartbeat file written by the running bot.
