from python_dashing.importer import import_module
from python_dashing.errors import MissingModule

import pkg_resources
import logging
import os

log = logging.getLogger("python_dashing.core_modules.base")

class Module(object):
    relative_to = NotImplemented

    def __init__(self, name):
        self.name = name
        self.data = None

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

    def make_server(self, server_kwargs):
        return self.server_kls(self, **server_kwargs)

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
    def __init__(self, module, **kwargs):
        self.module = module
        self.data = {}

        self.setup(**kwargs)

    def setup(self, **kwargs):
        pass

    @property
    def register_checks(self):
        return []

    def run_check(self, func, *args, **kwargs):
        for key, value in func(*args, **kwargs):
            self.data[key] = value

