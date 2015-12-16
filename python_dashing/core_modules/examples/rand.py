from python_dashing.core_modules.base import Module as ModuleBase
import random


class Module(ModuleBase):
    @property
    def register_checks(self):
        yield "*/5 * * * *",  self.make_stats

    def make_stats(self, time):
        yield 'value', random.randint(1, 1000)
