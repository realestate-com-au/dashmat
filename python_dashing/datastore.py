import logging
import json
import os

log = logging.getLogger("python_dashing.datastore")

class RedisDataStore(object):
    def __init__(self, redis, prefix=""):
        self.prefix = prefix
        self.redis_host = redis_host

    def prefixed(self, prefix):
        return RedisDataStore(self.redis, prefix=prefix)

    def create(self, key, value):
        self.redis.set("{0}-{1}".format(self.prefix, key), json.dumps({"value": value}))

    def retrieve(self, key):
        return json.loads(self.redis.get("{0}-{1}".format(self.prefix, key)).decode('utf-8'))["value"]

class JsonDataStore(object):
    def __init__(self, location, prefix=""):
        self.prefix = prefix
        self.location = location

    @property
    def data(self):
        if not os.path.exists(self.location):
            return {}

        last_read = getattr(self, "_data_last_read", None)
        if last_read is None or os.stat(self.location).st_mtime > last_read:
            try:
                with open(self.location) as fle:
                    self._data = json.loads(fle.read())
                self._data_last_read = os.stat(self.location).st_mtime
            except (OSError, TypeError, ValueError) as error:
                log.error("Failed to read the data")
                log.exception(error)
                self._data = {}

        return self._data

    def prefixed(self, prefix):
        ret = JsonDataStore(self.location, prefix=prefix)
        ret._data_last_read = getattr(self, "_data_last_read", None)
        ret._data = getattr(self, "_data", None)
        return ret

    def create(self, key, value):
        data = self.data
        data[key] = json.dumps({"value": value})
        with open(self.location, 'w') as fle:
            json.dump(data, fle)

    def retrieve(self, key):
        data = self.data
        if key in data:
            return json.loads(self.data[key])["value"]

