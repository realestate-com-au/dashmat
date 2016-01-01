from python_dashing.importer import import_module
from python_dashing.errors import MissingModule

import logging

log = logging.getLogger("python_dashing.core_modules.base")

class Module(object):

    def __init__(self, name, import_path):
        self.name = name
        self.import_path = import_path

    def make_server(self, server_kwargs):
        if callable(server_kwargs):
            server_kwargs = server_kwargs()
        return self.server_kls(self, **server_kwargs)

    @property
    def server_kls(self):
        try:
            return getattr(import_module(".".join([self.relative_to, "server"])), "Server")
        except MissingModule:
            return ServerBase

    @property
    def relative_to(self):
        return '.'.join(self.import_path.split(":")[0].split(".")[:-1])

    @classmethod
    def css(self):
        """
        Return a list of css to include in the request
        """
        return []

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

    @classmethod
    def npm_deps(self):
        """
        Returns a dictionary for package.json
        """
        return {}

class ServerBase(object):
    def __init__(self, module, **kwargs):
        self.module = module
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
    def register_checks(self):
        return []

