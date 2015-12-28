"""
Here we define the yaml specification for python_dashing options

The specifications are responsible for sanitation, validation and normalisation.
"""

from python_dashing.formatter import MergedOptionStringFormatter
from python_dashing.errors import UnknownModule

from input_algorithms.many_item_spec import many_item_formatted_spec
from input_algorithms.validators import regexed
from input_algorithms.spec_base import (
      defaulted, boolean, string_spec, formatted, match_spec, valid_string_spec, listof, overridden
    , filename_spec, dictof, create_spec, dictionary_spec, required, integer_spec, Spec, Spec
    , directory_spec, optional_spec, or_spec
    )
from input_algorithms.dictobj import dictobj

from textwrap import dedent
import six

valid_import_name = regexed("[a-zA-Z_][a-zA-Z_0-9]*(\.[a-zA-Z_][a-zA-Z_0-9]*)*:[a-zA-Z_][a-zA-Z_0-9]")

formatted_dict_or_string_or_list = lambda: match_spec(
      (six.string_types, formatted(string_spec(), MergedOptionStringFormatter))
    , ((list, ), lambda: listof(formatted_dict_or_string_or_list()))
    , fallback = lambda: dictof(string_spec(), formatted_dict_or_string_or_list())
    )

class import_line_spec(many_item_formatted_spec):
    value_name = "Import line"
    specs = [listof(string_spec()), string_spec()]
    optional_specs = [string_spec()]

    def create_result(self, imports, module_name, import_from, meta, val, dividers):
        """Default permissions to rw"""
        options = {"imports": imports, "module_name": module_name, "import_from": import_from}
        return ImportLine.FieldSpec(formatter=MergedOptionStringFormatter).normalise(meta, options)

class ImportLine(dictobj.Spec):
    module_name = dictobj.Field(
          string_spec
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
        if self.module_name not in modules:
            raise UnknownModule(module=self.module_name, available=list(modules.keys()))

        if len(self.imports) is 1:
            imports = self.imports[0]
        else:
            imports = "{{{0}}}".format(", ".join(self.imports))

        relative_to = modules[self.module_name].relative_to
        return 'import {0} from "/modules/{1}/{2}"'.format(imports, relative_to, self.import_from)

class Dashboard(dictobj.Spec):
    path = dictobj.Field(
          overridden("{_key_name_1}")
        , formatted = True
        , help = "Url path to the dashboard"
        )

    es6 = dictobj.Field(
          string_spec
        , help = "Extra es6 javascript to add to the dashboard module"
        )

    layout = dictobj.Field(
          string_spec
        , help = "Reactjs xml for the laytout of the dashboard"
        )

    imports = dictobj.Field(
          lambda: or_spec(string_spec(), listof(import_line_spec()))
        , help = "es6 imports for the dashboard"
        )

    enabled_modules = dictobj.Field(
          string_spec
        , formatted = True
        , wrapper = listof
        , help = "The modules to enable for this dashboard"
        )

    def make_dashboard_module(self, modules):
        imports = []
        for imprt in self.imports:
            if hasattr(imprt, "import_line"):
                imports.append(imprt.import_line(modules))
            else:
                imports.append(imprt)

        return dedent("""
            import styles from "/modules/python_dashing.server/Dashboard.css";
            import React, {{Component}} from 'react';
            import ReactDOM from 'react-dom';
            {imports}

            class Dashboard extends Component {{
                render() {{
                    return (
                        <div className={{styles.dashboard}}>
                            {layout}
                        </div>
                    )
                }};

                {es6}
            }}

            document.addEventListener("DOMContentLoaded", function(event) {{
                var element = React.createElement(Dashboard);
                ReactDOM.render(element, document.getElementById('page-content'));
            }});
        """).format(imports="\n".join(imports), layout=self.layout, es6=self.es6)

class PythonDashing(dictobj.Spec):
    debug = dictobj.Field(
          boolean
        , default = False
        , formatted = True
        , help = "Set debug capability"
        )

    host = dictobj.Field(
          string_spec
        , default = "localhost"
        , formatted = True
        , help = "The host to serve the server on"
        )

    port = dictobj.Field(
          integer_spec
        , default = 7546
        , formatted = True
        , help = "The port to serve the server on"
        )

    artifact = dictobj.Field(
          string_spec
        , formatted = True
        , help = "Arbitrary argument"
        )

    redis_host = dictobj.Field(
          string_spec
        , formatted = True
        , help = "Location of redis host for storing values"
        )

    config = dictobj.Field(
          filename_spec
        , help = "The config filename"
        )

    without_checks = dictobj.Field(
          boolean
        , default = False
        , formatted = True
        , help = "Whether to run the cronned checks or not"
        )

    dynamic_dashboard_js = dictobj.Field(
          boolean
        , default = True
        , formatted = True
        , help = "Whether to use docker to generate dashboard js at runtime"
        )

    compiled_static_prep = dictobj.Field(
          string_spec
        , default = "{config_root}/compiled_prep"
        , formatted = True
        , wrapper = directory_spec
        , help = "Folder for preparing webpack bundles"
        )

    compiled_static_folder = dictobj.Field(
          string_spec
        , default = "{config_root}/compiled_static"
        , formatted = True
        , wrapper = directory_spec
        , help = "Folder to cache compiled javascript"
        )

class ModuleOptions(dictobj.Spec):
    active = dictobj.Field(
          boolean
        , default = True
        , formatted = True
        , help = "Is this module active?"
        )

    import_path = dictobj.Field(
          valid_string_spec(valid_import_name)
        , formatted = True
        , wrapper = required
        , help = "Import path to the module to load"
        )

    server_options = dictobj.Field(
          lambda: dictof(string_spec(), formatted_dict_or_string_or_list())
        , help = "Options to pass into creating the Server class"
        )

PythonDashingConverters = lambda: dict(
      modules = dictof(string_spec(), ModuleOptions.FieldSpec(formatter=MergedOptionStringFormatter))
    , templates = dictof(string_spec(), dictionary_spec())
    , dashboards = dictof(string_spec(), Dashboard.FieldSpec(formatter=MergedOptionStringFormatter))
    , python_dashing = PythonDashing.FieldSpec(formatter=MergedOptionStringFormatter)
    )

