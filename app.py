from flask import Flask, render_template
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_socketio import SocketIO
from config import Config
from models import db
from model.user import User  # 从原有的位置导入 User 模型
import logging
from websocket.MyWebsocket import (
    handle_connect, 
    handle_disconnect, 
    handle_ai_first_move, 
    handle_player_move, 
    handle_reset_game, 
    handle_logout
)

# 创建 SocketIO 实例
socketio = SocketIO()

def create_app():
    """创建Flask应用实例"""
    app = Flask(__name__, static_folder='frontend/build/static', template_folder='frontend/build')
    
    # 启用跨域支持
    CORS(app)
    
    # 加载配置
    app.config.from_object(Config)
    
    # 初始化扩展
    db.init_app(app)
    JWTManager(app)
    socketio.init_app(app, cors_allowed_origins="*")

    # 注册蓝图
    from controller.game_controller import game_controller
    from controller.user_controller import user_controller
    app.register_blueprint(game_controller, url_prefix='/game')
    app.register_blueprint(user_controller, url_prefix='/user')

    # 配置日志
    logging.basicConfig(
        filename='app.log', 
        level=app.config.get('LOG_LEVEL', logging.DEBUG),
        format=app.config.get('LOG_FORMAT', '%(asctime)s %(levelname)s: %(message)s')
    )
    
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s')
    console_handler.setFormatter(formatter)
    logging.getLogger().addHandler(console_handler)

    @app.route('/')
    def index():
        """主页路由"""
        return render_template('index.html')

    return app

# 注册 WebSocket 事件处理器
socketio.on_event('connect', handle_connect)
socketio.on_event('disconnect', handle_disconnect)
socketio.on_event('aiFirstMove', handle_ai_first_move)
socketio.on_event('playerMove', handle_player_move)
socketio.on_event('resetGame', handle_reset_game)
socketio.on_event('logout', handle_logout)

# 让 gunicorn 能 import 到 Flask 实例和 socketio 实例
flask_app = create_app()

if __name__ == '__main__':
    app = flask_app
    # 启动应用
    socketio.run(app, host='0.0.0.0', port=app.config['PORT'], debug=True)
