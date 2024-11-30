from flask import Flask, render_template
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy
from config import Config  # 从 config.py 导入配置类
from flask_socketio import SocketIO
import logging
from websocket.MyWebsocket import handle_connect, handle_disconnect, handle_ai_first_move, handle_player_move, handle_reset_game, handle_logout
# 从 MyWebsocket 导入处理逻辑

# 创建数据库对象
db = SQLAlchemy()

# 创建 SocketIO 实例，允许异步 WebSocket 通信
socketio = SocketIO()


def create_app():
    app = Flask(__name__, static_folder='frontend/build/static', template_folder='frontend/build')
    CORS(app)  # 启用跨域支持
    app.config.from_object(Config)
    app.config['JWT_SECRET_KEY'] = 'your-secret-key'
    JWTManager(app)

    # 初始化数据库连接
    db.init_app(app)

    from controller.game_controller import game_controller
    from controller.user_controller import user_controller
    app.register_blueprint(game_controller, url_prefix='/game')
    app.register_blueprint(user_controller, url_prefix='/user')

    # 设置日志输出到文件
    logging.basicConfig(filename='app.log', level=logging.DEBUG, format='%(asctime)s %(levelname)s: %(message)s')
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s')
    console_handler.setFormatter(formatter)
    logging.getLogger().addHandler(console_handler)

    @app.route('/')
    def index():
        return render_template('index.html')

    # 初始化 SocketIO
    socketio.init_app(app, cors_allowed_origins="*")
    return app


# 将 MyWebsocket 中的逻辑与 SocketIO 事件关联
socketio.on_event('connect', handle_connect)  # 处理连接事件
socketio.on_event('disconnect', handle_disconnect)  # 处理断开连接事件
socketio.on_event('aiFirstMove', handle_ai_first_move)  # 处理断开连接事件
socketio.on_event('playerMove', handle_player_move)  # 处理断开连接事件
socketio.on_event('resetGame', handle_reset_game)
socketio.on_event('logout', handle_logout)

if __name__ == '__main__':
    app = create_app()
    # 在 5000 端口同时暴露 HTTP 和 WebSocket
    socketio.run(app, host='0.0.0.0', port=5000)
