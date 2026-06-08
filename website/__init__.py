from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import os

db = SQLAlchemy()
DB_NAME = "database.db"
UPLOAD_FOLDER = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'static/uploads')

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'do_an_web_chia_se_tai_lieu'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)

    db.init_app(app)

    from .routes import routes
    app.register_blueprint(routes, url_prefix='/')

    from .models import User
    with app.app_context():
        db.create_all()

    login_manager = LoginManager()
    login_manager.login_view = 'routes.login'
    login_manager.login_message = 'Vui lòng đăng nhập để sử dụng tính năng này.'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    return app