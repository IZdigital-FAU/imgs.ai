import redis
from env import Environment as env

env.load_ini()

redis_conn = redis.Redis(
    host=env.REDIS_HOST,
    port=env.REDIS_PORT
    # password='password'
)