LD_PRELOAD=/usr/local/lib/libjemalloc.so LRU_CACHE_CAPACITY=1 gunicorn --timeout 120 -b 0.0.0.0:$1 --access-logfile access.log app:app