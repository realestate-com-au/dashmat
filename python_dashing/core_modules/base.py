import logging

log = logging.getLogger("python_dashing.core_modules.base")

class Module(object):

    def __init__(self, name):
        self.name = name
        self.data = {}

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
    def register_checks(self):
        return []

    def run_check(self, func, *args, **kwargs):
        for key, value in func(*args, **kwargs):
            self.data[key] = value

class Widget(object):
    def get_pack(self):
        raise NotImplementedError

    def register_configuration(self):
        return {}
