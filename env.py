import os
import pwd

username = pwd.getpwuid(os.getuid()).pw_name

class Environment(object):
    SECRET_KEY = os.environ.get("SECRET_KEY") or os.urandom(64)
    SQLALCHEMY_DATABASE_URI = (
        f"sqlite:////home/{username}/imgs.ai/database/users.db"  # Absolute
    )

    MONGODB_DB = 'imgsai'
    MONGODB_HOST = '127.0.0.1'
    MONGODB_PORT = 27017
    MONGODB_USERNAME = ''

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOADS_PATH = f"/home/{username}/imgs.ai/uploads"  # Absolute
    PROJECTS_DIR = f"/home/{username}/projects"  # Absolute
    PROJECTS = [f.name for f in os.scandir(PROJECTS_DIR) if f.is_dir()]

    ANNOY_DISTANCE_METRICS = ["angular", "euclidean", "manhattan", "hamming", "dot"] # https://github.com/spotify/annoy#full-python-api

    NS = ["10", "20", "30", "40", "50", "60", "70", "80", "90", "100"]
    DEFAULT_N = "30"
    SIZES = ["32", "64", "96", "128", "160", "192", "224"]
    DEFAULT_SIZE = "128"
    MODES = ["ranking", "centroid"]
    DEFAULT_MODE = "ranking"
    
    SESSION_COOKIE_SECURE = True # Activate in production
    REMEMBER_COOKIE_SECURE = False # Activate in production

    SESSION_COOKIE_SAMESITE = 'Strict'