from python_dashing.importer import import_module
from python_dashing.errors import MissingModule

import pkg_resources
import logging
import redis
import json
import os

log = logging.getLogger("python_dashing.core_modules.base")

class Module(object):
    relative_to = NotImplemented

    def __init__(self, name):
        self.name = name

    @classmethod
    def dependencies(self):
        """
        Return a list of dependency modules to load
        """
        return []

    @classmethod
    def requirements(self):
        """
        Return a list of pip requirements for this module
        """
        return []

    @classmethod
    def register_configuration(self):
        """
        Returns a dictionary of {(priority, name): spec}

        Where priority is a number used to order the specs

        Where name refers to the section in the configuration

        Where spec is an input_algorithms specification for that part of the configuration
        """
        return {}

    @property
    def server_kls(self):
        try:
            return getattr(import_module(".".join([self.relative_to, "server"])), "Server")
        except MissingModule:
            return ServerBase

    @property
    def client_kls(self):
        try:
            return getattr(import_module(".".join([self.relative_to, "client"])), "Client")
        except MissingModule:
            return ClientBase

    @property
    def css(self):
        return []

    @property
    def javascript(self):
        return []

    def make_server(self, redis_host, server_kwargs):
        return self.server_kls(self, redis_host, **server_kwargs)

    def make_client(self, client_kwargs):
        return self.client_kls(self, **client_kwargs)

    def path_for(self, static_resource):
        return os.path.join(pkg_resources.resource_filename(self.relative_to, 'static'), static_resource)

class ClientBase(object):
    def __init__(self, module, **kwargs):
        self.module = module
        self.setup(**kwargs)

    def setup(self, **kwargs):
        pass

    @property
    def template_name(self):
        return 'module.jade'

    @property
    def template_context(self):
        return {}

    @property
    def css(self):
        return self.module.css

    @property
    def javascript(self):
        return self.module.javascript

class ServerBase(object):
    def __init__(self, module, redis_host, **kwargs):
        self.module = module
        self.redis_host = redis_host

        self.setup(**kwargs)

    @property
    def redis(self):
        if not getattr(self, "_redis", None):
            self._redis = redis.Redis(self.redis_host)
        return self._redis

    def setup(self, **kwargs):
        pass

    @property
    def routes(self):
        return []

    @property
    def update_registration(self):
        return []

    @property
    def register_checks(self):
        return []

    def add_to_list(self, key, **kwargs):
        key = "python_dashing:{0}:{1}".format(self.module.name, key)
        self.redis.rpush(key, json.dumps(kwargs))
        length = self.redis.llen(key)
        start = 0 if length - 20 < 0 else length - 20
        self.redis.ltrim(key, start, length)
        log.info("Recorded data for {0}".format(key))
        log.debug(kwargs)

    def get_list(self, key):
        key = "python_dashing:{0}:{1}".format(self.module.name, key)
        return [json.loads(r) for r in self.redis.lrange(key, 0, self.redis.llen(key))]

    def set_string(self, key, val):
        self.redis.set(key, val)

    def get_string(self, key):
        return self.redis.get(key)

    def set_data(self, key, val):
        self.redis.hmset(key, val)

    def get_data(self, key):
        return self.redis.hgetall(key)

    def delete(self, key):
        return self.redis.delete(key)

