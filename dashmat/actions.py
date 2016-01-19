from dashmat.server.server import Server, generate_dashboard_js
from dashmat.datastore import JsonDataStore, RedisDataStore
from dashmat.server.react import ReactServer
from dashmat.scheduler import Scheduler

from input_algorithms.spec_base import NotSpecified
from textwrap import dedent
import logging
import redis
import json
import six
import sys
import os

log = logging.getLogger("dashmat.actions")

available_actions = {}

def an_action(func):
    available_actions[func.__name__] = func
    func.label = "Default"
    return func

@an_action
def list_tasks(collector):
    """List the available_tasks"""
    print("Usage: dashmat <task>")
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
    dashboards = collector.configuration["dashboards"]
    module_options = collector.configuration["modules"]
    dashmat = collector.configuration["dashmat"]

    config_root = collector.configuration["config_root"]
    datastore = JsonDataStore(os.path.join(config_root, "data.json"))
    if dashmat.redis_host:
        datastore = RedisDataStore(redis.Redis(dashmat.redis_host))

    Server(
          dashmat.host
        , dashmat.port
        , dashmat.debug
        , dashboards
        , modules
        , module_options
        , datastore
        , dashmat.dynamic_dashboard_js
        , dashmat.compiled_static_prep
        , dashmat.compiled_static_folder
        , dashmat.without_checks
        ).serve()

@an_action
def requirements(collector):
    """Just print out the requirements"""
    out = sys.stdout
    artifact = collector.configuration['dashmat'].artifact
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
    artifact = collector.configuration["dashmat"].artifact
    chosen = artifact
    if chosen in (None, "", NotSpecified):
        chosen = None

    modules = collector.configuration["__active_modules__"]
    module_options = collector.configuration["modules"]

    scheduler = Scheduler()

    for name, module in modules.items():
        if chosen is None or name == chosen:
            server = module.make_server(module_options[name].server_options)
            scheduler.register(module, server, name)

    config_root = collector.configuration["config_root"]
    dashmat = collector.configuration["dashmat"]
    datastore = JsonDataStore(os.path.join(config_root, "data.json"))
    if dashmat.redis_host:
        datastore = RedisDataStore(redis.Redis(dashmat.redis_host))

    scheduler.run(datastore, force=True)

@an_action
def list_npm_modules(collector, no_print=False):
    """List the npm modules that get installed in a docker image for the react server"""
    default = ReactServer().default_npm_deps()
    for _, module in sorted(collector.configuration["__active_modules__"].items()):
        default.update(module.npm_deps())

    if not no_print:
        print(json.dumps(default, indent=4, sort_keys=True))
    return default

@an_action
def collect_dashboard_js(collector):
    """Generate dashboard javascript for each dashboard"""
    dashmat = collector.configuration["dashmat"]

    modules = collector.configuration["__active_modules__"]
    compiled_static_prep = dashmat.compiled_static_prep
    compiled_static_folder = dashmat.compiled_static_folder

    npm_deps = list_npm_modules(collector, no_print=True)
    react_server = ReactServer()
    react_server.prepare(npm_deps, compiled_static_folder)

    for dashboard in collector.configuration["dashboards"].values():
        log.info("Generating compiled javascript for dashboard:{0}".format(dashboard.path))
        filename = dashboard.path.replace("_", "__").replace("/", "_")
        location = os.path.join(compiled_static_folder, "dashboards", "{0}.js".format(filename))
        if os.path.exists(location):
            os.remove(location)
        generate_dashboard_js(dashboard, react_server, compiled_static_folder, compiled_static_prep, modules)

