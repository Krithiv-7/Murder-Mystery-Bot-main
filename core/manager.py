"""In-memory registry for lobbies and players.

The dicts in ``core.game_state`` stay the storage so existing callers keep
working. New code should go through ``game_manager`` instead of indexing
those lists.
"""

from __future__ import annotations

from core.game_state import allPlayers, availableGames, currentGames
from core.ids import generate_code, normalize_code


class GameManager:
    """Guild-scoped lookup for running games and the players in them."""

    def __init__(self) -> None:
        self.current_games = currentGames
        self.available_games = availableGames
        self.all_players = allPlayers
        self.accepting_new_games = True
        self._issued: set[str] = set()

    def allocate_code(self) -> str:
        used = set(self._issued)
        for games in self.current_games.values():
            for game in games:
                code = getattr(game, "code", None)
                if code:
                    used.add(code)
        code = generate_code(used)
        self._issued.add(code)
        return code

    def register(self, game) -> None:
        guild_id = game.guild.id
        self.current_games.setdefault(guild_id, [])
        if game not in self.current_games[guild_id]:
            self.current_games[guild_id].append(game)
        self.available_games.setdefault(guild_id, [])
        if game not in self.available_games[guild_id]:
            self.available_games[guild_id].append(game)
        code = getattr(game, "code", None)
        if code:
            self._issued.add(code)

    def mark_unavailable(self, game) -> None:
        games = self.available_games.get(game.guild.id, [])
        if game in games:
            games.remove(game)

    def get_games(self, guild_id):
        return list(self.current_games.get(guild_id, []))

    def get_game(self, guild_id, token):
        if token is None:
            return None
        wanted = normalize_code(str(token))
        for game in self.current_games.get(guild_id, []):
            if getattr(game, "code", None) == wanted:
                return game
        return None

    def remove_game(self, game) -> None:
        guild_id = game.guild.id
        current = self.current_games.get(guild_id, [])
        if game in current:
            current.remove(game)
        available = self.available_games.get(guild_id, [])
        if game in available:
            available.remove(game)

    def get_player(self, guild_id, member_id):
        for player in self.all_players.get(guild_id, []):
            member = getattr(player, "member", None)
            if member is not None and getattr(member, "id", None) == member_id:
                return player
        return None

    def get_player_game(self, guild_id, member_id):
        player = self.get_player(guild_id, member_id)
        if player is not None and getattr(player, "inGame", False):
            return getattr(player, "game", None)
        return None

    async def create_game(self, guild, debug=False, client=None, channel=None):
        if not self.accepting_new_games:
            raise RuntimeError("Bot is shutting down and is not accepting new games.")
        from core.game import Game

        game = Game(guild, debug)
        await game.createGame(client=client, channel=channel)
        return game

    def request_shutdown(self) -> None:
        """Stop new lobbies and ask in-flight phase loops to exit."""
        self.accepting_new_games = False
        for games in list(self.current_games.values()):
            for game in list(games):
                game._cancel_phase = True
                task = getattr(game, "_phase_task", None)
                if task is not None and not task.done():
                    task.cancel()


game_manager = GameManager()
