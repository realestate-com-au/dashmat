from importlib import import_module
import importlib

import logging
import imp
import six

log = logging.getLogger("dashmat.core_modules.base")

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
        if importlib.util.find_spec(".".join([self.relative_to, "server"])):
            module = import_module("{0}.server".format(self.relative_to))
            if hasattr(module, "Server"):
                return module.Server
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

class Route(object):
    def __init__(self, retrieve=None, prepend=None):
        self.prepend = prepend
        self.retrieve = retrieve
        self.dashmat_route = self

    def __call__(self, func):
        self.retrieve = func
        func.dashmat_route = self
        return func

    def data_retriever(self, datastore):
        if isinstance(self.retrieve, six.string_types):
            data = datastore.retrieve(self.retrieve)
        elif callable(self.retrieve):
            data = self.retrieve(self.instance, datastore)
        else:
            data = self.retrieve

        if self.prepend:
            result = {}
            parts = reversed(self.prepend.split("."))[:-1]
            while parts:
                result = {parts.pop(0): result}
            return {self.prepend.split('.')[-1]: data}
        else:
            return data

    def route_tuple(self, instance, name):
        self.instance = instance
        return name, self.data_retriever

class Checker(object):
    def __init__(self, func, every):
        self.func = func
        self.every = every
        self.dashmat_check = self

    def check_tuple(self, instance, name):
        return self.every, lambda *args, **kwargs: self.func(instance, *args, **kwargs)

class ServerBase(object):
    Route = Route

    def __init__(self, module, **kwargs):
        self.module = module
        self.setup(**kwargs)

    def setup(self, **kwargs):
        pass

    @classmethod
    def check_every(kls, every):
        """Decorator for registering a check to run every `every` (cronspec)"""
        def wrapper(func):
            func.dashmat_check = Checker(func, every)
            return func
        return wrapper

    @property
    def routes(self):
        for attr in dir(self):
            if not attr.startswith("_") and attr not in dir(ServerBase):
                val = getattr(self, attr)
                if getattr(val, "dashmat_route", False) and hasattr(val.dashmat_route.__class__, 'route_tuple'):
                    yield val.dashmat_route.route_tuple(self, attr)

    @property
    def register_checks(self):
        for attr in dir(self):
            if not attr.startswith("_") and attr not in dir(ServerBase):
                val = getattr(self, attr)
                if getattr(val, "dashmat_check", False) and hasattr(val.dashmat_check.__class__, "check_tuple"):
                    yield val.dashmat_check.check_tuple(self, attr)

