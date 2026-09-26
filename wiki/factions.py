"""Faction/team win conditions, for the higher-level !wiki overview page."""

FACTION_WIKI = {
    "villagers": {
        "emoji": ":busts_in_silhouette:",
        "name": "Villagers",
        "win": (
            "Kill the murderer (and the werewolf, if one is in the "
            "game) before they kill everyone else."
        ),
    },
    "murderer": {
        "emoji": ":dagger:",
        "name": "Murderer (+ Werewolf, if present)",
        "win": (
            "Kill every villager. If a werewolf is also in the game, "
            "they team up and share this win condition."
        ),
    },
    "fool": {
        "emoji": ":clown:",
        "name": "Fool",
        "win": "Get voted for execution during the day.",
    },
    "lovers": {
        "emoji": ":couple_with_heart:",
        "name": "Lovers (Cupid ability)",
        "win": (
            "Survive together. If one lover dies, the other dies too. "
            "A lover paired with the murderer wins alongside them "
            "instead of the villagers."
        ),
    },
}
