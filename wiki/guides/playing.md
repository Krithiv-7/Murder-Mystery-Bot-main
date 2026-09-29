# How to play

Last updated: September 29, 2026

Murder Mystery is a social deduction game in Discord. One player is the murderer. Everyone else has to find and execute them before the murderer kills the town.

Also see [roles](roles.md), [items](items.md), [commands](commands.md), and [server settings](settings.md).

## Joining a game

- Create a lobby with `!create` or `/create`. The host message has **Join & Play**, **Spectate instead**, and **Allow DMs from this bot**.
- Press **Allow DMs from this bot** once. That is the user-install authorization. Night actions and your role are sent as DMs after that. Joining does not send a separate DM.
- Share the lobby code, such as `MM-7F2A`. Others join with `!join MM-7F2A` or `/join`. Use `!list` or `/list` to see codes.
- A person can only be in one lobby, and only once. Use `!leave` before joining another.
- Discord administrators add `-overwriteAdminWarning` when joining, for example `!join MM-7F2A -overwriteAdminWarning`.
- The host can force-start with `!forceStart` (`!ownerstart` or `!fs`).

## Where messages go

Public status stays in the server's setup channel, or in the channel where the lobby was created. The bot does not create a channel, category, role, or voice channel per game. Each status message is tagged with the lobby code and shows the phase, day, player count, weather, and moon.

Private roles, night menus, shop use, and whispers are DMs.

## Day

1. The status channel announces the new day. Private night results stay in DMs.
2. If someone died overnight, the status channel says so without revealing secret roles.
3. Gold per day starts at 1, increases by 1 every 3 days, and increases again when 5 or fewer players remain.
4. Everyone receives that day's gold.
5. Vote with `!vote` or `/vote`. Executing the murderer wins the game for the town.
6. The player with the most votes is executed.
7. The status channel shows the coming weather and moon.
8. Night prompts go out by DM. The status channel only says that night has started.

## Night

- Shop with `!shop` and `!buy`, or `/shop` and `/buy`, in your DM.
- Role abilities use a menu in the DM. Typing the option number still works.
- When the murderer or werewolf attacks someone, the doctor gets **Heal them** and **Let them die**.

## Leveling

`!level` and `/level` show XP for this server. A finished game grants `5 × day count` XP, plus 20 for a murderer, werewolf, or fool win, or 10 for a villager win. The next level costs `(level + 1) × 5 × level` XP.

## Adding the bot

Guild install. Replace the application id if you self-host:

https://discord.com/oauth2/authorize?client_id=1452886075621249024&permissions=137439332416&integration_type=0&scope=applications.commands+bot

`client_id` is the Discord application id. The scope includes `applications.commands`. Enable the **Message Content** and **Server Members** intents. The invite grants Add Reactions, Send Messages, Embed Links, Attach Files, Read Message History, Use External Emojis, and Use External Sounds.

**Allow DMs from this bot** is a user install: `integration_type=1` and `scope=applications.commands`.

## Links

- [Commands](commands.md)
- [Privacy](privacy.md) and [terms](terms.md)
- [Code of Conduct](../../CODE_OF_CONDUCT.md)
- Support server: https://discord.gg/kriti
