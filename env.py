import os


class Environment:
    FLASK_ENV='production'
    TESTING=False
    SECRET_KEY = os.urandom(32)
    APPLICATION_ROOT='/'

    PROJECT_DATA_DIR = os.path.abspath('./data')
    VECTORS_DIR = os.path.abspath('./vectors')

    MONGODB_DB = None
    MONGODB_HOST = None
    MONGODB_PORT = 27017
    MONGODB_USERNAME = None
    MONGODB_PASSWORD = None

    REDIS_HOST = None
    REDIS_PORT = 6379

    USE_X_SENDFILE=False
    SERVER_NAME=None

    MAX_CONTENT_LENGTH=None   # dont read more than this many bytes from incoming request
    # SEND_FILE_MAX_AGE_DEFAULT=120
    PREFERRED_URL_SCHEME='http'

    JSON_AS_ASCII=True
    JSON_SORT_KEYS=True
    JSONIFY_PRETTYPRINT_REGULAR=False
    JSONIFY_MIMETYPE='application/json'
    TEMPLATES_AUTO_RELOAD=None
    EXPLAIN_TEMPLATE_LOADING=False

    MAX_COOKIE_SIZE=4093
    SESSION_COOKIE_NAME='session'
    SESSION_COOKIE_DOMAIN=None
    SESSION_COOKIE_PATH=None
    SESSION_COOKIE_HTTPONLY=True
    SESSION_COOKIE_SECURE=True
    SESSION_COOKIE_SAMESITE='Strict'
    # PERMANENT_SESSION_LIFETIME=None
    SESSION_REFRESH_EACH_REQUEST=True
    REMEMBER_COOKIE_SECURE=False

    ANNOY_DISTANCE_METRICS = ["angular", "euclidean", "manhattan", "hamming", "dot"] # https://github.com/spotify/annoy#full-python-api
    MODES = ['ranking', 'centroid']

    def load_ini():
        with open('./app/config.ini') as config:
            for line in config:
                if line == '\n': continue
                key, val = line.split('=')

                setattr(Environment, key, val.strip().strip('\r'))