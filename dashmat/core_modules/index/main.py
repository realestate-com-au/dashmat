from dashmat.core_modules.base import Module

class Index(Module):

    @classmethod
    def dependencies(self):
        yield "dashmat.core_modules.bootstrap.main:BootStrap"

