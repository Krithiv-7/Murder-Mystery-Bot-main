# Privacy Policy — Murder‑Mystery‑Bot

Last updated: December 23, 2025

This Privacy Policy explains what information the Murder‑Mystery‑Bot (the "Bot") processes and why. By inviting or interacting with the Bot, you acknowledge these practices.

## 1. Summary
We collect only the minimum data needed to operate the game inside Discord. This primarily includes Discord identifiers and game state. We do not permanently store message content.

## 2. Information We Process
- **Discord Identifiers:** server (guild) ID, user ID. Needed to associate game state with users and servers.
- **Game State and Configuration:** items, currency, role status, per‑user or per‑server settings required for gameplay.
- **Operational Metadata:** limited technical logs in memory for reliability and debugging. We do not persist message content beyond transient command handling.

## 3. Sources of Data
- Data is received via the Discord API when you use commands or when server administrators configure the Bot.

## 4. Storage and Retention
- **Storage options:** The Bot can store data in a local JSON file (`data.json`, with periodic backups) or in MongoDB (database `discord`, collection `murder-mystery`), depending on configuration.
- **Retention:** Game state is retained while the Bot is active in your server. Server administrators or the maintainers may delete data upon request. If the Bot is removed, data may be deleted as part of routine maintenance.

## 5. Self‑Hosted Deployments
- If you self‑host, you act as the data controller for your instance. You must configure security, retention, and lawful processing. This policy describes the maintainers' hosted instance; self‑hosted operators should publish their own privacy notice.

## 6. Security
- We use reasonable technical measures for the hosted instance (limited access to credentials, least privilege). No system is perfectly secure; please report issues responsibly.

## 7. Children
- The Bot is intended for users 13+ in accordance with Discord's policies. We do not knowingly collect information from children under 13.

## 8. Your Choices and Rights
- **Access/Correction/Deletion:** Contact your server administrators or the maintainers to request updates or deletion of game state associated with your user ID or server ID.
- **Opt‑Out:** You can stop using the Bot at any time; server administrators can remove the Bot.

## 9. Sharing and Third Parties
- We do not sell personal data. Data is shared only with infrastructure providers (e.g., MongoDB if enabled) strictly to operate the Bot.

## 10. Changes to This Policy
- We may update this Privacy Policy. Continued use of the Bot after updates indicates acceptance of the revised policy.

## 11. Contact
- For privacy questions or requests, use the support server (see README) or open an issue in the repository.