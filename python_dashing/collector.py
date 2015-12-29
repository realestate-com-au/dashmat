"""
Collects then parses configuration files and verifies that they are valid.
"""

from python_dashing.option_spec.python_dashing_specs import PythonDashingConverters
from python_dashing.errors import BadConfiguration, BadYaml, BadImport
from python_dashing.importer import import_module

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

log = logging.getLogger("python_dashing.collector")

class Collector(CollectorBase):

    BadFileErrorKls = BadYaml
    BadConfigurationErrorKls = BadConfiguration

    def alter_clone_args_dict(self, new_collector, new_args_dict, new_python_dashing_options=None):
        new_python_dashing = self.configuration["python_dashing"].clone()
        if new_python_dashing_options:
            new_python_dashing.update(new_python_dashing_options)
        new_args_dict["python_dashing"] = new_python_dashing

    def extra_prepare(self, configuration, args_dict):
        """Called before the configuration.converters are activated"""
        python_dashing = args_dict.pop("python_dashing")

        self.configuration.update(
            { "python_dashing": python_dashing }
        , source = "<args_dict>"
        )

    def home_dir_configuration_location(self):
        return os.path.expanduser("~/.python-dashingrc.yml")

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
        imported = {}
        registered = {}
        active_modules = {}

        def make_converter(name, spec):
            def converter(p, v):
                log.info("Converting %s", p)
                meta = Meta(p.configuration, [(name, "")])
                configuration.converters.started(p)
                return spec.normalise(meta, v)
            return converter
        configuration.install_converters(PythonDashingConverters(), make_converter)

        if "modules" in configuration and type(configuration["modules"]) is dict:
            found = {}
            first_pass_imported = {}
            for module_options in configuration["modules"].values():
                if "import_path" in module_options:
                    self.activate_module(None, module_options["import_path"], {}, found, first_pass_imported)

            by_name = dict((r[1], found[r]) for r in found)
            for thing in list(by_name.keys()):
                def make_converter(thing):
                    def converter(p, v):
                        log.info("Converting %s", p)
                        meta = Meta(p.configuration, [(thing, "")])
                        configuration.converters.started(p)
                        return by_name[thing].normalise(meta, v)
                    return converter
                configuration.add_converter(Converter(convert=make_converter(thing), convert_path=[thing]))

        configuration.converters.activate()
        if "modules" in configuration:
            for name, module in configuration["modules"].items():
                if module.active:
                    self.activate_module(name, module.import_path, active_modules, registered, imported)

        configuration['__imported__'] = imported
        configuration['__registered__'] = list(registered.values())
        configuration['__active_modules__'] = active_modules

    def extra_prepare_after_activation(self, configuration, args_dict):
        imported = configuration['__imported__']
        registered = dict((name, name) for name in configuration['__registered__'])
        active_modules = configuration['__active_modules__']
        module_options = configuration["modules"]

        options = namedtuple("Options", ["import_path", "server_options"])
        for dashboard in configuration["dashboards"].values():
            for imprt in dashboard.imports:
                if hasattr(imprt, "module_name") and type(imprt.module_name) is dict:
                    module_name = imprt.module_name["import_path"]
                    if module_name not in active_modules:
                        self.activate_module(module_name, module_name, active_modules, registered, imported)
                        if module_name not in module_options:
                            module_options[module_name] = options(module_name, {})
        configuration['__registered__'] = list(registered.values())

        def find_deps():
            added = False
            for name, module in list(active_modules.items()):
                for dependency in module.dependencies():
                    if dependency not in active_modules:
                        added = True
                        active_modules[dependency] = imported[dependency](dependency, dependency)
                        if dependency not in module_options:
                            module_options[dependency] = options(dependency, {})
            if added:
                find_deps()
        find_deps()

    def activate_module(self, name, import_path, active_modules, registered, imported):
        if import_path not in imported:
            import_module_path, import_class = import_path.split(":")
            module = import_module(import_module_path)

            if not hasattr(module, import_class):
                raise BadImport("Failed to find the specified class", wanted=import_class, module=module, available=dir(module))

            imported[import_path] = getattr(module, import_class)
            registered.update(imported[import_path].register_configuration())
            for dependency in imported[import_path].dependencies():
                self.activate_module(None, dependency, active_modules, registered, imported)

        # Instantiate the module for this instance of it
        if name is not None:
            active_modules[name] = imported[import_path](name, import_path)

