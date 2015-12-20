from python_dashing.core_modules.base import ServerBase

import random

class Server(ServerBase):
	@property
	def routes(self):
		yield "number", self.number

	@property
	def register_checks(self):
		yield "* * * * *", self.make_number

	def number(self, datastore):
		return datastore.retrieve("number")

	def make_number(self, time_since_last_check):
		yield "number", str(int(random.random() * 100))

