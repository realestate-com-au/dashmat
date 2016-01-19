from dashmat.formatter import MergedOptionStringFormatter
from dashmat.errors import UnknownModule

from input_algorithms.spec_base import boolean, string_spec, formatted, listof, overridden, or_spec, set_options
from input_algorithms.many_item_spec import many_item_formatted_spec
from input_algorithms.dictobj import dictobj

class import_line_spec(many_item_formatted_spec):
    value_name = "Import line"
    specs = [listof(string_spec()), or_spec(string_spec(), set_options(import_path=string_spec()))]
    optional_specs = [string_spec()]

    def create_result(self, imports, module_name, import_from, meta, val, dividers):
        """Default permissions to rw"""
        options = {"imports": imports, "module_name": module_name, "import_from": import_from}
        return ImportLine.FieldSpec(formatter=MergedOptionStringFormatter).normalise(meta, options)

class ImportLine(dictobj.Spec):
    module_name = dictobj.Field(
          lambda: or_spec(string_spec(), set_options(import_path=string_spec()))
        , formatted = True
        , help = "The name of the module this import comes from"
        )

    imports = dictobj.Field(
          string_spec
        , formatted = True
        , wrapper = listof
        , help = "The modules that are imported"
        )

    import_from = dictobj.Field(
          string_spec
        , formatted = True
        , default = "main.jsx"
        , help = "The module in our import_path to import the imports from"
        )

    def import_line(self, modules):
        module_name = self.module_name
        if type(module_name) is dict:
            module_name = self.module_name['import_path']

        if module_name not in modules:
            raise UnknownModule(module=module_name, available=list(modules.keys()))

        imports = "{{{0}}}".format(", ".join(self.imports))
        relative_to = modules[module_name].relative_to
        return 'import {0} from "/modules/{1}/{2}"'.format(imports, relative_to, self.import_from)

