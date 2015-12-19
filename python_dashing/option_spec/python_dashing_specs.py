"""
Here we define the yaml specification for python_dashing options

The specifications are responsible for sanitation, validation and normalisation.
"""

from python_dashing.formatter import MergedOptionStringFormatter

from input_algorithms.validators import regexed
from input_algorithms.spec_base import (
      defaulted, boolean, string_spec, formatted, match_spec, valid_string_spec, listof, overridden
    , filename_spec, dictof, create_spec, dictionary_spec, required, integer_spec, Spec, Spec
    , directory_spec
    )
from input_algorithms.dictobj import dictobj

from textwrap import dedent
import six

class Dashboard(dictobj):
    fields = {
          'path': "Url path to the dashboard"

        , 'es6': "Extra es6 javascript to add to the dashboard module"
        , 'layout': "Reactjs xml for the layout of the dashboard"
        , 'imports': "es6 imports for the dashboard"
        }

    def make_dashboard_module(self):
        return dedent("""
            {imports}

            class Dashboard extends React.Component {{
                render() {{
                    return (
                        {layout}
                    )
                }};

                {es6}
            }}

            document.addEventListener("DOMContentLoaded", function(event) {{
                var element = React.createElement(Dashboard);
                ReactDOM.render(element, document.getElementById('page-content'));
            }});
        """).format(imports="\n".join(self.imports), layout=self.layout, es6=self.es6)

class PythonDashing(dictobj):
    fields = {
          "debug": "Set debug capability"
        , "host": "The host to serve the server on"
        , "port": "The port to serve the server on"
        , "dry_run": "Whether to do a dry run or not"
        , "extra": "Sets the ``$@`` variable. Alternatively specify these after a ``--`` on the commandline"
        , "artifact": "Arbitrary argument"
        , "config": "The config filename"
        , "allowed_static_folders": "The folders we're allowed to use as static folders"
        , "without_checks": "Whether to run the cronned checks or not"
        , "compiled_static_prep": "Folder for preparing webpack bundles"
        , "compiled_static_folder": "Folder to cache compiled javascript"
        }

class ModuleOptions(dictobj):
    fields = {
          "active": "Is this module active?"
        , "import_path": "Import path to the module to load"
        , "server_options": "Options to pass into creating the Server class"
        }

class PythonDashingSpec(object):
    """Knows about python_dashing specific configuration"""

    @property
    def python_dashing_spec(self):
        """Spec for python_dashing options"""
        formatted_string = lambda: formatted(string_spec(), MergedOptionStringFormatter)
        return create_spec(PythonDashing
            , host = defaulted(formatted_string(), "localhost")
            , port = defaulted(formatted(integer_spec(), MergedOptionStringFormatter), 7546)
            , config = filename_spec()
            , extra = defaulted(formatted_string(), "")
            , debug = defaulted(boolean(), False)
            , dry_run = defaulted(boolean(), False)
            , artifact = formatted_string()
            , allowed_static_folders = listof(formatted_string())
            , without_checks = defaulted(boolean(), False)
            , compiled_static_prep = directory_spec(formatted(defaulted(string_spec(), "{config_root}/compiled_prep"), MergedOptionStringFormatter))
            , compiled_static_folder = directory_spec(formatted(defaulted(string_spec(), "{config_root}/compiled_static"), MergedOptionStringFormatter))
            )

    @property
    def templates_spec(self):
        """Spec for templates"""
        return dictof(string_spec(), dictionary_spec())

    @property
    def modules_spec(self):
        """Spec for modules"""
        valid_import_name = regexed("[a-zA-Z_][a-zA-Z_0-9]*(\.[a-zA-Z_][a-zA-Z_0-9]*)*:[a-zA-Z_][a-zA-Z_0-9]")

        formatted_dict_or_string = lambda: match_spec(
              (six.string_types, formatted(string_spec(), MergedOptionStringFormatter))
            , fallback = lambda: dictof(string_spec(), formatted_dict_or_string())
            )

        return dictof(string_spec(), create_spec(ModuleOptions
            , active = defaulted(boolean(), True)
            , import_path = required(formatted(valid_string_spec(valid_import_name), formatter=MergedOptionStringFormatter))
            , server_options = dictof(string_spec(), formatted_dict_or_string())
            ))

    @property
    def dashboards_spec(self):
        return dictof(string_spec()
            , create_spec(Dashboard
                , path = formatted(overridden("{_key_name_0}"), MergedOptionStringFormatter)
                , imports = listof(string_spec())
                , es6 = string_spec()
                , layout = string_spec()
                )
            )

