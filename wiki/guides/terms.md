# Terms of Service — Murder Mystery Bot

Last updated: September 29, 2026

These terms govern use of the Murder Mystery Bot (the "Bot") in Discord. Inviting or using the Bot means you agree to them.

## 1. Eligibility

You must meet Discord’s minimum age and follow Discord’s terms and community guidelines. Server rules and the [Code of Conduct](../../CODE_OF_CONDUCT.md) also apply.

## 2. Acceptable use

Do not spam, harass, cheat, exploit bugs, or bypass rate limits. Do not use the Bot to collect personal data unlawfully. Report abuse through the support server or the repository, without sending a bot token.

## 3. What the Bot does

The Bot is provided as is and may change or stop.

A server installs it with a guild invite: `integration_type=0`, scope `applications.commands` and `bot`, permission value `137439332416`. `client_id` is the application id. The application needs the Message Content and Server Members intents. `applications.commands` is part of that scope.

Public status is posted in one existing channel. Roles, night actions, and whispers are DMs. Lobby codes look like `MM-BZ7W`. **Allow DMs from this bot** is a user install (`integration_type=1`, `scope=applications.commands`).

The Bot does not create a channel, role, or voice channel for a game, and it has no purge command and no voice-lock setting. `/create` and `/join` are rate limited. One person cannot hold two seats in a lobby.

Self-hosters set their own application id, token, and intents. The maintainers are not responsible for self-hosted instances.

## 4. Data

The Bot processes the identifiers and saved progress described in the [privacy policy](privacy.md).

## 5. License

Source code is under the MIT License. See [LICENSE](../../LICENSE). That license does not cover Discord’s branding or other third-party names.

## 6. Warranties and liability

The Bot is provided without warranties. To the extent the law allows, the maintainers are not liable for indirect or consequential damages, or for loss of data, from use of the Bot.

## 7. Termination

Access may be suspended for breaking these terms or the Code of Conduct. A server admin may remove the Bot at any time.

## 8. Changes

The date at the top changes when these terms change. Continuing to use the Bot after that means you accept the new terms where the law allows.
