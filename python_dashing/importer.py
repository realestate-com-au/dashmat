from python_dashing.errors import BadImport, MissingModule

import imp
import sys

def import_module(head, rest=None, directory=None, first=True, original=None):
	if original is None:
		original = head

	if rest is None:
		parts = list(reversed(head.split('.')))
		head = parts[0]
		rest = parts[1:]

	if rest:
		directory = import_module(rest[0], rest=rest[1:], directory=directory, first=False, original=original)
	else:
		directory = sys.path

	try:
		args = imp.find_module(head, directory)
	except ImportError as error:
		raise MissingModule(directory=directory, importing=head, error=error)

	try:
		module = imp.load_module(head, *args)
	except SyntaxError as error:
		raise BadImport(importing='.'.join([head] + rest), error=error)

	if first:
		return module
	else:
		if not hasattr(module, '__path__'):
			raise BadImport("Reached a leaf module", module=module, looking_for=original)

		return module.__path__
