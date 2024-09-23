from app import db  # 保持不变，因为 `db` 在 `app.py` 中已全局定义
from sqlalchemy import text

class GameDAO:
    def __init__(self):
        self.game_table = db.Table('games', db.metadata)

    def save_game_state(self, board_state, current_turn):
        """
        Save the current game state (board and turn).
        """
        query = text("INSERT INTO games (board_state, current_turn) VALUES (:board_state, :current_turn)")
        db.session.execute(query, {'board_state': board_state, 'current_turn': current_turn})
        db.session.commit()

    def load_game_state(self):
        """
        Load the last saved game state (board and turn).
        """
        query = text("SELECT board_state, current_turn FROM games ORDER BY id DESC LIMIT 1")
        result = db.session.execute(query).fetchone()
        if result:
            return result[0], result[1]  # board_state, current_turn
        return None, None

    def reset_game(self):
        """
        Reset the game by clearing the game state.
        """
        query = text("DELETE FROM games")
        db.session.execute(query)
        db.session.commit()

    def save_game_result(self, winner):
        """
        Save the result of the game.
        """
        query = text("INSERT INTO game_results (winner) VALUES (:winner)")
        db.session.execute(query, {'winner': winner})
        db.session.commit()

    def get_game_history(self):
        """
        Retrieve the history of past games.
        """
        query = text("SELECT * FROM game_results ORDER BY id DESC")
        results = db.session.execute(query).fetchall()
        return results
