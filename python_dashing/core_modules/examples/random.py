from python_dashing.core_modules.base import ServerBase
from python_dashing.core_modules.base import Module as ModuleBase


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
        data = 444
        self.data = data
        #self.set_string('data', json.dumps(data))