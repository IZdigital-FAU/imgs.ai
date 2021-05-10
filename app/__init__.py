from flask import Flask, Blueprint, request
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect

from env import Environment as env

from .database import db

from .routes.auth import auth
from .routes.api import api
from .routes.views import view

from .session import CustomSessionInterface
from .models.user import User

from .scripts.project_loader import load_project


# Start app
app = Flask(__name__)
# app.session_interface = CustomSessionInterface()

env.load_ini()
print(env.__dict__)
app.config.from_object(env)

db.init_app(app)

csrf = CSRFProtect()
csrf.init_app(app)

app.register_blueprint(auth, url_prefix='/auth')
app.register_blueprint(api, url_prefix='/api')
app.register_blueprint(view)

# Auth
login_manager = LoginManager()  # Login
login_manager.login_view = 'auth.login'
login_manager.login_message_category = "warning"

login_manager.session_protection = None # https://flask-login.readthedocs.io/en/latest/#session-protection

login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.objects(pk=user_id).first()

@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-cache, no-store'
    return response


load_project()