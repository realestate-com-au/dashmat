from dashmat.core_modules.base import ServerBase

import random

class Server(ServerBase):
    number = ServerBase.Route(retrieve="number")

    @ServerBase.check_every("* * * * *")
    def make_number(self, time_since_last_check):
        yield "number", int(random.random() * 100)

