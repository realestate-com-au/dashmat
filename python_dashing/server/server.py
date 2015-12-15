from python_dashing.option_spec.cronned_checks import CronnedChecks
from python_dashing.jinja_filters import jinja_filters

from tornado.httpserver import HTTPServer
from tornado.wsgi import WSGIContainer
from tornado.ioloop import IOLoop

from flask import send_from_directory, render_template, Response, abort
from flask import Flask

from jinja2.loaders import FileSystemLoader
from jinja2 import Environment
from textwrap import dedent
import pkg_resources
import threading
import logging
import time
import json
import os

log = logging.getLogger("python_dashing.server")

here = os.path.dirname(__file__)

class Server(object):
    def __init__(self, host, port, debug, redis_host, dashboards, modules, module_options, allowed_static_folders, templates_by_module, without_checks):
        self.thread_stopper = {"finished": False}

        self.host = host
        self.port = port
        self.modules = modules
        self.redis_host = redis_host
        self.dashboards = dashboards
        self.module_options = module_options
        self.without_checks = without_checks
        self.templates_by_module = templates_by_module

        self.allowed_static_folders = allowed_static_folders

        static_folder = os.path.join(here, "static")
        if static_folder not in self.allowed_static_folders:
            self.allowed_static_folders.append(static_folder)

        for module in modules.values():
            static_path = pkg_resources.resource_filename(module.relative_to, "static")
            if static_path not in self.allowed_static_folders:
                self.allowed_static_folders.append(static_path)

    def serve(self):
        http_server = HTTPServer(WSGIContainer(self.app))
        http_server.listen(self.port, self.host)
        log.info("Starting server on http://%s:%s", self.host, self.port)

        try:
            IOLoop.instance().start()
        finally:
            self.thread_stopper["finished"] = True

    def start_checks(self, checks, thread_stopper):
        first_run = True
        while True:
            if thread_stopper['finished']:
                break

            try:
                for name, cronned_checks in checks.items():
                    try:
                        cronned_checks.run(force=first_run)
                    except Exception as error:
                        log.error("Failed to run a check for module {0}".format(name))
                        log.exception(error)
            except Exception as error:
                log.error("Failed to do a for loop....")
                log.exception(error)

            first_run = False
            time.sleep(5)

    def template_folders_for(self, module):
        return self.templates_by_module[module] + [os.path.join(here, "templates")]

    @property
    def app(self):
        if getattr(self, "_app", None) is None:
            self._app = Flask("python_dashing.server", static_url_path=os.path.join(here, "static"))
            self._app.jinja_env.add_extension('pyjade.ext.jinja.PyJadeExtension')

            # Remove auto generated static route
            while self._app.url_map._rules:
                self._app.url_map._rules.pop()
            for key in list(self._app.url_map._rules_by_endpoint):
                self._app.url_map._rules_by_endpoint.pop(key)
            self._app.url_map.update()
            self._app.view_functions.clear()

            servers = {}
            for name, module in list(self.modules.items()):
                servers[name] = module.make_server(self.redis_host, self.module_options[name].server_options)

            checks = {}
            if not self.without_checks:
                for name, server in servers.items():
                    registered = list(server.register_checks)
                    if registered:
                        checks[name] = CronnedChecks(registered, module_name=name)


            checks_thread = threading.Thread(target=self.start_checks, args=(checks, self.thread_stopper, ))
            checks_thread.daemon = True
            checks_thread.start()

            # Register our own routes
            self.register_routes(self._app, servers)
        return self._app

    def register_routes(self, app, servers):

        @app.route("/diagnostic/status/heartbeat", methods=['GET'])
        def heartbeat():
            return ""

        @app.route("/diagnostic/status/nagios", methods=['GET'])
        def nagios():
            return "OK"

        @app.route("/diagnostic/version", methods=['Get'])
        def version():
            static_dir = os.path.join(here, "static")
            return send_from_directory(static_dir, "version")

        @app.route('/static/<path:path>', methods=['GET'])
        def static(path):
            if path.startswith("module/"):
                module_name = path.split("/")
                rest = ""
                if len(module_name) == 1:
                    abort(404)

                if len(module_name) == 2:
                    module_name = module_name[1]
                elif len(module_name) == 3:
                    module_name, rest = module_name[1:]

                if module_name in self.modules:
                    path = self.modules[module_name].path_for(rest)
            else:
                while path and path.startswith("/"):
                    path = path[1:]
                path = os.path.join(here, "static", path)

            if any(path.startswith(folder) for folder in self.allowed_static_folders):
                return send_from_directory(os.path.dirname(path), os.path.basename(path))
            else:
                raise abort(404)

        @app.route('/data/<name>')
        def module_data(name):
            if not name in self.modules:
                raise abort(404)
            server = servers[name]
            return json.dumps(server.data)

        @app.route('/<name>')
        def dashboard(name):
            if not name in self.dashboards:
                raise abort(404)
            config = {
                'rows': self.dashboards[name]
            }
            title = name.replace('_', ' ').title()
            return render_template('index.html', config=config, title=title)

        for name, module in self.modules.items():
            for route, view_function in servers[name].routes:
                while route and route.startswith("/"):
                    route = route[1:]

                def make_view(name, view_function):
                    def view(*args, **kwargs):
                        result = view_function(*args, **kwargs)
                        if type(result) is not tuple:
                            return result
                        template, context = view_function(*args, **kwargs)

                        template_env = Environment(loader=FileSystemLoader(self.templates_by_module[name]))
                        template_env.add_extension("pyjade.ext.jinja.PyJadeExtension")
                        self.setup_jinja_env(template_env, dashboard, {})

                        def nonzero(data):
                            return any(item != 0 for item in data)
                        context['nonzero'] = nonzero

                        return template_env.get_template(template).render(context)

                    return view

                view = make_view(name, view_function)
                route_name = "/modules/{0}/{1}".format(name, route)
                view.__name__ = route_name[1:].replace("/", "__")
                log.info("Adding route: {0}".format(route_name))
                app.route(route_name)(view)

    def setup_jinja_env(self, env, dashboard, activated_clients):
        def module_filter(name, **client_options):
            module = self.modules[name]
            for dependency in module.dependencies():
                if dependency not in activated_clients:
                    activated_clients[dependency] = self.modules[dependency].make_client({})

            if name not in activated_clients:
                activated_clients[name] = module.make_client(client_options)

            template_env = Environment(loader=FileSystemLoader(self.templates_by_module[name]))
            template_env.add_extension("pyjade.ext.jinja.PyJadeExtension")
            self.setup_jinja_env(template_env, dashboard, activated_clients)

            return template_env.get_template(activated_clients[name].template_name).render(activated_clients[name].template_context)
        env.filters["module"] = module_filter

        env.filters.update(jinja_filters)

