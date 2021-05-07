from rq import Queue
from .redis import redis_conn

q = Queue(connection=redis_conn)