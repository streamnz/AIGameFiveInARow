from app import db  # 保持不变，因为 `db` 在 `app.py` 中已全局定义

class GameDAO:
    def __init__(self):
        self.game_table = db.Table('game')

    def save_game_state(self, board_state, current_turn):
        """
        Save the current game state (board and turn).
        """
        query = "INSERT INTO game (board_state, current_turn) VALUES (?, ?)"
        db.session.execute(query, (board_state, current_turn))
        db.session.commit()

    def load_game_state(self):
        """
        Load the last saved game state (board and turn).
        """
        query = "SELECT board_state, current_turn FROM game ORDER BY id DESC LIMIT 1"
        result = db.session.execute(query).fetchone()
        if result:
            return result[0], result[1]  # board_state, current_turn
        return None, None

    def reset_game(self):
        """
        Reset the game by clearing the game state.
        """
        query = "DELETE FROM game"
        db.session.execute(query)
        db.session.commit()

    def save_game_result(self, winner):
        """
        Save the result of the game.
        """
        query = "INSERT INTO game_results (winner) VALUES (?)"
        db.session.execute(query, (winner,))
        db.session.commit()

    def get_game_history(self):
        """
        Retrieve the history of past games.
        """
        query = "SELECT * FROM game_results ORDER BY id DESC"
        results = db.session.execute(query).fetchall()
        return results
