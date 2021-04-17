from os.path import join, isfile
from flask import Flask
from flask_login import LoginManager, current_user, login_user, logout_user, login_required
# from flask_cors import CORS
from flask_bootstrap import Bootstrap
from env import Environment as environment
from .project import Project

from .database import db

from .routes.auth import auth
from .routes.api import api
from .routes.views import view

from flask import Blueprint

from .session import CustomSessionInterface

# Start app
app = Flask(__name__)
app.session_interface = CustomSessionInterface()
app.config.from_object(environment)

# Session(app)

db.init_app(app)

app.register_blueprint(auth)
app.register_blueprint(api, url_prefix='/api')
app.register_blueprint(view)

# Auth
login_manager = LoginManager(app)  # Login
login_manager.login_view = "login"
login_manager.login_message_category = "warning"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

login_manager.blueprint_login_views = {
    'auth': '/',
    'api': '/api',
    'view': '/',
}