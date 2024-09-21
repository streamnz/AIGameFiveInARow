from flask import Blueprint, request, jsonify
from service.game_service import GameService

# Blueprint for game controller
game_controller = Blueprint('game_controller', __name__)
game_service = GameService()


# Route to start a new game
@game_controller.route('/start', methods=['POST'])
def start_game():
    game_service.reset_game()
    return jsonify({"status": "success", "message": "Game has been reset."}), 200


# Route to handle player move
@game_controller.route('/move', methods=['POST'])
def player_move():
    data = request.get_json()
    x = data.get('x')
    y = data.get('y')

    # Validate coordinates
    if x is None or y is None:
        return jsonify({"status": "error", "message": "Invalid move. Coordinates must be provided."}), 400

    # Process player's move
    move_result = game_service.player_move(x, y)
    if move_result["status"] == "error":
        return jsonify(move_result), 400

    # Check if the player won after their move
    if move_result["status"] == "win":
        return jsonify({
            "status": "win",
            "winner": "player",
            "player_move": move_result["move"]
        }), 200

    # AI makes its move
    ai_move_result = game_service.ai_move()

    # Check if AI won
    if ai_move_result["status"] == "win":
        return jsonify({
            "status": "win",
            "winner": "AI",
            "player_move": move_result["move"],
            "ai_move": ai_move_result["move"]
        }), 200

    # Both player and AI moves succeeded
    return jsonify({
        "status": "success",
        "player_move": move_result["move"],
        "ai_move": ai_move_result["move"]
    }), 200


# Route to reset the game
@game_controller.route('/reset', methods=['POST'])
def reset_game():
    game_service.reset_game()
    return jsonify({"status": "success", "message": "Game has been reset."}), 200
