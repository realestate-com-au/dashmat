from python_dashing.core_modules.base import Module

class Index(Module):

    @classmethod
    def dependencies(self):
		yield "python_dashing.core_modules.bootstrap.main:BootStrap"

