from flask import Flask, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config  # 从 config.py 导入配置类
# 注册蓝图


# 创建数据库对象
db = SQLAlchemy()

def create_app():
    # 创建Flask应用
    app = Flask(__name__, static_folder='frontend/build/static', template_folder='frontend/build')


    # 从Config类加载配置
    app.config.from_object(Config)

    # 初始化数据库连接
    db.init_app(app)

    # 数据库迁移工具
    migrate = Migrate(app, db)

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
