import os


class Config(object):
    SECRET_KEY = os.environ.get("SECRET_KEY") or "you-will-never-guess"
    SQLALCHEMY_DATABASE_URI = (
        "sqlite:////home/fabian/Desktop/dev/ML/imgs.ai/users.db"  # Absolute
    )
    # https://stackoverflow.com/questions/33738467/how-do-i-know-if-i-can-disable-sqlalchemy-track-modifications
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MODELS_PATH = "/home/fabian/Desktop/dev/ML/imgs.ai/models"  # Absolute
    MODELS = [f.name for f in os.scandir(MODELS_PATH) if f.is_dir()]
    NS = ["10", "20", "30", "40", "50", "60", "70", "80", "90", "100"]
    DEFAULT_N = "30"
    SIZES = ["32", "64", "96", "128", "160", "192", "224"]
    DEFAULT_SIZE = "128"
    MODES = ["ranking", "centroid"]
    DEFAULT_MODE = "ranking"
    UPLOAD_CACHE = "uploads"
    UPLOAD_FILE = "uploads.hdf5"
