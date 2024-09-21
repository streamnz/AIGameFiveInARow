from dao.game_dao import GameDAO
from source.AI import GomokuAI


class GameService:
    def __init__(self):
        self.game_dao = GameDAO()
        self.gomoku_ai = GomokuAI()

    def player_move(self, x, y):
        """
        Handle player's move.
        """
        if not self.gomoku_game.is_valid_move(x, y):
            return {"status": "error", "message": "Invalid move."}

        self.gomoku_game.make_move(x, y, "player")
        self.game_dao.save_game_state(self.gomoku_game.get_board(), self.gomoku_game.get_turn())

        if self.gomoku_game.check_winner():
            return {"status": "win", "winner": "player"}

        return {"status": "success", "move": (x, y)}

    def ai_move(self):
        """
        Handle AI's move.
        """
        ai_move = self.gomoku_ai.get_best_move(self.gomoku_game.get_board())
        self.gomoku_game.make_move(ai_move[0], ai_move[1], "ai")
        self.game_dao.save_game_state(self.gomoku_game.get_board(), self.gomoku_game.get_turn())

        if self.gomoku_game.check_winner():
            return {"status": "win", "winner": "AI", "move": ai_move}

        return {"status": "success", "move": ai_move}

    def reset_game(self):
        """
        Reset the game.
        """
        self.gomoku_game.reset_board()
        self.game_dao.reset_game()
