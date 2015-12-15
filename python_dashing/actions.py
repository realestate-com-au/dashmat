from python_dashing.server.server import Server
from python_dashing.scheduler import Scheduler

from input_algorithms.spec_base import NotSpecified
from collections import namedtuple
from textwrap import dedent
import logging
import six
import sys

log = logging.getLogger("python_dashing.actions")

available_actions = {}

def an_action(func):
    available_actions[func.__name__] = func
    func.label = "Default"
    return func

@an_action
def list_tasks(collector):
    """List the available_tasks"""
    print("Usage: python-dashing <task>")
    print("")
    print("Available tasks to choose from are:")
    print("-----------------------------------")
    print("")
    keygetter = lambda item: item[1].label
    tasks = sorted(available_actions.items(), key=keygetter)
    sorted_tasks = sorted(list(tasks), key=lambda item: len(item[0]))
    max_length = max(len(name) for name, _ in sorted_tasks)
    for key, task in sorted_tasks:
        desc = dedent(task.__doc__ or "").strip().split('\n')[0]
        print("\t{0}{1} :-: {2}".format(" " * (max_length-len(key)), key, desc))
    print("")

@an_action
def serve(collector):
    modules = collector.configuration["__active_modules__"]
    imported = collector.configuration["__imported__"]
    dashboards = collector.configuration["dashboards"]
    module_options = collector.configuration["modules"]
    python_dashing = collector.configuration["python_dashing"]
    templates_by_module = collector.configuration["__module_template_folders__"]

    options = namedtuple("Options", ["import_path", "server_options"])
    for name, module in list(modules.items()):
        for dependency in module.dependencies():
            if dependency not in modules:
                modules[dependency] = imported[dependency](dependency)
                if dependency not in module_options:
                    module_options[dependency] = options(dependency, {})

    Server(
          python_dashing.host
        , python_dashing.port
        , python_dashing.debug
        , dashboards
        , modules
        , module_options
        , python_dashing.allowed_static_folders
        , templates_by_module
        , python_dashing.without_checks
        ).serve()

@an_action
def requirements(collector):
    """Just print out the requirements"""
    out = sys.stdout
    artifact = collector.configuration['python_dashing'].artifact
    if artifact not in (None, "", NotSpecified):
        if isinstance(artifact, six.string_types):
            out = open(artifact, 'w')
        else:
            out = artifact

    for active in collector.configuration['__imported__'].values():
        for requirement in active.requirements():
            out.write("{0}\n".format(requirement))

@an_action
def run_checks(collector):
    """Just run the checks for our modules"""
    artifact = collector.configuration["python_dashing"].artifact
    chosen = artifact
    if chosen in (None, "", NotSpecified):
        chosen = None

    modules = collector.configuration["__active_modules__"]
    module_options = collector.configuration["modules"]

    scheduler = Scheduler()

    for name, module in modules.items():
        if chosen is None or name == chosen:
            log.info("Making server for {0} module".format(name))
            server = modules[name].make_server(module_options[name].server_options)
            scheduler.register(server, name)

    scheduler.run(force=True)

