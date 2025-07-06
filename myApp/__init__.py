from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_mail import Mail

app = Flask(__name__)
app.config['SECRET_KEY'] = '4v36non75hbv8oqu3f7c'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['MAIL_SERVER'] = 'smtp.googlemail.com'  # Replace with your mail server
app.config['MAIL_PORT'] = 587  # Replace
app.config['MAIL_USE_TLS'] = True  # Use TLS
app.config['MAIL_USERNAME'] = 'temirlan.yergazy@gmail.com'
app.config['MAIL_PASSWORD'] = 'fdru qyes kemd ojoj' # App password from google
db = SQLAlchemy(app)
migrate = Migrate(app, db)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
mail = Mail(app)

from myApp import routes