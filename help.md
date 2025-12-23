# Welcome to Murder Mystery
This is a game of murder mystery inside Discord. Every player receives a role, and one of them is the murderer. All the other players must figure out who the murderer is and execute them before the murderer kills them first.

## Tutorial Overview
This tutorial is split into four parts:
- Game: How the game itself works
- Roles: See the full list in [help-roles.md](help-roles.md)
- Items: See the full list in [help-items.md](help-items.md)
- Commands: See the full list in [help-commands.md](help-commands.md)

## Joining a Game
- Create a lobby with `!create` (or `/create`). You’ll be added automatically.
- Share the lobby ID with others. They can join using `!join <ID>` (or `/join <ID>`). Use `!list` (or `/list`) to find IDs.
- You can only be in one lobby at a time. Use `!leave` before creating or joining another lobby.
 - Lobby owners can force start their lobby with `!forceStart` (`!ownerstart`/`!fs`).

## Roles
Everyone gets a special role assigned, such as murderer, detective, doctor, etc. That role will have special abilities that can only be used at night time.

## Day/Night Cycle
The game cycles between day and night every few minutes.

### ☀️ During Daytime
The following things will happen during daytime (in order):
1. Sunrise: All players are locked out of their night channels and the daytime channel opens.
2. Deaths Announcement (optional): If someone got killed last night, everyone is notified when it becomes daytime.
3. Gold Per Day Increase (optional): Everyone receives gold each day. This amount starts at 1 and increases by 1 every 3 days. If 5 or fewer players remain, it also increases by 1.
4. Gold Distribution: Everyone receives gold based on the current gold-per-day.
5. Voting: Vote someone to execute using `!vote <player>`. If the murderer is executed, innocents win.
6. Execution: The most voted player gets executed and removed from the game.
7. Weather Forecast: Upcoming weather and moonlight for the night are shown. Different weather can affect different roles.
8. Sunset: Daytime channel locks; nighttime channels open.

### 🌕 During Nighttime
Nighttime does not follow a fixed order; actions happen based on what players do:
- Shop: Use `!shop` to view and purchase items with your gold. Buy items with `!buy <itemId>`.
- Role Abilities: Use your role’s special ability during the night.
- Other Events: Outcomes depend on roles, items used, and player actions.

## Basic Commands
- `!create` — Create a new lobby and join it
- `!join <ID>` — Join a lobby by ID
- `!list` — Show running games and IDs
- `!spectate <ID>` — Spectate a running game
- `!leave` — Leave your current game
- `!vote <@player>` — Vote to execute a player during day
- `!whisper <@player>` — Temporary private channel with another player (deleted at night)
- `!shop` — View items available at night
- `!buy <itemId>` — Buy an item from the shop
- `!use <itemId> [arg]` — Use an item (some require a target)
- `!balance` (aliases: `!money`, `!gold`, `!bal`) — Show your gold
 - Slash equivalents: `/create`, `/list`, `/join <ID>`, `/spectate <ID>`

## Advanced Docs
- Advanced/Admin Commands: [help-advanced.md](help-advanced.md)
- Server Settings Reference: [help-settings.md](help-settings.md)

## Support & Links
- Discord server: https://discord.gg/kriti
- GitHub: https://github.com/Krithiv-7/Murder-Mystery-Bot-main
- Policies: [Terms of Service](tos.md), [Privacy Policy](pp.md), [Code of Conduct](CODE_OF_CONDUCT.md)