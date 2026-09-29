# Murder Mystery Bot — code layout

Last updated: September 29, 2026

Version 2.0.0. The game rules still live in `core/game.py`, `roles.py`, `items.py`, and `objectives.py`. Discord commands call that code instead of reimplementing it.

```text
bot.py                 start, shutdown, token check
core/
  config.py            environment defaults and guild setting defaults
  manager.py           lobby registry and MM- codes
  game.py              day/night loop, voting, win, cleanup
  lobby.py             shared join checks for prefix and slash
  commands_meta.py     help text and disableable commands
  cli.py               status, backup, migrate, health
commands/              prefix cogs: game, player, admin, settings, wiki
discordbot/            client, events, slash commands, help, permissions
storage/sqlite_store.py
dataStorage.py         SQLite by default; JSON and Mongo remain optional
```

Lobby lookup goes through `game_manager.get_game(guild_id, code)`. Player stats and server settings go through `dataStorage`, which writes SQLite unless `MMB_STORAGE` is `json` or `mongo`.

Run `python bot.py` or `docker compose up -d`. Tests do not connect to Discord.
