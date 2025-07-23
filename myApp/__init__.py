from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_mail import Mail
from myApp.config import Config

db = SQLAlchemy()
migrate = Migrate()
bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_view = 'users.login'
mail = Mail()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)

    with app.app_context():
        from myApp.users.routes import users_bp
        from myApp.requests.routes import requests_bp
        from myApp.admin.routes import admin_bp
        from myApp.main.routes import main_bp

        app.register_blueprint(users_bp)
        app.register_blueprint(requests_bp)
        app.register_blueprint(admin_bp)
        app.register_blueprint(main_bp)

    return app
