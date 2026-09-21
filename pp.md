# Privacy Policy — Murder‑Mystery‑Bot

Last updated: September 21, 2026

This Privacy Policy explains what information the Murder-Mystery-Bot (the "Bot") processes and why. It is an operational summary, not legal advice. Self-hosted operators must publish a notice appropriate to their own deployment.

## 1. Summary
We collect only the minimum data needed to operate the game inside Discord. This primarily includes Discord identifiers and game state. We do not permanently store message content.

## 2. Information We Process
- **Discord Identifiers:** server (guild) ID, user ID. Needed to associate game state with users and servers.
- **Game State and Configuration:** items, currency, role status, statistics, XP, objectives, permissions, and per-user or per-server settings required for gameplay.
- **Message and DM content:** command and role-action content is processed transiently to respond to users. The project is not designed to persist ordinary command or DM message content, although Discord retains messages under Discord's own policies.
- **Operational Metadata:** limited technical logs and error data may be processed for reliability and debugging.

## 3. Sources of Data
- Data is received via the Discord API when you use commands or when server administrators configure the Bot.

## 4. Storage and Retention
- **Storage options:** Local mode uses `data.json`, rotating JSON backups, and a local disaster-recovery SQLite database. MongoDB mode may store equivalent records in the configured MongoDB deployment (the default database and collection are `discord` and `murder-mystery`).
- **Retention:** Active configuration and player progression may remain while the Bot is installed or while the maintainer considers the data necessary for operation. Backups and logs may persist longer according to operational retention. Removing the Bot does not automatically guarantee immediate deletion of every backup.
- **Deletion requests:** Contact the maintainer through the support server or repository issue tracker with the server ID and user ID involved. Do not include a bot token or other secret. Requests may require confirmation from a server administrator or the affected account.

## 5. Self‑Hosted Deployments
- If you self‑host, you act as the data controller for your instance. You must configure security, retention, and lawful processing. This policy describes the maintainers' hosted instance; self‑hosted operators should publish their own privacy notice.

## 6. Security
- We use reasonable technical measures for the hosted instance (limited access to credentials, least privilege). No system is perfectly secure; please report issues responsibly.

## 7. Children
- Users must meet Discord's minimum age requirement in their location. The Bot is not directed at children, and maintainers do not knowingly request information from children in violation of applicable law.

## 8. Your Choices and Rights
- **Access/Correction/Deletion:** Contact your server administrators or the maintainers to request updates or deletion of game state associated with your user ID or server ID.
- **Opt‑Out:** You can stop using the Bot at any time; server administrators can remove the Bot.

## 9. Sharing and Third Parties
- We do not sell personal data. Data is shared only with infrastructure providers (e.g., MongoDB if enabled) strictly to operate the Bot.

## 10. Changes to This Policy
- We may update this Privacy Policy from time to time. The effective date above will change when an update is published. Material changes should be reviewed before continued use.

## 11. Contact
- For privacy questions or requests, use the support server (see README) or open an issue in the repository.