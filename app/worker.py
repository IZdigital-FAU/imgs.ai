import redis
from rq import Worker, Queue, Connection

from env import Environment as env


listen = ['imgsai']

conn = redis.from_url(env.REDIS_URL)

if __name__ == '__main__':
    with Connection(conn):
        worker = Worker(list(map(Queue, listen)))
        worker.work()