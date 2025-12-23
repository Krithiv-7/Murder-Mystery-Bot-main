# Murder‑Mystery‑Bot — Commands Guide

Last updated: December 23, 2025

This guide lists the main commands you can use during a game and outside of a game.

## Commands During Game

### `!vote @<player>`
- Only usable during ☀️ daytime voting.
- Vote on which player should be executed. The player with the most votes is executed.

### `!shop`
- Only usable during 🌕 nighttime.
- View items available to purchase.

### `!buy <item>`
- Only usable during 🌕 nighttime.
- Buy an item from the shop.

### `!use <item> [optional argument]`
- Usable during day or night depending on the item.
- Use an item from your inventory. Some items require a target or text parameter.

### `!whisper <player>`
- Only usable during ☀️ daytime.
- Creates a temporary private channel between you and the specified player (deleted at night).

### `!leave`
- Leave your current game.

## Other Commands (Outside of a Game)

### `!create`
- Creates a new lobby and auto-adds you to it. Anyone can create a lobby if they aren’t already in one.

### `!join <ID>`
- Joins the lobby with the given ID. Use `!list` to find IDs. You must provide an ID; lobbies are not auto-created by `!join`.

### `!list`
- Shows all running games with their IDs. Useful when you need a game ID to spectate.

### `!spectate <ID>`
- Spectate a game with the specified ID. To stop spectating, use `!spectate` again.

### `!stats <user>`
- Shows stats such as how many games a user played and how many wins.

### `!level`
- Shows your level and how much XP you need to level up.

### `!objective`
- Gives you a new objective or shows your progress toward your current objective.

---

For the full advanced/admin command set, see [help-advanced.md](help-advanced.md). For roles and items, see [help-roles.md](help-roles.md) and [help-items.md](help-items.md).

Slash command equivalents: `/create`, `/list`, `/join <ID>`, `/spectate <ID>`, `/help`, `/ping`.