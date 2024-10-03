import datetime

from flask import Flask, redirect, url_for
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy
from config import Config  # 从 config.py 导入配置类
import logging

# 注册蓝图


# 创建数据库对象
db = SQLAlchemy()


def create_app():
    # 创建Flask应用
    app = Flask(__name__, static_folder='frontend/build/static', template_folder='frontend/build')
    CORS(app)
    # 从Config类加载配置
    app.config.from_object(Config)

    app.config['JWT_SECRET_KEY'] = 'your-secret-key'  # 替换成你自己的密钥
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = datetime.timedelta(hours=1)  # 令牌过期时间
    JWTManager(app)

    # 设置日志配置
    log_level = app.config['LOG_LEVEL']
    log_format = app.config['LOG_FORMAT']

    logging.basicConfig(
        level=log_level,
        format=log_format,
        handlers=[
            logging.FileHandler("app.log"),  # 输出日志到文件
            logging.StreamHandler()  # 同时输出到控制台
        ]
    )

    logging.getLogger().info("Logging is set up. Level: %s", log_level)


    # 初始化数据库连接
    db.init_app(app)

    from controller.game_controller import game_controller
    from controller.user_controller import user_controller
    # 将蓝图注册到应用
    app.register_blueprint(game_controller, url_prefix='/game')
    app.register_blueprint(user_controller, url_prefix='/user')

    # 定义首页路由，重定向到游戏控制器的 index 页面
    @app.route('/')
    def index():
        return redirect(url_for('game_controller.index'))

    return app


if __name__ == '__main__':
    # 创建应用并运行
    app = create_app()
    app.run(debug=True)
