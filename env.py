import os
import pwd

username = pwd.getpwuid(os.getuid()).pw_name

class Environment(object):
    SECRET_KEY = os.environ.get("SECRET_KEY") or os.urandom(64)
    SQLALCHEMY_DATABASE_URI = (
        f"sqlite:////home/{username}/imgs.ai/database/users.db"  # Absolute
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOADS_PATH = f"/home/{username}/imgs.ai/uploads"  # Absolute
    MODELS_PATH = f"/home/{username}/projects"  # Absolute
    MODELS = [f.name for f in os.scandir(MODELS_PATH) if f.is_dir()]
    NS = ["10", "20", "30", "40", "50", "60", "70", "80", "90", "100"]
    DEFAULT_N = "30"
    SIZES = ["32", "64", "96", "128", "160", "192", "224"]
    DEFAULT_SIZE = "128"
    MODES = ["ranking", "centroid"]
    DEFAULT_MODE = "ranking"
    SESSION_COOKIE_SECURE = True # Activate in production
    REMEMBER_COOKIE_SECURE = True # Activate in production