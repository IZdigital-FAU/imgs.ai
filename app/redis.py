import redis
from env import Environment as env


redis_conn = redis.Redis(
    host=env.REDIS_HOST,
    port=env.REDIS_PORT
    # password='password'
)