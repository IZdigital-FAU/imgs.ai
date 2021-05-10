import os

class Environment:
    DEBUG=False
    TESTING=False

    SECRET_KEY = os.urandom(32)    
    
    SESSION_COOKIE_SECURE=True
    SESSION_COOKIE_SAMESITE='Strict'

    PROJECT_DATA_DIR = os.path.abspath('./data')
    VECTORS_DIR = os.path.abspath('./vectors')

    MONGODB_DB = None
    MONGODB_HOST = None
    MONGODB_PORT = None
    MONGODB_USERNAME = None
    MONGODB_PASSWORD = None

    REDIS_HOST = None
    REDIS_PORT = None

    ANNOY_DISTANCE_METRICS = ["angular", "euclidean", "manhattan", "hamming", "dot"] # https://github.com/spotify/annoy#full-python-api
    MODES = ['ranking', 'centroid']

    def load_ini():
        with open('config.ini') as config:
            for line in config:
                if line == '\n': continue
                key, val = line.split('=')
                val = val.strip().strip('\r')

                if key.endswith('PORT'): val = int(val)

                setattr(Environment, key, val)