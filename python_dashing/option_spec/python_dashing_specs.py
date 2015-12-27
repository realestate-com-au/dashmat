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

valid_import_name = regexed("[a-zA-Z_][a-zA-Z_0-9]*(\.[a-zA-Z_][a-zA-Z_0-9]*)*:[a-zA-Z_][a-zA-Z_0-9]")

formatted_dict_or_string_or_list = lambda: match_spec(
      (six.string_types, formatted(string_spec(), MergedOptionStringFormatter))
    , ((list, ), lambda: listof(formatted_dict_or_string_or_list()))
    , fallback = lambda: dictof(string_spec(), formatted_dict_or_string_or_list())
    )

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
          listof(string_spec())
        , help = "es6 imports for the dashboard"
        )

    def make_dashboard_module(self):
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
        """).format(imports="\n".join(self.imports), layout=self.layout, es6=self.es6)

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

