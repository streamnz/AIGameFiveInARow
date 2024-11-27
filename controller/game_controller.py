from flask import Blueprint, render_template

# Blueprint for game controller
game_controller = Blueprint('game_controller', __name__)


@game_controller.route('/index')
def index():
    # 渲染 index.html 模板
    return render_template('index.html')


