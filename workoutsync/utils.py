import json
import redis


class Cache:
    REDIS_KEY_PREFIX = 'workout:'

    def __init__(self, redis_connect: redis.Redis):
        self.redis = redis_connect
        self.timeout = 60*60*24*30  # 30 days
        pass

    def keys(self):
        return map(lambda x: x[len(self.REDIS_KEY_PREFIX):].decode("utf-8"), self.redis.keys(f'{self.REDIS_KEY_PREFIX}*'))

    def store(self):
        pass

    def get(self, key):
        data = self.redis.get(f'{self.REDIS_KEY_PREFIX}{key}')
        return json.loads(data) if data is not None else None

    def set(self, key, value):
        self.redis.set(f'{self.REDIS_KEY_PREFIX}{key}', json.dumps(value), ex=self.timeout)
