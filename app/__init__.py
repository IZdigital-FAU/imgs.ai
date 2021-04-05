import logging
import sys
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
# from flask_cors import CORS
from flask_bootstrap import Bootstrap
from env import Environment as environment
from .model import EmbeddingModel
from datetime import date

from pymongo import MongoClient

# Start app
app = Flask(__name__)
app.config.from_object(environment)

# Plugins
Bootstrap(app)  # Bootstrap
# CORS(app)  # CORS
login_manager = LoginManager(app)  # Login
login_manager.login_view = "login"
login_manager.login_message_category = "warning"

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

client = MongoClient(environment.MONGODB)
mongodb = client["imgsai"]

print('MONGODB', mongodb)

# Models
models = {}
for model in environment.MODELS:
    models[model] = EmbeddingModel()
    MODEL_PATH = os.path.join(environment.MODELS_PATH, model)
    if os.path.isfile(os.path.join(MODEL_PATH, 'config.json')):
        models[model].load(MODEL_PATH)

from app import user, routes
