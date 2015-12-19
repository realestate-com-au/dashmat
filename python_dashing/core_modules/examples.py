from python_dashing.core_modules.base import Module as ModuleBase
import random

class Random(ModuleBase):
    @property
    def register_checks(self):
        yield "*/5 * * * *",  self.make_stats

    def make_stats(self, time):
        yield 'int', random.randint(1, 1000)
        yield 'float', random.random()
        random_series = [{'x': i, 'y': random.randint(1, 100)} for i in range(1, 10)]
        yield 'graph', {'series': random_series}
