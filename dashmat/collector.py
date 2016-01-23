"""
Collects then parses configuration files and verifies that they are valid.
"""

from dashmat.option_spec.module_imports import module_import_spec
from dashmat.option_spec.dashmat_specs import DashMatConverters
from dashmat.errors import BadConfiguration, BadYaml, BadImport
from dashmat.option_spec.dashmat_specs import ModuleOptions
from dashmat.core_modules.base import Module

from input_algorithms.dictobj import dictobj
from input_algorithms.meta import Meta

from option_merge.collector import Collector as CollectorBase
from option_merge import MergedOptions
from option_merge import Converter

from collections import namedtuple
import pkg_resources
import logging
import yaml
import os

log = logging.getLogger("dashmat.collector")

class Collector(CollectorBase):

    BadFileErrorKls = BadYaml
    BadConfigurationErrorKls = BadConfiguration

    def alter_clone_args_dict(self, new_collector, new_args_dict, new_dashmat_options=None):
        new_dashmat = self.configuration["dashmat"].clone()
        if new_dashmat_options:
            new_dashmat.update(new_dashmat_options)
        new_args_dict["dashmat"] = new_dashmat

    def extra_prepare(self, configuration, args_dict):
        """Called before the configuration.converters are activated"""
        dashmat = args_dict.pop("dashmat")

        self.configuration.update(
          { "dashmat": dashmat
          }
        , source = "<args_dict>"
        )

    def home_dir_configuration_location(self):
        return os.path.expanduser("~/.dashmatrc.yml")

    def start_configuration(self):
        """Create the base of the configuration"""
        return MergedOptions(dont_prefix=[dictobj])

    def read_file(self, location):
        """Read in a yaml file and return as a python object"""
        try:
            return yaml.load(open(location))
        except (yaml.parser.ParserError, yaml.scanner.ScannerError) as error:
            raise self.BadFileErrorKls("Failed to read yaml", location=location, error_type=error.__class__.__name__, error="{0}{1}".format(error.problem, error.problem_mark))

    def add_configuration(self, configuration, collect_another_source, done, result, src):
        """Used to add a file to the configuration, result here is the yaml.load of the src"""
        configuration.update(result, source=src)

    def extra_configuration_collection(self, configuration):
        """Hook to do any extra configuration collection or converter registration"""
        configuration["__imported__"] = {}
        configuration["__registered__"] = {}
        configuration["__active_modules__"] = {}

        def make_converter(name, spec):
            def converter(p, v):
                log.info("Converting %s", p)
                meta = Meta(p.configuration, [(name, "")])
                configuration.converters.started(p)
                return spec.normalise(meta, v)
            return converter
        configuration.install_converters(DashMatConverters(), make_converter)

        if "modules" in configuration:
            for module_name, module_options in list(configuration["modules"].items()):
                if "import_path" in module_options:
                    module = module_import_spec(Module).normalise(Meta(configuration, []).at("modules").at(module_name), module_options["import_path"])
                    import_path = "{0}:{1}".format(module.module_path, module.__name__)
                    self.activate_module(module_name, import_path, module, configuration)
                    configuration[["modules", module_name, "import_path"]] = module

    def extra_prepare_after_activation(self, configuration, args_dict):
        for dashboard in configuration["dashboards"].values():
            for imprt in dashboard.imports:
                if hasattr(imprt, "module_name") and type(imprt.module_name) is dict:
                    module = imprt.module_name["import_path"]
                    import_path = "{0}:{1}".format(module.module_path, module.__name__)
                    self.activate_module(import_path, import_path, module, configuration)

        for (_, thing), spec in sorted(configuration["__registered__"].as_dict().items()):
            def make_converter(thing, spec):
                def converter(p, v):
                    log.info("Converting %s", p)
                    meta = Meta(p.configuration, [(thing, "")])
                    configuration.converters.started(p)
                    return spec.normalise(meta, v)
                return converter
            converter = make_converter(thing, spec)
            configuration.add_converter(Converter(convert=converter, convert_path=[thing]))

    def activate_module(self, name, import_path, module, configuration):
        imported = configuration['__imported__']
        registered = configuration["__registered__"]
        module_options = configuration["modules"]
        active_modules = configuration['__active_modules__']

        if import_path not in imported:
            imported[import_path] = module
            configuration["__registered__"].update(imported[import_path].register_configuration())

        if import_path not in module_options and name == import_path:
            module_options[import_path] = ModuleOptions(import_path=import_path, server_options={}, active=True)

        for dependency in imported[import_path].dependencies():
            if dependency not in imported:
                m = module_import_spec(Module).normalise(Meta(configuration, []), dependency)
                ip = "{0}:{1}".format(m.module_path, m.__name__)
                self.activate_module(ip, ip, m, configuration)

        if name not in active_modules:
            active_modules[name] = imported[import_path](name, import_path)

