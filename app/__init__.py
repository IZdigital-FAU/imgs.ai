import logging
import sys
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_cors import CORS
from flask_bootstrap import Bootstrap
from config import Config
from model import EmbeddingModel
from datetime import date


# Start app
app = Flask(__name__)
app.config.from_object(Config)

# Plugins
Bootstrap(app)  # Bootstrap
CORS(app)  # CORS
login_manager = LoginManager(app)  # Login
login_manager.login_view = "login"

# Logging
logging.captureWarnings(True)
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
file_handler = logging.FileHandler(f"logs/{date.today()}.log")
console_handler = logging.StreamHandler(sys.stdout)
formatter = logging.Formatter("%(asctime)s : %(levelname)s : %(name)s : %(message)s")
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)
log.addHandler(file_handler)
log.addHandler(console_handler)

# Database
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Models
models = {}
for model in Config.MODELS:
    models[model] = EmbeddingModel()
    models[model].load(os.path.join(Config.MODELS_PATH, model))

from app import user, routes
