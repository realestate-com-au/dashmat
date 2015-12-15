from python_dashing.core_modules.base import ServerBase
from python_dashing.core_modules.base import Module as ModuleBase
import random


class Module(ModuleBase):
    relative_to = 'python_dashing.core_modules.examples'

    @property
    def server_kls(self):
        return Server

class Server(ServerBase):
    @property
    def register_checks(self):
        yield "*/5 * * * *",  self.make_stats

    def make_stats(self, time):
        yield 'value', random.randint(1, 1000)
        #self.set_string('data', json.dumps(data))
