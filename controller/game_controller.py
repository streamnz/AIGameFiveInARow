from flask import Blueprint, request, jsonify, render_template
from service.game_service import GameService

# Blueprint for game controller
game_controller = Blueprint('game_controller', __name__)
game_service = GameService()


@game_controller.route('/index')
def index():
    # 渲染 index.html 模板
    return render_template('index.html')


# Route to start a new game
@game_controller.route('/start', methods=['POST'])
def start_game():
    game_service.reset_game()
    return jsonify({"status": "success", "message": "Game has been reset."}), 200



# Route to reset the game
@game_controller.route('/reset', methods=['POST'])
def reset_game():
    game_service.reset_game()
    return jsonify({"status": "success", "message": "Game has been reset."}), 200
