from input_algorithms.spec_base import valid_string_spec
from input_algorithms.errors import BadSpecValue
from input_algorithms.validators import regexed
from importlib import import_module
import six

class module_import_spec(valid_string_spec):
    validators = [regexed("^(?P<module>[a-zA-Z_][a-zA-Z_0-9]*(\.[a-zA-Z_][a-zA-Z_0-9]*)*):(?P<class>[a-zA-Z_][a-zA-Z_0-9]*)$")]

    def setup(self, expected_ancestor_kls):
        self.expected_ancestor_kls = expected_ancestor_kls

    def normalise_filled(self, meta, val):
        if not isinstance(val, six.string_types) and issubclass(val, self.expected_ancestor_kls):
            return val

        # Run string & regex validator
        val = super(module_import_spec, self).normalise_filled(meta, val)

        # Get the parts of the path
        path = self.validators[0].regexes[0][1].match(val).groupdict()

        # Import it
        try:
            module = import_module(path['module'])
        except ImportError:
            raise BadSpecValue("Import not found", wanted=path['module'], meta=meta)

        # Get us the final attribute
        if not hasattr(module, path['class']):
            raise BadSpecValue("Module doesn't have expected class", module=module, has=dir(module), wanted=path['class'], meta=meta)
        val = getattr(module, path['class'])

        # Ensure it's got the expected ancestor
        if not issubclass(val, self.expected_ancestor_kls):
            raise BadSpecValue("Wrong class type"
                , expected = self.expected_ancestor_kls
                , got = val
                , meta = meta
                )

        # Return the result!
        val.module_path = path['module']
        return val

