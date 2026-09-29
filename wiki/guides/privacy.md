# Privacy Policy — Murder Mystery Bot

Last updated: September 29, 2026

This Privacy Policy explains what information the Murder Mystery Bot (the "Bot") processes and why. It is an operational summary, not legal advice. Self-hosted operators must publish a notice appropriate to their own deployment.

## 1. Summary

We collect only the minimum data needed to operate the game inside Discord. This primarily includes Discord identifiers and game progress. We do not permanently store message content.

## 2. Information we process

- **Discord identifiers:** server id and user id, so settings and statistics stay with the right person and server.
- **Saved progress:** gold is not saved between games. XP, level, objectives, win statistics, permissions, and server settings are saved.
- **Message and DM content:** prefix commands and night replies are read so the game can respond. The Bot needs Discord’s Message Content intent for that. This content is not stored as a chat log. Discord keeps messages under Discord’s own policies.
- **User install:** **Allow DMs from this bot** opens Discord’s authorization page (`integration_type=1`, `scope=applications.commands`). The Bot does not receive or store that OAuth grant.
- **Logs:** may include server id, user id, lobby code, command name, and phase. Logs must not contain the bot token, a database password, or the text of a private night action.

## 3. Sources

Data arrives through the Discord API when someone uses a command or an admin changes settings.

## 4. Storage and retention

- The default store is `data/bot.sqlite`, using WAL mode. Frequently read rows are cached in the Bot process. Each server’s rows are separate.
- The live lobby (players, roles, votes, night targets) stays in memory and is discarded when the game ends or the process stops.
- The Bot does not create Discord channels, roles, or voice channels, and it does not store voice state.
- An existing `data.json` is imported once when the database has no guilds, and that file is left on disk. MongoDB is used only when `MMB_STORAGE=mongo`.
- Backups and logs may outlive a removed bot. Deletion requests should go to the support server or the repository, with the server id and user id, and without a token.

## 5. Self-hosted deployments

If you self-host, you are the operator of that instance. This policy describes the maintainers’ hosted bot. Publish your own notice for your deployment.

## 6. Security

Lobby codes work only in the server where that lobby exists. Game slash commands do not run in DMs. Create and join are rate limited. A custom prefix is 1 to 7 characters and cannot contain spaces. Report issues without including a token.

## 7. Children

Users must meet Discord’s minimum age. The Bot is not directed at children.

## 8. Choices

Ask a server admin or the maintainers to correct or delete saved progress for a user id or server id. You can stop using the Bot, and an admin can remove it.

## 9. Sharing

We do not sell personal data. A self-hosted database stays on that machine unless the operator turns on MongoDB.

## 10. Changes

The date at the top changes when this policy changes.

## 11. Contact

Use the support server linked from the README, or open a repository issue.

See also the [terms](terms.md).
