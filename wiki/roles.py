"""Per-role wiki entries: ability, win condition, and availability."""

ROLE_WIKI = {
    "murderer": {
        "emoji": ":dagger:",
        "fancyName": "Murderer",
        "always": True,
        "ability": "Kill one player every night.",
        "win": "Kill everyone.",
        "availability": "Always in every game.",
    },
    "doctor": {
        "emoji": ":pill:",
        "fancyName": "Doctor",
        "always": True,
        "ability": (
            "When the murderer kills someone, the doctor is notified and "
            "can choose to heal them (only once per game)."
        ),
        "win": "Kill the murderer.",
        "availability": "Always in every game.",
    },
    "detective": {
        "emoji": ":spy:",
        "fancyName": "Detective",
        "ability": (
            "Inspect a player's role at night; the result is revealed the "
            "next night."
        ),
        "win": "Kill the murderer.",
        "availability": "Minimum players: 4",
    },
    "banker": {
        "emoji": ":person_in_tuxedo:",
        "fancyName": "Banker",
        "ability": "Starts with 3 gold and receives +1 extra gold per day.",
        "win": "Kill the murderer.",
        "availability": "Minimum players: 4",
    },
    "thief": {
        "emoji": ":unlock:",
        "fancyName": "Thief",
        "ability": (
            "Each night, attempt to steal gold from someone. 50% chance "
            "to steal half of that player's gold."
        ),
        "win": "Kill the murderer.",
        "availability": "Minimum players: 4",
    },
    "jailer": {
        "emoji": ":cop:",
        "fancyName": "Jailer",
        "ability": (
            "Choose someone to jail each night; they will be jailed the "
            "next night. Jailed players cannot use the shop or their "
            "role's ability."
        ),
        "win": "Kill the murderer.",
        "availability": "Minimum players: 5",
    },
    "broadcaster": {
        "emoji": ":radio:",
        "fancyName": "Broadcaster",
        "ability": (
            "Send a message to players of a specific role at night "
            "without knowing who they are, or broadcast to everyone at "
            "night. Messages are received the following night."
        ),
        "win": "Kill the murderer.",
        "availability": "Minimum players: 6",
    },
    "fool": {
        "emoji": ":clown:",
        "fancyName": "Fool",
        "ability": (
            "If the fool is voted for execution during the day, they "
            "win; if killed in any other way, they lose."
        ),
        "win": "Get voted for execution.",
        "availability": "Minimum players: 6",
    },
    "hunter": {
        "emoji": ":hunter:",
        "fancyName": "Hunter",
        "ability": (
            "Shoot someone at night. If the target is not the murderer "
            "or the werewolf, the hunter dies and the target survives."
        ),
        "win": "Kill the murderer.",
        "availability": "Minimum players: 6",
    },
    "werewolf": {
        "emoji": ":wolf:",
        "fancyName": "Werewolf",
        "ability": (
            "Works together with the murderer. On nights with a full "
            "moon, the werewolf must kill someone."
        ),
        "win": "Kill everyone except the murderer.",
        "availability": "Minimum players: 7",
    },
    "cupid": {
        "emoji": ":bow_and_arrow:",
        "fancyName": "Cupid",
        "ability": (
            "Select two players (including self if desired) to make "
            "them fall in love. Lovers share fate: if one dies, the "
            "other dies too. If one lover is the murderer, their goal "
            "changes to kill everyone except their lover."
        ),
        "win": "Kill the murderer (unless aligned with murderer as a lover).",
        "availability": "Minimum players: 8",
    },
    "mayor": {
        "emoji": ":crown:",
        "fancyName": "Mayor",
        "ability": "Your daytime vote counts as two votes.",
        "win": "Kill the murderer.",
        "availability": "Minimum players: 4",
    },
    "bodyguard": {
        "emoji": ":shield:",
        "fancyName": "Bodyguard",
        "ability": (
            "Protect one player each night. If that player is attacked, "
            "the bodyguard dies instead."
        ),
        "win": "Kill the murderer.",
        "availability": "Minimum players: 5",
    },
    "medium": {
        "emoji": ":crystal_ball:",
        "fancyName": "Medium",
        "ability": (
            "Once per game, receive a DM clue revealing the role of one "
            "dead player."
        ),
        "win": "Kill the murderer.",
        "availability": "Minimum players: 6",
    },
}
