from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy()


def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///gomoku.db'
    app.config['SECRET_KEY'] = 'your_secret_key'

    db.init_app(app)
    migrate = Migrate(app, db)

    from controller.game_controller import game_controller
    from controller.user_controller import user_controller

    # Register controllers
    app.register_blueprint(game_controller, url_prefix='/game')
    app.register_blueprint(user_controller, url_prefix='/user')

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
