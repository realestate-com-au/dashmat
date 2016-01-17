"""
Here we define the yaml specification for python_dashing options

The specifications are responsible for sanitation, validation and normalisation.
"""

from python_dashing.formatter import MergedOptionStringFormatter
from python_dashing.option_spec.dashboard import Dashboard

from input_algorithms.validators import regexed
from input_algorithms.spec_base import (
      boolean, string_spec, formatted, match_spec, valid_string_spec, listof
    , filename_spec, dictof, dictionary_spec, required, integer_spec
    , directory_spec, delayed, Spec
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

class dashboard_spec(Spec):
    def normalise(self, meta, val):
        val = dictionary_spec().normalise(meta, val)
        if val.get("is_index"):
            index_items = []
            for path, dashboard in meta.everything["dashboards"].items():
                if not dashboard.get("is_index"):
                    index_items.append('<IndexItem href="{0}" desc="{1}" />'.format(path, dashboard.get("description")))

            val['layout'] = dedent("""
                <Index>
                    {0}
                </Index>
            """.format('\n'.join(index_items)))

            val['imports'] = [[["Index", "IndexItem"], {"import_path": "python_dashing.core_modules.index.main:Index"}]]

        return Dashboard.FieldSpec(formatter=MergedOptionStringFormatter).normalise(meta, val)

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
        , wrapper = delayed
        , help = "Options to pass into creating the Server class"
        )

PythonDashingConverters = lambda: dict(
      modules = dictof(string_spec(), ModuleOptions.FieldSpec(formatter=MergedOptionStringFormatter))
    , templates = dictof(string_spec(), dictionary_spec())
    , dashboards = dictof(string_spec(), dashboard_spec())
    , python_dashing = PythonDashing.FieldSpec(formatter=MergedOptionStringFormatter)
    )

